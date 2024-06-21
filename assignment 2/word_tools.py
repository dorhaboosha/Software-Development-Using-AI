###### Our Names and IDs ######
# Moran Herzlinger - 314710500
# Dor Haboosha - 208663534
# Itay Golan - 206480402
#####################

def count_anagrams(text, word):
    res = 0
    word_len = len(word)

    # Create a dictionary to count character occurrences in the word
    word_counter = {}
    for char in word:
        word_counter[char] = word_counter.get(char, 0) + 1

    # Initial count for the first substring
    current_counter = {}
    for char in text[:word_len]:
        current_counter[char] = current_counter.get(char, 0) + 1

    if current_counter == word_counter:
        res += 1

    for i in range(word_len, len(text)):
        # Update the counters by removing the first character and adding the current character
        current_counter[text[i - word_len]] -= 1
        if current_counter[text[i - word_len]] == 0:
            del current_counter[text[i - word_len]]
        current_counter[text[i]] = current_counter.get(text[i], 0) + 1

        # Check if the current substring is an anagram of the word
        if current_counter == word_counter:
            res += 1

    return res
