import shutil
from pathlib import Path

from .arg_parse import build_parser
from .assets import get_lsps, get_nvim_plugins, get_nvim_tree_sitter_langs


def _copy_nvim_config(target_dir: Path) -> None:
    """Copy ~/.config/nvim to target directory"""
    nvim_config_source = Path.home() / ".config" / "nvim"
    nvim_config_dest = target_dir / "nvim_config"

    if nvim_config_source.exists():
        print(f"  📋 Copying nvim config...")
        if nvim_config_dest.exists():
            shutil.rmtree(nvim_config_dest)
        shutil.copytree(nvim_config_source, nvim_config_dest)
        print(f"  ✓ Copied nvim config to {nvim_config_dest}")
    else:
        print(f"  ⚠️  Warning: {nvim_config_source} does not exist, skipping")


def main() -> None:
    args = build_parser().parse_args()

    target_dir: Path = args.dst_folder
    if not target_dir.is_dir():
        exit("Desintation file must be a folder")

    # Print header
    print("=" * 70)
    print("🚀 Git Sync - Development Tools Downloader")
    print("=" * 70)
    print(f"📁 Target directory: {target_dir.absolute()}")
    print()

    nvim_plugins = target_dir / "nvim_plugins"
    nvim_tree_sitter = target_dir / "nvim_tree_sitter"
    binaries = target_dir / "bin"

    nvim_plugins.mkdir(exist_ok=True)
    nvim_tree_sitter.mkdir(exist_ok=True)
    binaries.mkdir(exist_ok=True)

    # Run all downloads
    get_nvim_plugins(nvim_plugins)
    get_nvim_tree_sitter_langs(nvim_tree_sitter)
    get_lsps(binaries)

    # Copy nvim config
    print("\n📋 Copying Neovim Configuration...")
    print("=" * 60)
    _copy_nvim_config(target_dir)

    # Print summary
    print("\n" + "=" * 70)
    print("✅ Sync Complete!")
    print("=" * 70)
    print(f"📂 All files saved to: {target_dir.absolute()}")
    print()


if __name__ == "__main__":
    main()
