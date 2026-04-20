import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dst-folder", required=True, type=Path, help="Path where the downloads will be placed")
    parser.add_argument(
        "--tree-sitter",
        action="store_true",
        help="Include ALL tree-sitter parser downloads (~300; skipped by default)",
    )
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Download a curated subset of tree-sitter parsers (~30). Overridden by --tree-sitter.",
    )
    return parser
