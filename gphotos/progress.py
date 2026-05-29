import time


class FileProgress:
    def __init__(self, file_name: str, total_bytes: int):
        self.file_name = file_name
        self.total_bytes = total_bytes
        self.bytes_uploaded = 0
        self.resume_offset = 0  # bytes already uploaded in a previous session
        self.attempt = 1
        self.status = "pending"  # pending, hashing, checking, uploading, resuming, committing, completed, error, skipped
        self.message = ""
        self._last_emit = 0.0
        self._emit_interval = 0.1

    @property
    def percentage(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_uploaded / self.total_bytes) * 100.0

    @property
    def percentage_str(self) -> str:
        return f"{self.percentage:.1f}%"

    @property
    def resumed_percentage(self) -> float:
        """Percentage already uploaded in a previous session (for display)."""
        if self.total_bytes == 0:
            return 0.0
        return (self.resume_offset / self.total_bytes) * 100.0

    def update_bytes(self, read: int, total: int):
        self.bytes_uploaded = read
        self.total_bytes = total

    def should_emit(self) -> bool:
        now = time.monotonic()
        if now - self._last_emit >= self._emit_interval:
            self._last_emit = now
            return True
        return False


class ProgressTracker:
    def __init__(self):
        self.files: dict[str, FileProgress] = {}
        self.total_files = 0
        self.total_bytes = 0
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = 0.0

    def add_file(self, file_path: str, file_size: int):
        name = file_path.split("/")[-1].split("\\")[-1]
        self.files[file_path] = FileProgress(name, file_size)
        self.total_files += 1
        self.total_bytes += file_size

    def get(self, file_path: str) -> FileProgress:
        return self.files[file_path]

    @property
    def done_count(self) -> int:
        return self.completed + self.failed + self.skipped

    @property
    def overall_percentage(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.done_count / self.total_files) * 100.0
