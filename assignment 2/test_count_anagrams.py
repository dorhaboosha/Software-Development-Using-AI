###### Our Names and IDs ######
# Moran Herzlinger - 314710500
# Dor Haboosha - 208663534
# Itay Golan - 206480402
#####################

import pytest
from word_tools import count_anagrams
import time


@pytest.mark.parametrize("text, word, expected", [
    #("", "", 1),
    ("forxxorfxdofr", "for", 3),
    ("fo rxxorfxdofr", "for", 2),
    ("cat", "cattac", 0),
    ("banana", "anna", 2),
    ("race", "car", 1),
    ("aabaabaa", "aaba", 4),
    ("silent", "listen", 1),
    ("debit card", "bad credit", 1),
    ("", "abc", 0),
    ("a", "a", 1),
])

def test_count_anagrams(text, word, expected):
    assert count_anagrams(text, word) == expected

def test_count_anagrams_time():
    start = time.time()
    for _ in range(1000):
        assert count_anagrams(
            'thisisalongtestcasewithlotsofcharactersandwordsthathavedifferentanagramsbutitshouldworkfine',
            'anagrams') == 1
    end = time.time()
    print(f"\n{end - start}")
    assert end - start < 0.34  # This is the time it took before improvement