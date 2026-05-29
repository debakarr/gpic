import json
import os
import platform
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


CONFIG_DIR_NAME = "gpic"
CONFIG_FILE_NAME = "config.json"


def get_config_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / CONFIG_DIR_NAME


def get_data_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / CONFIG_DIR_NAME


@dataclass
class Credential:
    email: str = ""
    auth_string: str = ""
    language: str = "en"


@dataclass
class AppConfig:
    selected_email: str = ""
    credentials: list[Credential] = field(default_factory=list)
    upload_threads: int = 3
    recursive: bool = False
    force_upload: bool = False
    delete_after_upload: bool = False
    saver_mode: bool = False
    use_quota: bool = False
    proxy: str = ""


class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (get_config_dir() / CONFIG_FILE_NAME)
        self.config = AppConfig()
        self.load()

    def load(self):
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.config.selected_email = data.get("selected_email", "")
            self.config.upload_threads = data.get("upload_threads", 3)
            self.config.recursive = data.get("recursive", False)
            self.config.force_upload = data.get("force_upload", False)
            self.config.delete_after_upload = data.get("delete_after_upload", False)
            self.config.saver_mode = data.get("saver_mode", False)
            self.config.use_quota = data.get("use_quota", False)
            self.config.proxy = data.get("proxy", "")
            creds_data = data.get("credentials", [])
            self.config.credentials = [
                Credential(**c) for c in creds_data
            ]

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(self.config)
        self.config_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # Restrict file permissions on Unix (user read/write only)
        if platform.system() != "Windows":
            try:
                self.config_path.chmod(0o600)
            except OSError:
                pass

    def add_credential(self, auth_string: str) -> Optional[Credential]:
        from urllib.parse import parse_qs

        params = parse_qs(auth_string)
        email = params.get("Email", [""])[0]
        if not email:
            return None
        existing = [c for c in self.config.credentials if c.email == email]
        if existing:
            existing[0].auth_string = auth_string
            cred = existing[0]
        else:
            lang = params.get("lang", ["en"])[0]
            cred = Credential(email=email, auth_string=auth_string, language=lang)
            self.config.credentials.append(cred)
        self.save()
        return cred

    def remove_credential(self, email: str):
        self.config.credentials = [
            c for c in self.config.credentials if c.email != email
        ]
        if self.config.selected_email == email:
            self.config.selected_email = (
                self.config.credentials[0].email if self.config.credentials else ""
            )
        self.save()

    def get_credential(self, email: str) -> Optional[Credential]:
        for c in self.config.credentials:
            if c.email == email:
                return c
        return None

    def set_active(self, email: str) -> bool:
        for c in self.config.credentials:
            if email in c.email:
                self.config.selected_email = c.email
                self.save()
                return True
        return False
