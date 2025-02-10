import json
import subprocess
from concurrent import futures
from dataclasses import dataclass
from pathlib import Path
from sys import argv

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
    base_dir = Path(LAZY_REPOS).expanduser()

    repo_urls = []
    for repo in base_dir.iterdir():
        if repo.is_dir and (repo / ".git").is_dir:
            url = _get_remote_url(repo)
            if url:
                repo_urls.append(Git(name=repo.name, git_url=url))
    return repo_urls


def _clone(url: str, path: Path) -> None:
    try:
        subprocess.run(["git", "clone", url, path], check=True)
    except subprocess.CalledProcessError as error:
        print(f"Failed to clone {url}: {error}")


def _clone_plugins(target_dir: Path) -> None:
    repo_urls = _get_repos()
    with futures.ThreadPoolExecutor(max_workers=None) as executor:
        future_to_url = {
            executor.submit(
                _clone, git.git_url, target_dir / git.name
            ): git.name
            for git in repo_urls
        }

        # Collect the results as they complete
        for future in futures.as_completed(future_to_url):
            item = future_to_url[future]
            try:
                future.result()
            except Exception as error:
                print(f"Error with {item} {error}")

def _clone_tree_sitter(target_dir: Path) -> None:
    with open("parsers.json") as file:
        parsers: dict = json.load(file)

    trees: list[TreeSitter] = []
    for k, v in parsers.items():
        trees.append(
            TreeSitter(
                name=k,
                git_url=v["install_info"].get("url"),
                files=v["install_info"].get("files"),
            )
        )

    with futures.ThreadPoolExecutor(max_workers=None) as executor:
        future_to_url = {
            executor.submit(
                _clone, tree.git_url, target_dir / "tree_objs" / tree.name
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


def main(target_dir: Path) -> None:
    _clone_plugins(target_dir)
    # _clone_tree_sitter(target_dir)


if __name__ == "__main__":
    if len(argv) != 2 or not Path(argv[1]).is_dir():
        exit(
            "Provide the path to the target directory where the repos will be cloned to"
        )
    main(Path(argv[1]))
