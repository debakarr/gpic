# gpic

Command-line tool that pushes photos and videos to Google Photos. Python port of [gotohp](https://github.com/xob0t/gotohp) by [xob0t](https://github.com/xob0t) — the protocol work is his.

## Features

- Uploads to Google Photos through the internal mobile API
- Per-file progress bars (0–100%)
- Thread count picked automatically from file sizes (override with `-t`)
- Speed and ETA while uploading
- Retry with exponential backoff and jitter
- Skips files already in the library (SHA-1 check)
- Recursive directory scan
- Create albums by folder (`AUTO`) or by name
- `--json` summary output for scripts
- Large-file resume via `Content-Range`

## Privacy & Data

- **No analytics or telemetry.** Dependencies are click, httpx, protobuf and rich.
- **Your photos go to Google Photos and nowhere else.** The tool reads files from the paths you give it and talks only to Google endpoints (`android.googleapis.com/auth`, `photos.googleapis.com`, `photosdata-pa.googleapis.com`).
- **Credentials sit in plain text** in the config file (see below), including any `--proxy` URL with a password in it. Anyone who can read that file can use your Photos login. File permissions are set to owner-only on creation, but on a shared machine delete the credential when you are done (`gpic creds remove <email>`).
- The bearer token is kept in memory and refreshed as needed. Nothing else is stored besides the config file and the upload-resume cache.

## Installation

```bash
# with uv (recommended)
uv tool install gpic

# or pip
pip install gpic
```

Needs Python 3.10+.

## Quick Start

### 1. Get the credential from your phone

You need:

- Android phone with Google Photos (ReVanced build, or official app on a rooted device)
- USB debugging on (`adb`)

On your PC:

```powershell
# clear logcat, then capture
adb logcat -c 2>$null
adb logcat | Select-String "auth"
```

Open Google Photos on the phone. A line with `androidId=...&Email=...&Token=...` shows up. Copy the whole line — it must include a `photos.native` service, a `userinfo.profile` line will fail every call with 403.

### 2. Save it

```powershell
gpic creds add "androidId=...&Email=...&Token=..."
```

### 3. Upload

```powershell
# one file
gpic upload "C:\DJI Recording\video.mp4"

# a folder, recursive
gpic upload -r "C:\DJI Recording"

# several files
gpic upload photo1.jpg video.mp4

# biggest files first
gpic upload -r --sort-size "C:\DJI Recording"
```

## CLI Reference

```
Usage: gpic [OPTIONS] COMMAND [ARGS]...

Commands:
  creds    Manage credentials
  upload   Upload files to Google Photos
  version  Show version
```

### `gpic upload`

```
Usage: gpic upload [OPTIONS] PATHS...

Options:
  -t, --threads INTEGER    Upload threads (0=auto-detect, default: auto)
  -r, --recursive          Scan directories recursively
  -f, --force              Upload even if file exists in library
  -d, --delete             Delete file from disk after successful upload
  -a, --album TEXT         Album name (use "AUTO" for folder-based albums)
  --saver                  Storage saver quality (mimics Pixel 2)
  --quota                  Use storage quota (mimics Pixel 8)
  --proxy TEXT             HTTP proxy URL
  --json                   Output JSON summary
  --sort-size              Process largest files first
```

### `gpic creds`

```
Usage: gpic creds [OPTIONS] COMMAND [ARGS]...

Commands:
  add     Add a credential
  list    List stored credentials
  remove  Remove a credential
  set     Set active credential
```

## Auto-Detect Threads

Thread count is picked from the file sizes:

| Files | Threads | Reason |
|---|---|---|
| Large (GB+) | 1–2 | Big files saturate bandwidth alone |
| Medium (50–500 MB) | 3–4 | Balanced |
| Small (<5 MB) | 5–6 | Overlaps network latency |
| Lots of tiny files (100+) | 6–8 | Max concurrency |

Override with `-t N`.

## Upload Resume

Interrupted large files resume where they stopped instead of restarting, using Google's resumable upload protocol (`Content-Range` headers). Resume state is cached on disk for 24 hours.

## Configuration

Config file (created automatically):

| OS | Path |
|---|---|
| Windows | `%APPDATA%\gpic\config.json` |
| macOS | `~/Library/Application Support/gpic/config.json` |
| Linux | `~/.config/gpic/config.json` |

## Troubleshooting

- **`UNREGISTERED_ON_API_CONSOLE` (HTTP 400):** the pasted string is incomplete. Re-copy the full logcat line with `service=...` in it.
- **403 after hashing:** the token works but the scope is wrong — you pasted a `userinfo.profile` line instead of a `photos.native` one. Filter logcat on `photos.native` and copy that line.
- **`Protocol message tag had invalid wire type`:** update gpic, then retry.

## Disclaimer

This uses the unofficial internal Google Photos mobile API, not the official Library API. Google can change or block it at any time. Use at your own risk.

## Credits

- **[gotohp](https://github.com/xob0t/gotohp)** by [xob0t](https://github.com/xob0t) — the original Go implementation this is based on.
- **[google_photos_mobile_client](https://github.com/xob0t/google_photos_mobile_client)** — Python reference for the same API.

## License

MIT
