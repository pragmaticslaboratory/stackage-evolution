import System.Environment
import System.IO

import Debug.Trace

import Distribution.Package
import Distribution.PackageDescription
import Distribution.PackageDescription.Parsec
import Distribution.Version
import Distribution.Text
import Distribution.ModuleName hiding(main)

import Data.List
import Data.List.Split
import qualified Data.ByteString.Char8 as B

import Control.Monad
--import Control.Monad.Parallel as MP


import Text.PrettyPrint

main :: IO ()
main = do files <- getContents
          results <- mapM parseCabalFile (lines files)
          putStr $ intercalate "\n" results

parseCabalFile :: String -> IO String
parseCabalFile cabalFile = withFile cabalFile ReadMode $ \handle -> do
          cbl <- hGetContents handle
          let cblPacked = B.pack(cbl)
          let (warnings, result) = runParseResult (parseGenericPackageDescription cblPacked)
          case result of
            Left (_, errors) -> error $ "Parse Error for cabal file: " ++ cabalFile
            Right d          -> return $
                               intercalate ";" $
                               showPackageHeader cabalFile d ++
                               [intercalate "," $ sort $ (mapOrEmpty (\(Dependency x y _) -> unPackageName x) $ nub $ extractDeps d)] ++
                               [intercalate "," (mapOrEmpty showModuleName (exposedModules d))] ++
                               [intercalate "," (mapOrEmpty id $ getSrcDirs d)] ++
                               [intercalate "," (mainModules d)]                               
          where exposedModules d = let (x, _) = exposedAndOtherModules d in x
                mainModules d = let (_, y) = exposedAndOtherModules d in y
                

extractDeps :: GenericPackageDescription -> [Dependency]
extractDeps d = ldeps ++ edeps
  where ldeps = case (condLibrary d) of
                Nothing -> []
                Just c -> condTreeConstraints c
        edeps = concat $ map (condTreeConstraints . snd) $ condExecutables d

exposedAndOtherModules :: GenericPackageDescription -> ([ModuleName], [FilePath])
exposedAndOtherModules d = (sort (nub (lmodules ++ emodules)), mainModules)
  where lmodules = case (condLibrary d) of
                     Nothing -> []
                     Just condl -> (exposedModules (condTreeData condl)) ++ (otherModules (libBuildInfo (condTreeData condl)))
        emodules = concatMap (\(_, ctree) -> (exeModules (condTreeData ctree))) (condExecutables d)
        mainModules = concatMap (\(_, ctree) -> [(modulePath (condTreeData ctree))]) (condExecutables d)

getSrcDirs :: GenericPackageDescription -> [FilePath]
getSrcDirs d = sort (nub (ldirs ++ edirs))
  where ldirs = case (condLibrary d) of
                    Nothing -> []
                    Just condl -> hsSourceDirs $ libBuildInfo (condTreeData condl)
        edirs = concatMap (\(_, ctree) -> hsSourceDirs $ buildInfo $ condTreeData ctree) (condExecutables d)

showPackageHeader :: String -> GenericPackageDescription -> [String]
showPackageHeader cabalFile d = let desc = packageDescription d
                      in [showPkgName desc
                         , showPkgVer desc
                         , stability desc
                         , cabalFile]
                         ++ [intercalate "," (sort (splitOn "," (filterLn (category desc))))]


showModuleName :: ModuleName -> String
showModuleName mname = (display mname)


showPkgName :: PackageDescription -> String
showPkgName desc = unPackageName (pkgName (package desc))

showPkgVer :: PackageDescription -> String
showPkgVer desc = display (pkgVersion (package desc))

showVersionInterval :: [VersionInterval] -> String
showVersionInterval [] = ""
showVersionInterval (((LowerBound lv lb), (UpperBound uv ub)) : vis) = showLowerBound lb ++ show lv ++ ", " ++ show uv ++ showUpperBound ub
showVersionInterval (((LowerBound lv lb), NoUpperBound) : vis)       = showLowerBound lb ++ show lv ++ ", ... "

showLowerBound :: Bound -> String
showLowerBound InclusiveBound = "["
showLowerBound ExclusiveBound = "]"

showUpperBound :: Bound -> String
showUpperBound InclusiveBound = "]"
showUpperBound ExclusiveBound = "["

mapOrElse :: (a -> b) -> [a] -> b -> [b]
mapOrElse _ [] d = [d]
mapOrElse f l  _ = map f l

mapOrEmpty :: (a -> String) -> [a] -> [String]
mapOrEmpty f l = mapOrElse f l ""

filterLn = filter (/= '\n')

showPkgExesBuildInfo :: GenericPackageDescription -> String
showPkgExesBuildInfo d = (concatMap (\(_, ctree) ->
                            (show (buildInfo (condTreeData ctree))))
                            (condExecutables d))