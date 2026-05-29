# gpic

**Python tool to push pics and videos to Google Photos.**

> Built as a Python alternative to [gotohp](https://github.com/xob0t/gotohp) by [xob0t](https://github.com/xob0t).  
> **Massive credit** to the gotohp project for the reverse engineering work on the Google Photos internal API.

## Features

- 🚀 **Upload to Google Photos** via the internal mobile API (unlimited free storage)
- 📊 **Per-file percentage progress** — live ASCII progress bars showing 0–100%
- ⚡ **Concurrent uploads** with auto-detected thread count based on file sizes
- ⏱️ **Transfer speed & ETA** — shows MB/s and time remaining
- 🔁 **Smart retry** — exponential backoff with jitter on failures
- 🔍 **Hash dedup** — skips files already in your library (SHA-1 check)
- 📁 **Recursive directory scanning** — upload entire folder trees
- 🖼️ **Album creation** — auto-create albums by folder, or specify a name
- 📦 **CLI-friendly JSON output** — `--json` flag for scripting
- 🔄 **Upload resume** (large files) — resumes interrupted uploads via `Content-Range`

## Installation

```bash
# Install with uv (recommended)
uv tool install gpic

# Or pip
pip install gpic
```

Requires Python 3.10+.

## Quick Start

### 1. Get credentials from your phone

**Prerequisites:**
- Android device with [ReVanced Google Photos](https://github.com/ReVanced/revanced-patches) or official Google Photos (root)
- USB debugging enabled (`adb`)

**On your PC:**

```powershell
# Clear logcat and start capturing
adb logcat -c 2>$null
adb logcat | Select-String "auth"
```

On your phone, open Google Photos. A log line containing `androidId=...&Email=...&Token=...` should appear. Copy the full line.

### 2. Add the credentials

```powershell
gpic creds add "androidId=...&Email=...&Token=..." 
```

### 3. Upload files

```powershell
# Single file
gpic upload "C:\DJI Recording\video.mp4"

# Directory (recursive)
gpic upload -r "C:\DJI Recording"

# Multiple files
gpic upload photo1.jpg video.mp4

# All WhatsApp images
gpic upload "C:\Users\me\Downloads\WhatsApp*"
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

The tool automatically chooses the optimal number of concurrent upload threads based on file sizes:

| Scenario | Threads | Why |
|---|---|---|
| Large files (GB+) | 1–2 | Avoid saturating bandwidth |
| Medium files (50–500 MB) | 3–4 | Balanced throughput |
| Small files (<5 MB) | 5–6 | Overlap network latency |
| Tons of tiny files (100+) | 6–8 | Maximize concurrency |

Override with `-t N` to set a fixed thread count.

## Upload Resume

For large files, if the upload is interrupted, the tool automatically resumes from where it left off instead of restarting from zero. This uses Google's resumable media upload protocol with `Content-Range` headers.

## Configuration

Config file location (auto-created):

| OS | Path |
|---|---|
| Windows | `%APPDATA%\gpic\config.json` |
| macOS | `~/Library/Application Support/gpic/config.json` |
| Linux | `~/.config/gpic/config.json` |

## Security Notes

- **Credentials are stored in plain text** in the config file. Protect your config file with appropriate file system permissions.
- The `--proxy` URL (if it contains credentials like `http://user:pass@host:port`) is also stored in plain text.
- On shared machines, consider deleting credentials after use.
- The bearer token is cached in memory only and refreshed automatically.

## Credits

- **[gotohp](https://github.com/xob0t/gotohp)** by [xob0t](https://github.com/xob0t) — the original Go implementation that this project is based on. All protocol reverse-engineering credit goes to them.
- **[google_photos_mobile_client](https://github.com/xob0t/google_photos_mobile_client)** — Python reference implementation of the same API.

## License

MIT
