import gzip
import json
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from concurrent import futures
from pathlib import Path

NPMS = [
    {"name": "pyright", "npm_loc": "pyright"},
    {"name": "basedpyright", "npm_loc": "basedpyright"},
    {"name": "vscode_extracted", "npm_loc": "vscode-langservers-extracted"},
    {"name": "yaml_ls", "npm_loc": "yaml-language-server"},
    {"name": "docker_comp_ls", "npm_loc": "@microsoft/compose-language-service"},
    {"name": "ai-sdk-openai-compatible", "npm_loc": "@ai-sdk/openai-compatible"},
    {"name": "ai-sdk-openai", "npm_loc": "@ai-sdk/openai"},
    {"name": "opencode-plugin", "npm_loc": "@opencode-ai/plugin"},
    {"name": "prettierd", "npm_loc": "@fsouza/prettierd"},
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
        "name": "fzf",
        "repo": "junegunn/fzf",
        "filename_template": "fzf-{version}-linux_amd64.tar.gz",
    },
    {
        "name": "fd",
        "repo": "sharkdp/fd",
        "filename_template": "fd-v{version}-x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "rg",
        "repo": "BurntSushi/ripgrep",
        "filename_template": "ripgrep-{version}-x86_64-unknown-linux-musl.tar.gz",
    },
    {
        "name": "taplo",
        "repo": "tamasfe/taplo",
        "filename_template": "taplo-linux-x86_64.gz",
    },
    {
        "name": "Zen",
        "repo": "zen-browser/desktop",
        "filename_template": "zen.installer.exe",
    },
    {"name": "Wezterm", "repo": "wezterm/wezterm", "filename_template": "WezTerm-{version}-setup.exe"},
    {"name": "Obsidian", "repo": "obsidianmd/obsidian-releases", "filename_template": "Obsidian-{version}.exe"},
    {"name": "komorebi", "repo": "LGUG2Z/komorebi", "filename_template": "komorebi-{version}-x86_64.msi"},
    {
        "name": "blink.cmp",
        "repo": "Saghen/blink.cmp",
        "filename_template": "x86_64-unknown-linux-gnu.so",
    },
    {
        "name": "codediff.nvim-libvscode",
        "repo": "esmuellert/codediff.nvim",
        "filename_template": "libvscode_diff_linux_x64_{version}.so",
    },
    {
        "name": "codediff.nvim-libgomp",
        "repo": "esmuellert/codediff.nvim",
        "filename_template": "libgomp_linux_x64_{version}.so.1",
    },
    {
        "name": "ruff",
        "repo": "astral-sh/ruff",
        "filename_template": "ruff-x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "ty",
        "repo": "astral-sh/ty",
        "filename_template": "ty-x86_64-unknown-linux-gnu.tar.gz",
    },
    {
        "name": "opencode",
        "repo": "anomalyco/opencode",
        "filename_template": "opencode-linux-x64.tar.gz",
    },
    {
        "name": "tree-sitter",
        "repo": "tree-sitter/tree-sitter",
        "filename_template": "tree-sitter-linux-x64.gz",
    },
    {
        "name": "shfmt",
        "repo": "mvdan/sh",
        "filename_template": "shfmt_v{version}_linux_amd64",
    },
    {
        "name": "yamlfmt",
        "repo": "google/yamlfmt",
        "filename_template": "yamlfmt_{version}_Linux_x86_64.tar.gz",
    },
]


