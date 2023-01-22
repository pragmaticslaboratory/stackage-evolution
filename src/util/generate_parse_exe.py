
from pathlib import Path
import os

#stack exec ghc --package Cabal -- ParseCabal.hs
#stack exec ghc -package Cabal -package haskell-src-exts -package cpphs --make PackageImports.hs
#stack exec ghc --package Cabal --package haskell-src-exts --package cpphs --package aeson --package extra -- PackageInfoJSON.hs

def generate_parse_exe(folder_path):
    os.chdir(os.getcwd()+'/parse')

    path = Path(folder_path+"/src/parse/ParseCabal.exe")
    if(path.is_file()):
        comand = 'stack exec ghc --package Cabal -- ParseCabal.hs'
        os.system(comand)
        
    path = Path(folder_path+"/src/parse/PackageImports.exe")
    if(path.is_file()):
        comand = 'stack exec ghc -package Cabal -package haskell-src-exts -package cpphs --make PackageImports.hs'
        os.system(comand)
