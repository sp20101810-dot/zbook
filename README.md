# ZBOOK

**ZBOOK** is a proposed JSON-based digital-book format using the `.zbook` file extension.

- **Format creator named by this project:** Surya Prakash V
- **Proposed media type:** `application/prs.zbook`
- **Specification:** Draft 0.1
- **Data format version in the draft:** 1.0

ZBOOK is intended to represent book metadata and ordered chapters, with optional embedded image and audio resources. This repository contains an early browser-based prototype and a draft specification.

> **Status notice:** ZBOOK is a project proposal. The specification is a draft, the software is an early prototype, and the proposed media type must not be described as IANA-registered unless and until it appears in the official IANA registry. Creator/owner fields are project attribution metadata, not cryptographic proof or a legal determination of ownership.

## Repository contents

```text
.
├── README.md
├── SPECIFICATION-DRAFT-0.1.md
├── schema/
│   └── zbook-1.0.schema.json
├── examples/
│   └── my-first-book.zbook
└── studio/
    ├── README.txt
    ├── index.html
    └── sample-book.zbook
```

## Try ZBOOK Studio

1. Download or clone this repository.
2. Open `studio/index.html` in a modern browser.
3. Use the tabs for **Book Creator**, **Reader**, **PDF Converter**, and **Validator**.

The prototype processes selected files locally in the browser. The PDF converter loads Mozilla PDF.js from a public CDN and therefore needs an internet connection. It extracts selectable PDF text; it does not perform OCR on scanned PDFs or preserve the original PDF page layout. The validator performs basic checks and is not formal certification.

## Example ZBOOK file

Open `examples/my-first-book.zbook` in a text editor to inspect the JSON structure, or load it in ZBOOK Studio's Reader.

## Specification and compatibility

Read [SPECIFICATION-DRAFT-0.1.md](SPECIFICATION-DRAFT-0.1.md) for the current draft rules and [schema/zbook-1.0.schema.json](schema/zbook-1.0.schema.json) for the JSON Schema draft.

This is an evolving proposal. Implementations should identify the exact draft/version they support and handle untrusted input safely.

## Contact

The registration contact supplied by the project author is `sp20101810@gmail.com`.


## License

ZBOOK is currently an open specification proposal (Draft 0.1).

No license has been assigned yet. Licensing terms will be announced in a future version.

For permissions regarding reuse or distribution, please contact the project author.
