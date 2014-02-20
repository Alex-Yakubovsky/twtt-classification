#!/usr/local/bin/python
import re
import sys
import arffObj

# clean up the class names
def getClassNames(argArray):
  argArray = [re.sub(r":.*", "", arg) for arg in argArray] 
  argArray = [re.sub(r"\.twt\+", "AND", arg) for arg in argArray]
  # strip trailing .twt
  argArray = [re.sub(r"\.twt", "", arg) for arg in argArray]
  argString = ",".join(argArray)
  return argString

# (string) -> (int)
# checks if checkString is in the format -xxx where xxx is a numeric value
# if the string is in that format, return xxx as an integer, otherwise return -1
def getNumTweets(checkString):
  if (checkString[0] == "-"):
    # check if the rest of string contains digits
    if(checkString[1:len(checkString)].isdigit()):
      # cast to int
      return int(checkString[1:len(checkString)])
  return -1

def initializeArff(outputfile, startArg):
  outputfile = open(outputfile, "w+")
  outputfile.write("@relation twit_classification\n")
  outputfile.write("@attribute 1st_person_pronouns numeric\n")
  outputfile.write("@attribute 2nd_person_pronouns numeric\n")
  outputfile.write("@attribute 3rd_person_pronouns numeric\n")
  outputfile.write("@attribute Coordinating_conjunctions numeric\n")
  outputfile.write("@attribute Past-tense_verbs numeric\n")
  outputfile.write("@attribute Future_tense_verbs numeric\n")
  outputfile.write("@attribute Commas numeric\n")
  outputfile.write("@attribute Colons_and_semi-colons numeric\n")
  outputfile.write("@attribute Dashes numeric\n")
  outputfile.write("@attribute Parentheses numeric\n")
  outputfile.write("@attribute Ellipses numeric\n")
  outputfile.write("@attribute Common_nouns numeric\n")
  outputfile.write("@attribute Proper_nouns numeric\n")
  outputfile.write("@attribute Advertsbs numeric\n")
  outputfile.write("@attribute wh-words numeric\n")
  outputfile.write("@attribute Modern_slang_acroynms numeric\n")
  outputfile.write("@attribute Words_all_in_upper_case numeric\n")
  outputfile.write("@attribute Average_length_of_sentences numeric\n")
  outputfile.write("@attribute Average_length_of_tokens numeric\n")
  outputfile.write("@attribute Number_of_sentences numeric\n")
  
  classNames = getClassNames(sys.argv[startArg:len(sys.argv) - 1]) 
  outputfile.write("@attribute twt {" + classNames + "}\n")
  outputfile.write("@data\n")
  outputfile.close()

  return 0

    
if __name__ == "__main__":

  argOne = sys.argv[1]
  startArg = -2
  #Check if argOne is in format -xxx where xxx is a numeric value
  argOne = getNumTweets(argOne)
  # if argOne returns -1, then we know that we can start at the very first argument passed from command line, other wise
  # we start from the second one
  if argOne == -1:
    startArg = 1
  else:
    startArg = 2
 
  # set up the relations and attribute parts for the arff file
  initializeArff(sys.argv[len(sys.argv)-1], startArg)

  # last argument is output file
  for arg in range(startArg, len(sys.argv) -1 ):
    test = arffObj.arffObj(sys.argv[arg], argOne)
    test.parseTweet(sys.argv[len(sys.argv) - 1])
