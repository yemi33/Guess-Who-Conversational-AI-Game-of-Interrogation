import random
from eliza import Eliza
from markov_model import MarkovModel
from grammar.grammar_engine import GrammarEngine
from NLU import NLU
from NLG import NLG
import spacy
import sys

class DialogueManager:
  def __init__(self, suspect_identity, suspect_memory=[]):
    self.memory = suspect_memory
    self.suspect_identity = suspect_identity
    self.keyphrases = {} # will be filled in by guess_who "generate keyphrases" function
    self.keyphrase_responses = {} # will be filled in by guess_who "generate trigger responses" function
    self.obligations = self.parse_obligation()
  
  # this is the method that will be invoked.
  def respond(self, message):
    strategy = self.strategize(message)
    return NLG(strategy).general_respond()
  
  # this is a tester method to see if a particular response technique is working.
  def test_single_respond(self, message, technique):
    strategy = self.strategize(message)
    return NLG(strategy).single_respond(technique)

  def strategize(self, message):
    nlu = NLU(message, self.obligations)

    ner = nlu.named_entities
    subject = nlu.dependencies[0]
    verb = nlu.dependencies[1]
    direct_object = nlu.dependencies[2]
    new_memory = Memory(ner=ner,text=message,subj=subject,verb=verb,obj=direct_object)
    self.memory.append(new_memory)

    eliza_grammar,eliza_variable = self.eliza_transformation(nlu)
    extracted_info_grammar,extracted_info_variable = self.refer_to_extracted_information(nlu)

    response_strategy = {
      "resolve_obligation" : self.resolve_obligation(nlu),
      "keyphrase_trigger" : self.keyphrase_trigger(nlu),
      "eliza" : eliza_grammar,
      "eliza_variable" : eliza_variable,
      "extracted_info" : extracted_info_grammar,
      "extracted_info_variable" : extracted_info_variable,
      "markov_chain" : self.markov_chain(nlu),
      "address_profanity" : self.address_profanity(nlu),
      "address_other_feature" : self.address_other_feature(nlu)
    }
    return response_strategy

  # Maanya
  def resolve_obligation(self, nlu):
    obligations_list = nlu.obligations
    resolved_obligation = None

    if len(obligations_list) > 0:
      obligation_choice = random.choice(obligations_list)
      resolved_obligation = obligation_choice + "-" + self.address_sentiment(nlu) + "-" + self.address_subjectivity(nlu)
      general_grammar = GrammarEngine("component6/grammar/general_conversation.txt")
      if resolved_obligation not in general_grammar.grammar.grammar.keys():
        resolved_obligation = "general-response"
    
    return resolved_obligation
  
  def parse_obligation(self):
    obligations = {}
    obligations_list = [] # list for a given dialog act
    file = open("component6/grammar/obligations.txt", "r").read().split("\n")
    for line in file:
      if line == "" or line == "\n" or line == " ":
        continue
      dialogue_acts = line.split(":")
      act = dialogue_acts[0]
      responses = dialogue_acts[1].replace("\n", "")
      responses = responses.split(",")
      obligations[act] = responses

    return obligations 

  # Nicole
  def address_sentiment(self, nlu):
    #negative
    if nlu.sentiment[0] < 0:
      return "negative"
    #positive
    elif nlu.sentiment[0] > 0:
      return "positive"
    #neutral
    else:
      return "neutral"
  
  # Sue
  def address_subjectivity(self, nlu):
    #objective
    if nlu.sentiment[1] < 0:
      return "objective"
    #subjective
    elif nlu.sentiment[1] > 0:
      return "subjective"
    #neutral
    else:
      return "neutral"
  
  # Yemi - needs fix
  def eliza_transformation(self, nlu):
    eliza_grammar_rules = ["congratulating-eliza", "empathetic-eliza", "neutral-eliza"]
    if nlu.eliza == True:
      eliza = Eliza()
      message = nlu.message
      # set the value of keyword "fact" for eliza grammar 
      eliza_fact = eliza.swap_pronouns(message)
      if nlu.sentiment[0] > 0.7:
        return "congratulating-eliza", eliza_fact 
      elif nlu.sentiment[0] < 0:
        return "empathetic-eliza", eliza_fact
      else:
        return "neutral-eliza", eliza_fact
    else:
      return None, None
  
  # Yemi
  def refer_to_extracted_information(self, nlu):
    extracted_info_grammar_rules = ["question-about-extracted-info", "acknowledge-extracted-info", "question-extracted-info", "express-anger-at-fact", "express-sadness-at-fact", "express-gladness-at-fact"]

    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = sys.maxsize
    message = nlu.message
    parsed_message = nlp(message)
    extracted_info_fact = ""
    for ent in parsed_message.ents:
      for item in self.memory:
        if item.ner == ent.label_: 
          extracted_info_fact = item.text
          
    if extracted_info_fact == "":
      extracted_info_fact = random.choice(self.memory).text
    
    if nlu.sentiment[0] > 0.5:
        return "express-gladness-at-fact", extracted_info_fact
    elif nlu.sentiment[0] < -0.3:
      return random.choice(["express-anger-at-fact", "express-sadness-at-fact", "question-extracted-info"]), extracted_info_fact
    else:
      return random.choice(["question-about-extracted-info", "acknowledge-extracted-info"]), extracted_info_fact
    
  # Maanya - requires interaction with guess_who.py because the slot values for generating keyphrase trigger depends on the scenario
  def keyphrase_trigger(self, nlu):
    message = nlu.message
    print(message.strip()[-1])
    if message.strip()[-1] == "?":
      message = message[:-1]
    
    for keyphrase_type in self.keyphrases.keys():
      keyphrases = self.keyphrases[keyphrase_type]
      for keyphrase in keyphrases:
        if keyphrase in message or keyphrase.capitalize() in message or message in keyphrase or message.capitalize() in keyphrase:
          response = keyphrase_type + "-Response"
          if response in self.keyphrase_responses.keys():
            return self.keyphrase_responses[response]
    return None
  
  #Sue - we can remove it; it's more like a helper function
  '''
  def utilize_dependency_structure(self, nlu):
    new_sentence = nlu.dependencies[3]
    return new_sentence
  '''
    
  # Nicole
  def markov_chain(self, nlu):
    if self.suspect_identity.lower() == "guilty":
      model = MarkovModel(corpus_filename = "component6/grammar/interrogation_guilty.txt", level = "word", order = 2, pos = True)
      return model.generate(20, "I")
    return None
  
  # Nicole
  def address_profanity(self, nlu):
    if nlu.profanity == True:
      if self.suspect_identity.lower() == "guilty":
        return "profanity-guilty"
      else:
        return "profanity-innocent"
    else:
      return None
  
  def address_other_feature(self, nlu):
    pass

