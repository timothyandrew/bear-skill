---
name: bear
description: >
  Interface with the Bear macOS note-taking app. Create notes, read notes, search notes,
  append or prepend text to notes, manage tags (list, rename, delete), trash or archive notes,
  view today's notes, todo notes, untagged notes, and grab web pages into Bear.
  Triggers on: "bear note", "create a note", "add to my bear", "search bear", "bear tags",
  "save to bear", "bear app", "note in bear", "append to bear note", "my notes".
---

# Bear App Integration

Interface with Bear notes via its x-callback-url API. All operations run silently (no focus stealing) by default.

## Prerequisites

Before first use, ensure:
1. **Bear app** is installed and has been opened at least once
2. **API token** is set: `export BEAR_API_TOKEN="your-token-here"` (get from Bear → Help → API Token)
3. **xcall-lite** will auto-build on first invocation (requires Xcode command-line tools)

If the token is not set, check if `BEAR_API_TOKEN` exists in the user's shell environment. If not, tell them to get it from Bear → Help → API Token and set it in their shell profile.

## Scripts

- `scripts/bear.py` — Main CLI wrapper. Run with `python3 <skill_path>/scripts/bear.py <command> [options]`
- `scripts/build-xcall-lite.sh` — Builds the xcall-lite helper app (auto-runs on first use)

## Quick Reference

| User intent                        | Command                                                              |
|------------------------------------|----------------------------------------------------------------------|
| Create a note                      | `bear.py create --title "Title" --text "Body" --tags "tag1,tag2"`    |
| Read a note by title               | `bear.py open --title "Note Title"`                                  |
| Read a note by ID                  | `bear.py open --id "NOTE-UUID"`                                      |
| Search notes                       | `bear.py search --term "query"`                                      |
| Search by tag                      | `bear.py search --tag "tagname"`                                     |
| Append text to a note              | `bear.py add-text --title "Title" --text "New content" --mode append`|
| Prepend text to a note             | `bear.py add-text --title "Title" --text "New content" --mode prepend`|
| Add text under a specific header   | `bear.py add-text --title "Title" --text "Content" --header "H2"`    |
| List all tags                      | `bear.py tags`                                                       |
| Rename a tag                       | `bear.py rename-tag --name "old" --new-name "new"`                   |
| Delete a tag                       | `bear.py delete-tag --name "tagname"`                                |
| Trash a note                       | `bear.py trash --id "NOTE-UUID"`                                     |
| Trash notes by search              | `bear.py trash --search "query"`                                     |
| Archive a note                     | `bear.py archive --id "NOTE-UUID"`                                   |
| Today's notes                      | `bear.py today`                                                      |
| Notes with todos                   | `bear.py todo`                                                       |
| Untagged notes                     | `bear.py untagged`                                                   |
| Save web page as note              | `bear.py grab-url --url "https://..." --tags "web,reading"`          |

## Common Workflows

### Search then read
```bash
# Find the note
python3 scripts/bear.py search --term "meeting notes"
# Read it (use the identifier from search results)
python3 scripts/bear.py open --id "IDENTIFIER-FROM-SEARCH"
```

### Create a rich note
```bash
python3 scripts/bear.py create --title "Project Plan" --text "## Overview\n\nDetails here..." --tags "work,projects" --pin
```

### Append to an existing note using a file
For long content, write it to a temp file first:
```bash
python3 scripts/bear.py add-text --title "Daily Log" --text-file /tmp/entry.md --mode append --newline
```

### Bulk operations
Search returns a JSON array of notes with identifiers. Use `jq` or Python to iterate:
```bash
python3 scripts/bear.py search --term "old project" | jq -r '.notes[].identifier'
```

## Important Notes

- **Silent mode**: All commands default to `show_window=no` and `open_note=no` to avoid stealing focus
- **URL encoding**: Handled automatically by `bear.py` — pass plain text
- **Note IDs**: Prefer `--id` over `--title` when you have the identifier (more reliable)
- **Title matching**: Case-insensitive; if duplicates exist, Bear picks the most recently modified
- **Tags**: Bear tags are inline (`#tag` in note body). The `--tags` parameter adds them to the body
- **Nested tags**: Use `/` separator, e.g. `--tags "work/projects"`
- **Long text**: Use `--text-file` to avoid shell escaping issues with long content
- **Return values**: `open` returns the full note content in a `note` field; `search` returns a `notes` array with metadata only

## Full API Details

See `references/api.md` for the complete Bear x-callback-url API reference with all parameters and return values.