def _get_npm_lsps(destination: Path) -> None:
    """Download all npm packages with dependencies bundled for Linux x86_64"""
    print(f"\n📦 Downloading NPM Packages with Dependencies ({len(NPMS)} packages)...")
    print("=" * 60)

    # Collect all npm package locations
    npm_packages = [npm_pkg.get("npm_loc", "") for npm_pkg in NPMS]

    print(f"  🔄 Installing packages with dependencies for Linux x86_64...")
    print(f"  📋 Using Docker to ensure correct architecture...")

    try:
        # Create a temporary directory on host that will be mounted in container
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create package.json for the install
            package_json = {
                "name": "npm-packages-bundle",
                "version": "1.0.0",
                "dependencies": {}
            }

            # Add all packages as dependencies (without version, npm will get latest)
            for pkg in npm_packages:
                # Extract package name (handles @scope/name format)
                package_json["dependencies"][pkg] = "latest"

            package_json_path = temp_path / "package.json"
            with open(package_json_path, "w") as f:
                json.dump(package_json, f, indent=2)

            # Run npm install in a Linux x86_64 container
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--platform", "linux/amd64",
                    "-v", f"{temp_path.absolute()}:/workspace",
                    "-w", "/workspace",
                    "node:22-slim",
                    "npm", "install", "--omit=dev"
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"  ✓ Installed all packages with dependencies")

            # Create tarball of node_modules
            print(f"  📦 Bundling node_modules...")
            node_modules = temp_path / "node_modules"
            if node_modules.exists():
                bundle_path = destination / "npm-packages-bundle.tar.gz"
                with tarfile.open(bundle_path, "w:gz") as tar:
                    tar.add(node_modules, arcname="node_modules")
                print(f"  ✓ Created bundle: npm-packages-bundle.tar.gz")
                print(f"  📝 Extract on air-gapped system with: tar -xzf npm-packages-bundle.tar.gz")
            else:
                print(f"  ⚠️  Warning: node_modules directory not found")

    except subprocess.CalledProcessError as error:
        print(f"  ✗ Failed to install npm packages")
        print(f"    Error: {error.stderr}")
        print(f"  💡 Make sure Docker is installed and running")
    except FileNotFoundError:
        print(f"  ✗ Docker not found. Please install Docker to download npm packages.")
        print(f"  💡 Alternatively, run this tool on a Linux x86_64 machine")


