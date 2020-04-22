#!/usr/bin/env python3

"""Create english-like nonsense words to announce "fresh drip"

The generation of English-like words
is based on the concepts in Wordle by Paul Crovella
Word length, bigram and trigram JSON files are cloned from Wordle,
used under the Apache 2.0 license.
https://github.com/pcrov/Wordle

Python port of Wordle functions and other code by
Mark Boszko

Start development: 2016-08-24
Added class:       2017-06-21
"""

import json
import logging
import os
import random
import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class DripWords(object):
    """
    DripWords includes methods to create the random english-like words 
    """

    def fill_word(self, word, length, trigrams):
        """Fill in the end of the word, using trigrams
        """
        while len(word) < length:
            _tail = word[-2:]
            logging.debug('_tail: ' + str(_tail))
            if _tail in trigrams.keys():
                word = word + self.dict_weighted_rand(trigrams[_tail])
            else:
                return word
        return word

    def return_trigram_letter(self, word, trigrams):
        """return a single letter addable to the word, using trigrams
        """
        _tail = word[-2:]
        logging.debug('_tail: ' + str(_tail))
        if _tail in trigrams.keys():
            return self.dict_weighted_rand(trigrams[_tail])
        else:
            return False

    @staticmethod
    def confirm_trigram_letter(word, trigrams, letter):
        """add a single letter to the word, using trigrams
        IF it matches the letter specified
        """
        _tail = word[-2:]
        logging.debug('_tail: ' + str(_tail))
        if _tail in trigrams.keys() and letter in trigrams[_tail].keys():
            return True
        else:
            return False

    def single_syllable_word(self, bigrams, start, length, trigrams, end='0'):
        """Create a word, using bigrams and trigrams.
        Make the end of the word match a set character.
        NOTE: Assumes that the
        :param bigrams: dictionary
        :param start: character
        :param length: int
        :param trigrams: dictionary
        :param end: character
        :return _word: string
        """

        _used = ""
        _letter = ""
        _word = self.start_with_letter(bigrams, start)

        if end == '0':
            _word = self.fill_word(_word, length, trigrams)
        else:
            end = end.upper()
            _word = self.fill_word(_word, length - 1, trigrams)

            while len(_word) < length:
                if self.confirm_trigram_letter(_word, trigrams, end):
                    # the desired end character is available
                    _word = _word + end
                else:
                    # the desired end character is not available, so
                    # step back one letter and try a different branch
                    _used = _used + _word[-1:]
                    _word = _word[:-2]
                    while True:
                        _letter = self.return_trigram_letter(_word, trigrams)
                        if isinstance(_letter, bool):
                            # this should check if the _letter is a bool, but
                            # FIXME: Why the hell is this ever a bool?
                            break
                        elif _letter not in _used:
                            # FIXME: This could result in an infinite loop
                            # FIXME: Also, there seems to be a bool in this comparison sometimes?
                            # Traceback (most recent call last):
                            #   File "freshdrip.py", line 211, in <module>
                            #     print(drip.fresh_drip())
                            #   File "freshdrip.py", line 195, in fresh_drip
                            #     drip = self.single_syllable_word(bigrams, 'd', length, trigrams, 'p')
                            #   File "freshdrip.py", line 105, in single_syllable_word
                            #     if _letter not in _used:
                            # TypeError: 'in <string>' requires string as left operand, not bool
                            break
                    _word = _word + _letter
        return _word

    @staticmethod
    def dict_weighted_rand(dictionary):
        """Weighted random selection for dictionaries
        """
        total_weight = 0
        for key, weight_str in dictionary.items():
            weight = int(weight_str)
            if weight < 0:
                raise ValueError('Weights cannot be negative.')
            total_weight += weight
        if total_weight == 0:
            raise ValueError('Total weight must exceed zero.')

        rand = random.randrange(1, total_weight + 1)
        for key, weight_str in dictionary.items():
            weight = int(weight_str)
            rand -= weight
            if rand <= 0:
                return key

    def start_with_letter(self, _bigrams, _letter):
        """Weighted random selection of start bigram,
        filtered to start with a specific letter
        """
        _letter_bigrams = {}
        _letter = _letter.upper()
        logging.debug(_letter)
        for _bigram, _weight in _bigrams.items():
            if _letter == _bigram[0]:
                _letter_bigrams[_bigram] = _weight
        logging.debug(_letter_bigrams)
        return self.dict_weighted_rand(_letter_bigrams)

    @staticmethod
    def list_weighted_rand(_list):
        """Weighted random selection for dictionaries:
        """
        total_weight = 0
        for weight in _list:
            if weight < 0:
                raise ValueError('Weights cannot be negative.')
            total_weight = total_weight + weight
        if total_weight == 0:
            raise ValueError('Total weight must exceed zero.')

        rand = random.randrange(1, total_weight + 1)
        list_index = 0
        for weight in _list:
            rand = rand - weight
            if rand <= 0:
                return list_index
            list_index += 1

    def fresh_drip(self):
        """
        Let's make some words!
        
        Make two words, one starting with "f",
        the other starting with "d" and ending with "p"
        """
        freshdrip_dir = os.path.dirname(__file__)
        with open(os.path.join(freshdrip_dir, 'data/distinct_word_lengths.json')) as lengths_file:
            lengths = json.load(lengths_file)
        with open(os.path.join(freshdrip_dir, 'data/word_start_bigrams.json')) as bigrams_file:
            bigrams = json.load(bigrams_file)
        with open(os.path.join(freshdrip_dir, 'data/trigrams.json')) as trigrams_file:
            trigrams = json.load(trigrams_file)

        # Can limit here with an end slice, but this won't work for a start slice
        length = self.list_weighted_rand(lengths[:7])
        fresh = self.single_syllable_word(bigrams, 'f', length, trigrams)

        length = self.list_weighted_rand(lengths[:7])
        drip = self.single_syllable_word(bigrams, 'd', length, trigrams, 'p')

        # Convert word to lower case and combine
        fresh_drip_phrase = fresh.title() + " " + drip.lower() + "."

        logging.debug("Fresh Drip Bot says, “" + fresh_drip_phrase + "”")
        return fresh_drip_phrase


if __name__ == "__main__":
    for i in range(0, 10):
        drip = DripWords()
        print(drip.fresh_drip())
