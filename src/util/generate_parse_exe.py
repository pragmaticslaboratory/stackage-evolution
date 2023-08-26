
from pathlib import Path
import os

import sys #pleger -> plataform
parseCabalBinary = 'src/parse/ParseCabal' + ('.exe' if sys.plataform == 'Win32' else '') #pleger path for different os
packageImportsBinary = 'src/parse/PackageImports' + ('.exe' if sys.plataform == 'Win32' else '') #pleger path for different os

#stack exec ghc --package Cabal -- ParseCabal.hs
#stack exec ghc --package Cabal --package haskell-src-exts --package cpphs PackageImports.hs 
#stack exec ghc --package Cabal --package haskell-src-exts --package cpphs --package aeson --package extra -- PackageInfoJSON.hs

def generate_parse_exe(folder_path):
    os.chdir(os.getcwd()+'/parse')

    path = Path(folder_path + parseCabalBinary)
    if(path.is_file()):
        comand = 'ghc --make ParseCabal.hs -package Cabal'
        os.system(comand)
        
    path = Path(folder_path + packageImportsBinary)
    if(path.is_file()):
        comand = 'ghc --make PackageImports.hs -package Cabal -package cpphs'
        os.system(comand)