class Memory:
  '''
  Struct representing a memory unit
  '''
  def __init__(self, ner = "", text = "", type_of_memory = "", subj = None, verb = None, obj = None):
    self.ner = ner
    self.text = text
    self.type_of_memory = type_of_memory
    self.subject = subj
    self.verb = verb
    self.object = obj
    '''
    Example file format:

    $ Innocent
    ner text type_of_memory subject verb obj

    $ Guilty
    ner text type_of_memory subject verb obj

    $ Case
    ner text type_of_memory subject verb obj

    Types of Memory (You can add more if necessary)
    - Location
    - Action
    - Residence 
    - Relationship 
    - Age 
    - Name 
    - Time Last Seen Victim
    - Company
    - Memory with Victim 
    - Person to be Blamed
    '''
  def __repr__(self):
    return f'''
    Memory(
      ner: {self.ner} \n 
      text: {self.text} \n 
      type of memory: {self.type_of_memory} \n 
      subject: {self.subject} \n 
      verb: {self.verb} \n 
      object: {self.object} \n 
    )
    '''
  
  def fill_in_memory(self, list_of_items):
    self.ner = list_of_items[0].strip()
    self.text = list_of_items[1].strip()
    self.type_of_memory = list_of_items[2].strip()
    self.subject = list_of_items[3].strip()
    self.verb = list_of_items[4].strip()
    self.object = list_of_items[5].strip()