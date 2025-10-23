import json
import subprocess
from concurrent import futures
from dataclasses import dataclass
from pathlib import Path

# Fetch all the plugins that are being used in the current repo
LAZY_REPOS = "~/.local/share/nvim/lazy"


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
    base_dir = Path(LAZY_REPOS).expanduser()

    repo_urls = []
    for repo in base_dir.iterdir():
        if repo.is_dir and (repo / ".git").is_dir:
            url = _get_remote_url(repo)
            if url:
                repo_urls.append(Git(name=repo.name, git_url=url))
    return repo_urls


def _clone(url: str, path: Path) -> None:
    """
    Worker function for the thread to clone the repo

    :param url: URL to clone
    :param path: Where to place the repo
    """
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", url, path], 
            check=True,
            capture_output=True  # Suppress git output for cleaner logs
        )
    except subprocess.CalledProcessError as error:
        print(f"Failed to clone {url}: {error}")


def get_nvim_plugins(target_dir: Path) -> None:
    """
    Iterate over all the URLs and thread the download of each
    repository to the target path

    :param target_dir: Path to place the cloned repos
    """
    repo_urls = _get_repos()
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {
            executor.submit(_clone, git.git_url, target_dir / git.name): git.name
            for git in repo_urls
        }

        # Collect the results as they complete
        for future in futures.as_completed(future_to_url):
            item = future_to_url[future]
            try:
                future.result()
            except Exception as error:
                print(f"Error with {item} {error}")


def get_nvim_tree_sitter_langs(target_dir: Path) -> None:
    # Get the path to parsers.json in the assets folder
    script_dir = Path(__file__).parent
    parsers_file = script_dir / "parsers.json"
    
    with parsers_file.open() as file:
        parsers = json.load(file)

    trees: list[TreeSitter] = []
    for k, v in parsers.items():
        trees.append(
            TreeSitter(
                name=k,
                git_url=v["install_info"].get("url"),
                files=v["install_info"].get("files"),
            )
        )

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {
            executor.submit(
                _clone, tree.git_url, target_dir / tree.name
            ): tree.name
            for tree in trees
        }

        # Collect the results as they complete

        for future in futures.as_completed(future_to_url):
            item = future_to_url[future]
            try:
                future.result()

            except Exception as error:
                print(f"Error with {item} {error}")
