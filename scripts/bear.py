#!/usr/bin/env python3
"""CLI wrapper for Bear app x-callback-url API."""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
XCALL_APP = os.path.join(SCRIPT_DIR, "xcall-lite.app", "Contents", "MacOS", "xcall-lite")
BUILD_SCRIPT = os.path.join(SCRIPT_DIR, "build-xcall-lite.sh")

# Actions that require an API token
TOKEN_ACTIONS = {
    "open-note", "create", "add-text", "add-file", "tags", "open-tag",
    "rename-tag", "delete-tag", "trash", "archive", "untagged", "todo",
    "today", "locked", "search", "grab-url",
}

# Actions where we default show_window=no
SILENT_ACTIONS = {
    "open-note", "create", "add-text", "tags", "search", "grab-url",
    "trash", "archive", "untagged", "todo", "today",
}


def ensure_xcall_built():
    """Build xcall-lite if not already built."""
    if not os.path.isfile(XCALL_APP):
        print("Building xcall-lite...", file=sys.stderr)
        result = subprocess.run(["bash", BUILD_SCRIPT], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to build xcall-lite:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print(result.stdout.strip(), file=sys.stderr)


def call_bear(action, params=None):
    """Call a Bear x-callback-url action and return parsed JSON response."""
    ensure_xcall_built()

    if params is None:
        params = {}

    # Inject API token if needed
    if action in TOKEN_ACTIONS:
        token = os.environ.get("BEAR_API_TOKEN", "")
        if not token:
            print(
                "Error: BEAR_API_TOKEN environment variable is required for this action.\n"
                "Get your token from Bear → Help → API Token.",
                file=sys.stderr,
            )
            sys.exit(1)
        params["token"] = token

    # Default to silent mode where applicable
    if action in SILENT_ACTIONS:
        params.setdefault("show_window", "no")
    if action in ("create", "add-text", "grab-url"):
        params.setdefault("open_note", "no")

    # Build URL
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    url = f"bear://x-callback-url/{action}"
    if query:
        url += f"?{query}"

    # Call xcall-lite
    result = subprocess.run(
        [XCALL_APP, url],
        capture_output=True,
        text=True,
        timeout=35,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        try:
            error_data = json.loads(result.stdout)
            print(json.dumps(error_data, indent=2))
        except (json.JSONDecodeError, ValueError):
            if stderr:
                print(f"Error: {stderr}", file=sys.stderr)
            if result.stdout.strip():
                print(result.stdout.strip(), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        data = {"raw_output": result.stdout.strip()}

    # Some Bear responses contain JSON-encoded arrays in 'notes' or 'tags' fields
    for key in ("notes", "tags"):
        if key in data and isinstance(data[key], str):
            try:
                data[key] = json.loads(data[key])
            except (json.JSONDecodeError, ValueError):
                pass

    return data


def read_text_input(args):
    """Get text content from --text or --text-file."""
    if hasattr(args, "text_file") and args.text_file:
        with open(args.text_file, "r") as f:
            return f.read()
    if hasattr(args, "text") and args.text:
        return args.text
    return None


def cmd_create(args):
    params = {}
    if args.title:
        params["title"] = args.title
    text = read_text_input(args)
    if text:
        params["text"] = text
    if args.tags:
        params["tags"] = args.tags
    if args.pin:
        params["pin"] = "yes"
    if args.timestamp:
        params["timestamp"] = "yes"
    result = call_bear("create", params)
    print(json.dumps(result, indent=2))


def cmd_open(args):
    params = {}
    if args.id:
        params["id"] = args.id
    if args.title:
        params["title"] = args.title
    if args.header:
        params["header"] = args.header
    if args.exclude_trashed:
        params["exclude_trashed"] = "yes"
    result = call_bear("open-note", params)
    print(json.dumps(result, indent=2))


def cmd_search(args):
    params = {}
    if args.term:
        params["term"] = args.term
    if args.tag:
        params["tag"] = args.tag
    result = call_bear("search", params)
    print(json.dumps(result, indent=2))


def cmd_add_text(args):
    params = {}
    if args.id:
        params["id"] = args.id
    if args.title:
        params["title"] = args.title
    text = read_text_input(args)
    if text:
        params["text"] = text
    if args.header:
        params["header"] = args.header
    if args.mode:
        params["mode"] = args.mode
    if args.newline:
        params["new_line"] = "yes"
    if args.timestamp:
        params["timestamp"] = "yes"
    result = call_bear("add-text", params)
    print(json.dumps(result, indent=2))


def cmd_tags(args):
    result = call_bear("tags")
    print(json.dumps(result, indent=2))


def cmd_open_tag(args):
    params = {"name": args.name}
    result = call_bear("open-tag", params)
    print(json.dumps(result, indent=2))


def cmd_rename_tag(args):
    params = {"name": args.name, "new_name": args.new_name}
    result = call_bear("rename-tag", params)
    print(json.dumps(result, indent=2))


def cmd_delete_tag(args):
    params = {"name": args.name}
    result = call_bear("delete-tag", params)
    print(json.dumps(result, indent=2))


def cmd_trash(args):
    params = {}
    if args.id:
        params["id"] = args.id
    if args.search:
        # Search first, then trash each result
        search_result = call_bear("search", {"term": args.search})
        notes = search_result.get("notes", [])
        if isinstance(notes, str):
            try:
                notes = json.loads(notes)
            except (json.JSONDecodeError, ValueError):
                notes = []
        trashed = []
        for note in notes:
            note_id = note.get("identifier")
            if note_id:
                call_bear("trash", {"id": note_id, "show_window": "no"})
                trashed.append({"id": note_id, "title": note.get("title", "")})
        print(json.dumps({"trashed": trashed}, indent=2))
        return
    result = call_bear("trash", params)
    print(json.dumps(result, indent=2))


def cmd_archive(args):
    params = {}
    if args.id:
        params["id"] = args.id
    result = call_bear("archive", params)
    print(json.dumps(result, indent=2))


def cmd_today(args):
    result = call_bear("today")
    print(json.dumps(result, indent=2))


def cmd_todo(args):
    result = call_bear("todo")
    print(json.dumps(result, indent=2))


def cmd_untagged(args):
    result = call_bear("untagged")
    print(json.dumps(result, indent=2))


def cmd_grab_url(args):
    params = {"url": args.url}
    if args.tags:
        params["tags"] = args.tags
    if args.pin:
        params["pin"] = "yes"
    result = call_bear("grab-url", params)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Bear app CLI wrapper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p = subparsers.add_parser("create", help="Create a new note")
    p.add_argument("--title", help="Note title")
    p.add_argument("--text", help="Note body (markdown)")
    p.add_argument("--text-file", help="Read note body from file")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--pin", action="store_true", help="Pin the note")
    p.add_argument("--timestamp", action="store_true", help="Prepend timestamp")
    p.set_defaults(func=cmd_create)

    # open
    p = subparsers.add_parser("open", help="Open/read a note")
    p.add_argument("--id", help="Note unique identifier")
    p.add_argument("--title", help="Note title")
    p.add_argument("--header", help="Scroll to header")
    p.add_argument("--exclude-trashed", action="store_true", help="Exclude trashed notes")
    p.set_defaults(func=cmd_open)

    # search
    p = subparsers.add_parser("search", help="Search notes")
    p.add_argument("--term", help="Search term")
    p.add_argument("--tag", help="Filter by tag")
    p.set_defaults(func=cmd_search)

    # add-text
    p = subparsers.add_parser("add-text", help="Append/prepend text to a note")
    p.add_argument("--id", help="Note unique identifier")
    p.add_argument("--title", help="Note title")
    p.add_argument("--text", help="Text to add")
    p.add_argument("--text-file", help="Read text from file")
    p.add_argument("--header", help="Add text under this header")
    p.add_argument("--mode", choices=["prepend", "append", "replace_all", "replace"],
                   default="append", help="Where to add text (default: append)")
    p.add_argument("--newline", action="store_true", help="Add newline before text")
    p.add_argument("--timestamp", action="store_true", help="Prepend timestamp")
    p.set_defaults(func=cmd_add_text)

    # tags
    p = subparsers.add_parser("tags", help="List all tags")
    p.set_defaults(func=cmd_tags)

    # open-tag
    p = subparsers.add_parser("open-tag", help="Open tag in Bear")
    p.add_argument("--name", required=True, help="Tag name")
    p.set_defaults(func=cmd_open_tag)

    # rename-tag
    p = subparsers.add_parser("rename-tag", help="Rename a tag")
    p.add_argument("--name", required=True, help="Current tag name")
    p.add_argument("--new-name", required=True, help="New tag name")
    p.set_defaults(func=cmd_rename_tag)

    # delete-tag
    p = subparsers.add_parser("delete-tag", help="Delete a tag")
    p.add_argument("--name", required=True, help="Tag name to delete")
    p.set_defaults(func=cmd_delete_tag)

    # trash
    p = subparsers.add_parser("trash", help="Trash a note")
    p.add_argument("--id", help="Note unique identifier")
    p.add_argument("--search", help="Search term — trash all matching notes")
    p.set_defaults(func=cmd_trash)

    # archive
    p = subparsers.add_parser("archive", help="Archive a note")
    p.add_argument("--id", required=True, help="Note unique identifier")
    p.set_defaults(func=cmd_archive)

    # today
    p = subparsers.add_parser("today", help="Show today's notes")
    p.set_defaults(func=cmd_today)

    # todo
    p = subparsers.add_parser("todo", help="Show notes with todos")
    p.set_defaults(func=cmd_todo)

    # untagged
    p = subparsers.add_parser("untagged", help="Show untagged notes")
    p.set_defaults(func=cmd_untagged)

    # grab-url
    p = subparsers.add_parser("grab-url", help="Create note from web page URL")
    p.add_argument("--url", required=True, help="Web page URL to grab")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--pin", action="store_true", help="Pin the note")
    p.set_defaults(func=cmd_grab_url)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
