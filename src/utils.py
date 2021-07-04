import os
import os.path
import string
import time
import unicodedata
from typing import List, Optional, TypeVar

from humanfriendly import format_timespan

T = TypeVar('T')


def clean_word(word: str, allowed_chars: str = string.ascii_letters) -> Optional[str]:
    """
    Remove all accents and non-allowed characters from the given word, and uppercase it

    >>> clean_word('Mongolië')
    'MONGOLIE'
    >>> clean_word('100!')
    """

    word = remove_accents(word).upper()
    if any(letter not in allowed_chars for letter in word):
        return None
    return ''.join(letter for letter in word if letter in allowed_chars)


def remove_accents(word: str) -> str:
    """
    Return the same word with all accents removed

    >>> remove_accents('Mongolië')
    'Mongolie'
    """

    nfkd_form = unicodedata.normalize('NFKD', word)
    return u''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def available_elements(*elements: Optional[T]) -> List[T]:
    """
    Return the original positional arguments as a list, with all non-empty values removed from it

    :param elements: positional arguments
    :return List of elements that are in the input arguments that are available

    >>> available_elements(0, 1, 2, None, 3)
    [0, 1, 2, 3]
    >>> available_elements('0', '1', '2', '', 3)
    ['0', '1', '2', 3]
    """

    return [element for element in elements if element not in {None, ''}]


def get_root_dir() -> str:
    """
    Return the root dir of the repository
    """

    return os.path.dirname(os.path.dirname(__file__))


def get_data_dir() -> str:
    """
    Return the data dir of the repository
    """

    return os.path.join(get_root_dir(), 'data')


class measure_time:
    """
    Class, used as a context manager, to measure the time spent within the context.

    After exiting this context, the object variable `seconds` contains the spent time in seconds.

    Typical usage:

    with measure_time() as t:
        do_something_lengthy()
    print('The operation took {} seconds to complete'.format(t.seconds))
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()

    def __str__(self):
        return format_timespan(round(self.total_seconds), max_units=2)

    @property
    def total_seconds(self) -> float:
        """
        Return the time spent since entering the context manager in seconds
        """

        if self.start_time is None:
            raise ValueError('Not started yet')
        end_time = self.end_time or time.time()
        return end_time - self.start_time


if __name__ == '__main__':
    print(available_elements(1, 2, None, 3))
