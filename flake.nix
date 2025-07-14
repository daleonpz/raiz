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

        pythonEnv = python.withPackages (ps: with ps; [
          pytest
          robotframework
          typer
          black
          ruff
        ]);
      in {
        devShells.default = pkgs.mkShell {
          name = "trace-cli-dev";
          buildInputs = [
            pythonEnv
            pkgs.gcc
            pkgs.gnumake
            pkgs.gh  # Optional: GitHub CLI for future integration
          ];

          shellHook = ''
            echo "Dev environment for C/Python/Robot ready."
          '';
        };
      });
}

