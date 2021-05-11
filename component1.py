#All group members
from textblob import TextBlob
# must do:
# pip install -U textblob
# python -m textblob.download_corpora

def testing(input_string):
  wiki = TextBlob(input_string)
  print(wiki)
  print("Sujectivity: " + str(wiki.sentiment.subjectivity))
  print("Polarity: " + str(wiki.sentiment.polarity))

def main():
  testing("I absolutely love Taco Bell's crunch wrap supreme.")
  print("\n")
  testing("I absolutely love Taco Bell's crunch wrap supreme, but only the black bean one.")
  print("\n")
  testing("Do you hate me?")
  print("\n")
  testing("Can you believe this?")
  print("\n")
  testing("OMG, I am so angry.")
  print("\n")
  testing("You look so happy!")
  print("\n")
  testing("Are you happy?")

main()