#!/usr/local/bin/python
import re

#arffObj is used to work with clean parsed tweets to extract features
class arffObj:

  # which ".twt" files are used with this arffObj
  twtArray = []
  # the number of tweets to parse from ".twt" files
  toParse = 0
  # class name
  name = ""

  # dirtyTwts are passed in the format "aaa.py+bbb.py+....+zzzz.py", we will need to split this array and assign
  # it to twtArray
  def __init__(self, encodedString, numParse): 
    self.decodeString(encodedString)
    self.toParse = numParse

  # Callback for regular expression, substitutes each value with a regex that would accept a capital or lower case version
  # e.g. calling Regex with "Hello" would return "[Hh][Ee][Ll][Ll][Oo]"
  def makeRegex(self, string):
    return '[' + string.group(1).upper() + string.group(1).lower() + "]"


  # decodes a string
  # private function
  def decodeString(self, encodedString):
    # the ":" character indicates that the preceding word is the object name, if it doesn't exist we are going
    # to have to create our own name 
    if ":" in encodedString: 
      encodedString = encodedString.split(":")
      # everything before the ":" is the name
      self.name = encodedString[0]
      # everything after the ":" is the rest of the encodedString
      encodedString = encodedString[1]
    else:
      #if we get here, we need to create our own name
      # we will use the names of the .twt file to name them, if there are multiple .twt files then
      # we will seperate by 'AND'
      self.name = re.sub(r"\.twt\+",r"AND",encodedString)
      # remove the trailing .twt
      self.name = re.sub(r"\.twt", "", self.name)

    self.twtArray = encodedString.split("+")

  # the .twt files will have have each tweet seperated by the "|" character, so we store the the tweet in a buffer
  # until we hit a line which consists of "|", in which case we know the tweet has ended
  def parseTweet(self, outputfile):
    # there are many Slang words, we will use the provided slang file to help with parsing
    slangArray = []
    with open ('/u/cs401/Wordlists/Slang') as slangFile:
      # THE FOLLOWING LINE IS TAKEN FROM STACKOVERFLOW TO NOT INCLUDE NEW LINE CHARACTERS
      slangArray = slangFile.read().splitlines()

    # we notice that every slang term is lowercase, we need to create valid regex expressions
    slangArray = [re.sub(r"(\w)", self.makeRegex, slang) for slang in slangArray]
    #we have an array of slang, lets join it now with the | symbol so we can use it with regex
    slangRegex = "|".join(slangArray)
    # they provided text file has trailing \n characters which in turn genreate extra "|" characters.
    # It would be best to remove the trailing "|" characters
    slangRegex = re.sub(r"\|[\|]+", "", slangRegex)
    #we also need to add word boundaries, so slang such as "k" does not set off for each "k" character
    slangRegex = re.sub(r"\[([^\|]+)\]", r"\\b[\1]\\b", slangRegex)
    
    buf = ""

    # check if we need to read a predefined amount of tweets or the whole file
    readFull = (self.toParse == -1)

    # count will be used to keep track of how many tweets we read
    count = 0
    # attArray will be an array of the numeric values of the attributes
    attArray = []

    outputFile = open(outputfile, 'a')

    for twt in self.twtArray:
      twtFile = open(twt, 'r')
      line = twtFile.readline()
      # we need to check whether we are reading the all of the tweets or a pre defined amount
      while line and (readFull or count < self.toParse):
        # we will push to the buffer until we have a full tweet, in which case we shall count our features
        line = line.rstrip('\n')
        if line == "|":
          # do feature counting
          attArray.append(self.countFPPronouns(buf))
          attArray.append(self.countSPPronouns(buf))
          attArray.append(self.countTPPronouns(buf))
          attArray.append(self.countConjunct(buf))
          attArray.append(self.countPastTenseVerb(buf))
          attArray.append(self.countFutureTenseVerb(buf))
          attArray.append(self.countComma(buf))
          attArray.append(self.countColon(buf))
          attArray.append(self.countDash(buf))
          attArray.append(self.countParentheses(buf))
          attArray.append(self.countEllipsis(buf))
          attArray.append(self.countCommonNoun(buf))
          attArray.append(self.countProperNoun(buf))
          attArray.append(self.countAdverb(buf))
          attArray.append(self.countWhWord(buf))
          attArray.append(self.countSlang(buf, slangRegex))
          attArray.append(self.countUpper(buf))
          attArray.append(self.avgLengthSentence(buf))
          attArray.append(self.avgLengthToken(buf))
          attArray.append(self.numSent(buf))
          attArray.append(self.name)

          # we have an array of ints, but we need to convert them to strings before we can join
          attString = ",".join(map(str,attArray))
          outputFile.write(attString + "\n")
          
          
          attArray = []
          buf = ""
          count = count + 1
        else:
          # push to the buffer but exlude empty lines
          if len(line) > 0:
            buf = buf + " " + line

        line = twtFile.readline()

  # counts the number of first person pronouns
  # returns the number of pronouns
  # (str) -> (int)
  def countFPPronouns(self, buf):
    # split on common pronouns,
    # then return the amount of subsections we have -1, we will also take into the case where they words may be all capitalized
    pattern = r"\b[Ii]\b|\b[WwMm][Ee]\b|\b[Uu][Ss]\b|\b[Mm][Yy]\b|\b[Oo][Uu][Rr][Ss]?\b|"
    split = re.split(pattern, buf) 
    return len(split) -1

  # counts the number of second person pronouns
  # returns the number of pronouns
  # (str) -> (int)
  def countSPPronouns(self, buf):
    pattern = r"\b[Yy][Oo][Uu]\b|\b[Yy][Oo][Uu][Rr][Ss]?\b|\b[Uu]\b|\b[Uu][Rr][Ss]?\b"
    split = re.split(pattern, buf)
    return len(split) - 1
  
  # counts the number of third person pronouns
  # returns the number of pronouns
  # (str) -> (int)
  def countTPPronouns(self, buf):
    pattern = r"\b[Ss]?[Hh][Ee]\b|[Hh][Ii][MmSs]\b|\b[Hh][Ee][Rr][Ss]?\b|\b[Ii][Tt][Ss]?\b|\b[Tt][Hh][Ee][YyMm]\b|\b[Tt][Hh][Ee][Ii][Rr][Ss]?\b"
    split = re.split(pattern, buf) 
    return len(split) - 1

  # counts the number of Coordinating conjunctions
  # returns the number of Coordinating conjunctions
  # (string) -> (int)
  def countConjunct(self,buf):
    #this is messy because there are lots of cases
    # WARNING: BEFORE LOOKING AT THIS MAKE SURE YOU WEAR PROTECTIVE EYEWARE (May cause eye damage)
    pattern = r"\b[Aa][Ll][Tt][Oo][Gg][Ee][Tt][Hh][Ee][Rr]\b|"\
    r"\b[Aa][Ll][Tt][Ee][Rr][Nn][Aa][Tt][Ii][Vv][Ee][Ll][Yy]\b|"\
    r"\b[Aa][Ll][Tt][Oo][Gg][Ee][Tt][Hh][Ee][Rr]\b|"\
    r"\b[Cc][Oo][Nn][Ss][Ee][Qq][Uu][Ee][Nn][Tt][Ll][Yy]\b|"\
    r"\b[Cc][Oo][Nn][Vv][Ee][Rr][Ss][Ee][Ll][Yy]\b|" \
    r"\b[Ee].[Gg].|" \
    r"\b[Ee][Ll][Ss][Ee]\b|" \
    r"\b[Ff][Uu][Rr][Tt][Hh][Ee][Rr][Mm][Oo][Rr][Ee]\b|" \
    r"\b[Hh][Ee][Nn][Cc][Ee]\b|" \
    r"\b[Hh][Oo][Ww][Ee][Vv][Ee][Rr]\b|" \
    r"\b[Ii].[Ee].|" \
    r"\b[Ii][Nn][Ss][Tt][Ee][Aa][Dd]\b|" \
    r"\b[Ll][Ii][Kk][Ee][Ww][Ii][Ss][Ee]\b|" \
    r"\b[Mm][Oo][Rr][Ee][Oo][Vv][Ee][Rr]\b|" \
    r"\b[Nn][Aa][Mm][Ee][Ll][Yy]\b|" \
    r"\b[Nn][Ee][Vv][Ee][Rr][Tt][Hh][Ee][Ll][Ee][Ss][Ss]\b|" \
    r"\b[Nn][Oo][Nn][Ee][Tt][Hh][Ee][Ll][Ee][Ss][Ss]\b|" \
    r"\b[Nn][Oo][Tt][Ww][Ii][Tt][Hh][Ss][Tt][Aa][Nn][Dd][Ii][Nn][Gg]\b|" \
    r"\b[Oo][Tt][Hh][Ee][Rr][Ww][Ii][Ss][Ee]\b|" \
    r"\b[Rr][Aa][Tt][Hh][Ee][Rr]\b|" \
    r"\b[Ss][Ii][Mm][Ii][Ll][Aa][Rr][Ll][Yy]\b|" \
    r"\b[Tt][Hh][Ee][Rr][Ee][Ff][Oo][Rr][Ee]\b|" \
    r"\b[Tt][Hh][Uu][Ss]\b|" \
    r"\b[Vv][Ii][Zz]\."
    split = re.split(pattern, buf)
    return len(split) - 1 

  # counts the number of Past tense verbs
  # returns the number of past tense verbs
  # (str) -> (int)
  def countPastTenseVerb(self, buf):
    pattern = r"/VB[DN]"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of future tense verbs
  # returns the number of future tense verbs
  # (str) -> (int)
  def countFutureTenseVerb(self, buf):
    pattern = r"'[Ll][Ll]\b|\b[Ww][Ii][Ll][Ll]\b|\b[Gg][Oo][Ii][Nn][Gg]\b\s+[Tt][Oo]\b\s+\w+/VB\b|\b[Gg][Oo][Nn][Nn][Aa]\b"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of commas
  # returns the number of commas
  # (str) -> (int)
  def countComma(self, buf):
    pattern = r"[^/],"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of colons and semi colons
  # returns the number of colons and semi colons
  # (str) -> (int)
  def countColon(self, buf):
    pattern = r"[^/][;:]"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the nubmer of dashes
  # returns the number of dashes
  # (str) -> (int)
  def countDash(self, buf):
    pattern = r"-"
    split = re.split(pattern, buf) 
    return len(split) - 1

  # counts the number of Parentheses
  # returns the number of Parentheses
  # (str) -> (int)
  def countParentheses(self, buf):
    pattern = r"[^/]\(|[^/]\)"
    split = re.split(pattern, buf) 
    return len(split) - 1

  # counts the number of ellipsis
  # returns the number of ellipes
  # (str) -> (int)
  def countEllipsis(self, buf):
    pattern = r"\.\.\.[\.]*"
    split = re.split(pattern, buf) 
    return len(split) - 1

  # counts the number of common nouns
  # returns the number of common nouns
  # (str) -> (int)
  def countCommonNoun(self, buf):
    pattern = r"/NNS?"
    split = re.split(pattern, buf)
    return len(split) - 1
  
  # counts the number of proper nouns
  # returns the number of proper nouns
  # (str) -> (int)
  def countProperNoun(self, buf):
    pattern = r"/NNPS?"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of adverbs
  # returns the number of adverbs
  # (str) -> (int)
  def countAdverb(self, buf):
    pattern = r"/RB[RS]?"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of "wh" words
  # returns the number of "wh" words
  # (str) -> (int)
  def countWhWord(self, buf):
    pattern = r"/WDT|/WP|/WP$|/WRB"
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of slang occurances
  # returns the number of slang occurances
  # (str, str) -> (int)
  def countSlang(self, buf, pattern):    
    split = re.split(pattern, buf)
    return len(split) - 1

  # counts the number of uppercase words
  # returns the number of upper cased words (those of 2 or more length)
  # (str) -> (int)
  def countUpper(self, buf):
    pattern = r"\s[A-Z][A-Z]+\b"
    split = re.split(pattern, buf)
    return len(split) - 1
  
  # counts average sentence length
  # returns the average sentence length
  # (str) -> (int)
  def avgLengthSentence(self, buf):
    pattern = r"/\.|/\?|/!"
    lengths = 0 
    split = re.split(pattern, buf)
    
    # We must account for the cases of a sentence ending with a /. token and when a tweet didn't include
    # the final "." i.e. "Hello there. I am writing this ." and "Hello there. I am writing this" to both be considered
    # as 2 sentences, i.e the trailing "." character of the first example does not generate an extra sentence
    # white space will also be counted as a token
    split = filter(None, split)
    
    # We want to avoid the division by 0 case
    if len(split) == 0:
      return 0

    # we don't want to include the tags when calculating length
    split = [re.sub(r"/[^\b]+", "", sentence) for sentence in split]
    # now we split each into tokens (words)
    split = [sentence.split() for sentence in split]
    # this is based off an example from a STACKOVERFLOW post
    lengths = [len(i) for i in split]
    return sum(lengths)/len(lengths)

  # counts the average length of tokens (excluding punctation
  # returns thens the average length of the tokesn
  # (str) -> (int)
  def avgLengthToken(self, buf): 
    # remove all punctation
    # remove tags
    split = re.sub(r"/\S+", "", buf)
    split = re.sub(r"(\.|\?|!|,|\"|'|\(|\)|\$|#)+", r"", split)
         
    # we can now split into tokens
    split = split.split()

    if len(split) == 0:
      return 0
 
    return sum(len(token) for token in split)/len(split)

  # counts the number of sentences
  # returns the number of sentences
  # (str) -> (int)
  def numSent(self, buf):
    pattern = r"!/!|\./\.|\?/\?|$" 

    split = re.split(pattern, buf)
    split = filter(None, split)
    return len(split)

