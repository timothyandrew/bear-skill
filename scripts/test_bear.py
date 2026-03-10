#!/usr/bin/env python3
"""Integration tests for Bear skill.

Requires:
  - Bear app running
  - BEAR_API_TOKEN set
  - xcall-lite built (auto-builds if missing)

Run:
  python3 test_bear.py
  python3 test_bear.py -v          # verbose
  python3 test_bear.py TestBear.test_tags  # single test
"""

import json
import os
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bear import call_bear


def unique(prefix="Claude Test"):
    """Generate a unique note title to avoid collisions."""
    return f"{prefix} {uuid.uuid4().hex[:8]}"


class TestBear(unittest.TestCase):
    """Tests that only read — safe to run without cleanup."""

    def test_tags(self):
        result = call_bear("tags")
        self.assertIn("tags", result)
        self.assertIsInstance(result["tags"], list)
        # Every tag should have a "name" field
        for tag in result["tags"]:
            self.assertIn("name", tag)

    def test_today(self):
        result = call_bear("today")
        self.assertIn("notes", result)
        self.assertIsInstance(result["notes"], list)

    def test_todo(self):
        result = call_bear("todo")
        self.assertIn("notes", result)
        self.assertIsInstance(result["notes"], list)

    def test_untagged(self):
        result = call_bear("untagged")
        self.assertIn("notes", result)
        self.assertIsInstance(result["notes"], list)

    def test_search(self):
        result = call_bear("search", {"term": "bear"})
        self.assertIn("notes", result)
        self.assertIsInstance(result["notes"], list)


class TestBearNoteLifecycle(unittest.TestCase):
    """Create → search → read → modify → trash lifecycle.

    Each test method is sequenced via ordering. A single note is created
    in setUpClass and trashed in tearDownClass so the suite cleans up
    even if individual tests fail.
    """

    note_id = None
    note_title = None

    @classmethod
    def setUpClass(cls):
        cls.note_title = unique()
        cls.note_body = "Hello from the test suite."
        result = call_bear("create", {
            "title": cls.note_title,
            "text": cls.note_body,
            "tags": "bear-test,temporary",
        })
        cls.note_id = result.get("identifier")
        assert cls.note_id, f"Failed to create note: {result}"

    @classmethod
    def tearDownClass(cls):
        if cls.note_id:
            call_bear("trash", {"id": cls.note_id})

    def test_1_create_returned_fields(self):
        self.assertIsNotNone(self.note_id)
        self.assertEqual(self.note_title, self.__class__.note_title)

    def test_2_search_finds_note(self):
        result = call_bear("search", {"term": self.note_title})
        notes = result.get("notes", [])
        ids = [n["identifier"] for n in notes]
        self.assertIn(self.note_id, ids)

    def test_3_search_by_tag(self):
        result = call_bear("search", {"tag": "bear-test"})
        notes = result.get("notes", [])
        ids = [n["identifier"] for n in notes]
        self.assertIn(self.note_id, ids)

    def test_4_open_by_id(self):
        result = call_bear("open-note", {"id": self.note_id})
        self.assertEqual(result["identifier"], self.note_id)
        self.assertEqual(result["title"], self.note_title)
        self.assertIn(self.note_body, result["note"])
        self.assertEqual(result["is_trashed"], "no")

    def test_5_open_by_title(self):
        result = call_bear("open-note", {"title": self.note_title})
        self.assertEqual(result["identifier"], self.note_id)

    def test_6_add_text_append(self):
        appended = "Appended line."
        result = call_bear("add-text", {
            "id": self.note_id,
            "text": appended,
            "mode": "append",
        })
        self.assertEqual(result["title"], self.note_title)
        # Verify content
        note = call_bear("open-note", {"id": self.note_id})
        self.assertIn(appended, note["note"])

    def test_7_add_text_prepend(self):
        prepended = "Prepended line."
        call_bear("add-text", {
            "id": self.note_id,
            "text": prepended,
            "mode": "prepend",
        })
        note = call_bear("open-note", {"id": self.note_id})
        # Prepended text should appear before original body
        body = note["note"]
        prep_pos = body.find(prepended)
        orig_pos = body.find(self.note_body)
        self.assertNotEqual(prep_pos, -1)
        self.assertLess(prep_pos, orig_pos)


class TestBearTextFile(unittest.TestCase):
    """Test --text-file equivalent: creating a note with file-sourced content."""

    note_id = None

    @classmethod
    def tearDownClass(cls):
        if cls.note_id:
            call_bear("trash", {"id": cls.note_id})

    def test_create_with_long_text(self):
        content = "## Section\n\n" + ("Lorem ipsum. " * 50) + "\n\n## End"
        title = unique("TextFile Test")
        result = call_bear("create", {"title": title, "text": content, "tags": "temporary"})
        self.__class__.note_id = result.get("identifier")
        self.assertIsNotNone(self.note_id)

        note = call_bear("open-note", {"id": self.note_id})
        self.assertIn("Lorem ipsum", note["note"])
        self.assertIn("## End", note["note"])


class TestBearCreateWithTags(unittest.TestCase):
    """Test creating a note with tags and verify they appear."""

    note_id = None

    @classmethod
    def tearDownClass(cls):
        if cls.note_id:
            call_bear("trash", {"id": cls.note_id})

    def test_tags_on_created_note(self):
        title = unique("Tags Test")
        result = call_bear("create", {
            "title": title,
            "text": "Body",
            "tags": "bear-test,bear-test-sub,temporary",
        })
        self.__class__.note_id = result.get("identifier")
        self.assertIsNotNone(self.note_id)

        note = call_bear("open-note", {"id": self.note_id})
        tags = note.get("tags", [])
        tag_names = [t if isinstance(t, str) else t.get("name", "") for t in tags]
        self.assertIn("bear-test", tag_names)
        self.assertIn("bear-test-sub", tag_names)


class TestBearAddTextUnderHeader(unittest.TestCase):
    """Test adding text under a specific header."""

    note_id = None

    @classmethod
    def tearDownClass(cls):
        if cls.note_id:
            call_bear("trash", {"id": cls.note_id})

    def test_add_under_header(self):
        title = unique("Header Test")
        result = call_bear("create", {
            "title": title,
            "text": "## Section A\nOriginal A\n## Section B\nOriginal B",
            "tags": "temporary",
        })
        self.__class__.note_id = result.get("identifier")
        self.assertIsNotNone(self.note_id)

        call_bear("add-text", {
            "id": self.note_id,
            "text": "Injected under B",
            "header": "Section B",
            "mode": "append",
        })
        note = call_bear("open-note", {"id": self.note_id})
        body = note["note"]
        self.assertIn("Injected under B", body)
        # Should appear after Section B header, not before Section A content
        b_pos = body.find("## Section B")
        inj_pos = body.find("Injected under B")
        self.assertGreater(inj_pos, b_pos)


if __name__ == "__main__":
    if not os.environ.get("BEAR_API_TOKEN"):
        print("Error: BEAR_API_TOKEN must be set.", file=sys.stderr)
        print("  export BEAR_API_TOKEN='your-token'", file=sys.stderr)
        sys.exit(1)
    unittest.main()
