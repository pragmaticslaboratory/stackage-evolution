import System.Environment
import System.IO

import Data.List hiding(map)

import Distribution.Package
import Distribution.PackageDescription
import Distribution.Text
import qualified Distribution.PackageDescription.Parsec as DP

import Language.Haskell.Exts hiding (Extension)
import Language.Haskell.Exts.SrcLoc
import Language.Haskell.Exts.Pretty
import qualified Language.Haskell.Exts.Extension as HSE_XT
import qualified Language.Haskell.Extension as CABAL_XT
import qualified Language.Haskell.Exts as STX

import Text.PrettyPrint

-- import qualified Control.Monad.Parallel as MP
import qualified Control.Monad
import qualified Data.ByteString.Char8 as B

import Language.Preprocessor.Cpphs

-- TODO handle I/O exceptions using handle, catch, or other
-- https://stackoverflow.com/questions/6009384/exception-handling-in-haskell
main :: IO ()
main = do pkgConf <- getContents
          let all_lines = lines pkgConf
          let cabalFile = head all_lines
          let pkgFiles = tail all_lines
          putStrLn (show all_lines)
          putStrLn (show cabalFile)
          putStrLn (show pkgFiles)
          results <- mapM (\x -> getImportsForURI cabalFile x) pkgFiles
          putStr $ intercalate "," (map prettyPrint (nub (concat results)))
          return ()

getImportsForURI :: String -> String -> IO [ModuleName SrcSpanInfo]
getImportsForURI cabalFile uri = do
    withFile uri ReadMode $ \handle -> do
      hSetEncoding handle latin1      
      doc <- hGetContents handle
      exts <- getPackageExtensions cabalFile
      parsedFileResult <- parseFileMaybeCPP (map cabalXTToHSEXT exts) uri doc
      case parsedFileResult of
          ParseFailed srcLoc err ->
            -- undefined is being called!! fix
            return $ [ModuleName noSrcSpan ("IsmaParseError[" ++ uri ++ "][" ++ err ++ "][" ++ show srcLoc ++ "]")]
          ParseOk res ->
            return (getModuleImports res)

-- TODO: add proper support for running CPPhs
-- We need CPP options and several parameters from the cabal package file
parseFileMaybeCPP :: [HSE_XT.Extension] -> String -> String -> IO (ParseResult (STX.Module SrcSpanInfo))
parseFileMaybeCPP pkgExts filename doc =
  do let allExts = pkgExts ++ fileExts
     if containsCPP allExts
      then do cppParsedDoc <- runCpphs defaultCpphsOptions filename doc
              return $ parseFileContentsWithExts allExts cppParsedDoc
      else return $ parseFileContentsWithExts allExts doc
  where fileExts = case (readExtensions doc) of
            Nothing -> []
            Just(_, xts) -> xts

        containsCPP xts = elem HSE_XT.CPP (enabledKnownExtensions xts)
        enabledKnownExtensions xts =
              case xts of
                [] -> []
                (xt:xtss) -> case xt of
                  (HSE_XT.EnableExtension known_ext) -> known_ext : enabledKnownExtensions xtss
                  _ -> enabledKnownExtensions xtss

getModuleImports :: STX.Module SrcSpanInfo -> [ModuleName SrcSpanInfo]
getModuleImports (STX.Module _ _ _ imports _) = map (\idecl -> (importModule idecl)) imports
getModuleImports (XmlPage _ _ _ _ _ _ _) = []
getModuleImports (XmlHybrid  _ _ _ imports _ _ _ _ _) = map (\idecl -> (importModule idecl)) imports

fromRight :: Either String r -> r
fromRight (Right r)  = r
fromRight (Left err) = error err

getPackageExtensions :: String -> IO [CABAL_XT.Extension]
getPackageExtensions cabalFile = withFile cabalFile ReadMode $ \handle -> do
          cbl <- hGetContents handle
          let cblPacked = B.pack(cbl)
          let (warnings, result) = DP.runParseResult (DP.parseGenericPackageDescription cblPacked)
          case result of
            Left (_, errors) -> error $ "Parse Error for cabal file: " ++ cabalFile
            Right d          -> return $ (extractPackageExtensions d)

extractPackageExtensions :: GenericPackageDescription -> [CABAL_XT.Extension]
extractPackageExtensions d = lexts ++ eexts
  where lexts = case (condLibrary d) of
                    Nothing -> []
                    Just condl -> allExtensions $ libBuildInfo (condTreeData condl)
        eexts = (concatMap (\(_, ctree) -> (allExtensions (buildInfo (condTreeData ctree))))
                           (condExecutables d))

cabalXTToHSEXT :: CABAL_XT.Extension -> HSE_XT.Extension
cabalXTToHSEXT cext = classifyExtension (display cext)