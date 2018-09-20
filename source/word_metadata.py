from typing import List, Set


class WordMetadata(object):
    word: str
    count: int
    documents: Set[str]
    references: List[str]

    def __init__(self, word: str):
        self.word = word
        self.count = 0
        self.documents = set()
        self.references = list()

    def add_reference(self, reference: str, document: str) -> None:
        self.references.append(reference)
        self.documents.add(document)
        self.count += 1

    def merge(self, wordmetadata):
        if self._is_compatible(wordmetadata):
            self.documents = self.documents & wordmetadata.documents
            self.references.extend(wordmetadata.references)
            self.count += wordmetadata.count

    def _is_compatible(self, wordmetadata):
        return wordmetadata.word == self.word

    def __str__(self):
        return str({'count': self.count,
                'documents': list(self.documents),
                'references': self.references})

    def __repr__(self):
        return self.__str__()
