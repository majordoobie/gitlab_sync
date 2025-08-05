import json
import subprocess
from pathlib import Path

NPMS = [
    {"name": "pyright", "npm_loc": "pyright"},
    {"name": "vscode_extracted", "npm_loc": "vscode-langservers-extracted"},
    {"name": "yaml_ls", "npm_loc": "yaml-language-server"},
    {"name": "docker_comp_ls", "npm_loc": "@microsoft/compose-language-service"},
]

BINARIES = [
    {
        "name": "lazygit",
        "repo": "jesseduffield/lazygit",
        "filename_template": "lazygit_{version}_linux_x86_64.tar.gz",
    },
    {
        "name": "neovim",
        "repo": "neovim/neovim",
        "filename_template": "nvim-linux-x86_64.tar.gz",
    },
    {
        "name": "lua-language-server",
        "repo": "LuaLS/lua-language-server",
        "filename_template": "lua-language-server-{version}-linux-x64.tar.gz",
    },
    {
        "name": "starship",
        "repo": "starship/starship",
        "filename_template": "starship-x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "stylua",
        "repo": "JohnnyMorganz/StyLua",
        "filename_template": "stylua-linux-x86_64.zip",
    },
    {
        "name": "eza",
        "repo": "eza-community/eza",
        "filename_template": "eza_x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "asm-lsp",
        "repo": "bergercookie/asm-lsp",
        "filename_template": "asm-lsp-x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "taplo-toml-langserver",
        "repo": "tamasfe/taplo",
        "filename_template": "taplo-linux-x86_64.gz",
    },
]

def _get_npm_lsps(destination: Path) -> None:
    for npm_pkg in NPMS:
        try:
            subprocess.run(
                [
                    "npm",
                    "pack",
                    npm_pkg.get("npm_loc", ""),
                    "--pack-destination",
                    destination.as_posix(),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"Downloaded npm package: {npm_pkg['name']} ({npm_pkg.get('npm_loc', '')})")
        except subprocess.CalledProcessError as error:
            print(f"Command failed for {npm_pkg['name']}: {error.cmd}")
            print(f"Return code: {error.returncode}")
            print(f"Stdout: {error.stdout}")
            print(f"Stderr: {error.stderr}")


def _get_latest_binary(binary_info: dict[str, str], destination: Path) -> None:
    """Download the latest binary release for a given repo"""
    try:
        # Get latest release info from GitHub API
        result = subprocess.run(
            [
                "curl",
                "-s",
                f"https://api.github.com/repos/{binary_info['repo']}/releases/latest",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        release_data = json.loads(result.stdout)
        latest_version = release_data["tag_name"]

        # Construct filename based on template
        if "{version}" in binary_info["filename_template"]:
            # Remove 'v' prefix from version for filename
            version_no_v = (
                latest_version[1:] if latest_version.startswith("v") else latest_version
            )
            filename = binary_info["filename_template"].format(version=version_no_v)
        else:
            filename = binary_info["filename_template"]

        # Construct download URL
        download_url = f"https://github.com/{binary_info['repo']}/releases/download/{latest_version}/{filename}"

        # Download the file
        subprocess.run(
            ["curl", "-L", "-o", (destination / filename).as_posix(), download_url],
            capture_output=True,
            text=True,
            check=True,
        )

        print(f"Downloaded {binary_info['name']} {latest_version}: {filename}")

    except subprocess.CalledProcessError as error:
        print(f"Command failed for {binary_info['name']}: {error.cmd}")
        print(f"Return code: {error.returncode}")
        print(f"Stdout: {error.stdout}")
        print(f"Stderr: {error.stderr}")
    except json.JSONDecodeError as error:
        print(f"Failed to parse GitHub API response for {binary_info['name']}: {error}")


def _get_binaries(destination: Path) -> None:
    """Download all binary releases"""
    for binary in BINARIES:
        _get_latest_binary(binary, destination)


def get_lsps(destination: Path) -> None:
    _get_npm_lsps(destination)
    _get_binaries(destination)
