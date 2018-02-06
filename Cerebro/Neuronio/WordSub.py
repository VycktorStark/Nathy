
try: dict
except: from UserDict import UserDict as dict 

import configparser
import re
import string

class WordSub(dict):

    def _wordToRegex(self, word):
        if word != "" and word[0].isalpha() and word[-1].isalpha():
            return "\\b%s\\b" % re.escape(word)
        else: 
            return r"\b%s\b" % re.escape(word)
    
    def _update_regex(self):
        self._regex = re.compile("|".join(map(self._wordToRegex, list(self.keys()))))
        self._regexIsDirty = False

    def __init__(self, defaults = {}):
        self._regex = None
        self._regexIsDirty = True
        for k,v in list(defaults.items()):
            self[k] = v

    def __call__(self, match):
        """Handler invoked for each regex match."""
        return self[match.group(0)]

    def __setitem__(self, i, y):
        self._regexIsDirty = True
        super(type(self),self).__setitem__(i.lower(),y.lower())
        super(type(self),self).__setitem__(string.capwords(i), string.capwords(y)) 
        super(type(self),self).__setitem__(i.upper(), y.upper()) 

    def sub(self, text):
        if self._regexIsDirty:
            self._update_regex()
        return self._regex.sub(self, text)
if __name__ == "__main__":
    subber = WordSub()
    subber["apple"] = "banana"
    subber["orange"] = "pear"
    subber["banana" ] = "apple"
    subber["he"] = "she"
    subber["I'd"] = "I would"

    # test case insensitivity
    inStr =  "I'd like one apple, one Orange and one BANANA."
    outStr = "I Would like one banana, one Pear and one APPLE."
    if subber.sub(inStr) == outStr: print("Test #1 PASSED")    
    else: print("Test #1 FAILED: '%s'" % subber.sub(inStr))

    inStr = "He said he'd like to go with me"
    outStr = "She said she'd like to go with me"
    if subber.sub(inStr) == outStr: print("Test #2 PASSED")    
    else: print("Test #2 FAILED: '%s'" % subber.sub(inStr))
