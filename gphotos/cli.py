from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import click

from gphotos import __version__
from gphotos.config import ConfigManager, get_config_dir
from gphotos.upload import UploadManager, UploadResult
from gphotos.progress import FileProgress
from gphotos.rich_display import RichUploadDisplay, _format_size


def format_size(size: int) -> str:
    return _format_size(size)


@click.group()
@click.version_option(version=__version__, prog_name="gphotos")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj["config"] = ConfigManager()


@cli.command()
def version():
    click.echo(f"gphotos-py v{__version__}")


@cli.group()
def creds():
    pass


@creds.command("list")
@click.pass_context
def creds_list(ctx):
    config: ConfigManager = ctx.obj["config"]
    if not config.config.credentials:
        click.echo("No credentials stored.")
        return
    for c in config.config.credentials:
        marker = " [active]" if c.email == config.config.selected_email else ""
        click.echo(f"  {c.email}{marker}")


@creds.command("add")
@click.argument("auth_string", required=False)
@click.option("--stdin", is_flag=True, help="Read auth string from stdin (more secure)")
@click.pass_context
def creds_add(ctx, auth_string, stdin):
    """Add a credential.
    
    AUTH_STRING is the full auth string from ADB logcat.
    For security, omit AUTH_STRING and use --stdin to pipe it:
      adb logcat | grep "auth" | gphotos creds add --stdin
    Or set the GP_AUTH_DATA environment variable.
    """
    config: ConfigManager = ctx.obj["config"]
    
    if stdin:
        auth_string = sys.stdin.read().strip()
    elif not auth_string:
        env_auth = os.environ.get("GP_AUTH_DATA", "")
        if env_auth:
            auth_string = env_auth
        else:
            click.echo("Provide auth string as argument, use --stdin, or set GP_AUTH_DATA env var", err=True)
            return
    
    if not auth_string:
        click.echo("Empty auth string", err=True)
        return
    
    cred = config.add_credential(auth_string)
    if cred:
        click.echo(f"Added credential for {cred.email}")
        if not config.config.selected_email:
            config.set_active(cred.email)
            click.echo(f"Set as active")
    else:
        click.echo("Failed to parse auth string", err=True)


@creds.command("remove")
@click.argument("email")
@click.pass_context
def creds_remove(ctx, email):
    config: ConfigManager = ctx.obj["config"]
    config.remove_credential(email)
    click.echo(f"Removed credential for {email}")


@creds.command("set")
@click.argument("email")
@click.pass_context
def creds_set(ctx, email):
    config: ConfigManager = ctx.obj["config"]
    if config.set_active(email):
        click.echo(f"Active credential set to {config.config.selected_email}")
    else:
        click.echo(f"No credential matching '{email}'", err=True)


@cli.command()
@click.argument("paths", nargs=-1, required=True)
@click.option("-r", "--recursive", is_flag=True, help="Scan directories recursively")
@click.option("-t", "--threads", default=0, type=int, help="Upload threads (0=auto-detect, default: auto)")
@click.option("-f", "--force", is_flag=True, help="Upload even if file exists")
@click.option("-d", "--delete", is_flag=True, help="Delete file after upload")
@click.option("-a", "--album", default="", help="Add to album (use AUTO for folder-based)")
@click.option("--saver", is_flag=True, help="Storage saver mode (mimics Pixel 2)")
@click.option("--quota", is_flag=True, help="Use storage quota (mimics Pixel 8)")
@click.option("--proxy", default="", help="HTTP proxy URL")
@click.option("--json", "json_output", is_flag=True, help="Output JSON summary")
@click.pass_context
def upload(
    ctx, paths, recursive, threads, force, delete, album,
    saver, quota, proxy, json_output,
):
    config: ConfigManager = ctx.obj["config"]
    if not config.config.selected_email:
        click.echo("No active credential. Add one with: gphotos creds add <auth_string>", err=True)
        return

    if not config.config.credentials:
        click.echo("No credentials found. Add one with: gphotos creds add <auth_string>", err=True)
        return

    active_cred = config.get_credential(config.config.selected_email)
    if not active_cred:
        click.echo(f"Active credential '{config.config.selected_email}' not found", err=True)
        return

    album_auto = album.upper() == "AUTO"
    album_name = "" if album_auto else album

    manager = UploadManager(
        credential=active_cred,
        threads=threads,
        force=force,
        recursive=recursive,
        saver=saver,
        use_quota=quota,
        proxy=proxy,
        album_name=album_name,
        album_auto=album_auto,
        delete_after=delete,
        on_event=lambda e, d: None,
    )

    files = manager._scan_files(list(paths))
    if not files:
        click.echo("No supported files found to upload.")
        return

    total_bytes = sum(os.path.getsize(f) for f in files)

    # Auto-detect optimal thread count when 0 or not specified
    if threads == 0:
        threads = UploadManager.auto_threads(files)
        manager._threads = threads

    click.echo(f"Preparing to upload {len(files)} files ({format_size(total_bytes)})")
    click.echo(f"Using {threads} upload thread(s)")
    if album_name:
        click.echo(f"Album: {album_name}")
    if album_auto:
        click.echo("Album mode: AUTO (by folder)")
    if force:
        click.echo("Force upload: ON (will re-upload existing files)")
    click.echo("")

    # Handle Ctrl+C gracefully
    cancelled = False

    def _on_sigint(sig, frame):
        nonlocal cancelled
        if cancelled:
            sys.stderr.write("\nForce quitting...\n")
            os._exit(1)
        cancelled = True
        sys.stderr.write("\nCancelling... (press Ctrl+C again to force quit)\n")
        manager.cancel()

    signal.signal(signal.SIGINT, _on_sigint)

    # Rich-based progress display
    with RichUploadDisplay(manager.progress, len(files), total_bytes) as display:

        def on_event(event: str, data: object):
            nonlocal cancelled
            if event == "cancelled":
                cancelled = True
            elif event == "file_progress" and isinstance(data, FileProgress):
                display.update_file(data)

        manager._on_event = on_event
        manager.start(list(paths))

    succeeded = len([r for r in manager.results if r.success])
    failed = len([r for r in manager.results if not r.success])

    click.echo(f"Done: {succeeded} succeeded, {failed} failed")

    for r in manager.results:
        if not r.success:
            click.echo(f"  FAIL: {r.file_path}")
            click.echo(f"    Error: {r.error}")

    if json_output:
        summary = {
            "total": manager.progress.total_files,
            "succeeded": succeeded,
            "failed": failed,
            "results": [
                {
                    "path": r.file_path,
                    "success": r.success,
                    "media_key": r.media_key,
                    "error": r.error,
                }
                for r in manager.results
            ],
        }
        click.echo(json.dumps(summary, indent=2))
