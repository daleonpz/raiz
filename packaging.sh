# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0
#!/bin/bash

# This script sets up a Nix shell environment for packaging Python projects.
nix-shell -p python313Packages.build python313Packages.pip python313Packages.twine --pure
