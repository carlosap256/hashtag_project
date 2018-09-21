from typing import List, Set, Dict

import util


class ReferencesPerDocument(object):
    references: Dict[str, List[str]]

    def __init__(self):
        self.references = dict()

    def add_reference(self, reference: str, document: str):
        self._add_references([reference], document)

    def get_all_references(self):
        return self.references

    def _add_references(self, reference: List[str], document: str):
        reference_list = self._get_references_from_document(document)
        reference_list.extend(reference)
        self._set_references_from_document(document, reference_list)

    def _get_references_from_document(self, document: str) -> List[str]:
        return self.references.get(document, list())

    def _set_references_from_document(self, document: str, reference_list: List[str]):
        self.references[document] = reference_list

    def merge(self, reference_per_document):
        self.references = util.merge_two_dicts(self.references, reference_per_document.references)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self.references)


class WordMetadata(object):
    word: str
    count: int
    documents: Set[str]
    references_per_document: ReferencesPerDocument

    def __init__(self, word: str):
        self.word = word
        self.count = 0
        self.documents = set()
        self.references_per_document = ReferencesPerDocument()

    def add_reference(self, reference: str, document: str) -> None:
        self.references_per_document.add_reference(reference, document)

        self.documents.add(document)
        self.count += 1

    def get_references(self):
        return self.references_per_document.get_all_references()

    def merge(self, wordmetadata):
        if self._is_compatible(wordmetadata):
            self.documents = self.documents | wordmetadata.documents
            self.references_per_document.merge(wordmetadata.references_per_document)
            self.count += wordmetadata.count

    def _is_compatible(self, wordmetadata):
        return wordmetadata.word == self.word

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str({'count': self.count,
                    'documents': sorted(list(self.documents)),
                    'references_per_document': str(self.references_per_document)})
