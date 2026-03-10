# Bear x-callback-url API Reference

Base URL: `bear://x-callback-url/<action>`

All actions support `x-success`, `x-error`, and `x-cancel` callback parameters.

## Authentication

Many actions require an **API token** passed as `token=<value>`. Get your token from Bear → Help → API Token. Set it as `BEAR_API_TOKEN` environment variable.

---

## Actions

### /create

Create a new note.

| Parameter        | Required | Description                                                    |
|-----------------|----------|----------------------------------------------------------------|
| `title`         | No       | Title of the note                                              |
| `text`          | No       | Body of the note (markdown)                                    |
| `clipboard`     | No       | Set to `yes` to use clipboard contents as body                 |
| `tags`          | No       | Comma-separated list of tags                                   |
| `open_note`     | No       | `yes`/`no` — open the note after creation (default: yes)       |
| `new_window`    | No       | `yes`/`no` — open in new window                                |
| `float`         | No       | `yes`/`no` — make window float on top                          |
| `show_window`   | No       | `yes`/`no` — show Bear main window (default: yes)              |
| `pin`           | No       | `yes`/`no` — pin the note                                      |
| `edit`          | No       | `yes`/`no` — place cursor inside the note                      |
| `timestamp`     | No       | `yes`/`no` — prepend creation date as title                    |
| `token`         | Yes      | API token                                                      |

**Returns:** `identifier` (note UUID), `title`

### /open-note

Open or retrieve a note by ID or title.

| Parameter          | Required | Description                                          |
|-------------------|----------|------------------------------------------------------|
| `id`              | No*      | Note unique identifier                               |
| `title`           | No*      | Note title (case-insensitive)                        |
| `header`          | No       | Scroll to and select this header                     |
| `exclude_trashed` | No       | `yes`/`no` — exclude trashed notes from title search |
| `new_window`      | No       | `yes`/`no`                                           |
| `float`           | No       | `yes`/`no`                                           |
| `show_window`     | No       | `yes`/`no`                                           |
| `open_note`       | No       | `yes`/`no`                                           |
| `selected`        | No       | `yes`/`no` — return only selected text               |
| `pin`             | No       | `yes`/`no`                                           |
| `edit`            | No       | `yes`/`no`                                           |
| `token`           | Yes      | API token                                            |

*At least one of `id` or `title` is required.

**Returns:** `note` (full markdown content), `identifier`, `title`, `is_trashed`, `modificationDate`, `creationDate`, `tags`

### /search

Search notes.

| Parameter      | Required | Description                                      |
|---------------|----------|--------------------------------------------------|
| `term`        | No       | Search term                                      |
| `tag`         | No       | Tag to filter by                                 |
| `show_window` | No       | `yes`/`no`                                       |
| `token`       | Yes      | API token                                        |

**Returns:** `notes` — JSON array of `{identifier, title, tags, modificationDate, creationDate, pin}`

### /add-text

Add text to an existing note.

| Parameter    | Required | Description                                                        |
|-------------|----------|--------------------------------------------------------------------|
| `id`        | No*      | Note unique identifier                                             |
| `title`     | No*      | Note title                                                         |
| `text`      | Yes      | Text to add (markdown supported)                                   |
| `clipboard` | No       | `yes` to use clipboard                                             |
| `header`    | No       | Add text below this header                                         |
| `mode`      | No       | `prepend`, `append` (default), `replace_all`, `replace`            |
| `new_line`  | No       | `yes`/`no` — add newline before text                               |
| `tags`      | No       | Comma-separated tags to add                                        |
| `edit`      | No       | `yes`/`no`                                                         |
| `open_note` | No       | `yes`/`no`                                                         |
| `show_window`| No      | `yes`/`no`                                                         |
| `timestamp` | No       | `yes`/`no`                                                         |
| `token`     | Yes      | API token                                                          |

*At least one of `id` or `title` is required.

**Returns:** `identifier`, `title`

### /add-file

Add a file to a note.

