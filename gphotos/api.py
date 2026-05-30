from __future__ import annotations

import base64
import hashlib
import logging
import os
import time
from typing import Callable, Optional

import httpx
from google.protobuf import message as proto_message

from .auth import AuthManager
from .retry import RetryConfig, calculate_backoff, should_retry

from .AddMediaToAlbum_pb2 import AddMediaToAlbum
from .CommitToken_pb2 import CommitToken
from .CommitUpload_pb2 import CommitUpload
from .CommitUploadResponse_pb2 import CommitUploadResponse
from .CreateAlbum_pb2 import CreateAlbum
from .CreateAlbumResponse_pb2 import CreateAlbumResponse
from .GetUploadToken_pb2 import GetUploadToken
from .HashCheck_pb2 import HashCheck
from .RemoteMatches_pb2 import RemoteMatches

log = logging.getLogger(__name__)


class GooglePhotosAPI:
    def __init__(
        self,
        auth_string: str,
        language: str = "en",
        proxy: str = "",
        saver_mode: bool = False,
        use_quota: bool = False,
    ):
        transport = httpx.HTTPTransport(retries=0)
        if proxy:
            transport = httpx.HTTPTransport(proxy=httpx.Proxy(proxy))

        self._user_agent = (
            "com.google.android.apps.photos/49029607 "
            "(Linux; U; Android 9; en; Pixel XL; Build/PQ2A.190205.001; "
            "Cronet/127.0.6510.5) (gzip)"
        )
        self._client = httpx.Client(
            transport=transport,
            timeout=None,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=20,
            ),
            headers={
                "Accept-Encoding": "gzip",
                "Accept-Language": language,
                "User-Agent": self._user_agent,
            },
        )
        self._auth = AuthManager(self._client, language)
        self._auth_string = auth_string
        self._language = language
        self._retry_config = RetryConfig(max_retries=3)

        self._android_api_version = 28
        self._model = "Pixel 2" if saver_mode else "Pixel XL"
        if use_quota:
            self._model = "Pixel 8"
        self._make = "Google"
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _bearer(self) -> str:
        return self._auth.get_bearer_token(self._auth_string)

    def _post_proto_raw(
        self,
        url: str,
        data: bytes,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        headers = {
            "Content-Type": "application/x-protobuf",
            "Authorization": f"Bearer {self._bearer()}",
            "User-Agent": self._user_agent,
        }
        if extra_headers:
            headers.update(extra_headers)

        last_error: Optional[Exception] = None
        for attempt in range(self._retry_config.max_retries + 1):
            try:
                resp = self._client.post(url, content=data, headers=headers)
                resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                last_error = e
                if isinstance(e, httpx.HTTPStatusError) and not should_retry(
                    e.response.status_code
                ):
                    raise
                if attempt < self._retry_config.max_retries:
                    delay = calculate_backoff(attempt, self._retry_config)
                    log.info(f"Retrying in {delay:.1f}s (attempt {attempt+2}/{self._retry_config.max_retries+1})")
                    time.sleep(delay)

        raise RuntimeError(
            f"Request failed after {self._retry_config.max_retries + 1} attempts: {last_error}"
        )

    def get_upload_token(self, sha1_b64: str, file_size: int) -> str:
        msg = GetUploadToken(
            f1=2, f2=2, f3=1, f4=3, file_size_bytes=file_size
        )
        data = msg.SerializeToString()

        resp = self._post_proto_raw(
            "https://photos.googleapis.com/data/upload/uploadmedia/interactive",
            data,
            {
                "X-Goog-Hash": f"sha1={sha1_b64}",
                "X-Upload-Content-Length": str(file_size),
            },
        )
        upload_id = resp.headers.get("X-GUploader-UploadID")
        if not upload_id:
            raise RuntimeError("Missing X-GUploader-UploadID header")
        return upload_id

    def get_upload_token_skip_hash(self, file_size: int) -> str:
        """Get upload token without X-Goog-Hash (hash computed during upload)."""
        msg = GetUploadToken(
            f1=2, f2=2, f3=1, f4=3, file_size_bytes=file_size
        )
        data = msg.SerializeToString()

        resp = self._post_proto_raw(
            "https://photos.googleapis.com/data/upload/uploadmedia/interactive",
            data,
            {
                "X-Upload-Content-Length": str(file_size),
            },
        )
        upload_id = resp.headers.get("X-GUploader-UploadID")
        if not upload_id:
            raise RuntimeError("Missing X-GUploader-UploadID header")
        return upload_id

    def upload_file(
        self,
        file_path: str,
        upload_id: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
        resume_offset: int = 0,
        compute_hash: bool = False,
        hash_out: Optional[list] = None,
    ) -> CommitToken:
        file_size = os.path.getsize(file_path)
        upload_url = (
            "https://photos.googleapis.com/data/upload/uploadmedia/interactive"
            f"?upload_id={upload_id}"
        )

        last_error: Optional[Exception] = None
        for attempt in range(self._retry_config.max_retries + 1):
            if self._cancelled:
                raise RuntimeError("Upload cancelled")
            try:
                return self._do_upload_attempt(
                    file_path, upload_url, file_size, on_progress, attempt,
                    resume_offset, compute_hash, hash_out,
                )
            except (httpx.RequestError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                last_error = e
                if isinstance(e, httpx.HTTPStatusError) and not should_retry(e.response.status_code):
                    raise
                if attempt < self._retry_config.max_retries:
                    delay = calculate_backoff(attempt, self._retry_config)
                    log.info(f"Upload retry in {delay:.1f}s (attempt {attempt+2})")
                    time.sleep(delay)

        raise RuntimeError(
            f"Upload failed after {self._retry_config.max_retries + 1} attempts: {last_error}"
        )

    def try_resume_session(
        self, upload_id: str, file_size: int
    ) -> tuple[Optional[int], Optional[CommitToken]]:
        """Check if a previous upload session can be resumed.
        
        Returns (offset, None) to resume from offset, or (None, token) if already complete,
        or (None, None) if session expired.
        """
        upload_url = (
            "https://photos.googleapis.com/data/upload/uploadmedia/interactive"
            f"?upload_id={upload_id}"
        )
        return self._try_resume(upload_url, file_size)

    def _try_resume(self, upload_url: str, file_size: int) -> tuple[Optional[int], Optional[CommitToken]]:
        """Query upload status. Returns (resume_from_byte, commit_token).
        
        - (None, None): No existing session, upload from scratch
        - (offset, None): Resume from offset+1
        - (None, token): Upload already complete
        """
        try:
            resp = self._client.put(
                upload_url,
                content=b"",
                headers={
                    "Authorization": f"Bearer {self._bearer()}",
                    "Content-Length": "0",
                    "Content-Range": f"bytes */{file_size}",
                    "User-Agent": self._user_agent,
                },
            )
            if resp.status_code == 200 or resp.status_code == 201:
                token = CommitToken()
                token.ParseFromString(resp.content)
                return (None, token)
            if resp.status_code == 308:
                range_header = resp.headers.get("Range", "")
                if "=" in range_header:
                    parts = range_header.split("=")[1].split("-")
                    last_byte = int(parts[1]) if len(parts) > 1 and parts[1] else None
                    if last_byte is not None:
                        log.info(f"Resumable: bytes 0-{last_byte} received")
                        return (last_byte, None)
                return (0, None)
            return (None, None)
        except Exception:
            return (None, None)

    def _do_upload_attempt(
        self,
        file_path: str,
        upload_url: str,
        file_size: int,
        on_progress: Optional[Callable[[int, int], None]] = None,
        attempt: int = 0,
        start_byte: int = 0,
        compute_hash: bool = False,
        hash_out: Optional[list] = None,
    ) -> CommitToken:
        import typing
        import hashlib

        # On retries, also check if server has partial data
        if attempt > 0:
            resume_byte, existing_token = self._try_resume(upload_url, file_size)
            if existing_token is not None:
                log.info(f"Upload already complete, using existing session")
                return existing_token
            if resume_byte is not None:
                start_byte = resume_byte + 1

        # Stream the file, optionally computing SHA1 on the fly
        sha1_hasher = hashlib.sha1() if compute_hash else None

        def _chunked_reader() -> typing.Generator[bytes, None, None]:
            total_read = start_byte
            with open(file_path, "rb") as f:
                if start_byte > 0:
                    f.seek(start_byte)
                while True:
                    if self._cancelled:
                        raise RuntimeError("Upload cancelled")
                    chunk = f.read(256 * 1024)
                    if not chunk:
                        break
                    total_read += len(chunk)
                    if sha1_hasher is not None:
                        sha1_hasher.update(chunk)
                    if on_progress:
                        on_progress(total_read, file_size)
                    yield chunk

        content_length = file_size - start_byte
        headers = {
            "Authorization": f"Bearer {self._bearer()}",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(content_length),
            "Content-Range": f"bytes {start_byte}-{file_size - 1}/{file_size}",
            "User-Agent": self._user_agent,
        }

        resp = self._client.put(
            upload_url,
            content=_chunked_reader(),
            headers=headers,
        )
        if resp.status_code >= 400:
            body = resp.content[:500]
            log.error(f"Upload failed ({resp.status_code}): {body}")
            raise RuntimeError(
                f"Upload rejected ({resp.status_code}): {body.decode(errors='replace')}"
            )

        # If computing hash on the fly, store the result
        if sha1_hasher is not None and hash_out is not None:
            hash_out.append(sha1_hasher.digest())

        token = CommitToken()
        token.ParseFromString(resp.content)
        return token

    def commit_upload(
        self,
        commit_token: CommitToken,
        file_name: str,
        sha1_hash: bytes,
        timestamp: int,
    ) -> str:
        msg = CommitUpload(
            field1=CommitUpload.Field1Type(
                field1=CommitUpload.Field1Type.Field1Type(
                    field1=commit_token.field1,
                    field2=commit_token.field2,
                ),
                file_name=file_name,
                sha1_hash=sha1_hash,
                field4=CommitUpload.Field1Type.Field4Type(
                    file_last_modified_timestamp=timestamp,
                    field2=46000000,
                ),
                quality=3,
                field10=1,
            ),
            field2=CommitUpload.Field2Type(
                model=self._model,
                make=self._make,
                android_api_version=self._android_api_version,
            ),
            field3=b"\x01\x03",
        )
        if self._model == "Pixel 2":
            msg.field1.quality = 1

        data = msg.SerializeToString()
        resp = self._post_proto_raw(
            "https://photosdata-pa.googleapis.com/6439526531001121323/16538846908252377752",
            data,
            {
                "x-goog-ext-173412678-bin": "CgcIAhClARgC",
                "x-goog-ext-174067345-bin": "CgIIAg==",
            },
        )
        response = CommitUploadResponse()
        response.ParseFromString(resp.content)
        media_key = response.field1.field3.media_key
        if not media_key:
            raise RuntimeError("Upload rejected: no media key returned")
        return media_key

    def find_media_by_hash(self, sha1_hash: bytes) -> str:
        msg = HashCheck(
            field1=HashCheck.Field1Type(
                field1=HashCheck.Field1Type.Field1Type(sha1_hash=sha1_hash),
                field2=HashCheck.Field1Type.Field2Type(),
            )
        )
        data = msg.SerializeToString()
        resp = self._post_proto_raw(
            "https://photosdata-pa.googleapis.com/6439526531001121323/5084965799730810217",
            data,
        )
        response = RemoteMatches()
        response.ParseFromString(resp.content)
        return response.field1.field2.field2.media_key if response.field1 else ""

    def create_album(self, album_name: str, media_keys: list[str]) -> str:
        proto_keys = [
            CreateAlbum.Field4Type(
                field1=CreateAlbum.Field4Type.Field1Type(media_key=key)
            )
            for key in media_keys
        ]
        msg = CreateAlbum(
            album_name=album_name,
            timestamp=int(time.time()),
            field3=1,
            media_keys=proto_keys,
            field7=CreateAlbum.Field7Type(field1=3),
            device_info=CreateAlbum.Field8Type(
                model=self._model,
                make=self._make,
                android_api_version=self._android_api_version,
            ),
        )
        data = msg.SerializeToString()
        resp = self._post_proto_raw(
            "https://photosdata-pa.googleapis.com/6439526531001121323/8386163679468898444",
            data,
            {
                "x-goog-ext-173412678-bin": "CgcIAhClARgC",
                "x-goog-ext-174067345-bin": "CgIIAg==",
            },
        )
        response = CreateAlbumResponse()
        response.ParseFromString(resp.content)
        return response.field1.album_media_key

    def add_media_to_album(self, album_media_key: str, media_keys: list[str]):
        msg = AddMediaToAlbum(
            media_keys=media_keys,
            album_media_key=album_media_key,
            field5=AddMediaToAlbum.Field5Type(field1=2),
            device_info=AddMediaToAlbum.Field6Type(
                model=self._model,
                make=self._make,
                android_api_version=self._android_api_version,
            ),
            timestamp=int(time.time()),
        )
        data = msg.SerializeToString()
        self._post_proto_raw(
            "https://photosdata-pa.googleapis.com/6439526531001121323/484917746253879292",
            data,
            {
                "x-goog-ext-173412678-bin": "CgcIAhClARgC",
                "x-goog-ext-174067345-bin": "CgIIAg==",
            },
        )

    def calculate_sha1(self, file_path: str) -> bytes:
        h = hashlib.sha1()
        with open(file_path, "rb") as f:
            while True:
                buf = f.read(1024 * 1024)
                if not buf:
                    break
                h.update(buf)
        return h.digest()

    @staticmethod
    def get_supported_extensions() -> set[str]:
        return {
            ".avif", ".bmp", ".gif", ".heic", ".heif", ".ico",
            ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp",
            ".cr2", ".cr3", ".nef", ".arw", ".orf", ".raf", ".rw2", ".pef", ".sr2", ".dng",
            ".3gp", ".3g2", ".asf", ".avi", ".divx", ".m2t", ".m2ts", ".m4v", ".mkv",
            ".mmv", ".mod", ".mov", ".mp4", ".mpg", ".mpeg", ".mts", ".tod", ".wmv", ".ts",
        }
