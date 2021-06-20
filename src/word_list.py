import os
import string
from typing import Iterator

from utils import available_elements, clean_word, get_data_dir


class WordList:
    DEFAULT_WORD_LIST = 'dutch_words'

    def __init__(self, word_list: str = None, nr_letters: int = 0):
        """
        Initialize the given word list

        :param word_list: Specify the word list to load. By default, use all Dutch words
        """

        if word_list is None:
            word_list = self.DEFAULT_WORD_LIST
        filename = f'{word_list}.txt'
        with open(os.path.join(get_data_dir(), filename), 'r') as f:
            if nr_letters:
                self._words = [word.replace('\n', '').upper() for word in f if len(word) == nr_letters + 1]
            else:
                self._words = [word.replace('\n', '').upper() for word in f]

    def __len__(self) -> int:
        return len(self._words)

    def __iter__(self) -> Iterator[str]:
        yield from self._words

    def __getitem__(self, item: int) -> str:
        return self._words[item]

    @staticmethod
    def clean_original(filename_in: str, filename_out: str,
                       allowed_chars: str = string.ascii_letters):
        """
        Run this function once to clean an original file of words, and save it as another file

        Cleaning consists of:
        - Replace all non-ASCII letters with decent letters
        - Remove all punctuation
        - Uppercase all words
        - Remove duplicates

        :param filename_in: Filename to read the original from and clean
        :param filename_out: Filename to write the cleaned version to
        :param allowed_chars: Only keep words with the given characters. All words that have any other
                              character (after removing accents) are not included in the final list.
        """

        with open(os.path.join(get_data_dir(), filename_in), 'r') as f:
            original_words = [word.replace('\n', '') for word in f]
        cleaned_words = sorted(available_elements(*{clean_word(word, allowed_chars)
                                                    for word in original_words}))
        with open(os.path.join(get_data_dir(), filename_out), 'w') as f:
            f.write('\n'.join(cleaned_words))


if __name__ == '__main__':
    # This is how to clean a new list of words
    WordList.clean_original('dutch_words_original.txt', 'dutch_words.txt')

    # Example how to count the number of 13 letter words
    wl_13 = WordList(nr_letters=13)
    print(f'There are {len(wl_13)} words with 13 letters')
