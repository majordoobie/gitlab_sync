import shutil
from pathlib import Path
from sys import argv

from assets import get_lsps, get_nvim_tree_sitter_langs, get_nvim_plugins


def _copy_nvim_config(target_dir: Path) -> None:
    """Copy ~/.config/nvim to target directory"""
    nvim_config_source = Path.home() / ".config" / "nvim"
    nvim_config_dest = target_dir / "nvim_config"
    
    if nvim_config_source.exists():
        if nvim_config_dest.exists():
            shutil.rmtree(nvim_config_dest)
        shutil.copytree(nvim_config_source, nvim_config_dest)
        print(f"Copied nvim config from {nvim_config_source} to {nvim_config_dest}")
    else:
        print(f"Warning: {nvim_config_source} does not exist, skipping nvim config copy")


def main(target_dir: Path) -> None:
    nvim_plugins = target_dir / "nvim_plugins"
    nvim_plugins.mkdir(exist_ok=True)
    get_nvim_plugins(nvim_plugins)

    nvim_tree_sitter = target_dir / "nvim_tree_sitter"
    nvim_tree_sitter.mkdir(exist_ok=True)
    get_nvim_tree_sitter_langs(nvim_tree_sitter)

    lsps = target_dir / "lsps"
    lsps.mkdir(exist_ok=True)
    get_lsps(lsps)
    
    _copy_nvim_config(target_dir)


if __name__ == "__main__":
    if len(argv) != 2 or not Path(argv[1]).is_dir():
        exit(
            "Provide the path to the target directory where the repos will be cloned to"
        )
    main(Path(argv[1]))
