import itertools
import random
import sys
import time
from statistics import mean
from typing import List, Optional, Set

from anagram_searcher import AnagramSearcher
from utils import clean_word, measure_time
from word_list import WordList


class WordFinder:
    word: str = ''
    anagrams: List[str] = []
    hint_level: int = 0
    guessed_words: Set[str] = set()

    def __init__(self):
        print('Welcome to Word Finder!')

        self.word_list = WordList()
        self.anagram_searcher = AnagramSearcher()

    @property
    def nr_anagrams(self) -> int:
        return len(self.anagrams)

    @property
    def puzzle(self) -> str:
        return ''.join(sorted(self.word))

    def play(self):
        self._reset_game_state()
        game_is_finished = False
        with measure_time() as time_elapsed:
            while not game_is_finished:
                print(f'Your puzzle is {self.puzzle}. You have guessed '
                      f'{len(self.guessed_words)}/{self.nr_anagrams} words. '
                      f'Type H to see the game options.')
                guess = clean_word(input())
                game_is_finished = self._handle_guess(guess)

        self._print_end_stats(time_elapsed)
        self._query_play_again()

    def _reset_game_state(self):
        self._select_word()
        self.guessed_words = set()

        # Since you know the amount of letters of the first word, the first hint shall reveal a letter already
        # Subsequent hints, you don't necessarily know the amount of letters in the next word, so we do not
        # reveal any letter in subsequent hints.
        self.hint_level = 1

    def _handle_guess(self, guess: Optional[str]) -> bool:
        """
        Handle the user input and update the game state accordingly

        :param guess: User input for this turn, cleaned
        :return: Flag indicating whether the game is finished
        """

        if not guess:
            return False
        elif guess == 'B':
            guessed_words_str = ', '.join(sorted(sorted(self.guessed_words), key=len))
            print(f'You have guessed: {guessed_words_str}')
            self._print_word_length_info()
        elif guess == 'H':
            print('B = check which words you have already guessed.\n'
                  'L = get a hint, use multiple times for more revealing hints.\n'
                  'Q = quit the game.')
        elif guess == 'L':
            self._print_hint()
        elif guess == 'Q':
            self._quit()
            # When the user quits, the game is finished
            return True
        elif len(guess) < 3:
            print(f'All words need to be at least 3 letters, you guessed {guess}')
        elif guess in self.guessed_words:
            print(f'You have already guessed the word {guess}')
        elif guess in self.anagrams:
            next_word_for_hint = self._next_word_for_hint(self.guessed_words, self.anagrams)
            self.guessed_words.add(guess)
            if guess == next_word_for_hint and self.hint_level > 0:
                print(f'Correct! {guess} is a valid word. Next hint is reset.')
                self.hint_level = 0
            else:
                print(f'Correct! {guess} is a valid word')
            # When the user correctly guesses the last word, the game is finished
            return len(self.guessed_words) == len(self.anagrams)
        elif all(letter in self.word for letter in guess):
            # TODO: This does not check for too much duplicated letters
            print(f'{guess} is not a valid word')
        else:
            print(f'{guess} cannot be made from {self.puzzle}')
        # In all other cases, the game is finished
        return False

    def _print_end_stats(self, time_elapsed: measure_time):
        if len(self.guessed_words) == self.nr_anagrams:
            guessed_words_str = ', '.join(sorted(self.guessed_words))
            print(f'Congratulations! You found all {self.nr_anagrams} words in {time_elapsed}: {guessed_words_str}')
        else:
            print(f'Total playing time is {time_elapsed}')

    def _query_play_again(self):
        print('Do you want to play again? Y/N')
        while answer := clean_word(input()):
            if answer == 'Y':
                self.play()
            elif answer in {'N', 'Q'}:
                print('Thank you for playing Word Finder!')
                sys.exit()

    def _select_word(self) -> (str, List[str]):
        candidate_words = [word for word in self.word_list if 6 <= len(word) <= 8]
        random.seed(time.time())  # Undo a possible previous seed
        random.shuffle(candidate_words)
        for word in candidate_words:
            min_word_length = 3
            anagrams = self._find_anagrams(word, min_word_length)
            while len(anagrams) > 80:
                if min_word_length == len(word):
                    # This rare event happens when there are basically only 3-letter words as anagrams
                    continue
                min_word_length += 1
                anagrams = self._find_anagrams(word, min_word_length)
            # Only select words with a minimum number of anagrams and where not all anagrams are short
            mean_word_length = mean([len(anagram) for anagram in anagrams])
            if len(anagrams) >= 8 and mean_word_length >= 4:
                # Sort by word length, then alphabetically
                anagrams = sorted(sorted(anagrams), key=len, reverse=True)
                self.word = word
                self.anagrams = anagrams
                self._print_word_length_info()
                return
        raise AssertionError('No word can be selected')

    def _find_anagrams(self, word: str, min_length: int):
        assert min_length <= len(word)
        anagrams = set()
        for nr_letters in range(min_length, len(word) + 1):
            for subword in itertools.combinations(word, nr_letters):
                # noinspection PyTypeChecker
                anagrams |= set(self.anagram_searcher.find_anagrams_for(subword))
        return anagrams

    @staticmethod
    def _next_word_for_hint(guessed_words: Set[str], anagrams: List[str]) -> str:
        for anagram in anagrams:
            if anagram not in guessed_words:
                return anagram

    def _print_hint(self) -> None:
        anagram = self._next_word_for_hint(self.guessed_words, self.anagrams)
        random.seed(anagram)  # Ensure that we reveal the same letters next time
        nr_hidden_letters = len(anagram) - self.hint_level
        positions = range(len(anagram))
        hidden_letter_positions = random.sample(positions, k=nr_hidden_letters)
        hint = ''.join(
            '.' if position in hidden_letter_positions else anagram[position]
            for position in positions
        ) + f' ({len(anagram)})'
        print(hint)
        self.hint_level += 1

    def _print_word_length_info(self):
        min_word_length = min([len(anagram) for anagram in self.anagrams])
        mean_word_length = mean([len(anagram) for anagram in self.anagrams])
        print(f'The min word length for this puzzle is {min_word_length}\n'
              f'The mean word length for this puzzle is {mean_word_length:.2f}')

    def _quit(self) -> None:
        guessed_words_str = ', '.join(sorted(self.guessed_words))
        print(f'You have successfully found: {guessed_words_str}')
        not_found = [word for word in self.anagrams if word not in self.guessed_words]
        not_found_str = ', '.join(not_found)
        print(f'You have not found: {not_found_str}')


if __name__ == '__main__':
    wf = WordFinder()
    wf.play()
