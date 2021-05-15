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
  def __init__(self, message, dialogue_tag_model):
    self.dialogue_tag_model = dialogue_tag_model
    self.message = message
    self.sentiment = self.sentiment() #tuple
    self.detected_keyphrase,self.keyphrases = self.keyphrases() #string representing the type of keyphrase
    self.obligations = self.obligations() #list
    self.dependencies = self.dependencies() #dictionary containing subj, verb, obj
    self.eliza = self.eliza() #bool
    self.named_entities = self.named_entities() #dictionary
    self.profanity = self.profanity() #bool
  
  def __repr__(self):
    return f'''
    message: {self.message}
    sentiment: {self.sentiment}
    keyphrases: {self.keyphrases}
    obligations: {self.obligations}
    dependencies: {self.dependencies}
    eliza: {self.eliza}
    named_entities: {self.named_entities}
    profanity: {self.profanity}
    '''
    
  def sentiment(self):
    blob = TextBlob(self.message)
    subjectivity = blob.sentiment.subjectivity
    polarity = blob.sentiment.polarity
    return tuple((polarity,subjectivity))
  
  def profanity(self):
    return profanity.contains_profanity(self.message)

  def keyphrases(self):
    model = Keyphrases()
    return model.detect_keyphrase(self.message), model

  def obligations(self):
    model = Obligations(self.dialogue_tag_model)
    return model.get_dialogue_tag(self.message)
  
  def dependencies(self):
    model = Dependency()
    return model.find_actionable_chunk(self.message)
  
  def eliza(self):
    model = Eliza()
    if self.message == model.swap_pronouns(self.message):
      return False
    return True

  def named_entities(self):
    model = Ner()
    return model.find_named_entities(self.message)

if __name__ == "__main__":
  print(NLU("How do you know blah?"))