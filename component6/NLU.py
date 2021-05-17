import logging
logging.disable(logging.CRITICAL)
from textblob import TextBlob
from better_profanity import profanity
import os
from helper.eliza import Eliza
from helper.keyphrases import Keyphrases
from helper.obligations import Obligations
from helper.dependency import Dependency
from helper.ner import Ner

"""
Required Installation:

pip install better_profanity
pip install -U textblob
python3 -m textblob.download_corpora
pip install -U pip setuptools wheel
pip install -U spacy
python3 -m spacy download en_core_web_sm 
pip install DialogTag

"""

class NLU:
  '''
  Class representing the Natural Language Understanding module.
  '''
  def __init__(self, message, dialogue_tag_model):
    self.dialogue_tag_model = dialogue_tag_model # will be passed on from the dialogue manager - this is to load the model only once, instead of every time we need to analyze a message.
    self.message = message
    self.sentiment = self.sentiment()
    self.detected_keyphrase,self.keyphrases = self.keyphrases() 
    self.dialogue_tag = self.obligations() 
    self.dependencies = self.dependencies() 
    self.eliza = self.eliza() 
    self.named_entities = self.named_entities()
    self.profanity = self.profanity()
  
  def __repr__(self):
    return f'''
    message: {self.message}
    sentiment: {self.sentiment}
    keyphrases: {self.detected_keyphrase}
    dialogue_tag: {self.dialogue_tag}
    dependencies: {self.dependencies}
    eliza: {self.eliza}
    named_entities: {self.named_entities}
    profanity: {self.profanity}
    '''
    
  def sentiment(self):
    '''
    Helper method to analyze the sentiment of user input

    Returns:
      tuple containing the polarity and subjectivity of the message
    '''
    blob = TextBlob(self.message)
    subjectivity = blob.sentiment.subjectivity
    polarity = blob.sentiment.polarity
    return tuple((polarity,subjectivity))
  
  def profanity(self):
    '''
    Helper method to detect whether the user input contains profanity

    Returns:
      boolean value that will be True if the message contains profanity
    '''
    return profanity.contains_profanity(self.message)

  def keyphrases(self):
    '''
    Helper method to detect any keyphrase from user input

    Returns:
      1) a string representing the type of the detected keyphrase (i.e. Solicit, Greeting)
      2) Keyphrases object containing a dictionary of keyphrases and a dictionary of keyphrase_responses
    '''
    model = Keyphrases()
    return model.detect_keyphrase(self.message), model

  def obligations(self):
    '''
    Helper method to analyze the sentiment of user input

    Returns:
      a string containing the detected dialogue tag in the user input
    '''
    model = Obligations(self.dialogue_tag_model)
    return model.get_dialogue_tag(self.message)
  
  def dependencies(self):
    '''
    Helper method to find actionable chunks in the user input (i.e. subject, verb, object)

    Returns:
      a dictionary containing components of the actionable chunk (i.e. subject, verb, object)
    '''
    model = Dependency()
    return model.find_actionable_chunk(self.message)
  
  def eliza(self):
    '''
    Helper method to determine whether an Eliza transformation is possible
  
    Returns:
      boolean value indicating whether or not Eliza transformation is possible
    '''
    model = Eliza()
    if self.message == model.swap_pronouns(self.message):
      return False
    return True

  def named_entities(self):
    '''
    Helper method to identify any named entities in the user input 

    Returns:
      a dictionary containing all named entities
    '''
    model = Ner()
    return model.find_named_entities(self.message)

if __name__ == "__main__":
  print(NLU("How do you know blah?"))