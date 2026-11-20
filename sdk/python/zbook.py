"""Small, dependency-free reader/writer and validator for ZBOOK 1.0.

This SDK follows the repository's ZBOOK Format Specification Draft 0.1.
It handles the JSON document structure; it does not render Markdown, fetch
external resources, unpack archives, or execute embedded content.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

MEDIA_TYPE = "application/prs.zbook"
FORMAT_NAME = "ZBOOK"
FORMAT_VERSION = "1.0"

DEFAULT_MAX_FILE_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_RESOURCE_BYTES = 20 * 1024 * 1024
DEFAULT_MAX_CHAPTERS = 10_000
DEFAULT_MAX_RESOURCES = 1_000

_MEDIA_TYPE_RE = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$")
_BLOCK_TYPES = {"paragraph", "heading", "image", "audio", "quote", "list"}


class ZbookError(Exception):
    """Base exception for ZBOOK SDK errors."""


class ZbookParseError(ZbookError):
    """Raised when a ZBOOK file is not valid UTF-8 JSON."""


class ZbookValidationError(ZbookError):
    """Raised when a ZBOOK document does not satisfy the supported 1.0 rules."""

    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("Invalid ZBOOK document:\n- " + "\n- ".join(self.errors))


def validate_book(
    book: Any,
    *,
    max_chapters: int = DEFAULT_MAX_CHAPTERS,
    max_resources: int = DEFAULT_MAX_RESOURCES,
    max_resource_bytes: int = DEFAULT_MAX_RESOURCE_BYTES,
) -> list[str]:
    """Return validation errors. An empty list means the document passed.

    Unknown optional properties are preserved and ignored, as described by
    the specification. Resource paths are checked but never opened.
    """
    errors: list[str] = []

    def err(path: str, message: str) -> None:
        errors.append(f"{path}: {message}")

    if not isinstance(book, dict):
        return ["$: document must be a JSON object"]

    if book.get("format") != FORMAT_NAME:
        err("$.format", 'must be exactly "ZBOOK"')

    if book.get("version") != FORMAT_VERSION:
        err("$.version", 'this SDK supports version "1.0" only')

    metadata = book.get("metadata")
    if not isinstance(metadata, dict):
        err("$.metadata", "must be an object")
    else:
        title = metadata.get("title")
        if not isinstance(title, str) or not title.strip():
            err("$.metadata.title", "is required and must be a non-empty string")
        author = metadata.get("author")
        if author is not None:
            if isinstance(author, str):
                pass
            elif isinstance(author, list) and all(isinstance(item, str) for item in author):
                pass
            else:
                err("$.metadata.author", "must be a string or an array of strings")
        for key in ("language", "description", "publisher", "published", "identifier", "rights"):
            if key in metadata and not isinstance(metadata[key], str):
                err(f"$.metadata.{key}", "must be a string")

    ownership = book.get("ownership")
    if ownership is not None:
        if not isinstance(ownership, dict):
            err("$.ownership", "must be an object")
        else:
            for key in ("creator", "format_name", "specification_version", "website"):
                if key in ownership and not isinstance(ownership[key], str):
                    err(f"$.ownership.{key}", "must be a string")
            if "format_name" in ownership and ownership["format_name"] != FORMAT_NAME:
                err("$.ownership.format_name", 'must be "ZBOOK"')

    chapters = book.get("chapters")
    chapter_ids: set[str] = set()
    if not isinstance(chapters, list):
        err("$.chapters", "is required and must be an array")
        chapters = []
    elif len(chapters) > max_chapters:
        err("$.chapters", f"contains more than the limit of {max_chapters} chapters")

    for index, chapter in enumerate(chapters):
        prefix = f"$.chapters[{index}]"
        if not isinstance(chapter, dict):
            err(prefix, "must be an object")
            continue
        chapter_id = chapter.get("id")
        if not isinstance(chapter_id, str) or not chapter_id.strip():
            err(prefix + ".id", "is required and must be a non-empty string")
        elif chapter_id in chapter_ids:
            err(prefix + ".id", "must be unique within the book")
        else:
            chapter_ids.add(chapter_id)
        if not isinstance(chapter.get("title"), str):
            err(prefix + ".title", "is required and must be a string")
        if "content" in chapter and not isinstance(chapter["content"], str):
            err(prefix + ".content", "must be a string")
        blocks = chapter.get("blocks")
        if blocks is not None:
            if not isinstance(blocks, list):
                err(prefix + ".blocks", "must be an array")
            else:
                for block_index, block in enumerate(blocks):
                    _validate_block(block, f"{prefix}.blocks[{block_index}]", err)

    resources = book.get("resources", [])
    resource_ids: set[str] = set()
    if not isinstance(resources, list):
        err("$.resources", "must be an array when present")
        resources = []
    elif len(resources) > max_resources:
        err("$.resources", f"contains more than the limit of {max_resources} resources")

    resource_types: dict[str, str] = {}
    for index, resource in enumerate(resources):
        prefix = f"$.resources[{index}]"
        if not isinstance(resource, dict):
            err(prefix, "must be an object")
            continue
        resource_id = resource.get("id")
        if not isinstance(resource_id, str) or not resource_id.strip():
            err(prefix + ".id", "is required and must be a non-empty string")
        elif resource_id in resource_ids:
            err(prefix + ".id", "must be unique within the book")
        else:
            resource_ids.add(resource_id)

        kind = resource.get("type")
        if kind not in ("image", "audio"):
            err(prefix + ".type", 'must be "image" or "audio"')
        elif isinstance(resource_id, str):
            resource_types[resource_id] = kind

        media_type = resource.get("mediaType")
        if not isinstance(media_type, str) or not _MEDIA_TYPE_RE.fullmatch(media_type):
            err(prefix + ".mediaType", "must be a syntactically valid media type")
        elif kind in ("image", "audio") and not media_type.lower().startswith(kind + "/"):
            err(prefix + ".mediaType", f"must start with {kind}/ for a {kind} resource")

        data = resource.get("data")
        path = resource.get("path")
        if data is not None and path is not None:
            err(prefix, "use either data or path, not both")
        if data is not None:
            if not isinstance(data, str):
                err(prefix + ".data", "must be a base64 string")
            else:
                try:
                    decoded = base64.b64decode(data, validate=True)
                    if len(decoded) > max_resource_bytes:
                        err(prefix + ".data", f"decoded resource exceeds {max_resource_bytes} bytes")
                except (binascii.Error, ValueError):
                    err(prefix + ".data", "must contain valid base64 data")
        if path is not None:
            if not isinstance(path, str) or not path:
                err(prefix + ".path", "must be a non-empty relative path")
            elif not _is_safe_relative_path(path):
                err(prefix + ".path", "must be a safe relative path without traversal")

    for index, chapter in enumerate(chapters):
        if not isinstance(chapter, dict) or not isinstance(chapter.get("blocks"), list):
            continue
        for block_index, block in enumerate(chapter["blocks"]):
            if not isinstance(block, dict) or block.get("type") not in ("image", "audio"):
                continue
            ref = block.get("resource")
            if ref is None:
                ref = block.get("resourceId")
            if not isinstance(ref, str):
                err(f"$.chapters[{index}].blocks[{block_index}].resource", "must identify a resource")
            elif ref not in resource_ids:
                err(f"$.chapters[{index}].blocks[{block_index}].resource", f"unknown resource id {ref!r}")
            elif resource_types.get(ref) != block.get("type"):
                err(f"$.chapters[{index}].blocks[{block_index}].resource", "resource type does not match block type")

    if "navigation" in book and not isinstance(book["navigation"], list):
        err("$.navigation", "must be an array")
    if "accessibility" in book and not isinstance(book["accessibility"], dict):
        err("$.accessibility", "must be an object")

    return errors


def _validate_block(block: Any, prefix: str, err: Any) -> None:
    if not isinstance(block, dict):
        err(prefix, "must be an object")
        return
    kind = block.get("type")
    if kind not in _BLOCK_TYPES:
        err(prefix + ".type", "must be one of: " + ", ".join(sorted(_BLOCK_TYPES)))
        return

    if kind in ("paragraph", "quote"):
        if not isinstance(block.get("text"), str):
            err(prefix + ".text", "must be a string")
    elif kind == "heading":
        if not isinstance(block.get("text"), str):
            err(prefix + ".text", "must be a string")
        level = block.get("level")
        if not isinstance(level, int) or isinstance(level, bool) or not 1 <= level <= 6:
            err(prefix + ".level", "must be an integer from 1 to 6")
    elif kind in ("image", "audio"):
        ref = block.get("resource", block.get("resourceId"))
        if not isinstance(ref, str) or not ref:
            err(prefix + ".resource", "must be a non-empty resource id")
        if kind == "image" and "alt" in block and not isinstance(block["alt"], str):
            err(prefix + ".alt", "must be a string")
        for key in ("caption", "transcript"):
            if key in block and not isinstance(block[key], str):
                err(prefix + "." + key, "must be a string")
    elif kind == "list":
        if not isinstance(block.get("ordered"), bool):
            err(prefix + ".ordered", "must be a boolean")
        items = block.get("items")
        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            err(prefix + ".items", "must be an array of strings")
    if kind == "quote" and "attribution" in block and not isinstance(block["attribution"], str):
        err(prefix + ".attribution", "must be a string")


def _is_safe_relative_path(value: str) -> bool:
    if value in (".", "..") or value.startswith(("/", "\\")) or "\\" in value or "://" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    parsed = PurePosixPath(value)
    return not parsed.is_absolute() and all(part not in ("", ".", "..") for part in parsed.parts)


def loads(
    text: str | bytes,
    *,
    validate: bool = True,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> dict[str, Any]:
    """Parse a JSON string or UTF-8 byte sequence into a ZBOOK dictionary."""
    raw = text.encode("utf-8") if isinstance(text, str) else text
    if not isinstance(raw, bytes):
        raise TypeError("text must be str or bytes")
    if len(raw) > max_file_bytes:
        raise ZbookParseError(f"file exceeds the {max_file_bytes}-byte limit")
    try:
        book = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ZbookParseError(f"could not parse UTF-8 JSON: {exc}") from exc
    if validate:
        errors = validate_book(book)
        if errors:
            raise ZbookValidationError(errors)
    if not isinstance(book, dict):
        raise ZbookValidationError(["$: document must be a JSON object"])
    return book


def load(
    path: str | Path,
    *,
    validate: bool = True,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> dict[str, Any]:
    """Read a local .zbook JSON file. No resource paths or URLs are fetched."""
    file_path = Path(path)
    size = file_path.stat().st_size
    if size > max_file_bytes:
        raise ZbookParseError(f"file exceeds the {max_file_bytes}-byte limit")
    return loads(file_path.read_bytes(), validate=validate, max_file_bytes=max_file_bytes)


def dumps(
    book: dict[str, Any],
    *,
    indent: int | None = 2,
    validate: bool = True,
    ensure_ascii: bool = False,
) -> str:
    """Serialize a ZBOOK document as UTF-8-compatible JSON text."""
    if validate:
        errors = validate_book(book)
        if errors:
            raise ZbookValidationError(errors)
    try:
        return json.dumps(book, ensure_ascii=ensure_ascii, indent=indent, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise ZbookError(f"document cannot be serialized as JSON: {exc}") from exc


def dump(
    book: dict[str, Any],
    path: str | Path,
    *,
    indent: int | None = 2,
    validate: bool = True,
) -> Path:
    """Write a ZBOOK JSON document to a local file."""
    destination = Path(path)
    if destination.suffix.lower() != ".zbook":
        raise ValueError("ZBOOK files should use the .zbook extension")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dumps(book, indent=indent, validate=validate), encoding="utf-8")
    return destination


def new_book(
    title: str,
    *,
    author: str | list[str] | None = None,
    language: str = "en",
    description: str | None = None,
) -> dict[str, Any]:
    """Create a minimal valid ZBOOK 1.0 document."""
    metadata: dict[str, Any] = {"title": title, "language": language}
    if author is not None:
        metadata["author"] = author
    if description is not None:
        metadata["description"] = description
    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "metadata": metadata,
        "chapters": [],
    }


__all__ = [
    "MEDIA_TYPE",
    "FORMAT_NAME",
    "FORMAT_VERSION",
    "ZbookError",
    "ZbookParseError",
    "ZbookValidationError",
    "validate_book",
    "loads",
    "load",
    "dumps",
    "dump",
    "new_book",
]
