def sentences(s):
    try: s+""
    except: raise TypeError("s must be a string")
    pos = 0
    sentenceList = []
    l = len(s)
    while pos < l:
        try: p = s.index('.', pos)
        except: p = l+1
        try: q = s.index('?', pos)
        except: q = l+1
        try: e = s.index('!', pos)
        except: e = l+1
        end = min(p,q,e)
        sentenceList.append( s[pos:end].strip() )
        pos = end+1
    if len(sentenceList) == 0: sentenceList.append(s)
    return sentenceList
if __name__ == "__main__":
    sents = sentences("First.  Second, still?  Third and Final!  Well, not really")
    assert(len(sents) == 4)
