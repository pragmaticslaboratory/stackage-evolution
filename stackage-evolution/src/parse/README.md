# Compilación y ejecución parser en Windows

## Pre-requisitos

1. Instalar GHCUP, desde www.haskell.org/ghcup con las siguientes opciones:
   - Instalar HLS? Sí
   - Instalar stack? Sí
   - Instalar MSys2 toolchain? Sí
2. Una vez instalado con éxito, iniciar una consola Powershell y verificar que `ghc --version` retorna la versión 9.2.5 de GHC.
3. Instalar librerías cabal necesarias: `cabal install --lib split haskell-src-exts aeson extra`.
4. Instalar pre-procesador de C++: `cabal install cpphs`.

## Versiones instaladas/necesarias

- GHC: 9.2.5
- Cabal: 3.6.3.0

## ParseCabal

En el directorio `src/parse`, ejecutar lo siguiente: `ghc --make ParseCabal.hs
-package Cabal`. Esto generará el ejecutable `ParseCabal.exe`. Los archivos
`.hi` y `.o` se pueden borrar.

## PackageImports

En el directorio `src/parse`, ejecutar lo siguiente: `ghc --make
PackageImports.hs -package Cabal -package cpphs`. Esto generará el ejecutable
`PackageImports.exe`. Los archivos `.hi` y `.o` se pueden borrar.

## PackageInfoJSON

En el directorio `src/parse` ejecutar lo siguiente: `ghc --make PackageInfoJSON.hs -package Cabal -package cpphs`. Esto generará el ejecutable `PackageInfoJSON.exe`. Los archivos `.hi` y `.o` se pueden borrar.
