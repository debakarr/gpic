"""Rich-powered upload progress display with speed, ETA, and per-file bars."""

from typing import Optional

from rich.console import Group, RenderableType
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table
from rich.text import Text

from gphotos.progress import FileProgress, ProgressTracker


def _format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


class RichUploadDisplay:
    """Live-updating rich terminal display for upload progress."""

    def __init__(self, tracker: ProgressTracker, total_files: int, total_bytes: int):
        self._tracker = tracker
        self._total_files = total_files
        self._total_bytes = total_bytes
        self._task_id: Optional[TaskID] = None
        self._file_tasks: dict[str, TaskID] = {}
        self._live: Optional[Live] = None

        # Overall progress bar
        self._overall = Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(" "),
            TransferSpeedColumn(),
            TextColumn(" "),
            TimeRemainingColumn(),
        )

        # Per-file progress bar
        self._files = Progress(
            TextColumn("  {task.fields[name]:<40.40s}"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(" "),
            TransferSpeedColumn(),
            TextColumn(" "),
            TimeRemainingColumn(),
            TextColumn("{task.fields[status]}"),
        )

        # Summary line
        self._summary = Text("")

    def __enter__(self):
        self._task_id = self._overall.add_task(
            "Files",
            total=self._total_files,
            completed=0,
        )

        self._live = Live(
            self._build_renderable(),
            refresh_per_second=8,
            transient=False,
        )
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        if self._live:
            self._live.__exit__(*args)
            self._live = None

    def _build_renderable(self) -> RenderableType:
        done = self._tracker.done_count
        completed = self._tracker.completed
        failed = self._tracker.failed
        skipped = self._tracker.skipped
        remaining = self._total_files - done

        # Update overall task
        if self._task_id is not None:
            self._overall.update(self._task_id, completed=done)

        # Build summary
        parts = []
        if completed:
            parts.append(f"[green]{completed} ok[/green]")
        if failed:
            parts.append(f"[red]{failed} failed[/red]")
        if skipped:
            parts.append(f"[yellow]{skipped} skipped[/yellow]")
        if remaining:
            parts.append(f"{remaining} remaining")
        summary_text = "  |  ".join(parts) if parts else ""

        return Group(
            Text(f"Uploading {self._total_files} files ({_format_size(self._total_bytes)})"),
            self._overall,
            Text(summary_text) if summary_text else Text(""),
            Text(""),
            self._files,
        )

    def update_file(self, fp: FileProgress):
        """Update or create a per-file progress bar."""
        task_id = self._file_tasks.get(fp.file_name)

        if fp.status in ("completed", "error", "skipped"):
            if task_id is not None:
                try:
                    self._files.remove_task(task_id)
                except Exception:
                    pass
                self._file_tasks.pop(fp.file_name, None)
            return

        total = fp.total_bytes
        completed = fp.bytes_uploaded

        status_tag = {
            "hashing": "yellow",
            "resuming": "blue",
            "uploading": "cyan",
            "committing": "green",
        }.get(fp.status, "white")
        status = fp.status.capitalize()
        if fp.attempt > 1:
            status += f" [retry {fp.attempt}]"
        elif fp.status == "resuming" and fp.resumed_percentage > 0:
            status = f"[blue]Resuming from {fp.resumed_percentage:.1f}%[/blue]"

        if task_id is None:
            task_id = self._files.add_task(
                "",
                name=fp.file_name,
                total=total,
                completed=completed,
                status=status,
            )
            self._file_tasks[fp.file_name] = task_id
        else:
            self._files.update(
                task_id,
                total=total,
                completed=completed,
                status=status,
            )

        if self._live:
            self._live.update(self._build_renderable())
