--------------------------------------------------------------------------------
{-# LANGUAGE OverloadedStrings #-}
--------------------------------------------------------------------------------

import           Text.Pandoc.JSON
import           Text.Pandoc.Builder
  ( text
  , setMeta )
import           Text.CSL.Pandoc
  ( processCites' )
import           Control.Arrow
  ( second )
import qualified Data.Map as M

--------------------------------------------------------------------------------

main :: IO ()
main = toJSONFilter multiBibs

multiBibs :: Pandoc -> IO Pandoc
multiBibs doc = processCites'
              . setMeta "suppress-bibliography"
                        (MetaBool True)
              . (\ (Pandoc m _) (Pandoc _ d') -> Pandoc m d') doc
            =<< foldl addBib (return doc) (getBibs doc)

addBib :: IO Pandoc -> (String, Block) -> IO Pandoc
addBib doc (bibFile, header)
    = processCites'
    . addBlock header
    . setMeta "bibliography"
              (text bibFile)
  =<< doc
  where
    addBlock x (Pandoc m b) = Pandoc m (b ++ [x])

getBibs :: Pandoc -> [(String, Block)]
getBibs (Pandoc m _)
    = maybe [] (metaMap toEntry)
    $ lookupMeta "bibliographies" m
  where
    metaMap f (MetaList x) = map f x
    metaMap _ _ = error "'bibliographies' yaml key incorrectly formatted"

    toEntry (MetaMap x) = second toHeader
                        $ head
                        $ M.toList x
    toEntry _ = error "'bibliographies' yaml key incorrectly formatted"

    toHeader (MetaInlines x) = Header 1 nullAttr x
    toHeader _ = error "'bibliographies' yaml key incorrectly formatted"

--------------------------------------------------------------------------------
