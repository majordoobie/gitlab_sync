from pathlib import Path
from sys import argv

from assets import get_lsps, get_nvim_plugins


def main(target_dir: Path) -> None:
    nvim_plugins = target_dir / "nvim_plugins"
    nvim_plugins.mkdir(exist_ok=True)

    nvim_tree_sitter = target_dir / "nvim_tree_sitter"
    nvim_tree_sitter.mkdir(exist_ok=True)

    lsps = target_dir / "lsps"
    lsps.mkdir(exist_ok=True)

    get_lsps(lsps)


if __name__ == "__main__":
    if len(argv) != 2 or not Path(argv[1]).is_dir():
        exit(
            "Provide the path to the target directory where the repos will be cloned to"
        )
    main(Path(argv[1]))
