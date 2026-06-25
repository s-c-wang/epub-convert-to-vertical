"""Command-line interface for epub-vertical."""

from __future__ import annotations

import argparse
import os
import sys

from .converter import ConversionError, convert_epub


def _default_output(input_path: str) -> str:
    base, ext = os.path.splitext(input_path)
    return f"{base}.vertical{ext or '.epub'}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epub-vertical",
        description="Convert a horizontal (CJK) EPUB into vertical right-to-left layout.",
    )
    p.add_argument("inputs", nargs="+", help="EPUB file(s) to convert.")
    p.add_argument(
        "-o", "--output",
        help="Output path (single input only). Default: <name>.vertical.epub",
    )
    p.add_argument(
        "--ltr", action="store_true",
        help="Keep left-to-right page progression (skip the spine RTL change).",
    )
    p.add_argument(
        "--fix-punctuation", action="store_true",
        help="Replace “ ” ‘ ’ with the corner brackets 「 」 『 』 used in vertical text.",
    )
    p.add_argument(
        "--force", action="store_true",
        help="Convert even if the book looks like it was already converted.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.output and len(args.inputs) > 1:
        print("error: --output cannot be used with multiple inputs.", file=sys.stderr)
        return 2

    rc = 0
    for input_path in args.inputs:
        if not os.path.isfile(input_path):
            print(f"error: file not found: {input_path}", file=sys.stderr)
            rc = 1
            continue
        output_path = args.output or _default_output(input_path)
        try:
            report = convert_epub(
                input_path,
                output_path,
                rtl=not args.ltr,
                fix_punctuation=args.fix_punctuation,
                force=args.force,
            )
        except ConversionError as exc:
            print(f"error: {input_path}: {exc}", file=sys.stderr)
            rc = 1
            continue

        if report.already_vertical:
            print(f"{input_path}: already vertical (use --force to redo) -> {output_path}")
            continue

        bits = []
        if report.stylesheets_edited:
            bits.append(f"{len(report.stylesheets_edited)} stylesheet(s)")
        if report.documents_styled:
            bits.append(f"{len(report.documents_styled)} document(s)")
        if report.spine_updated:
            bits.append("spine=rtl")
        if report.punctuation_fixed:
            bits.append(f"{report.punctuation_fixed} punctuation marks")
        detail = ", ".join(bits) if bits else "no changes"
        print(f"{input_path} -> {output_path}  ({detail})")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
