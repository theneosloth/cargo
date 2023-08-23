{
    description = "Application packaged using poetry2nix";

    inputs.flake-utils.url = "github:numtide/flake-utils";
    inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    inputs.poetry2nix = {
        url = "github:nix-community/poetry2nix";
        inputs.nixpkgs.follows = "nixpkgs";
    };

    outputs = { self, nixpkgs, flake-utils, poetry2nix }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
                inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication defaultPoetryOverrides mkPoetryEnv;
                pkgs = nixpkgs.legacyPackages.${system};
                overrides = defaultPoetryOverrides.extend
                    (self: super: {
                        ruff = super.ruff.override {
                            preferWheel = true;
                        };
                        wikitextparser = super.wikitextparser.overridePythonAttrs(
                            old: {
                                buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
                            }
                        );
                    });
            in
              {
                  packages = {
                      default =  mkPoetryApplication {
                          projectDir = self;
                          overrides = overrides;
                      };

                      dockerStream =  pkgs.dockerTools.streamLayeredImage {
                          name = "neosloth/huntinghawk";
                          tag = "latest";
                          created = "now";
                          config = { Cmd = [ "${self.packages.${system}.default}/bin/api" ]; };
                      };
                  };

                  devShells.default = pkgs.mkShell {
                      packages = [
                          pkgs.redis
                          pkgs.flyctl
                          pkgs.poetry
                          (mkPoetryEnv{
                              projectDir = self;
                              overrides = overrides;
                          })
                      ];
                  };
              });
}
