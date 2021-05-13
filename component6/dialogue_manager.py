import random
from eliza import Eliza
from markov_model import MarcovModel
from grammar.grammar_engine import GrammarEngine
from NLU import NLU
from NLG import NLG
import spacy
import sys

class DialogueManager:
  def __init__(self, suspect_identity, suspect_memory=[]):
    self.memory = suspect_memory
    self.suspect_identity = suspect_identity
    self.keyphrases = GrammarEngine("component6/grammar/keyphrases.txt")
    self.keyphrase_responses = {} # will be filled in by guess_who "generate trigger responses" function
  
  # this is the method that will be invoked.
  def respond(self, message):
    strategy = self.strategize(message)
    response = NLG(strategy).general_respond()
    return response
  
  def test_single_respond(self, message, technique):
    strategy = self.strategize(message)
    response = NLG(strategy).single_respond(technique)
    return response

  def strategize(self, message):
    nlu = NLU(message)

    ner = nlu.named_entities
    subject = nlu.dependencies[0]
    verb = nlu.dependencies[1]
    direct_object = nlu.dependencies[2]
    switched_verb = nlu.dependencies[3]
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
      "utilize_dependency_structure" : self.utilize_dependency_structure(nlu),
      "marcov_chain" : self.marcov_chain(nlu),
      "address_profanity" : self.address_profanity(nlu),
      "address_other_feature" : self.address_other_feature(nlu)
    }
    return response_strategy

  # Maanya
  def resolve_obligation(self, nlu):
    obligations_list = nlu.obligations
    option = random.randint(0, len(obligations_list)-1)
    obligation_choice = obligations_list[option]
    resolved_obligation = obligation_choice + "-" + self.address_sentiment(nlu) + "-" + self.address_subjectivity(nlu)
    return resolved_obligation
  
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
  
  # Yemi
  def eliza_transformation(self, nlu):
    eliza_grammar_rules = ["congratulating-eliza", "empathetic-eliza", "neutral-eliza"]
    if nlu.eliza == True:
      eliza = Eliza()
      message = nlu.message
      # set the value of keyword "fact" for eliza grammar 
      eliza_fact = eliza.swap_pronouns(message)
      if nlu.sentiment[0] > 0.5:
        return "congratulating-eliza", eliza_fact 
      elif nlu.sentiment[0] < -0.3:
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
    extracted_info_fact = random.choice(self.memory).text
    
    if nlu.sentiment[0] > 0.5:
        return "express-gladness-at-fact", extracted_info_fact
    elif nlu.sentiment[0] < -0.3:
      return random.choice(["express-anger-at-fact", "express-sadness-at-fact", "question-extracted-info"]), extracted_info_fact
    else:
      return random.choice(["question-about-extracted-info", "acknowledge-extracted-info"]), extracted_info_fact
    
  # Maanya
  def keyphrase_trigger(self, nlu):
    grammar = self.keyphrases.grammar.grammar
    message = nlu.message
    for nonterminal in grammar.keys():
      nonterminal_object = grammar[nonterminal]
      for rule in nonterminal_object.rules:
        if rule.body[0] in message:
          response = nonterminal + "-Response"
          if response in self.keyphrase_responses.keys():
            return self.keyphrase_responses[response]
    return None
  
  #Sue
  def utilize_dependency_structure(self, nlu):
    new_sentence = nlu.dependencies[3]
    return new_sentence
    
  # Nicole
  def marcov_chain(self, nlu):
    if self.suspect_identity.lower() == "guilty":
      model = MarcovModel(corpus_filename = "component6/grammar/interrogation_guilty.txt", level = "word", order = 2, pos = False, hybrid = False)
      return model.generate(20, "I")
    
    return None
  
  # Nicole
  def address_profanity(self, nlu):
    if nlu.profanity == True:
      if self.suspect.identity.lower() == "guilty":
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