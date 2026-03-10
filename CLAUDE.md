# CLAUDE.md

## Project overview

A CLI for Bear's x-callback-url API, designed for both standalone use and as a tool for AI agents. Three layers:

1. `xcall-lite.swift` — Swift CLI that opens a `bear://` URL, captures the callback via a registered URL scheme (`xcall-lite-callback://`), and prints JSON to stdout.
2. `bear.py` — Python CLI (stdlib only) with subcommands for each Bear action. Calls xcall-lite via subprocess.
3. `AGENT.md` — Agent-readable tool instructions. `SKILL.md` is the Claude Code-specific integration.

## Key files

- `scripts/xcall-lite.swift` — The Swift source. Compiles to an `.app` bundle so macOS recognizes its URL scheme.
- `scripts/Info.plist` — Registers the `xcall-lite-callback://` scheme. `LSBackgroundOnly=true` so no Dock icon.
- `scripts/build-xcall-lite.sh` — Builds the .app bundle and registers with LaunchServices. Idempotent (skips if source unchanged).
- `scripts/bear.py` — The main CLI. `call_bear(action, params)` is the core function — builds the URL, injects token, invokes xcall-lite, parses response. Auto-builds xcall-lite on first use.
- `scripts/test_bear.py` — Integration tests against a live Bear instance. All created notes are tagged `#temporary` and trashed in `tearDownClass`.
- `references/api.md` — Full Bear x-callback-url API parameter reference.
- `AGENT.md` — Generic agent instructions: every command, its params, output format, and workflows. Any agent framework can consume this.
- `SKILL.md` — Claude Code skill entry point with frontmatter triggers. Points to bear.py.

## Development patterns

- `bear.py` uses only the Python standard library — no dependencies.
- `call_bear()` handles token injection, silent mode defaults (`show_window=no`, `open_note=no`), URL encoding, and JSON parsing of nested fields (`notes`, `tags`).
- xcall-lite uses `NSAppleEventManager` to register a `kAEGetURL` handler, then `NSWorkspace.shared.open()` to launch the Bear URL. `NSApplication.run()` blocks until callback or 30s timeout.
- The `.app` bundle is gitignored — built locally via `build-xcall-lite.sh`.

## Testing

```bash
BEAR_API_TOKEN="..." python3 scripts/test_bear.py -v
```

- Tests require Bear running and a valid API token.
- `TestBear` — Read-only tests (tags, today, todo, untagged, search). No side effects.
- `TestBearNoteLifecycle` — Full CRUD: create → search → open → append → prepend. Sequenced via `test_1_` naming.
- `TestBearTextFile`, `TestBearCreateWithTags`, `TestBearAddTextUnderHeader` — Focused feature tests.
- All notes tagged `#temporary` with UUID-suffixed titles. Trashed in `tearDownClass`.
