# Wiki-Index-Search

This is a scalable and efficient search engine on Wikipedia pages. Through this project, we explore 'index creation', 'ranking' and 'searching' of the large corpus of Wikipedia pages.


The Indexing Section of the project involves the following tasks:

- XML Parsing
- Tokenisation
- Case Folding
- Stop Word removal
- Stemming / Lemmatisation
- Inverted Index creation

While parsing, the information in the wikipedia files is classified into different fields - Title, infobox, references, etc. Hence, this will enable the user to search with keywords in these specific fields.

['Phase-1'](./Phase%201/) deals with the indexing portion of the project. We used the NLTK library for text processing. 

The final wikipedia data corpus which we indexed was over 90 GB in size. Hence, we needed to optimise the indexer further to reduce space and improve the indexing time. This is the optimised version of the indexer: [`Indexer`](./Phase%202/Indexer.py).

The code for the Searcher is implemented in [`Searcher`](./Search.py)

The Searcher can handle field queries. The ranking of the documents is decided by their TF-IDF scores.