| Parameter     | Required | Description                                      |
|--------------|----------|--------------------------------------------------|
| `id`         | No*      | Note unique identifier                           |
| `title`      | No*      | Note title                                       |
| `file`       | Yes      | Base64-encoded file data                         |
| `filename`   | Yes      | File name with extension                         |
| `header`     | No       | Place file below this header                     |
| `mode`       | No       | `prepend`, `append` (default), `replace_all`     |
| `open_note`  | No       | `yes`/`no`                                       |
| `show_window`| No       | `yes`/`no`                                       |
| `token`      | Yes      | API token                                        |

**Returns:** `identifier`, `title`

### /tags

List all tags.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `token`   | Yes      | API token   |

**Returns:** `tags` — JSON array of `{name, count}`

### /open-tag

Show notes with a specific tag.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name`    | Yes      | Tag name    |
| `token`   | Yes      | API token   |

**Returns:** `notes` — JSON array (same format as `/search`)

### /rename-tag

Rename a tag across all notes.

| Parameter  | Required | Description     |
|-----------|----------|-----------------|
| `name`    | Yes      | Current tag name|
| `new_name`| Yes      | New tag name    |
| `token`   | Yes      | API token       |

**Returns:** (empty on success)

### /delete-tag

Remove a tag from all notes (does not delete the notes).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name`    | Yes      | Tag name    |
| `token`   | Yes      | API token   |

**Returns:** (empty on success)

### /trash

Move a note to trash.

| Parameter      | Required | Description                  |
|---------------|----------|------------------------------|
| `id`          | Yes      | Note unique identifier       |
| `show_window` | No       | `yes`/`no`                   |
| `token`       | Yes      | API token                    |

**Returns:** (empty on success)

### /archive

Archive a note.

| Parameter      | Required | Description                  |
|---------------|----------|------------------------------|
| `id`          | Yes      | Note unique identifier       |
| `show_window` | No       | `yes`/`no`                   |
| `token`       | Yes      | API token                    |

**Returns:** (empty on success)

### /untagged

Show untagged notes.

| Parameter      | Required | Description  |
|---------------|----------|--------------|
| `show_window` | No       | `yes`/`no`   |
| `token`       | Yes      | API token    |

**Returns:** `notes` — JSON array

### /todo

Show notes containing todo items.

| Parameter      | Required | Description  |
|---------------|----------|--------------|
| `show_window` | No       | `yes`/`no`   |
| `token`       | Yes      | API token    |

**Returns:** `notes` — JSON array

### /today

Show today's notes.

| Parameter      | Required | Description  |
|---------------|----------|--------------|
| `show_window` | No       | `yes`/`no`   |
| `token`       | Yes      | API token    |

**Returns:** `notes` — JSON array

### /locked

Show locked notes (only titles, no content).

| Parameter      | Required | Description  |
|---------------|----------|--------------|
| `show_window` | No       | `yes`/`no`   |
| `token`       | Yes      | API token    |

**Returns:** `notes` — JSON array

### /grab-url

Create a note from a web page.

| Parameter      | Required | Description                                |
|---------------|----------|--------------------------------------------|
| `url`         | Yes      | Web page URL                               |
| `tags`        | No       | Comma-separated tags                       |
| `pin`         | No       | `yes`/`no`                                 |
| `open_note`   | No       | `yes`/`no`                                 |
| `show_window` | No       | `yes`/`no`                                 |
| `token`       | Yes      | API token                                  |

**Returns:** `identifier`, `title`

---

## Notes

- **Note identifiers** are stable UUIDs. Prefer `id` over `title` when you have it.
- **Title lookups** are case-insensitive. If multiple notes share a title, Bear uses the most recently modified one.
- **Tags** in Bear are inline (`#tag` in note body). The `tags` parameter on `/create` adds them to the body.
- **Nested tags** use `/` separator: `#work/projects`.
- **Markdown** is the native format. Bear uses its own flavor but standard markdown works.
- **show_window=no** prevents Bear from stealing focus — ideal for programmatic use.
- **open_note=no** prevents the note from being opened in the editor after creation/modification.
