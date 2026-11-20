# ZBOOK Format Specification — Draft 0.1

**Format name:** ZBOOK  
**Filename extension:** `.zbook`  
**Registered media type:** `application/prs.zbook`  
**IANA media type status:** Registered  
**Specification status:** Community design draft; this document is not an approved IANA standard  
**Creator listed by this project:** Surya Prakash V  
**Version covered by this draft:** ZBOOK 1.0

## 1. Purpose

ZBOOK is an open, cross-platform digital-book format. A ZBOOK document can contain book metadata, a sequence of chapters, formatted text, images, audio, and references to other resources. A compatible ZBOOK reader presents the content as a readable book.

ZBOOK is intended to complement—not claim to replace—PDF and EPUB. PDF is useful for fixed page layouts; EPUB is an established reflowable ebook format. ZBOOK should demonstrate a clear interoperability benefit before claiming to replace either.

## 2. Core design principles

- **Portable:** UTF-8 JSON and documented resource rules.
- **Readable:** chapters can be rendered on phones, tablets, computers, and the web.
- **Accessible:** semantic headings, alternative text, language metadata, and reading order.
- **Extensible:** unknown optional fields are ignored; required core fields remain stable.
- **Safe by default:** no scripts, macros, executable payloads, or automatic external resource loading.
- **Versioned:** every document declares its format and version.

## 3. File representation

For ZBOOK 1.0, a `.zbook` file is a UTF-8 encoded JSON text document conforming to RFC 8259. It is not a ZIP archive in this draft. Binary media is represented as a resource object using either a relative resource path in a future package profile or a `data` field containing base64. Readers must support the JSON text itself; they may impose reasonable size limits.

Recommended media type encoding consideration: `8bit` for UTF-8 JSON text. Do not describe the JSON-only representation as `binary`. If a future ZIP-based package is introduced, it must have a separately specified package profile and matching media-type/encoding review.

## 4. Required top-level members

A ZBOOK 1.0 document MUST contain:

- `format`: exactly `"ZBOOK"`.
- `version`: a version string, initially `"1.0"`.
- `metadata`: an object containing at least `title`.
- `chapters`: an array; it may be empty for a book template.

Recommended members:

- `ownership`: creator and attribution metadata.
- `resources`: media resources referenced by chapters.
- `navigation`: optional table-of-contents structure.
- `accessibility`: optional accessibility metadata.

## 5. Metadata

`metadata` SHOULD contain:
- `title` (string, required)
- `author` (string or array of strings)
- `language` (BCP 47 language tag, e.g. `en` or `ta`)
- `description` (string)
- `publisher` (string)
- `published` (date string, preferably YYYY-MM-DD)
- `identifier` (stable identifier, if available)
- `rights` (copyright/licence statement)

## 6. Ownership and attribution

The optional `ownership` object MAY contain:
- `creator`: person or organization that designed the ZBOOK format.
- `format_name`: `"ZBOOK"`.
- `specification_version`: version of this specification.
- `website`: public project/specification URL, when one exists.

The example project records `Surya Prakash V` as the creator named by the project author. The IANA media type registry also lists Surya Prakash V as the registrant for `application/prs.zbook`. These are attribution and registration-record details; they are not cryptographic proof, a legal ownership determination, or a guarantee that every ZBOOK file was authored by that person. A book's `metadata.author` identifies the book author and is distinct from the format creator.

Readers SHOULD show format creator information only when the document's `ownership` object is present and valid, or when the reader is displaying its own clearly labelled built-in format information. Readers MUST NOT treat an arbitrary file's `ownership` field as authenticated identity.

## 7. Chapters and content blocks

Each chapter SHOULD contain:
- `id`: unique chapter identifier within the book.
- `title`: chapter title.
- `blocks`: ordered array of content blocks.

Supported block types in version 1.0:
- `paragraph`: plain text in `text`.
- `heading`: text plus heading `level` from 1 to 6.
- `image`: resource `id`, descriptive `alt`, optional `caption`.
- `audio`: resource `id`, optional `caption` and `transcript`.
- `quote`: text and optional attribution.
- `list`: `ordered` boolean and an array of text items.

For the first prototype, `markdown` may be used as a chapter's `content` string instead of `blocks`. Readers must render Markdown safely: disable raw HTML, scripts, event handlers, and unsafe URL schemes. A later specification version can standardize rich text blocks as the preferred representation.

