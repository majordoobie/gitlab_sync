# gitlab_sync

```bash
nix develop -c fish
uv run git-sync -d /tmp
```



# LSPs To Download
## Python Modules
- [ ] Black
- [ ] cmake-language-server
- [ ] isort
- [ ] robotframework_ls
- [ ] ruff


## NPM
- [x] pyright-language-server
```bash
npm pack pyright --pack-destination .
```

- [ ] vscode-langserver-extracted
```bash
npm pack vscode-langserver-extracted --pack-destination .
```

- [ ] yaml-language-server
```bash
npm pack yaml-language-server --pack-destination .
```

- [ ] ms-docker-compose
```bash
npm pack @microsoft/compose-language-service --pack-destination .
```


Installing them requires using NPM on the target machine
```bash
  # Extract and install the tarball
  npm install /path/to/pyright-1.1.379.tgz -g

  # The binaries will be in /usr/local/lib/node_modules/.bin/
  # Create symlink if needed
  ln -s /usr/local/lib/node_modules/.bin/pyright-langserver /usr/local/bin/pyright-langserver

```


## Binary
- [x] [lazygit](https://github.com/jesseduffield/lazygit/releases)
- [x] [nvim](https://github.com/neovim/neovim/releases)
- [x] [lua-language-server](https://github.com/LuaLS/lua-language-server/releases)
- [x] [starship](https://github.com/starship/starship/releases)
- [x] [stylua](https://github.com/JohnnyMorganz/StyLua/releases)
- [x] [eza](https://github.com/eza-community/eza/releases)
- [x] [asm-lsp](https://github.com/bergercookie/asm-lsp/releases)
- [x] [taplo-toml-langserver](https://github.com/tamasfe/taplo/releases)

## For Later
- [ ] containerd
- [ ] LLVM-20
