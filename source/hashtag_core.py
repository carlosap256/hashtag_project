import re
import os
from string import ascii_lowercase, digits
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger = logging.getLogger(__name__)


def clean_sentence(sentence):
    """
    Returns the sentence with only lowercase characters and spaces, and strips any contractions
    :param sentence:
    :return:
    """
    if len(sentence) > 1 and sentence[-1] == '.':
        sentence = sentence[:-1]

    allowed_chars = ascii_lowercase + digits + '.- '
    sentence = sentence.lower()

    sentence = re.sub(r"(?<!ca)n\'t(?!-)", ' ', sentence)
    sentence = sentence.replace("'ve", "").replace("'d", "").replace("'m", "")
    sentence = sentence.replace("'re", "").replace("'s", "").replace("'ll", "")

    """
        Take into account dashed words like fuel-efficient as a single word, but remove leading dash
        For example "-they"
    """
    sentence = re.sub(r'\s[-]+\s', ' ', sentence)
    sentence = re.sub(r'\s-(\S*)', r' \1', sentence)

    """
        Remove digits that do not belong to a word, like "105-year-old"
    """
    sentence = re.sub(r'(\d+)\s*(?!\S)', "", sentence)

    return "".join([char for char in sentence if char in allowed_chars]).strip('\n')


def line_splitter(line_):
    """
    Returns an array with sentences from a line, by grouping with a regular expression instead of
    splitting by the character '.' to avoid splitting things like "U.S."
    :param line_:
    :return:
    """
    p = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<!etc\.)(?<=\.|\?)\s')
    return p.split(line_)


def update_word_metadata(metadata, document, sentence):
    """
    Increments the counter for the instances of the word, and adds the corresponding sentence
    :param metadata:
    :param document:
    :param sentence:
    :return:
    """
    metadata['count'] = metadata['count'] + 1
    word_references = metadata['references']
    sentence_in_document = word_references.get(document, [])
    sentence_in_document.append(sentence)
    word_references[document] = sentence_in_document

    metadata['references'] = word_references


def word_metadata_from_line(document_name, line_, word_metadata, min_word_length):
    sentence_counter = 1

    for sentence in line_splitter(line_):

        for word in clean_sentence(sentence).split(' '):
            if len(word) >= min_word_length:

                if word not in word_metadata.keys():
                    word_metadata[word] = {'count': 1,
                                           'references': {document_name: [sentence.strip('\n')]}
                                           }
                else:
                    update_word_metadata(word_metadata[word], document_name, sentence.strip('\n'))
        sentence_counter += 1

    return word_metadata


def get_hashtags_from_files(file_list, min_word_length):
    """
    Returns a dictionary with the metadata including the word, counter for instances and the sentences
    :param file_list:
    :return:
    """
    word_metadata = dict()

    for filename in file_list:

        with open(filename, "r", encoding='utf-8') as document:
            line_counter = 1

            for line in document:

                word_metadata = word_metadata_from_line(filename, line, word_metadata, min_word_length)
                line_counter += 1

    return word_metadata


def sort_metadata(word_metadata):
    return sorted(((metadata['count'], word, metadata) for word, metadata in word_metadata.items()), reverse=True)

