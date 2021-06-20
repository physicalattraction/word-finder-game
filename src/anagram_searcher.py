import json
import os
from collections import defaultdict
from typing import Dict, List

from utils import get_data_dir
from word_list import WordList

MIN_LENGTH = 3


class AnagramSearcher:
    DEFAULT_ANAGRAM_INDEX_FILE = 'anagram_index.json'

    # Mapping from the letters sorted alphabetically to all possible anagrams
    _anagrams: Dict[str, List[str]] = {}

    def __init__(self, filename: str = DEFAULT_ANAGRAM_INDEX_FILE):
        self.filename = filename

    @property
    def anagrams(self) -> Dict[str, List[str]]:
        if not self._anagrams:
            if os.path.exists(self.anagram_index_file):
                with open(self.anagram_index_file, 'r') as f:
                    self._anagrams = json.loads(f.read())
            else:
                self._anagrams = {}
        return self._anagrams

    @property
    def anagram_index_file(self) -> str:
        """
        Full path to the anagram index file
        """

        return os.path.join(get_data_dir(), self.filename)

    def find_anagrams_for(self, word: str) -> List[str]:
        """
        Find all possible anagrams for the given input string

        >>> anagram_searcher = AnagramSearcher()
        >>> anagram_searcher.find_anagrams_for('HEEL')
        ['HEEL', 'HELE', 'LHEE']
        """

        key = ''.join(sorted(word))
        return self.anagrams.get(key, [])

    def index_anagrams_simple(self, word_list: WordList = None):
        """
        Call this function once to index anagrams
        """

        if not word_list:
            word_list = WordList()

        result = defaultdict(list)
        for word in word_list:
            key = ''.join(sorted(word))
            result[key].append(word)
        with open(self.anagram_index_file, 'w+') as f:
            print(f'Creating/updating file {self.anagram_index_file}')
            f.write(json.dumps(result, indent=4))

        # After writing the file, immediately read it in memory
        with open(self.anagram_index_file, 'r') as f:
            self._anagrams = json.loads(f.read())


if __name__ == '__main__':
    # Run this once to create the index file from the given word list
    # anagram_searcher = AnagramSearcher()
    # anagram_searcher.index_anagrams_simple(word_list=WordList())

    # Example how to search anagrams for a certain string
    # anagram_searcher = AnagramSearcher()
    # print(anagram_searcher.find_anagrams_for('HEEL'))

    # Example how to create smaller anagram index files
    # anagram_searcher = AnagramSearcher(filename='anagram_index_8_letters.json')
    # anagram_searcher.index_anagrams_simple(word_list=WordList(nr_letters=8))
    pass