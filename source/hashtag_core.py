import re
import os
from string import ascii_lowercase, digits
import logging
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
        for line in self._get_text(file_path):
            file_name = self._get_file_name(file_path)
            self.hashtags = self._hashtags_from_line(file_name, line)

    def _get_text(self, file_path: str) -> Iterator[str]:
        try:
            with open(file_path, "r", encoding='utf-8') as document:
                for line in document:
                    yield line
        except Exception as e:
            logger.error("File '" + file_path + "' does not exist: " + str(e))

    def _get_file_name(self, file_path):
        return os.path.basename(file_path)

    def _hashtags_from_line(self, file_name: str, line: str) -> dict:
        sentence_counter = 1

        for sentence in self._sentences_from_line(line):
            sentence = self._clean_up_sentence(sentence)
            for word in sentence.split(' '):
                if len(word) >= self.min_word_length:
                    wordmetadata = self.hashtags.get(word, WordMetadata(word))
                    wordmetadata.add_reference_from_document(sentence.strip(), file_name)
                    self.hashtags[word] = wordmetadata

            sentence_counter += 1

        return self.hashtags

    def _sentences_from_line(self, line: str) -> List[str]:
        p = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<!etc\.)(?<=\.|\?)\s')
        return p.split(line)

    def _clean_up_sentence(self, sentence):
        sentence = sentence.lower()
        sentence = self.__remove_period(sentence)
        sentence = self._remove_contractions(sentence)
        sentence = self._remove_unnecessary_dashes(sentence)
        sentence = self._remove_wordless_digits(sentence)
        return self._remove_non_alphanumeric(sentence)

    def __remove_period(self, sentence):
        if len(sentence) > 1 and sentence[-1] == '.':
            sentence = sentence[:-1]
        return sentence

    def _remove_contractions(self, sentence):
        sentence = re.sub(r"(?<!ca)n\'t(?!-)", ' ', sentence)
        sentence = sentence.replace("'ve", "").replace("'d", "").replace("'m", "")
        return sentence.replace("'re", "").replace("'s", "").replace("'ll", "")

    def _remove_unnecessary_dashes(self, sentence):
        sentence = re.sub(r'\s[-]+\s', ' ', sentence)
        return re.sub(r'\s-(\S*)', r' \1', sentence)

    def _remove_wordless_digits(self, sentence):
        return re.sub(r'(\d+)\s*(?!\S)', "", sentence)

    def _remove_non_alphanumeric(self, sentence):
        allowed_chars = ascii_lowercase + digits + '.- '
        return "".join([char for char in sentence if char in allowed_chars]).strip('\n')

    def _add_wordmetadata(self):
        pass

    def get_sorted_hashtags(self):
        return sorted(((metadata['count'], word, metadata) for word, metadata in self.hashtags.items()), reverse=True)

    def reset_hashtags(self) -> None:
        self.hashtags.clear()


if __name__ == "__main__":
    import os
    from os import listdir
    from os.path import isfile, join

    h = Hashtag(6)

    def get_files():
        resources_dir = os.path.join(BASE_DIR, 'resources')
        text_files = [f for f in listdir(resources_dir) if isfile(join(resources_dir, f)) and f.endswith('.txt')]
        return map(lambda f: join(resources_dir, f), text_files)

    for file_path in get_files():
        h.append_to_hashtags(file_path)

    #print(str(h.get_sorted_hashtags()))
    for m in h.hashtags.items():
        print(m)