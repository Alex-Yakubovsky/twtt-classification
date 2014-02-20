#!/usr/local/bin/python
import re
import sys
#sys.path.append("/u/cs401/A1/tagger")
import NLPlib

# (string) -> (string)
# Removes the html tags and attributes from the input value
def removeHtml(text):
	#text = re.sub('<\w.\1>', '', text
	text = re.sub('<\\\\?[^>]+>', '', text)
	return text


# (string) -> (string)
# Removes any url from the input value
def removeUrl(text):
	text = re.sub('((http)|(www))\S*', '', text)

	return text

# (string) -> (string)
# Removes first character in Twitter user names (@ and #)
def removeTags(text):
       	text = re.sub(r"(\A|\s)(@|#)(\w+)", r"\1\3", text)
        return text

# (string) -> (string)
# Splits sentences with a new line character
# seperates multiple punctuations with a word it may be concatinated with, for example;
# "What happened????" will return "What happened ????"

def splitPunctuation(text):
         
         # Check for common words that are followed by a name e.g; "Mr.", "Mrs." "Prof." and substitue "." with our own tag
         # which we will later replace back with a "." to safe gaurd from mistaking as a start of sentence
         text= re.sub(r"(([Dd]r)|([Mm]rs?)|([Pp]rof)|([Jj]r))\.",r"\1\SAFEDOT", text)
         
         # space out the punctation, punctation that shouldn't be split will be safe since it has been replaced
         # by "SAFEDOT" place holder
         text = re.sub(r"(\w)([\?.\!,:;\"\'$#])\1*", r"\1 \2 ", text) 

         # check that there there is a preceding space after a ".", so phrases like "e.g" do not get cut
         # Check that the next following letter is capitalized to take of abbreviaitions like "etc." or "Jr." most of the time
         
         text = re.sub(r"([\.\!\?])\s*([A-Z])", r"\1 \n\2", text)
         
         
         #return \SAFEDOT back to "." 
         text = re.sub(r"\\SAFEDOT\.?", ".", text);
         return text


# (string) -> (string)
# Seperates possessive and clitic apostrophes, e.g; "can't" becomes "ca n't" and 
# "Jim's scarf" becomes "Jim 's scarf"
def spaceCliticPossessiveApostrophe(text):
  text = re.sub(r"((n't)|('s)|('ve))", r" \1", text)
  return text

def cleanTweet(text):
  text = removeHtml(text)
  text = removeUrl(text)
  text = removeTags(text)
  text = spaceCliticPossessiveApostrophe(text)
  text = splitPunctuation(text)
  text = re.split(r"(\s)", text)
  return text



if __name__ == "__main__":
   
  tweetCorpus = open(sys.argv[1], 'r')
  tweetCorpusOutput = open(sys.argv[2], 'w+') 
  tagger = NLPlib.NLPlib() 
  for tweet in tweetCorpus:
    #keep track of count variable so that we can later check if tweet 
    count = 0
    # hide the complexities with cleanTweet
    tweet = cleanTweet(tweet)
    tags = tagger.tag(tweet)
    # we don't want to include tagging spaces
    for word in tweet:
      tweetCorpusOutput.write(word)
      if re.match(r'\S', word):
        tweetCorpusOutput.write("/" + tags[count])
        count = count + 1

    #write the tweet delimiter
    tweetCorpusOutput.write("|\n")
