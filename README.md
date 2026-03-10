# bear-skill

A command-line interface for the [Bear](https://bear.app) macOS note-taking app. Wraps Bear's x-callback-url API into a simple `bear.py` CLI that outputs JSON — suitable for scripting, automation, or as a tool for AI agents.

## How it works

Bear exposes an `x-callback-url` API (`bear://x-callback-url/...`), but these callbacks need a registered macOS app to receive responses. This repo bundles:

1. **`xcall-lite`** — A minimal Swift app (~50 lines) that sends a `bear://` URL, captures the callback response, and prints it as JSON to stdout. Runs as a background-only app (no Dock icon), times out after 30 seconds.

2. **`bear.py`** — A Python CLI (stdlib only, no dependencies) with subcommands for every Bear API action. Handles URL encoding, API token injection, and response parsing.

## Setup

### Prerequisites

- macOS with [Bear](https://bear.app) installed
- Xcode command-line tools (`xcode-select --install`)
- Python 3

### Install

```bash
git clone https://github.com/timothyandrew/bear-skill.git
cd bear-skill
```

### Set your API token

Get your token from Bear → Help → API Token, then add to your shell profile:

```bash
echo 'export BEAR_API_TOKEN="your-token-here"' >> ~/.zshrc
```

### Build xcall-lite

This happens automatically on first use, but you can also build manually:

```bash
bash scripts/build-xcall-lite.sh
```

## Usage

```bash
export BEAR_API_TOKEN="your-token"

# List all tags
python3 scripts/bear.py tags

# Create a note
python3 scripts/bear.py create --title "My Note" --text "Content here" --tags "tag1,tag2"

# Search
python3 scripts/bear.py search --term "meeting"

# Read a note
python3 scripts/bear.py open --title "My Note"

# Append text
python3 scripts/bear.py add-text --title "My Note" --text "More content" --mode append

# Trash
python3 scripts/bear.py trash --id "NOTE-UUID"
```

Run `python3 scripts/bear.py --help` for all subcommands, or `python3 scripts/bear.py <subcommand> --help` for details.

## Supported actions

| Command      | Description                        |
|--------------|------------------------------------|
| `create`     | Create a new note                  |
| `open`       | Read a note by ID or title         |
| `search`     | Search notes by term or tag        |
| `add-text`   | Append/prepend text to a note      |
| `tags`       | List all tags                      |
| `open-tag`   | List notes with a tag              |
| `rename-tag` | Rename a tag across all notes      |
| `delete-tag` | Remove a tag from all notes        |
| `trash`      | Move a note to trash               |
| `archive`    | Archive a note                     |
| `today`      | Show today's notes                 |
| `todo`       | Show notes with todo items         |
| `untagged`   | Show untagged notes                |
| `grab-url`   | Create a note from a web page URL  |

## Tests

Integration tests run against a live Bear instance:

```bash
export BEAR_API_TOKEN="your-token"
python3 scripts/test_bear.py -v
```

Tests create notes tagged `#temporary` and trash them after each test class, even on failure.

## Agent integration

`AGENTS.md` contains tool-use instructions that any AI agent can consume — it describes every subcommand, its parameters, output format, and common workflows. Point your agent at this file to give it Bear access.

For Claude Code specifically, install as a skill:

```bash
git clone https://github.com/timothyandrew/bear-skill.git ~/.claude/skills/bear
```

## API reference

See `references/api.md` for the full Bear x-callback-url API with all parameters and return values.
