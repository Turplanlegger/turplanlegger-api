{
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
    in
    {
      devShells = systems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python311
              podman-compose
              ruff
              pre-commit

              # Required for psycopg
              libpq
              stdenv.cc.cc.lib
            ];
            shellHook = ''
              venvDir="venv";

              # https://github.com/astral-sh/ruff/issues/1699
              echo "OS path for ruff: ${pkgs.ruff}/bin/ruff"

              # Prioritize venv binaries over Nix
              export PATH="$PWD/$venvDir/bin:$PATH"

              # Make libpq visible
              export LD_LIBRARY_PATH=${pkgs.libpq}/lib:$LD_LIBRARY_PATH

              # Make libstdc++ visible
              export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH

              if [ ! -d "$venvDir" ]; then
                mkdir -p $venvDir
                python3 -m venv $venvDir
              fi

              source $venvDir/bin/activate

              pip install --editable '.[dev]' --quiet
            '';
          };
        });
    };
}
