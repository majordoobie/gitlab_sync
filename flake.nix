{
  description = "Nix flake for a Python development environment using pip and venv";

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
          # Include Python and pip in the environment
          packages = [
            pkgs.python313
            pkgs.python313Packages.pip
            pkgs.python313Packages.debugpy
            pkgs.git
          ];

          # Create and activate a virtual environment, then install requirements
          shellHook = ''
            if [ ! -d .venv ]; then
              echo "Creating virtual environment..."
              python -m venv .venv
            fi
            source .venv/bin/activate
            pip install --upgrade pip
            if [ -f requirements.txt ]; then
              echo "Installing Python dependencies from requirements.txt..."
              pip install -r requirements.txt
            else
              echo "No requirements.txt found."
            fi
          '';
        };
      }
    );
}