def _get_latest_binary(binary_info: dict[str, str], destination: Path) -> None:
    """Download the latest binary release for a given repo"""
    print(f"  📥 Downloading binary: {binary_info['name']} from {binary_info['repo']}...")
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
        try:
            latest_version = release_data["tag_name"]
        except:
            exit(f"Could not get tag name for {binary_info} -- {release_data}")

        # Construct filename based on template
        if "{version}" in binary_info["filename_template"]:
            # Remove 'v' prefix from version for filename
            version_no_v = latest_version[1:] if latest_version.startswith("v") else latest_version
            filename = binary_info["filename_template"].format(version=version_no_v)
        else:
            filename = binary_info["filename_template"]

        # Construct download URL
        download_url = f"https://github.com/{binary_info['repo']}/releases/download/{latest_version}/{filename}"

        print(f"download url [{download_url}]")

        # Download the file
        download_path = destination / filename
        subprocess.run(
            ["curl", "-L", "-o", download_path.as_posix(), download_url],
            capture_output=True,
            text=True,
            check=True,
        )

        # Handle archives based on binary type
        binary_name = binary_info["name"]

        # Special extraction cases: extract and keep only the binary
        if binary_name in ["asm-lsp", "eza", "lazygit", "stylua", "starship", "opencode", "ruff", "ty", "fzf", "fd", "rg", "yamlfmt"] and (filename.endswith(".tar.gz") or filename.endswith(".zip")):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract to temp directory based on archive type
                if filename.endswith(".tar.gz"):
                    with tarfile.open(download_path, "r:gz") as tar:
                        tar.extractall(path=temp_path)
                elif filename.endswith(".zip"):
                    with zipfile.ZipFile(download_path, "r") as zip_file:
                        zip_file.extractall(temp_path)

                # Find and move the binary with version in name
                if binary_name == "lua-language-server":
                    # Find bin/lua-language-server in extracted files
                    binary_path = None
                    for extracted in temp_path.rglob("*"):
                        if extracted.is_file() and extracted.parts[-2:] == ("bin", "lua-language-server"):
                            binary_path = extracted
                            break

                    if binary_path and binary_path.exists():
                        final_path = destination / f"lua-language-server_{latest_version}"
                        shutil.move(str(binary_path), str(final_path))
                        print(f"  ✓ Downloaded and extracted: {binary_name} {latest_version}")
                    else:
                        print(f"  ⚠️  Warning: Could not find bin/lua-language-server in extracted archive")
                else:
                    # For asm-lsp, eza, lazygit, stylua, and starship, find the binary file
                    binary_path = None
                    for extracted in temp_path.rglob("*"):
                        if extracted.is_file() and extracted.name == binary_name:
                            binary_path = extracted
                            break

                    if binary_path and binary_path.exists():
                        final_path = destination / f"{binary_name}_{latest_version}"
                        shutil.move(str(binary_path), str(final_path))
                        print(f"  ✓ Downloaded and extracted: {binary_name} {latest_version}")
                    else:
                        print(f"  ⚠️  Warning: Could not find {binary_name} binary in extracted archive")

            # Remove the original archive
            download_path.unlink()
        elif filename.endswith(".tar.gz"):
            # Keep other tarballs as-is but rename to include version
            file_extension = ".tar.gz"
            new_filename = f"{binary_name}_{latest_version}{file_extension}"
            new_path = destination / new_filename
            download_path.rename(new_path)
            print(f"  ✓ Downloaded: {binary_name} {latest_version} (archive kept)")
        elif filename.endswith(".zip"):
            # Keep zip files as-is but rename to include version
            file_extension = ".zip"
            new_filename = f"{binary_name}_{latest_version}{file_extension}"
            new_path = destination / new_filename
            download_path.rename(new_path)
            print(f"  ✓ Downloaded: {binary_name} {latest_version} (archive kept)")
        elif filename.endswith(".gz"):
            # Decompress single-file gz archives (these are standalone binaries, not multi-file archives).
            # gzip streams carry no file-mode metadata, so we must set the execute bit ourselves
            # — otherwise the symlinked binary fails with "Permission denied" on first invocation.
            decompressed_path = destination / f"{binary_name}_{latest_version}"
            with gzip.open(download_path, "rb") as gz_file, open(decompressed_path, "wb") as out_file:
                out_file.write(gz_file.read())
            decompressed_path.chmod(0o755)
            download_path.unlink()
            print(f"  ✓ Downloaded and decompressed: {binary_name} {latest_version}")
        else:
            # Keep as-is for other file types (.exe, .so, .dll, .msi, etc.) but rename to include version
            # Preserve the original extension
            # Use regex to extract only the real extension (.so, .so.1, .exe, .msi, .dll, .dylib)
            # because Path.suffixes splits on every dot (e.g., "file_2.43.10.so" -> ['.43', '.10', '.so'])
            import re

            # The regex is the source of truth for "real extension". Falling back to
            # Path.suffixes is wrong because it splits on every dot — e.g.
            # Path("shfmt_v3.13.1_linux_amd64").suffixes -> [".13", ".1_linux_amd64"].
            ext_match = re.search(r"(\.(so(\.\d+)?|dll|dylib|exe|msi))$", download_path.name)
            file_extension = ext_match.group(1) if ext_match else ""
            new_filename = f"{binary_name}_{latest_version}{file_extension}"
            new_path = destination / new_filename
            download_path.rename(new_path)
            # Bare Linux binaries (no extension) come from curl with mode 0644.
            # Mark them executable so the symlink in /usr/local/bin actually runs.
            # Shared libs and Windows installers (.so/.dll/.exe/.msi/.dylib) stay untouched.
            if not file_extension:
                new_path.chmod(0o755)
            print(f"  ✓ Downloaded: {binary_name} {latest_version}")

    except subprocess.CalledProcessError as error:
        print(f"  ✗ Failed: {binary_info['name']}")
        print(f"    Error: {error.stderr}")
    except json.JSONDecodeError as error:
        print(f"  ✗ Failed to parse GitHub API response for {binary_info['name']}: {error}")


def _get_binaries(destination: Path) -> None:
    """Download all binary releases concurrently"""
    print(f"\n📥 Downloading Binary Releases ({len(BINARIES)} binaries)...")
    print("=" * 60)

    with futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_binary = {
            executor.submit(_get_latest_binary, binary, destination): binary["name"] for binary in BINARIES
        }

        completed = 0
        for future in futures.as_completed(future_to_binary):
            binary_name = future_to_binary[future]
            completed += 1
            try:
                future.result()
                print(f"  Progress: {completed}/{len(BINARIES)}")
            except Exception as error:
                print(f"  ✗ Error downloading binary {binary_name}: {error}")
                print(f"  Progress: {completed}/{len(BINARIES)}")


def get_binaries(destination: Path) -> None:
    # Create separate directories for npm packages and binaries
    npm_dir = destination / "npm_packages"
    binaries_dir = destination / "binaries"

    npm_dir.mkdir(parents=True, exist_ok=True)
    binaries_dir.mkdir(parents=True, exist_ok=True)

    _get_npm_lsps(npm_dir)
    _get_binaries(binaries_dir)
