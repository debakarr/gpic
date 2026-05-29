from __future__ import annotations

import base64
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from typing import Callable, Optional, Set

from gphotos.api import GooglePhotosAPI
from gphotos.config import Credential
from gphotos.progress import FileProgress, ProgressTracker
from gphotos.upload_cache import UploadCache


class UploadResult:
    def __init__(self, file_path: str, success: bool, media_key: str = "", error: str = ""):
        self.file_path = file_path
        self.success = success
        self.media_key = media_key
        self.error = error


class UploadManager:
    @staticmethod
    def auto_threads(files: list[str]) -> int:
        """Auto-detect optimal thread count based on file sizes."""
        if not files:
            return 3

        sizes = []
        for f in files:
            try:
                sizes.append(os.path.getsize(f))
            except OSError:
                sizes.append(0)

        if not sizes:
            return 3

        count = len(sizes)
        total = sum(sizes)
        avg = total / count if count else 0
        biggest = max(sizes)

        # Score system: start neutral, adjust for conditions
        score = 3  # base

        # Factor 1: Average file size (bandwidth saturation risk)
        if avg > 500_000_000:       # >500MB avg → big files, few threads
            score -= 1
        elif avg > 50_000_000:      # >50MB avg → moderate
            pass  # score stays at 3
        elif avg > 5_000_000:       # 5-50MB → slightly more threads
            score += 1
        else:                       # <5MB avg → many small files
            score += 2

        # Factor 2: Largest file (head-of-line blocking risk)
        if biggest > 5_000_000_000:  # >5GB file present → very conservative
            score = max(score - 1, 1)
        elif biggest > 1_000_000_000:  # >1GB file present
            score = max(score - 1, 1)

        # Factor 3: File count (concurrency opportunity)
        if count >= 50:
            score += 1
        elif count <= 3 and avg > 100_000_000:
            score = min(score, 2)  # few big files → don't overload

        return max(1, min(score, 8))

    def __init__(
        self,
        credential: Credential,
        threads: int = 3,
        force: bool = False,
        recursive: bool = False,
        saver: bool = False,
        use_quota: bool = False,
        proxy: str = "",
        album_name: str = "",
        album_auto: bool = False,
        delete_after: bool = False,
        on_event: Optional[Callable[[str, object], None]] = None,
    ):
        self._credential = credential
        self._threads = max(1, threads)
        self._force = force
        self._recursive = recursive
        self._saver = saver
        self._use_quota = use_quota
        self._proxy = proxy
        self._album_name = album_name
        self._album_auto = album_auto
        self._delete_after = delete_after
        self._on_event = on_event
        self._cancelled = False

        self.progress = ProgressTracker()
        self.results: list[UploadResult] = []
        self._api: Optional[GooglePhotosAPI] = None

    def _emit(self, event: str, data: object):
        if self._on_event:
            self._on_event(event, data)

    def cancel(self):
        self._cancelled = True
        if self._api:
            self._api.cancel()

    def _scan_files(self, paths: list[str]) -> list[str]:
        supported = GooglePhotosAPI.get_supported_extensions()
        files: list[str] = []
        for p in paths:
            path = Path(p)
            if not path.exists():
                continue
            if path.is_file():
                if path.suffix.lower() in supported:
                    files.append(str(path.absolute()))
            elif path.is_dir():
                if self._recursive:
                    for f in path.rglob("*"):
                        if f.is_file() and f.suffix.lower() in supported:
                            files.append(str(f.absolute()))
                else:
                    for f in path.iterdir():
                        if f.is_file() and f.suffix.lower() in supported:
                            files.append(str(f.absolute()))
        return files

    def start(self, paths: list[str]):
        self._emit("upload_start", None)
        files = self._scan_files(paths)
        if not files:
            self._emit("upload_done", None)
            return

        for f in files:
            try:
                size = os.path.getsize(f)
            except OSError:
                size = 0
            self.progress.add_file(f, size)

        self._emit("batch_start", {
            "total": self.progress.total_files,
            "total_bytes": self.progress.total_bytes,
        })

        self._api = GooglePhotosAPI(
            auth_string=self._credential.auth_string,
            language=self._credential.language,
            proxy=self._proxy,
            saver_mode=self._saver,
            use_quota=self._use_quota,
        )

        with ThreadPoolExecutor(max_workers=self._threads) as executor:
            futures: Set = {
                executor.submit(self._upload_file, f): f for f in files
            }
            while futures and not self._cancelled:
                done, futures = wait(futures, timeout=0.5, return_when=FIRST_COMPLETED)
                if self._cancelled:
                    for f in futures:
                        f.cancel()
                    break
                for future in done:
                    result = future.result()
                    self.results.append(result)
                    self._emit("file_result", result)

        self._handle_albums()
        self._emit("upload_done", None)

    def _upload_file(self, file_path: str) -> UploadResult:
        if self._cancelled:
            return UploadResult(file_path, False, error="Cancelled")

        fp = self.progress.get(file_path)
        api = self._api
        assert api is not None

        file_name = os.path.basename(file_path)
        timestamp = int(os.path.getmtime(file_path))

        try:
            # Stage 1: Hash
            fp.status = "hashing"
            fp.message = "Calculating SHA1..."
            self._emit("file_progress", fp)
            sha1 = api.calculate_sha1(file_path)
            sha1_b64 = base64.urlsafe_b64encode(sha1).decode()

            # Stage 2: Check
            if not self._force:
                fp.status = "checking"
                fp.message = "Checking if already uploaded..."
                self._emit("file_progress", fp)
                media_key = api.find_media_by_hash(sha1)
                if media_key:
                    fp.status = "skipped"
                    fp.message = "Already in library"
                    self._emit("file_progress", fp)
                    self.progress.skipped += 1
                    if self._delete_after:
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
                    return UploadResult(file_path, True, media_key)

            # Stage 3: Try resume from cache, or get new upload token
            cache = UploadCache()
            file_size = os.path.getsize(file_path)
            upload_id = None
            resume_offset = None
            commit_token = None

            cached = cache.get(file_path)
            if cached:
                resume_offset, existing_token = api.try_resume_session(
                    cached["upload_id"], file_size
                )
                if existing_token is not None:
                    commit_token = existing_token
                elif resume_offset is not None:
                    upload_id = cached["upload_id"]
                    fp.status = "resuming"
                    fp.resume_offset = resume_offset
                    fp.update_bytes(resume_offset, file_size)
                    resumed_pct = resume_offset / max(file_size, 1) * 100
                    fp.message = f"Resuming from {resumed_pct:.1f}%"
                    self._emit("file_progress", fp)

            if upload_id is None and commit_token is None:
                # No cache, or session expired — get a fresh token
                fp.status = "uploading"
                fp.message = "Requesting upload token..."
                fp.attempt = 1
                self._emit("file_progress", fp)
                upload_id = api.get_upload_token(sha1_b64, file_size)
                cache.set(file_path, upload_id, file_size)

            # Stage 4: Upload with progress (skip if already complete from resume)
            if commit_token is None:
                if fp.status != "resuming":
                    fp.status = "uploading"
                fp.message = "Uploading..."
                self._emit("file_progress", fp)

                def on_upload_progress(read_bytes: int, total_bytes: int):
                    fp.update_bytes(read_bytes, total_bytes)
                    # Transition from "resuming" to "uploading" once past resume point
                    if fp.status == "resuming" and read_bytes >= fp.resume_offset + 1024 * 1024:
                        fp.status = "uploading"
                    if fp.should_emit():
                        self._emit("file_progress", fp)

                commit_token = api.upload_file(
                    file_path, upload_id, on_upload_progress,
                    resume_offset=resume_offset or 0,
                )
                fp.bytes_uploaded = file_size
                self._emit("file_progress", fp)

            # Clear from cache on successful upload
            cache.remove(file_path)

            # Stage 5: Commit
            fp.status = "committing"
            fp.message = "Committing upload..."
            self._emit("file_progress", fp)
            media_key = api.commit_upload(commit_token, file_name, sha1, timestamp)

            fp.status = "completed"
            fp.message = "Uploaded"
            self._emit("file_progress", fp)
            self.progress.completed += 1

            if self._delete_after:
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            return UploadResult(file_path, True, media_key)

        except Exception as e:
            fp.status = "error"
            fp.message = str(e)
            self._emit("file_progress", fp)
            self.progress.failed += 1
            return UploadResult(file_path, False, error=str(e))

    def _handle_albums(self):
        if not self._album_name and not self._album_auto:
            return
        if self._cancelled:
            return

        successful = [r for r in self.results if r.success and r.media_key]
        if not successful:
            return

        api = self._api
        assert api is not None

        media_keys = [r.media_key for r in successful]

        if self._album_auto:
            from collections import defaultdict
            by_dir: dict[str, list[str]] = defaultdict(list)
            for r in successful:
                parent = os.path.dirname(r.file_path)
                by_dir[parent].append(r.media_key)

            for dir_path, keys in by_dir.items():
                album_name = os.path.basename(dir_path) or "Uploads"
                self._emit("album_progress", {"album": album_name, "items": len(keys)})
                try:
                    api.create_album(album_name, keys)
                    self._emit("album_done", {"album": album_name})
                except Exception as e:
                    self._emit("album_error", {"album": album_name, "error": str(e)})
        else:
            self._emit("album_progress", {"album": self._album_name, "items": len(media_keys)})
            try:
                api.create_album(self._album_name, media_keys)
                self._emit("album_done", {"album": self._album_name})
            except Exception as e:
                self._emit("album_error", {"album": self._album_name, "error": str(e)})
