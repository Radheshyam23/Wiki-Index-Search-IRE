# Phase 1 deals with Parsing, Processing and Indexing - Creating a posting list

The important stages:
- XML Parsing
- Tokenisation
- Case Folding
- Stop Word removal
- Stemming / Lemmatisation
- Inverted Index creation

To run the Indexer:
```
$ bash index.sh <path_to_wiki_dump> <path_to_inverted_index>
```