"""Convert a horizontally-typeset (CJK) EPUB into vertical right-to-left layout.

The work mirrors the manual Sigil process:

1. Inject ``writing-mode: vertical-rl`` rules into the book's stylesheets
   (or into each content document when the book has no stylesheet).
2. Add ``page-progression-direction="rtl"`` to the OPF ``<spine>`` so readers
   page from right to left.
3. (Optional) swap straight CJK quotation marks for the corner-bracket forms
   that render correctly in vertical text.

No external dependencies; only the Python standard library is used.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field

# --- the CSS block injected to turn the book vertical -----------------------
VERTICAL_CSS = """
/* --- injected by epub-vertical : horizontal -> vertical-rl --- */
html {
    writing-mode: vertical-rl;
    -webkit-writing-mode: vertical-rl;
    -epub-writing-mode: vertical-rl;
    -epub-word-break: normal;
    word-break: normal;
    -epub-line-break: strict;
    line-break: strict;
}
"""

# straight / smart quotes -> corner brackets used in vertical CJK text
PUNCTUATION_MAP = {
    "\u201c": "\u300c",  # “  ->  「
    "\u201d": "\u300d",  # ”  ->  」
    "\u2018": "\u300e",  # ‘  ->  『
    "\u2019": "\u300f",  # ’  ->  』
}

# XML namespaces
NS_CONTAINER = "urn:oasis:names:tc:opendocument:xmlns:container"
NS_OPF = "http://www.idpf.org/2007/opf"

# A marker so a book is never processed twice.
MARKER = "epub-vertical : horizontal -> vertical-rl"


class ConversionError(Exception):
    """Raised when the input is not a usable EPUB."""


@dataclass
class Report:
    """Summary of what the conversion touched."""

    stylesheets_edited: list[str] = field(default_factory=list)
    documents_styled: list[str] = field(default_factory=list)
    spine_updated: bool = False
    punctuation_fixed: int = 0
    already_vertical: bool = False


# --- small helpers ----------------------------------------------------------
def _find_opf(root: str) -> str:
    """Return the absolute path to the OPF file via META-INF/container.xml."""
    container = os.path.join(root, "META-INF", "container.xml")
    if not os.path.isfile(container):
        raise ConversionError("META-INF/container.xml not found - not a valid EPUB.")
    from xml.etree import ElementTree as ET

    tree = ET.parse(container)
    rootfile = tree.find(f".//{{{NS_CONTAINER}}}rootfile")
    if rootfile is None or not rootfile.get("full-path"):
        raise ConversionError("No rootfile declared in container.xml.")
    opf = os.path.join(root, rootfile.get("full-path").replace("/", os.sep))
    if not os.path.isfile(opf):
        raise ConversionError(f"OPF file referenced but missing: {opf}")
    return opf


def _parse_manifest(opf_text: str):
    """Return {id: (href, media_type)} from the OPF manifest."""
    items = {}
    for m in re.finditer(r"<item\b[^>]*?/?>", opf_text, re.IGNORECASE):
        tag = m.group(0)
        iid = _attr(tag, "id")
        href = _attr(tag, "href")
        media = _attr(tag, "media-type")
        if iid and href:
            items[iid] = (href, media or "")
    return items


def _spine_order(opf_text: str) -> list[str]:
    """Return the list of manifest ids referenced by the spine, in order."""
    spine = re.search(r"<spine\b[^>]*>(.*?)</spine>", opf_text, re.IGNORECASE | re.DOTALL)
    if not spine:
        return []
    return re.findall(r'idref=["\']([^"\']+)["\']', spine.group(1), re.IGNORECASE)


def _attr(tag: str, name: str):
    m = re.search(rf'{name}\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
    return m.group(1) if m else None


def _add_rtl_to_spine(opf_text: str) -> tuple[str, bool]:
    """Add page-progression-direction="rtl" to the <spine> open tag."""
    m = re.search(r"<spine\b[^>]*>", opf_text, re.IGNORECASE)
    if not m:
        return opf_text, False
    tag = m.group(0)
    if re.search(r"page-progression-direction", tag, re.IGNORECASE):
        new_tag = re.sub(
            r'page-progression-direction\s*=\s*["\'][^"\']*["\']',
            'page-progression-direction="rtl"',
            tag,
            flags=re.IGNORECASE,
        )
    else:
        new_tag = tag[:-1].rstrip() + ' page-progression-direction="rtl">'
    if new_tag == tag:
        return opf_text, False
    return opf_text[: m.start()] + new_tag + opf_text[m.end():], True


_STYLE_BLOCK = "<style type=\"text/css\">\n" + VERTICAL_CSS + "\n</style>"


def _inject_style_into_doc(text: str) -> str:
    """Insert a <style> block into a content document's <head>."""
    head_close = re.search(r"</head\s*>", text, re.IGNORECASE)
    if head_close:
        return text[: head_close.start()] + _STYLE_BLOCK + "\n" + text[head_close.start():]
    # no </head>; fall back to inserting after the opening <html ...> tag
    html_open = re.search(r"<html\b[^>]*>", text, re.IGNORECASE)
    if html_open:
        insert = "<head>" + _STYLE_BLOCK + "</head>"
        return text[: html_open.end()] + insert + text[html_open.end():]
    return _STYLE_BLOCK + text


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="surrogatepass") as fh:
        return fh.read()


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", errors="surrogatepass") as fh:
        fh.write(text)


