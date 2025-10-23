{
  description = "Nix flake for a Python development environment using uv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = pkgs.mkShell {
          packages = [
            pkgs.uv
            pkgs.python313
            pkgs.git
            pkgs.nodejs
            pkgs.nodePackages.npm
          ];

          shellHook = ''
          '';
        };
      }
    );
}
