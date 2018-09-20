import logging
import unittest

from hashtag_core import Hashtag

logger = logging.getLogger(__name__)


class TestHashtag(unittest.TestCase):
    hashtag: Hashtag

    def setUp(self):
        self.hashtag = Hashtag(0)

    def test_get_text_from_file(self):
        test_file_name = "test_file"
        expected = ["Test file text"]
        self.assertEqual(expected, list(self.hashtag._get_text_from_file(test_file_name)))

    def test_remove_trailing_period(self):
        test_sentence = "Test sentence."
        expected = "Test sentence"

        self.assertEqual(expected, self.hashtag._remove_trailing_period(test_sentence).strip())

    def test_remove_contractions(self):
        test_sentence = " you're, i'm, you've, they're can't don't "
        expected = "you, i, you, they can do"

        self.assertEqual(expected, self.hashtag._remove_contractions(test_sentence).strip())

    def test_remove_unnecessary_dashes(self):
        test_sentence = "Test dashes -- - "
        expected = "Test dashes"
        self.assertEqual(expected, self.hashtag._remove_unnecessary_dashes(test_sentence).strip())

    def test_remove_wordless_digits(self):
        test_sentence = "numbers: 100 2000 "
        expected = "numbers:"
        self.assertEqual(expected, self.hashtag._remove_wordless_digits(test_sentence).strip())

    def test_remove_special_characters(self):
        test_sentence = "?£€&*test special!?~"
        expected = "test special"
        self.assertEqual(expected, self.hashtag._remove_special_characters(test_sentence).strip())

    def test_clean_up_sentence(self):
        test_sentence = "Test sentence -- " \
                        "Contractions: You're, I'm, You've, They're can't don't -- " \
                        "Dashed words: Commander-in-Chief 100-year-old " \
                        "Numbers: 100 2000."
        expected = "test sentence contractions you i you they can do  " \
                   "dashed words commander-in-chief 100-year-old numbers"

        self.assertEqual(expected, self.hashtag._clean_up_sentence(test_sentence))

    def test_split_in_sentences(self):
        test_sentence = "Sentence with titles like Mr. Ms. Jr. etc. should not break. Sentences with question mark? " \
                        "Sentence with elipsis... And also numbers 1.2 and .3 should work."

        expected = ['Sentence with titles like Mr. Ms. Jr. etc. should not break.',
                    'Sentences with question mark?', 'Sentence with elipsis...',
                    'And also numbers 1.2 and .3 should work.']
        self.assertEqual(expected, self.hashtag._split_in_sentences(test_sentence))