def _rezip(root: str, output: str) -> None:
    """Repackage a directory tree as a valid EPUB (mimetype first, stored)."""
    if os.path.exists(output):
        os.remove(output)
    with zipfile.ZipFile(output, "w") as zf:
        # mimetype MUST be the first entry and stored uncompressed
        mimetype = os.path.join(root, "mimetype")
        if os.path.isfile(mimetype):
            zf.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                full = os.path.join(dirpath, name)
                arc = os.path.relpath(full, root).replace(os.sep, "/")
                if arc == "mimetype":
                    continue
                zf.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)


# --- public API -------------------------------------------------------------
def convert_epub(
    input_path: str,
    output_path: str,
    *,
    rtl: bool = True,
    fix_punctuation: bool = False,
    force: bool = False,
) -> Report:
    """Convert ``input_path`` to vertical layout, writing ``output_path``.

    Returns a :class:`Report` describing what changed.
    """
    if not zipfile.is_zipfile(input_path):
        raise ConversionError(f"{input_path} is not a ZIP/EPUB file.")

    report = Report()
    tmp = tempfile.mkdtemp(prefix="epub-vertical-")
    try:
        with zipfile.ZipFile(input_path) as zf:
            zf.extractall(tmp)

        opf_path = _find_opf(tmp)
        opf_dir = os.path.dirname(opf_path)
        opf_text = _read(opf_path)

        if MARKER in opf_text and not force:
            report.already_vertical = True
            # still produce an output copy so the caller always gets a file
            shutil.copyfile(input_path, output_path)
            return report

        manifest = _parse_manifest(opf_text)

        css_items = [
            href for href, media in manifest.values()
            if media == "text/css" or href.lower().endswith(".css")
        ]
        xhtml_ids = [
            iid for iid, (href, media) in manifest.items()
            if media in ("application/xhtml+xml", "text/html")
            or href.lower().endswith((".xhtml", ".html", ".htm"))
        ]

        # 1. inject the vertical CSS
        if css_items:
            for href in css_items:
                css_path = os.path.normpath(os.path.join(opf_dir, href.replace("/", os.sep)))
                if os.path.isfile(css_path):
                    css_text = _read(css_path)
                    if MARKER not in css_text:
                        _write(css_path, css_text.rstrip() + "\n" + VERTICAL_CSS)
                        report.stylesheets_edited.append(href)
            # safety net: any content doc that links no stylesheet gets a <style>
            for iid in xhtml_ids:
                href = manifest[iid][0]
                doc_path = os.path.normpath(os.path.join(opf_dir, href.replace("/", os.sep)))
                if not os.path.isfile(doc_path):
                    continue
                doc = _read(doc_path)
                if re.search(r"<link[^>]+stylesheet", doc, re.IGNORECASE):
                    continue
                if MARKER in doc:
                    continue
                _write(doc_path, _inject_style_into_doc(doc))
                report.documents_styled.append(href)
        else:
            # no stylesheets at all -> inject a <style> into every content doc
            for iid in xhtml_ids:
                href = manifest[iid][0]
                doc_path = os.path.normpath(os.path.join(opf_dir, href.replace("/", os.sep)))
                if not os.path.isfile(doc_path):
                    continue
                doc = _read(doc_path)
                if MARKER in doc:
                    continue
                _write(doc_path, _inject_style_into_doc(doc))
                report.documents_styled.append(href)

        # 2. page progression direction
        if rtl:
            opf_text, report.spine_updated = _add_rtl_to_spine(opf_text)

        # leave a marker in the OPF so we don't double-convert
        if MARKER not in opf_text:
            opf_text = opf_text.replace("</package>", f"<!-- {MARKER} -->\n</package>", 1)
        _write(opf_path, opf_text)

        # 3. punctuation (optional)
        if fix_punctuation:
            for iid in xhtml_ids:
                href = manifest[iid][0]
                doc_path = os.path.normpath(os.path.join(opf_dir, href.replace("/", os.sep)))
                if not os.path.isfile(doc_path):
                    continue
                doc = _read(doc_path)
                count = 0
                for src, dst in PUNCTUATION_MAP.items():
                    count += doc.count(src)
                    doc = doc.replace(src, dst)
                if count:
                    _write(doc_path, doc)
                    report.punctuation_fixed += count

        _rezip(tmp, output_path)
        return report
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
