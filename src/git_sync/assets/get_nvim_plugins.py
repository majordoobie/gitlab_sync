import json
import subprocess
from concurrent import futures
from dataclasses import dataclass
from pathlib import Path

# Fetch all the plugins that are being used in the current repo.
# Neovim config uses vim.pack (Neovim 0.12 built-in), which installs plugins here:
PACK_REPOS = "~/.local/share/nvim/site/pack/core/opt"

# Curated "brief" subset of tree-sitter parsers for minimal installs.
# Covers everyday dev languages + the injection/doc parsers that Neovim
# highlighting quietly depends on (comment, regex, markdown_inline, vimdoc).
BRIEF_PARSERS: frozenset[str] = frozenset({
    "asm",
    "bash",
    "c",
    "cmake",
    "comment",
    "cpp",
    "css",
    "diff",
    "dockerfile",
    "gitcommit",
    "go",
    "html",
    "java",
    "javascript",
    "json",
    "json5",
    "llvm",
    "lua",
    "make",
    "markdown",
    "markdown_inline",
    "objdump",
    "python",
    "query",
    "regex",
    "rust",
    "sql",
    "toml",
    "tsx",
    "typescript",
    "vimdoc",
    "yaml",
})


@dataclass
class Git:
    name: str
    git_url: str


@dataclass
class TreeSitter:
    name: str
    git_url: str
    files: list[str]


def _get_remote_url(repo_path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", repo_path.as_posix(), "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as error:
        print(error)
        return None


def _get_repos() -> list[Git]:
    """
    Fetch all the repos used currently in my neovim config

    :return:
    """
    base_dir = Path(PACK_REPOS).expanduser()

    repo_urls = []
    for repo in base_dir.iterdir():
        if repo.is_dir and (repo / ".git").is_dir:
            url = _get_remote_url(repo)
            if url:
                repo_urls.append(Git(name=repo.name, git_url=url))
    return repo_urls


def _clone(url: str, path: Path, name: str) -> None:
    """
    Worker function for the thread to clone the repo

    :param url: URL to clone
    :param path: Where to place the repo
    :param name: Name of the repo for logging
    """
    print(f"  🔄 Cloning: {name}...")
    try:
        subprocess.run(
            ["git", "clone", "--mirror", url, path],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ Cloned: {name}")
    except subprocess.CalledProcessError as error:
        print(f"  ✗ Failed to clone {name}: {error}")


def get_nvim_plugins(target_dir: Path) -> None:
    """
    Iterate over all the URLs and thread the download of each
    repository to the target path

    :param target_dir: Path to place the cloned repos
    """
    repo_urls = _get_repos()
    print(f"\n🔌 Cloning Neovim Plugins ({len(repo_urls)} repositories)...")
    print("=" * 60)

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {
            executor.submit(_clone, git.git_url, target_dir / git.name, git.name): git.name for git in repo_urls
        }

        completed = 0
        # Collect the results as they complete
        for future in futures.as_completed(future_to_url):
            item = future_to_url[future]
            completed += 1
            try:
                future.result()
                print(f"  Progress: {completed}/{len(repo_urls)}")
            except Exception as error:
                print(f"  ✗ Error with {item}: {error}")
                print(f"  Progress: {completed}/{len(repo_urls)}")


def get_nvim_tree_sitter_langs(target_dir: Path, brief: bool = False) -> None:
    # Get the path to parsers.json in the assets folder
    script_dir = Path(__file__).parent
    parsers_file = script_dir / "parsers.json"

    with parsers_file.open() as file:
        parsers = json.load(file)

    if brief:
        missing = BRIEF_PARSERS - parsers.keys()
        if missing:
            print(f"  ⚠️  Brief parsers not found in parsers.json: {sorted(missing)}")
        parsers = {k: v for k, v in parsers.items() if k in BRIEF_PARSERS}

    trees: list[TreeSitter] = []
    for k, v in parsers.items():
        trees.append(
            TreeSitter(
                name=k,
                git_url=v["install_info"].get("url"),
                files=v["install_info"].get("files"),
            )
        )

    label = "brief" if brief else "full"
    print(f"\n🌳 Cloning Tree-sitter Parsers ({len(trees)} parsers, {label})...")
    print("=" * 60)

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {
            executor.submit(_clone, tree.git_url, target_dir / tree.name, tree.name): tree.name for tree in trees
        }

        completed = 0
        # Collect the results as they complete
        for future in futures.as_completed(future_to_url):
            item = future_to_url[future]
            completed += 1
            try:
                future.result()
                print(f"  Progress: {completed}/{len(trees)}")
            except Exception as error:
                print(f"  ✗ Error with {item}: {error}")
                print(f"  Progress: {completed}/{len(trees)}")
