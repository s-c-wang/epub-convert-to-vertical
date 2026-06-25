"""epub-vertical: turn horizontal CJK EPUBs into vertical right-to-left books."""

from .converter import ConversionError, Report, convert_epub

__all__ = ["convert_epub", "Report", "ConversionError"]
__version__ = "0.1.0"
