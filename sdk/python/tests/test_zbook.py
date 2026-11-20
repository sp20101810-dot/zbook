import base64
import tempfile
import unittest
from pathlib import Path

from sdk.python import zbook


class ZbookSdkTests(unittest.TestCase):
    def test_new_book_round_trip(self):
        book = zbook.new_book("Test book", author="Test Author")
        book["chapters"].append({
            "id": "chapter-1",
            "title": "Start",
            "content": "# Hello",
        })
        encoded = zbook.dumps(book)
        decoded = zbook.loads(encoded)
        self.assertEqual(decoded["metadata"]["title"], "Test book")
        self.assertEqual(decoded["chapters"][0]["id"], "chapter-1")

    def test_example_shape_is_valid(self):
        book = {
            "format": "ZBOOK",
            "version": "1.0",
            "metadata": {"title": "Example"},
            "chapters": [{"id": "one", "title": "First", "content": "Text"}],
            "resources": [],
        }
        self.assertEqual(zbook.validate_book(book), [])

    def test_missing_required_fields_fail(self):
        with self.assertRaises(zbook.ZbookValidationError):
            zbook.loads('{"format":"ZBOOK","version":"1.0"}')

    def test_duplicate_chapter_ids_fail(self):
        book = zbook.new_book("Duplicate IDs")
        book["chapters"] = [
            {"id": "same", "title": "One"},
            {"id": "same", "title": "Two"},
        ]
        self.assertTrue(any("must be unique" in item for item in zbook.validate_book(book)))

    def test_invalid_base64_fails(self):
        book = zbook.new_book("Bad resource")
        book["resources"] = [{
            "id": "cover",
            "type": "image",
            "mediaType": "image/png",
            "data": "not base64!",
        }]
        self.assertTrue(any("valid base64" in item for item in zbook.validate_book(book)))

    def test_valid_embedded_resource_and_reference(self):
        payload = base64.b64encode(b"fake-image-bytes").decode("ascii")
        book = zbook.new_book("With image")
        book["resources"] = [{
            "id": "cover",
            "type": "image",
            "mediaType": "image/png",
            "data": payload,
        }]
        book["chapters"] = [{
            "id": "one",
            "title": "Cover",
            "blocks": [{"type": "image", "resource": "cover", "alt": "Cover image"}],
        }]
        self.assertEqual(zbook.validate_book(book), [])

    def test_unsafe_resource_path_fails(self):
        book = zbook.new_book("Unsafe path")
        book["resources"] = [{
            "id": "cover",
            "type": "image",
            "mediaType": "image/png",
            "path": "../outside.png",
        }]
        self.assertTrue(any("safe relative path" in item for item in zbook.validate_book(book)))

    def test_file_write_and_read(self):
        book = zbook.new_book("File test")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "test.zbook"
            zbook.dump(book, path)
            self.assertEqual(zbook.load(path)["metadata"]["title"], "File test")

    def test_wrong_extension_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                zbook.dump(zbook.new_book("Wrong extension"), Path(folder) / "book.json")

    def test_invalid_json_fails(self):
        with self.assertRaises(zbook.ZbookParseError):
            zbook.loads("{ definitely not json }")


if __name__ == "__main__":
    unittest.main()
