{
  description = "Flake for raiz - CLI requirements management tool";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
        pythonPackages = pkgs.python313Packages;

        # robotframework-jsonlibrary isn't in nixpkgs, so package it ourselves
        robotframework-jsonlibrary = pythonPackages.buildPythonPackage rec {
          pname = "robotframework-jsonlibrary";
          version = "0.5";
          format = "setuptools";

          src = pythonPackages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-AArC5Tx/luO3Sca1WV/OyH1SkbSvwD+yUkcDVqfV2h8=";
          };

          propagatedBuildInputs = with pythonPackages; [
            robotframework
            jsonpath-ng
          ];

          doCheck = false;
        };

        raiz = pythonPackages.buildPythonApplication {
          pname = "raiz";
          # should match the version in pyproject.toml
          version = "0.2.0";
          format = "pyproject";
          src = ./.;

          nativeBuildInputs = with pythonPackages; [
            setuptools
          ];

          propagatedBuildInputs = with pythonPackages; [
            typer
            pyyaml
            rich
            robotframework
            robotframework-jsonlibrary
          ];

          doCheck = false;
        };
      in
      {
        packages.default = raiz;
        packages.raiz = raiz;

        devShells.default = pkgs.mkShell {
          name = "raiz-dev";
          packages = with pkgs; [
            cmake
            gnumake
            gcc
            sqlite
            python
            pythonPackages.wheel
            pythonPackages.pytest
            pythonPackages.typer
            pythonPackages.black
            pythonPackages.ruff
            pythonPackages.pyyaml
            pythonPackages.rich
            pythonPackages.build
            pythonPackages.twine
            pythonPackages.robotframework
            robotframework-jsonlibrary
          ];

          shellHook = ''
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            echo "Dev environment for raiz (C/Python/Robot) ready."
          '';
        };
      });
}
