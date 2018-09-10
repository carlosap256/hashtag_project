from source import hashtag_core


class TestHashtagCore:

    def test_clean_sentence(self):
        test_sentence = "Test sentence -- " \
                        "Contractions: You're, I'm, You've, They're can't don't -- " \
                        "Dashed words: Commander-in-Chief 100-year-old " \
                        "Numbers: 100 2000."
        expected_sentence = "test sentence contractions you i you they cant do  " \
                            "dashed words commander-in-chief 100-year-old numbers"

        assert hashtag_core.clean_sentence(test_sentence) == expected_sentence

    def test_line_splitter(self):
        test_sentence = "Sentence with titles like Mr. Ms. Jr. etc. should not break. Sentences with question mark? " \
                        "Sentence with elipsis... And also numbers 1.2 and .3 should work."

        expected_array = ['Sentence with titles like Mr. Ms. Jr. etc. should not break.',
                          'Sentences with question mark?', 'Sentence with elipsis...',
                          'And also numbers 1.2 and .3 should work.']
        assert hashtag_core.line_splitter(test_sentence) == expected_array

