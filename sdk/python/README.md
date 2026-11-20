# ZBOOK Python SDK (preview)

A small, dependency-free Python library for reading, validating, creating, and writing **ZBOOK 1.0** JSON documents.

- File extension: .zbook
- Media type: application/prs.zbook
- Specification: [ZBOOK Format Specification — Draft 0.1](../../SPECIFICATION-DRAFT-0.1.md)
- Supported data version: 1.0

> This is an early reference SDK, not a certified implementation. The ZBOOK specification is still a community design draft.

## Requirements

- Python 3.10 or newer
- No third-party packages required

## Quick start

From the repository root:

    from sdk.python import zbook

    book = zbook.new_book(
        "My first programmatic book",
        author="A. Reader",
        language="en",
    )
    book["chapters"].append({
        "id": "chapter-1",
        "title": "Hello",
        "content": "# Hello ZBOOK\n\nCreated with the Python SDK.",
    })

    zbook.dump(book, "hello.zbook")

    loaded = zbook.load("hello.zbook")
    print(loaded["metadata"]["title"])

You can also import the module directly when the sdk/python directory is on PYTHONPATH:

    import zbook

    book = zbook.load("hello.zbook")

## API

| Function | Purpose |
|---|---|
| new_book(title, ...) | Create a minimal ZBOOK 1.0 document |
| load(path) | Read and validate a local .zbook file |
| loads(text) | Parse JSON text or UTF-8 bytes |
| dump(book, path) | Validate and write a .zbook file |
| dumps(book) | Validate and serialize to JSON text |
| validate_book(book) | Return a list of validation errors |

load, loads, dump, and dumps validate by default. Pass validate=False only when you deliberately need to inspect a non-conforming document. validate_book returns an empty list when no supported validation errors are found.

## Safety behavior

- Reads only the selected local .zbook file.
- Does not fetch URLs or resource paths.
- Does not execute scripts, macros, or embedded programs.
- Checks JSON structure, chapter IDs, supported content-block shapes, resource IDs, media types, and embedded base64 data.
- Applies a default 50 MiB input-file limit and 20 MiB decoded limit per embedded resource.
- Checks relative resource paths for obvious traversal/absolute-path forms; it does not open those paths.
- Does not render Markdown. A reader application must render Markdown with raw HTML and unsafe URL schemes disabled.

## Supported structure

The SDK follows the repository's Draft 0.1 description of ZBOOK 1.0:

- Required top-level fields: format, version, metadata, chapters.
- metadata.title is required.
- Chapters use id and title; content may contain Markdown text.
- Structured blocks support paragraph, heading, image, audio, quote, and list.
- Optional resources may carry base64 data or a relative path.
- Unknown optional object properties are preserved.

For image/audio blocks, the SDK accepts resource (preferred) or resourceId as the referenced resource identifier. Resource data is not decoded into files or displayed by this library.

## Run tests

From the repository root:

    python -m unittest discover -s sdk/python/tests -v

## Status and feedback

This SDK is an initial implementation intended for experimentation and interoperability testing. Report issues in the [ZBOOK GitHub repository](https://github.com/sp20101810-dot/zbook/issues).
