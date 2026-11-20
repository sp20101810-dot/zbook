# ZBOOK

**ZBOOK** is a JSON-based digital-book format using the `.zbook` file extension.

- **Format creator named by this project:** Surya Prakash V
- **Registered media type:** `application/prs.zbook`
- **IANA registration status:** Registered
- **Specification:** Community design draft 0.1
- **Data format version described by the draft:** 1.0

ZBOOK is designed to represent book metadata and ordered chapters, with optional embedded image and audio resources. This repository contains the draft specification, JSON Schema, example books, and an early browser-based prototype.

## IANA media type registration

The media type `application/prs.zbook` is registered in the IANA Media Types Registry.

- **Media type:** `application/prs.zbook`
- **File extension:** `.zbook`
- **Registrant listed in the registry:** Surya Prakash V
- **Registry:** [IANA Media Types Registry](https://www.iana.org/assignments/media-types)

The registration identifies the media type for ZBOOK files. It does not mean that IANA has approved or standardized the ZBOOK format specification, certified reader software, or granted trademark or copyright rights.

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

The specification remains a community design draft and may evolve. Implementations should identify the exact draft/version they support and handle untrusted input safely.

## Contact

The registration contact supplied by the project author is `sp20101810@gmail.com`.

## License

ZBOOK is currently an open specification proposal (Draft 0.1).

No license has been assigned yet. Licensing terms will be announced in a future version.

For permissions regarding reuse or distribution, please contact the project author.
