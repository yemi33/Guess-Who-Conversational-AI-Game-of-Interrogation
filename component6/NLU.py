from textblob import TextBlob
import spacy
from eliza import Eliza
import dependency
from better_profanity import profanity
from grammar.grammar_engine import GrammarEngine 
from parser.island_parser import IslandParser
import logging
logging.disable(logging.CRITICAL)
from dialog_tag import DialogTag
import os

"""
pip install better_profanity
pip install -U textblob
python3 -m textblob.download_corpora
pip install -U pip setuptools wheel
pip install -U spacy
python3 -m spacy download en_core_web_sm 
pip install DialogTag

"""

class NLU:
  def __init__(self, message):
    self.message = message
    self.sentiment = self.sentiment()#tuple
    self.obligations = self.obligations()#list
    self.dependencies = self.dependencies()#tuple
    self.eliza = self.eliza()#bool
    self.named_entities = self.named_entities()#dictionary
    self.profanity = self.profanity()#bool
    # self.lie = self.detect_lie()
  
  def __repr__(self):
    return f'''
    message: {self.message}\n
    sentiment: {self.sentiment}\n
    obligations: {self.obligations}\n 
    dependencies: {self.dependencies}\n 
    eliza: {self.eliza}\n 
    named_entities: {self.named_entities}\n 
    profanity: {self.profanity}\n
    '''
    
  def sentiment(self):
    #returns tuple of polarity and subjectivity of message
    blob = TextBlob(self.message)
    subjectivity = blob.sentiment.subjectivity
    polarity = blob.sentiment.polarity
    return tuple((polarity,subjectivity))
  
  def obligations(self):
    # returns list, where keys are dialogue acts and values are obligations
    # Have to analyze our message
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'critical'

    model = DialogTag('distilbert-base-uncased')
    output = model.predict_tag(self.message)

    obligations = {}
    obligations_list = [] #list for a given dialog act
    file = open("grammar/obligations.txt", "r").read().split("\n")
    for line in file:
      if line == "" or line == "\n" or line == " ":
        continue
      dialogue_acts = line.split(":")
      act = dialogue_acts[0]
      responses = dialogue_acts[1].replace("\n", "")
      responses = responses.split(",")
      obligations[act] = responses
    
    if output in obligations.keys():
      obligations_list = obligations[output]

    return obligations_list
  
  def dependencies(self):
    # The actionable structures built extractors for in Component 3 in tuple form.
    nlp = spacy.load("en_core_web_sm")
    message = nlp(self.message)
    verb = dependency.find_verb(message)
    subj = dependency.find_subject(message)
    obj = dependency.find_direct_object(message)
    changed_verb = dependency.change_verb(message)
    return tuple((subj, verb, obj, changed_verb))

  
  def eliza(self):
    #returns boolean value that represents whether an ELIZA-style transformation (of the form you coded up for Component 4) is possible. 
    eliza = Eliza()
    if self.message == eliza.swap_pronouns(self.message):
      return False
    return True

  def named_entities(self):
    #A collection of named entities, structured so as to support the kind of associated chatbot functionality that you implemented in Homework 2.
    named_entities = {}
    nlp = spacy.load("en_core_web_sm")
    parsed_msg = nlp(self.message)
    for ent in parsed_msg.ents:
      named_entities[ent.label_] = ent
    return named_entities

  def profanity(self):
    # Whether the user message contains profanity. There’s a simple Python library called profanity that will allow you to detect this.
    return profanity.contains_profanity(self.message)

  def detect_lie(self):
    # You should come up with at least one other feature that your NLU model will look for when processing incoming messages. This could leverage off-the-shelf NLP technology, or some kind of custom code that you write.

    # detect lie?
    # hard to find a library doing this, and probs hard complex to code
    # detect accusation? "You did", "I know you" etc in the user input?
    pass

if __name__ == "__main__":
  nlu = NLU("I know you did it.")
  print(nlu)