{
  description = "Traceable C + Python CLI + Robot + Pytest Project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
  };

  outputs = { self, nixpkgs, flake-utils }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { system = system; };
#         pkgs = nixpkgs.legacyPackages.${system};
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
        python
        pythonPackages.pip
        pythonPackages.setuptools
        pythonPackages.wheel
        pythonPackages.pytest
        pythonPackages.robotframework
        pythonPackages.typer
        pythonPackages.black
        pythonPackages.ruff
      ];
     
      shellHook = ''
            echo "Dev environment for C/Python/Robot ready."
      '';
    };
  };
}
