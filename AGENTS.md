# Bear Notes — Agent Tool Instructions

You have access to Bear, a macOS note-taking app, via a CLI tool at `scripts/bear.py`. All commands output JSON to stdout.

## Prerequisites

- `BEAR_API_TOKEN` must be set in the environment. If missing, tell the user to get it from Bear → Help → API Token.
- xcall-lite (the callback helper) auto-builds on first invocation. Requires Xcode command-line tools.

## Commands

Run as: `python3 <repo_path>/scripts/bear.py <command> [options]`

### Reading

| Command | Usage | Returns |
|---------|-------|---------|
| `open --id ID` | Read a note by UUID | Full note content in `note` field, plus `identifier`, `title`, `tags`, `creationDate`, `modificationDate`, `is_trashed` |
| `open --title TITLE` | Read a note by title (case-insensitive) | Same as above |
| `search --term TERM` | Full-text search | `notes` array: `{identifier, title, tags, modificationDate, creationDate, pin}` — metadata only, no content |
| `search --tag TAG` | Filter by tag | Same format as `--term` |
| `tags` | List all tags | `tags` array: `{name}` |
| `today` | Today's notes | `notes` array |
| `todo` | Notes with todo items | `notes` array |
| `untagged` | Notes without tags | `notes` array |
| `open-tag --name NAME` | Notes with a specific tag | `notes` array |

### Writing

| Command | Usage | Returns |
|---------|-------|---------|
| `create --title TITLE --text TEXT` | Create a note | `{identifier, title}` |
| `create --title TITLE --text-file PATH` | Create from file content | `{identifier, title}` |
| `add-text --id ID --text TEXT --mode MODE` | Add text to note | `{title}` |
| `add-text --title TITLE --text TEXT --header HEADER` | Add under a specific heading | `{title}` |
| `grab-url --url URL` | Create note from web page | `{identifier, title}` |

**`add-text` modes:** `append` (default), `prepend`, `replace_all`, `replace`

**Optional flags on `create`:** `--tags "t1,t2"`, `--pin`, `--timestamp`
**Optional flags on `add-text`:** `--newline` (add blank line before text), `--timestamp`
**Optional flags on `grab-url`:** `--tags "t1,t2"`, `--pin`

### Organizing

| Command | Usage |
|---------|-------|
| `trash --id ID` | Move note to trash |
| `trash --search TERM` | Trash all notes matching search term |
| `archive --id ID` | Archive a note |
| `rename-tag --name OLD --new-name NEW` | Rename tag across all notes |
| `delete-tag --name NAME` | Remove tag from all notes (notes kept) |

## Key behaviors

- **All commands run silently** — they don't steal focus or open Bear's window.
- **Prefer `--id` over `--title`** when you have the identifier. Title lookups are case-insensitive but if duplicates exist, Bear picks the most recently modified.
- **`search` returns metadata only** — to read content, follow up with `open --id`.
- **Tags are inline** in Bear (`#tag` in note body). The `--tags` parameter on `create` adds them to the body.
- **Nested tags** use `/`: `--tags "work/projects"`.
- **Long text** — use `--text-file` with a temp file to avoid shell escaping issues.
- **All JSON output** — pipe through `jq` or parse programmatically.

## Common workflows

### Search then read
```bash
python3 scripts/bear.py search --term "meeting notes"
# Pick an identifier from the results
python3 scripts/bear.py open --id "IDENTIFIER"
```

### Create with tags
```bash
python3 scripts/bear.py create --title "Title" --text "Body" --tags "project,notes"
```

### Append to existing note
```bash
python3 scripts/bear.py add-text --title "Daily Log" --text "New entry" --mode append --newline
```

### Append long content via temp file
Write content to a temp file, then:
```bash
python3 scripts/bear.py add-text --id "ID" --text-file /tmp/content.md --mode append
```

## Full API reference

See `references/api.md` for every Bear x-callback-url parameter and edge case.
