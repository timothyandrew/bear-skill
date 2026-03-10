# Bear Skill for Claude Code

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that interfaces with the [Bear](https://bear.app) macOS note-taking app via its x-callback-url API.

## What it does

When installed as a Claude Code skill, Claude can directly read, create, search, and modify your Bear notes through natural conversation. Ask things like:

- "Search my Bear notes for meeting notes"
- "Create a note in Bear titled Project Plan with these details..."
- "Append this summary to my Daily Log note"
- "What tags do I have in Bear?"
- "Trash the note called Old Draft"

## How it works

Bear exposes an `x-callback-url` API (`bear://x-callback-url/...`), but these callbacks need a registered macOS app to receive responses. This skill bundles:

1. **`xcall-lite`** — A minimal Swift app (~50 lines) that sends a `bear://` URL, captures the callback response, and prints it as JSON to stdout. It registers a `xcall-lite-callback://` URL scheme, runs as a background-only app (no Dock icon), and times out after 30 seconds.

2. **`bear.py`** — A Python CLI wrapper (stdlib only) with subcommands for every Bear API action. It builds URLs, handles encoding, injects the API token, and parses responses.

3. **`SKILL.md`** — The skill definition that teaches Claude when and how to use these tools.

## Setup

### Prerequisites

- macOS with [Bear](https://bear.app) installed
- Xcode command-line tools (`xcode-select --install`)
- Python 3

### Install as a Claude Code skill

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/timothyandrew/bear-skill.git ~/.claude/skills/bear
```

### Set your API token

Get your token from Bear → Help → API Token, then add to your shell profile:

```bash
echo 'export BEAR_API_TOKEN="your-token-here"' >> ~/.zshrc
```

### Build xcall-lite

This happens automatically on first use, but you can also build manually:

```bash
cd ~/.claude/skills/bear
bash scripts/build-xcall-lite.sh
```

## Standalone CLI usage

The `bear.py` script works independently of Claude Code:

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

Run `python3 scripts/bear.py --help` for all subcommands, or `python3 scripts/bear.py <subcommand> --help` for details on each.

## Tests

Integration tests run against a live Bear instance:

```bash
export BEAR_API_TOKEN="your-token"
python3 scripts/test_bear.py -v
```

Tests create notes tagged `#temporary` and trash them after each test class, even on failure.

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
