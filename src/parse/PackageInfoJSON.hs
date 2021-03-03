{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DeriveGeneric #-}

import qualified Control.Monad
import Control.Monad.Extra
import Data.Aeson
import Data.Aeson.Types
import qualified Data.ByteString.Char8 as B
import Data.List hiding (map)
import Data.List.Split
import Data.Maybe
import qualified Data.Text as TXT
import qualified Data.Text.Lazy.Encoding as T
import qualified Data.Text.Lazy.IO as T
import Distribution.Package
import Distribution.PackageDescription
import qualified Distribution.PackageDescription.Parsec as DP
import Distribution.Text
import GHC.Generics
import qualified Language.Haskell.Extension as CABAL_XT
import Language.Haskell.Exts hiding (Extension)
import qualified Language.Haskell.Exts as STX
import qualified Language.Haskell.Exts.Extension as HSE_XT
import Language.Haskell.Exts.Pretty
import Language.Haskell.Exts.SrcLoc
import Language.Preprocessor.Cpphs
import System.Environment
import System.IO
import Text.PrettyPrint

-- TODO handle I/O exceptions using handle, catch, or other
-- https://stackoverflow.com/questions/6009384/exception-handling-in-haskell
main :: IO ()
main = do
  pkgConf <- getContents
  let all_lines = lines pkgConf
  let cabalFile = head all_lines
  let pkgFiles = tail all_lines
  putStrLn (show "cabal file: " ++ show cabalFile)
  putStrLn (show "pkg files: " ++ show pkgFiles)
  putStrLn (show "cabalFile: " ++ cabalFile)
  mapM (putStrLn . show) pkgFiles

  resultsCalledFunctions <-
    concatMapM
      ( \uri ->
          withFile uri ReadMode $ \handle -> do
            hSetEncoding handle latin1 -- TO DO: set to UTF8?
            doc <- hGetContents handle
            exts <- getPackageExtensions cabalFile
            parsedFileResult <- parseFileMaybeCPP (map cabalXTToHSEXT exts) uri doc
            case parsedFileResult of
              ParseFailed srcLoc err -> return []
              ParseOk mod -> return $ [moduleInfoToJSON uri mod]
      )
      pkgFiles

  -- Obtain package imports, processing per Module
  --resultsImportedModules <- mapM (\uri -> getImportsForURI cabalFile uri) pkgFiles
  --mapM (putStrLn . show) $ (map prettyPrint (nub (concat resultsImportedModules)))

  -- Obtain function declarations, processing per Module
  -- resultsDeclaredFunctions <- mapM (\uri -> getDeclaredFunctionsForURI cabalFile uri) pkgFiles
  -- mapM (putStrLn . show) $ (map prettyPrint (nub (concat resultsDeclaredFunctions)))
  putStrLn "###################"

  -- Obtain called functions, processing per Module
  -- resultsCalledFunctions <- mapM (\uri -> getCalledFunctionsForURI cabalFile uri) pkgFiles
  mapM (T.putStrLn . T.decodeUtf8 . encode) $ resultsCalledFunctions

  return ()

data ModuleResultData = ModuleResultData
  { file :: String,
    declares :: [(String, String)],
    imports :: [String],
    exports :: [String],
    calls :: [String]
  }
  deriving (Show, Generic, ToJSON)

moduleInfoToJSON :: String -> STX.Module l -> ModuleResultData
moduleInfoToJSON uri mod =
  ModuleResultData
    { file = uri,
      declares = map (\x -> let y = splitOn "::" x in (lrtrim $ y !! 0, lrtrim $ y !! 1)) $ map prettyPrint (getModuleDeclaredFunctions mod),
      imports = map prettyPrint (getModuleImports mod),
      exports = map prettyPrint (getModuleExports mod),
      calls = map prettyPrint (concat (getModuleCalledFunctions mod))
    }

-- just the left and the right side of the input is to be trimmed
lrtrim :: String -> String
lrtrim = \xs -> rtrim $ ltrim xs
  where
    ltrim = dropWhile (isSpace')
    rtrim xs
      | Prelude.null xs = []
      | otherwise =
        if isSpace' $ last xs
          then rtrim $ init xs
          else xs

-- returns True if input equals ' '
isSpace' :: Char -> Bool
isSpace' = \c -> (c == ' ')

getModuleCalledFunctions :: STX.Module l -> [[QName l]]
getModuleCalledFunctions (STX.Module _ _ _ _ declarations) =
  map getBindCalledFunctions $
    filter
      ( \decl -> case decl of
          (PatBind _ _ _ _) -> True
          _ -> False
      )
      declarations
getModuleCalledFunctions _ = []

getBindCalledFunctions :: Decl l -> [QName l]
getBindCalledFunctions (PatBind _ pat rhs _) = getPatApplications pat ++ getRhsApplications rhs

getPatApplications :: Pat l -> [QName l]
getPatApplications (PInfixApp _ _ qname _) = [qname]
getPatApplications (PApp _ qname patlist) = [qname] ++ (concatMap getPatApplications patlist)
getPatApplications (PTuple _ _ patlist) = concatMap getPatApplications patlist
getPatApplications (PUnboxedSum _ _ _ pat) = getPatApplications pat
getPatApplications (PList _ patlist) = concatMap getPatApplications patlist
getPatApplications (PParen _ pat) = getPatApplications pat
getPatApplications (PRec _ _ patfields) = concatMap getPatFieldApplications patfields
  where
    getPatFieldApplications (PFieldPat _ _ pat) = getPatApplications pat
    getPatFieldApplications _ = []
getPatApplications (PAsPat _ _ pat) = getPatApplications pat
getPatApplications (PIrrPat _ pat) = getPatApplications pat
getPatApplications (PatTypeSig _ pat _) = getPatApplications pat
getPatApplications (PViewPat _ exp pat) = getExpApplications exp ++ getPatApplications pat
getPatApplications (PRPat _ rpats) = concatMap getRPPatApplications rpats
  where
    getRPPatApplications (RPPat _ pat) = getPatApplications pat
    getRPPatApplications _ = []
getPatApplications (PXTag _ _ _ maybepat patlist) = concatMap getPatApplications (maybeToList maybepat) ++ concatMap getPatApplications patlist
getPatApplications (PXETag _ _ _ maybepat) = concatMap getPatApplications (maybeToList maybepat)
getPatApplications (PXPatTag _ pat) = getPatApplications pat
getPatApplications (PSplice _ splice) = getSpliceApplications splice
getPatApplications (PBangPat _ pat) = getPatApplications pat
getPatApplications _ = []

getSpliceApplications :: Splice l -> [QName l]
getSpliceApplications (ParenSplice _ exp) = getExpApplications exp
getSpliceApplications (TParenSplice _ exp) = getExpApplications exp
getSpliceApplications _ = []

getDeclaredFunctionsForURI :: String -> String -> IO [Decl SrcSpanInfo]
getDeclaredFunctionsForURI cabalFile uri = do
  withFile uri ReadMode $ \handle -> do
    hSetEncoding handle latin1 -- TO DO: set to UTF8?
    doc <- hGetContents handle
    exts <- getPackageExtensions cabalFile
    parsedFileResult <- parseFileMaybeCPP (map cabalXTToHSEXT exts) uri doc
    case parsedFileResult of
      ParseFailed srcLoc err ->
        -- undefined is being called!! fix
        return $ [] --Decl noSrcSpan ("IsmaParseError[" ++ uri ++ "][" ++ err ++ "][" ++ show srcLoc ++ "]")]
      ParseOk mod ->
        return (getModuleDeclaredFunctions mod)

getRhsApplications :: Rhs l -> [QName l]
getRhsApplications (UnGuardedRhs _ exp) = getExpApplications exp
getRhsApplications (GuardedRhss _ grhss) = concatMap getGuardedRhsApplications grhss

getGuardedRhsApplications :: GuardedRhs l -> [QName l]
getGuardedRhsApplications (GuardedRhs _ stmts exp) = concatMap getStmtApplications stmts ++ getExpApplications exp

getStmtApplications :: Stmt l -> [QName l]
getStmtApplications (Generator _ pat exp) = getPatApplications pat ++ getExpApplications exp
getStmtApplications (Qualifier _ exp) = getExpApplications exp
getStmtApplications (LetStmt _ bindings) = getBindsApplications bindings
getStmtApplications (RecStmt _ stmts) = concatMap getStmtApplications stmts

getBindsApplications :: Binds l -> [QName l]
getBindsApplications (BDecls _ declarations) = [] -- TO DO: IS THIS NECESSARY?? to inspect yet again all Decls?
getBindsApplications (IPBinds _ ipbinds) = concatMap getIPBindsApplications ipbinds

getIPBindsApplications :: IPBind l -> [QName l]
getIPBindsApplications (IPBind _ name exp) = getExpApplications exp

getExpApplications :: Exp l -> [QName l]
getExpApplications (App _ exp1 exp2) =
  case exp1 of
    (STX.Var _ qname) -> [qname] ++ getExpApplications exp2
    _ -> getExpApplications exp2
getExpApplications (InfixApp _ exp1 qop exp2) =
  case qop of
    (QVarOp _ qname) -> [qname] ++ getExpApplications exp1 ++ getExpApplications exp2
    (QConOp _ qname) -> [qname] ++ getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (NegApp _ exp) = getExpApplications exp
getExpApplications (Lambda _ patlist exp) = concatMap getPatApplications patlist ++ getExpApplications exp
getExpApplications (Let _ binds exp) = getBindsApplications binds ++ getExpApplications exp
getExpApplications (If _ exp1 exp2 exp3) = getExpApplications exp1 ++ getExpApplications exp2 ++ getExpApplications exp3
getExpApplications (MultiIf _ grhss) = concatMap getGuardedRhsApplications grhss
getExpApplications (Case _ exp alts) = getExpApplications exp ++ concatMap getAltApplications alts
getExpApplications (Do _ stmts) = concatMap getStmtApplications stmts
getExpApplications (MDo _ stmts) = concatMap getStmtApplications stmts
getExpApplications (Tuple _ _ exps) = concatMap getExpApplications exps
getExpApplications (UnboxedSum _ _ _ exp) = getExpApplications exp
getExpApplications (TupleSection _ _ maybeExpList) = concatMap getExpApplications (concatMap maybeToList maybeExpList)
getExpApplications (List _ exps) = concatMap getExpApplications exps
getExpApplications (ParArray _ exps) = concatMap getExpApplications exps
getExpApplications (Paren _ exp) = getExpApplications exp
getExpApplications (LeftSection _ exp qop) = getExpApplications exp
getExpApplications (RightSection _ qop exp) = getExpApplications exp
getExpApplications (RecConstr _ _ fieldUpdates) = concatMap getFieldUpdateApplications fieldUpdates
getExpApplications (RecUpdate _ exp fieldUpdates) = getExpApplications exp ++ concatMap getFieldUpdateApplications fieldUpdates
getExpApplications (EnumFrom _ exp) = getExpApplications exp
getExpApplications (EnumFromTo _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (EnumFromThenTo _ exp1 exp2 exp3) = getExpApplications exp1 ++ getExpApplications exp2 ++ getExpApplications exp3
getExpApplications (ParArrayFromTo _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (ParArrayFromThenTo _ exp1 exp2 exp3) = getExpApplications exp1 ++ getExpApplications exp2 ++ getExpApplications exp3
getExpApplications (ListComp _ exp qualStmts) = getExpApplications exp ++ concatMap getQualStmtApplications qualStmts
getExpApplications (ParComp _ exp nestedQualStmts) = getExpApplications exp ++ (concatMap getQualStmtApplications (concat nestedQualStmts))
getExpApplications (ParArrayComp _ exp nestedQualStmts) = getExpApplications exp ++ (concatMap getQualStmtApplications (concat nestedQualStmts))
getExpApplications (ExpTypeSig _ exp _) = getExpApplications exp
getExpApplications (BracketExp _ bracket) = getBracketApplications bracket
getExpApplications (SpliceExp _ splice) = getSpliceApplications splice
getExpApplications (XTag _ _ _ maybeExp exps) = concatMap getExpApplications (maybeToList maybeExp) ++ concatMap getExpApplications exps
getExpApplications (XETag _ _ _ maybeExp) = concatMap getExpApplications (maybeToList maybeExp)
getExpApplications (XExpTag _ exp) = getExpApplications exp
getExpApplications (XChildTag _ exps) = concatMap getExpApplications exps
getExpApplications (CorePragma _ _ exp) = getExpApplications exp
getExpApplications (SCCPragma _ _ exp) = getExpApplications exp
getExpApplications (GenPragma _ _ _ _ exp) = getExpApplications exp
getExpApplications (Proc _ pat exp) = getPatApplications pat ++ getExpApplications exp
getExpApplications (LeftArrApp _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (RightArrApp _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (LeftArrHighApp _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (RightArrHighApp _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getExpApplications (ArrOp _ exp) = getExpApplications exp
getExpApplications (LCase _ alts) = concatMap getAltApplications alts
getExpApplications _ = []

getBracketApplications :: Bracket l -> [QName l]
getBracketApplications (ExpBracket _ exp) = getExpApplications exp
getBracketApplications (TExpBracket _ exp) = getExpApplications exp
getBracketApplications (PatBracket _ pat) = getPatApplications pat
getBracketApplications _ = [] -- TO DO: should I go into Decls? and Types?

getQualStmtApplications :: QualStmt l -> [QName l]
getQualStmtApplications (QualStmt _ stmt) = getStmtApplications stmt
getQualStmtApplications (ThenTrans _ exp) = getExpApplications exp
getQualStmtApplications (ThenBy _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2
getQualStmtApplications (GroupBy _ exp) = getExpApplications exp
getQualStmtApplications (GroupUsing _ exp) = getExpApplications exp
getQualStmtApplications (GroupByUsing _ exp1 exp2) = getExpApplications exp1 ++ getExpApplications exp2

getFieldUpdateApplications (FieldUpdate _ _ exp) = getExpApplications exp
getFieldUpdateApplications _ = []

getAltApplications :: Alt l -> [QName l]
getAltApplications (Alt _ pat rhs maybebinds) = getPatApplications pat ++ getRhsApplications rhs ++ maybeBindApplications
  where
    maybeBindApplications = case maybebinds of
      (Just binds) -> getBindsApplications binds
      Nothing -> []

-- TODO: add proper support for running CPPhs
-- We need CPP options and several parameters from the cabal package file
parseFileMaybeCPP :: [HSE_XT.Extension] -> String -> String -> IO (ParseResult (STX.Module SrcSpanInfo))
parseFileMaybeCPP pkgExts filename doc =
  do
    let allExts = pkgExts ++ fileExts
    if containsCPP allExts
      then do
        cppParsedDoc <- runCpphs defaultCpphsOptions filename doc
        return $ parseFileContentsWithExts allExts cppParsedDoc
      else return $ parseFileContentsWithExts allExts doc
  where
    fileExts = case (readExtensions doc) of
      Nothing -> []
      Just (_, xts) -> xts

    containsCPP xts = elem HSE_XT.CPP (enabledKnownExtensions xts)
    enabledKnownExtensions xts =
      case xts of
        [] -> []
        (xt : xtss) -> case xt of
          (HSE_XT.EnableExtension known_ext) -> known_ext : enabledKnownExtensions xtss
          _ -> enabledKnownExtensions xtss

getModuleDeclaredFunctions :: STX.Module l -> [Decl l]
getModuleDeclaredFunctions (STX.Module _ _ _ _ declarations) =
  filter
    ( \decl -> case decl of
        (TypeSig _ _ _) -> True -- FILTER: how to know they are only functions?
        _ -> False
    )
    declarations
getModuleDeclaredFunctions _ = []

getModuleImports :: STX.Module l -> [ModuleName l]
getModuleImports (STX.Module _ _ _ imports _) = map (\idecl -> (importModule idecl)) imports
getModuleImports (XmlPage _ _ _ _ _ _ _) = []
getModuleImports (XmlHybrid _ _ _ imports _ _ _ _ _) = map (\idecl -> (importModule idecl)) imports

getModuleExports :: STX.Module l -> [ExportSpec l]
getModuleExports (STX.Module _ (Just (ModuleHead _ name _ (Just (ExportSpecList _ exports)))) _ _ _) = exports
getModuleExports (STX.Module _ (Just (ModuleHead _ name _ Nothing)) _ _ _) = []
getModuleExports (STX.Module _ Nothing _ _ _) = []

fromRight :: Either String r -> r
fromRight (Right r) = r
fromRight (Left err) = error err

getPackageExtensions :: String -> IO [CABAL_XT.Extension]
getPackageExtensions cabalFile = withFile cabalFile ReadMode $ \handle -> do
  cbl <- hGetContents handle
  let cblPacked = B.pack (cbl)
  let (warnings, result) = DP.runParseResult (DP.parseGenericPackageDescription cblPacked)
  case result of
    Left (_, errors) -> error $ "Parse Error for cabal file: " ++ cabalFile
    Right d -> return $ (extractPackageExtensions d)

extractPackageExtensions :: GenericPackageDescription -> [CABAL_XT.Extension]
extractPackageExtensions d = lexts ++ eexts
  where
    lexts = case (condLibrary d) of
      Nothing -> []
      Just condl -> allExtensions $ libBuildInfo (condTreeData condl)
    eexts =
      ( concatMap
          (\(_, ctree) -> (allExtensions (buildInfo (condTreeData ctree))))
          (condExecutables d)
      )

cabalXTToHSEXT :: CABAL_XT.Extension -> HSE_XT.Extension
cabalXTToHSEXT cext = classifyExtension (display cext)