{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    pkgs.python314
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
    ]}:''${NIX_LD_LIBRARY_PATH:-}:''$LD_LIBRARY_PATH"

    if [ -d "backend/.venv" ]; then
      source backend/.venv/bin/activate
    fi
  '';
}
