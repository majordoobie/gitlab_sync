import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dst-folder", required=True, type=Path, help="Path where the downloads will be placed")
    return parser
