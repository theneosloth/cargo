{
<<<<<<< HEAD
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }: {
    overlay = nixpkgs.lib.composeManyExtensions [
      (final: prev: {
        myApp = prev.poetry2nix.mkPoetryApplication {
          projectDir = self;
        };
      })
    ];
  } // (flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlay ];
      };
    in
    {
      apps = {
        inherit (pkgs) myApp;
      };

      defaultApp = pkgs.myApp;

      devShell =
        let
          pythonPackages = pkgs.python310Packages;
        in
        pkgs.mkShellNoCC {
          buildInputs = with pythonPackages; [ python venvShellHook ];
          packages = [ pkgs.poetry ];
          venvDir = "./.venv";
          postVenvCreation = ''
            unset SOURCE_DATE_EPOCH
            poetry env use .venv/bin/python
            poetry install
          '';
          postShellHook = ''
            unset SOURCE_DATE_EPOCH
            poetry env info
          '';
        };
    }));
=======
    inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    outputs = { self, nixpkgs }:
        let
            supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
            forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
            pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
        in
          {
              packages = forAllSystems (system: {
                  default = pkgs.${system}.poetry2nix.mkPoetryApplication {
                      overrides = pkgs.${system}.poetry2nix.defaultPoetryOverrides.extend
                          (self: super: {
                              types-pyopenssl = super.types-pyopenssl.overridePythonAttrs(
                                  old: {
                                      buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
                                  }
                              );
                              url-normalize = super.url-normalize.overridePythonAttrs(
                                  old: {
                                      buildInputs = (old.buildInputs or [ ]) ++ [ super.poetry ];
                                  }
                              );
                          });
                      projectDir = ./.;
                      preferWheels = true;
                  };
              });

              devShells = forAllSystems (system: {
                  default = pkgs.${system}.mkShellNoCC {
                      packages = with pkgs.${system}; [
                          (poetry2nix.mkPoetryEnv {
                              projectDir = ./.;
                              preferWheels = true;
                              overrides = pkgs.${system}.poetry2nix.defaultPoetryOverrides.extend
                                  (self: super: {
                                      types-pyopenssl = super.types-pyopenssl.overridePythonAttrs(
                                          old: {
                                              buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
                                          }
                                      );
                                      url-normalize = super.url-normalize.overridePythonAttrs(
                                          old: {
                                              buildInputs = (old.buildInputs or [ ]) ++ [ super.poetry ];
                                          }
                                      );
                                  });
                          })

                      ];
                  };
              });
          };
>>>>>>> b02f42ddf13b2bb9971a410d0edfd4b28ad148f0
}
