{
  description = "Flake for requirements  management tool";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs, flake-utils }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { system = system; };
    python = pkgs.python311;
    pythonPackages = pkgs.python311Packages;
  in 
  {
    devShells.${system}.default = pkgs.mkShell {
      name = "trace-cli";
      packages = with pkgs; [
        cmake
        gnumake
        gcc
        sqlite
        python
        pythonPackages.pip
        pythonPackages.setuptools
        pythonPackages.wheel
        pythonPackages.pytest
        pythonPackages.typer
        pythonPackages.black
        pythonPackages.ruff
        pythonPackages.pyyaml
        pythonPackages.rich
        pythonPackages.build
        pythonPackages.twine
      ];
     
      shellHook = ''
            echo "Dev environment for C/Python/Robot ready."
            if [ ! -d .env ]; then
                python -m venv .env
            fi 
            source .env/bin/activate
            python -m pip install robotframework
            python -m pip install robotframework-jsonlibrary
      '';
    };
  };
}
