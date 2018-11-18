import re
from functools import partial
from yaml import load, dump


class Tokenizer(object):
    '''
    This class implements basic tokenizing functions
    '''

    def __init__(self):
        # read all regex from yaml config file
        with open("config.yaml", 'r') as stream:
            self.__dict__.update(load(stream))

        # automatically create function of type 'find_{}' for every defined regular expression
        for reg, value in dict(self.__dict__).items():
            setattr(self, 'find_{}'.format(reg), partial(lambda reg_exp, text: re.findall(reg_exp, text), value))

        self.multi_words = {}
        self.additional = {}

    def tokenize(self, text):
        '''
        Join all regular expressions with | and perform search through given text
        '''
        res_regex = '|'.join([
            self.tel, self.dates,
            self.numerals, self.nums_measure,
            self.measure, self.models,
            self.names, self.names,
            self.short, self.word
        ])

        additional = list(self.additional.values())
        if len(additional) != 0:
            res_regex  = '|'.join(additional) + '|' + res_regex
        return re.findall(res_regex, text)

    def get_models(self):
        '''
        Return dict with all regex models, saved in class object.
        '''
        res = dict()
        for key, value in self.__dict__.items():
            # we don't need functions in our dict
            if type(value) != str: continue
            res[key] = value

        for key, value in self.additional.items():
            res[key] = value

        return res

    def register_regex(self, regex, regex_name):
        '''
        Add new regex to class object and register appropriate find_{} for this expression.
        @regex - regular expression itself
        @regex_name - name for substrings, this regex is searching for (will be used for creating function)
        @save - whether to save it to config file for future use
        '''
        self.additional[regex_name] = regex
        setattr(self, 'find_{}'.format(regex_name), partial(lambda reg_exp, text: re.findall(reg_exp, text), regex))

    def __subfinder(self, mylist, pattern, sep):
        new_list = []
        for i in range(len(mylist)):
            if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == list(pattern):
                new_list = mylist[:i] + [sep.join(pattern)] + mylist[i+len(pattern):]
        return new_list

    def multi_word_tokenize(self, token_list):
        '''
        This takes a string which has already been divided into tokens and
        retokenizes it, merging multi-word expressions into single tokens,
        using a lexicon added through add_multi_word function
        '''
        for key, value in self.multi_words.items():
            for pattern in value:
                tmp_ = self.__subfinder(token_list, pattern, key)
                token_list = token_list if len(tmp_) == 0 else tmp_

        return token_list

    def add_multi_word(self, words_list, separator):
        '''
        This function is used to add combinations of words, that should be recognized
        as one token
        @words_list - list of tuples with words that should be recognized as one token
        @separator - letter or sign that should be used for concatinating words
        '''
        self.multi_words[separator] = self.multi_words.get('-', []) + words_list
