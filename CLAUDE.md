# CLAUDE.md

## Project overview

A Claude Code skill wrapping Bear's x-callback-url API. The architecture has three layers:

1. `xcall-lite.swift` — Swift CLI app that opens a `bear://` URL, captures the callback via a registered URL scheme (`xcall-lite-callback://`), and prints JSON to stdout.
2. `bear.py` — Python CLI (stdlib only) with subcommands for each Bear action. Calls xcall-lite via subprocess.
3. `SKILL.md` — Tells Claude when/how to invoke bear.py.

## Key files

- `scripts/xcall-lite.swift` — The Swift source. Compiles to an `.app` bundle so macOS recognizes its URL scheme.
- `scripts/Info.plist` — Registers the `xcall-lite-callback://` scheme. `LSBackgroundOnly=true` so no Dock icon.
- `scripts/build-xcall-lite.sh` — Builds the .app bundle and registers with LaunchServices. Idempotent (skips if source unchanged).
- `scripts/bear.py` — The main CLI. `call_bear(action, params)` is the core function — builds the URL, injects token, invokes xcall-lite, parses response. Auto-builds xcall-lite on first use.
- `scripts/test_bear.py` — Integration tests against a live Bear instance. All created notes are tagged `#temporary` and trashed in `tearDownClass`.
- `references/api.md` — Full Bear x-callback-url API parameter reference.
- `SKILL.md` — Skill entry point with trigger descriptions, quick reference table, and workflow examples.

## Development patterns

- `bear.py` uses only the Python standard library — no dependencies to install.
- `call_bear()` handles token injection, silent mode defaults (`show_window=no`, `open_note=no`), URL encoding, and JSON parsing of nested fields (`notes`, `tags`).
- xcall-lite uses `NSAppleEventManager` to register a `kAEGetURL` handler, then `NSWorkspace.shared.open()` to launch the Bear URL. The event loop (`NSApplication.run()`) blocks until the callback arrives or 30s timeout.
- The `.app` bundle is gitignored — it's built locally via `build-xcall-lite.sh`.

## Testing

```bash
BEAR_API_TOKEN="..." python3 scripts/test_bear.py -v
```

- Tests require Bear running and a valid API token.
- `TestBear` — Read-only tests (tags, today, todo, untagged, search). Safe, no side effects.
- `TestBearNoteLifecycle` — Full CRUD lifecycle: create → search by term → search by tag → open by ID → open by title → append → prepend. Single note, sequenced via test naming (`test_1_`, `test_2_`, ...).
- `TestBearTextFile`, `TestBearCreateWithTags`, `TestBearAddTextUnderHeader` — Focused tests for specific features.
- All notes are created with a `#temporary` tag and unique UUID-suffixed titles.
- Cleanup happens in `tearDownClass` so notes are trashed even if tests fail.

## Packaging

The skill can be packaged for distribution:
```bash
python3 ~/.claude/skills/skill-creator/scripts/package_skill.py ~/.claude/skills/bear
```
This validates and creates a `.skill` archive. The `.skill` file is gitignored.
