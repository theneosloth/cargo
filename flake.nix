{
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
}
