import re
import os
import logging
from string import ascii_lowercase, digits
from typing import Iterator, List

from word_metadata import WordMetadata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


class Hashtag:
    min_word_length: int
    hashtags: dict

    def __init__(self, min_word_length: int):
        self.min_word_length = min_word_length
        self.hashtags = dict()

    def append_to_hashtags(self, file_path: str) -> None:
        for line in self._get_text_from_file(file_path):
            file_name = self._get_file_name(file_path)
            self._extract_hashtags(file_name, line)

    def _get_text_from_file(self, file_path: str) -> Iterator[str]:
        try:
            with open(file_path, "r", encoding='utf-8') as document:
                for line in document:
                    yield line
        except FileNotFoundError as e:
            logger.error(str(e))

    def _get_file_name(self, file_path) -> str:
        return os.path.basename(file_path)

    def _extract_hashtags(self, file_name: str, line: str) -> None:
        for sentence in self._split_in_sentences(line):
            sentence = self._clean_up_sentence(sentence)
            for word in self._extract_valid_words(sentence):
                metadata = WordMetadata(word)
                metadata.add_reference(sentence, file_name)
                self._add_or_merge_metadata(metadata)

    def _split_in_sentences(self, line: str) -> List[str]:
        p = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<!etc\.)(?<=\.|\?)\s')
        return p.split(line)

    def _clean_up_sentence(self, sentence) -> str:
        sentence = sentence.lower()
        sentence = self._remove_trailing_period(sentence)
        sentence = self._remove_contractions(sentence)
        sentence = self._remove_unnecessary_dashes(sentence)
        sentence = self._remove_wordless_digits(sentence)
        return self._remove_special_characters(sentence).strip()

    def _extract_valid_words(self, sentence) -> List[str]:
        return [word for word in sentence.split(' ') if len(word) >= self.min_word_length]

    def _add_or_merge_metadata(self, metadata: WordMetadata):
        stored_metadata = self.hashtags.get(metadata.word, WordMetadata(metadata.word))
        stored_metadata.merge(metadata)
        self.hashtags[metadata.word] = stored_metadata

    def _remove_trailing_period(self, sentence) -> str:
        if len(sentence) > 1 and sentence[-1] == '.':
            sentence = sentence[:-1]
        return sentence

    def _remove_contractions(self, sentence) -> str:
        sentence = re.sub(r"(?<!ca)n\'t(?!-)", ' ', sentence)
        sentence = re.sub(r"can\'t", 'can', sentence)
        sentence = sentence.replace("'ve", "").replace("'d", "").replace("'m", "")
        return sentence.replace("'re", "").replace("'s", "").replace("'ll", "")

    def _remove_unnecessary_dashes(self, sentence) -> str:
        sentence = re.sub(r'\s[-]+\s', ' ', sentence)
        return re.sub(r'\s-(\S*)', r' \1', sentence)

    def _remove_wordless_digits(self, sentence) -> str:
        return re.sub(r'(\d+)\s*(?!\S)', "", sentence)

    def _remove_special_characters(self, sentence) -> str:
        allowed_chars = ascii_lowercase + digits + '.- '
        return "".join([char for char in sentence if char in allowed_chars]).strip('\n')

    def get_sorted_hashtags(self):
        return sorted(((metadata['count'], word, metadata) for word, metadata in self.hashtags.items()), reverse=True)

    def reset_hashtags(self) -> None:
        self.hashtags.clear()