## 8. Images and audio

A `resources` entry SHOULD include:
- `id`: unique identifier.
- `type`: `image` or `audio`.
- `mediaType`: valid media type such as `image/png` or `audio/ogg`.
- `data`: base64-encoded bytes for self-contained single-file books, OR
- `path`: relative path under a separately defined package profile.

For this JSON-only draft, use `data` for embedded binary resources. Readers MUST validate base64, enforce size limits, check declared media types against actual content where practical, and never execute resource data. Do not fetch remote URLs automatically. External links, if supported, should require user action.

## 9. Navigation and reading order

The `chapters` array defines the default reading order. A `navigation` array MAY provide labels and chapter IDs for a table of contents. Readers SHOULD allow moving between chapters and preserving the declared order.

## 10. Accessibility

Authors SHOULD provide:
- language metadata;
- meaningful heading structure;
- alternative text for informative images;
- captions and transcripts for audio;
- logical reading order;
- sufficient text contrast and keyboard navigation in reader software.

## 11. Versioning and compatibility

The `version` member identifies the ZBOOK data format version. A reader that does not support the major version MUST show a clear unsupported-version message rather than silently misrendering the book. For unknown optional properties, readers SHOULD ignore them and preserve them when re-saving if feasible. A future incompatible format change requires a new major version and migration guidance.

## 12. Security considerations

ZBOOK files are untrusted input. Readers MUST:
- parse JSON with a standards-conforming parser;
- reject malformed JSON and enforce file-size, nesting-depth, chapter-count, and resource-size limits;
- render Markdown or rich text with raw HTML and executable content disabled;
- reject or neutralize unsafe URL schemes such as `javascript:`;
- never execute scripts, macros, or embedded programs;
- avoid automatic network requests for remote resources;
- validate resource references and prevent path traversal if a package profile is later defined;
- avoid trusting creator, author, publisher, or ownership strings as verified identity;
- keep software dependencies updated.

The format itself does not provide encryption, digital signatures, access control, or integrity protection. Applications needing authenticity or confidentiality should define an interoperable signature/encryption profile separately and use secure transport such as TLS when transferring files.

## 13. Interoperability considerations

A conforming ZBOOK 1.0 file is UTF-8 JSON. Implementations should follow RFC 8259 and this specification, support the required members, preserve chapter order, and safely handle unknown optional members. Markdown support must specify a common safe subset; differences between Markdown engines may otherwise produce different output. This draft does not guarantee identical rendering on every platform.

## 14. File extension and media type

- Extension: `.zbook`
- Registered media type: `application/prs.zbook`
- Required parameters: none
- Optional parameters: none
- Fragment identifiers: none defined by this draft
- Magic number: none; the file is identified by its media type/extension and JSON structure, not a unique byte signature.

The media type `application/prs.zbook` is registered in the IANA Media Types Registry. See the [IANA Media Types Registry](https://www.iana.org/assignments/media-types) and search for `application/prs.zbook`.

IANA registration records the media type and its registrant. It does not mean that IANA has approved this specification as a standard, reviewed or certified ZBOOK reader software, or granted trademark or copyright rights. The ZBOOK format specification remains a community design draft.

## 15. Conformance

A ZBOOK 1.0 reader conforms to this draft if it:
1. accepts UTF-8 JSON;
2. verifies `format`, `version`, `metadata`, and `chapters`;
3. presents chapters in array order;
4. handles unknown optional members without crashing;
5. applies the security requirements in Section 12.

A ZBOOK 1.0 authoring tool conforms if it produces documents meeting the required structure and does not emit unsafe executable content.

## 16. Example

See `examples/my-first-book.zbook` and `schema/zbook-1.0.schema.json` in this project.

## 17. Status and open design decisions

The `application/prs.zbook` media type is registered with IANA. This specification remains an early community design draft, not a final standard. Future work should decide:
- whether Markdown-only chapters or structured content blocks are normative;
- whether embedded base64 media is acceptable for large books;
- whether a future ZIP package profile is needed;
- the exact supported Markdown subset;
- licensing and governance for the specification and reference reader.

## References

- RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format.
- RFC 6838: Media Type Specifications and Registration Procedures.
- BCP 47: Tags for Identifying Languages.
