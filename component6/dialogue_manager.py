import sys
import random
import spacy
from NLU import NLU
from NLG import NLG
from helper.obligations import Obligations
from helper.eliza import Eliza
from helper.markov_model import MarkovModel
from grammar.grammar_engine import GrammarEngine
import logging
logging.disable(logging.CRITICAL)
from dialog_tag import DialogTag

class DialogueManager:
  '''
  Class representing a dialogue manager that brings NLU module and NLG module together.
  '''
  def __init__(self, suspect_identity="", suspect_memory=[], verbose=False):
    self.verbose = verbose # whether or not you want helpful output
    self.suspect_identity = suspect_identity
    self.memory = suspect_memory
    self.dialogue_tag_model = DialogTag('distilbert-base-uncased') # one time loading DialogTag
    self.nlp = spacy.load("en_core_web_sm") # one time loading spacy
    self.nlp.max_length = sys.maxsize
  
  def respond(self, message):
    '''
    Method that will be invoked by guess_who.py

    Args:
      message: user input that needs to be responded to
    Returns:
      a single string containing the appropriate response
    '''
    strategy = self.strategize(message)
    if self.verbose:
      print("Strategy:")
      print(strategy)
    return NLG(strategy).general_respond()
  
  def test_single_respond(self, message, technique):
    '''
    Method to test a particular response technique (i.e. resolve_obligation)

    Args:
      message: user input that needs to be responded to
      technique: technique to test (i.e. resolve_obligation)
    Returns:
      a single string containing the appropriate response
    '''
    strategy = self.strategize(message)
    return NLG(strategy).single_respond(technique)

  def strategize(self, message):
    '''
    Method that saves the user message to self.memory, and invokes several helper methods 
    to come up with a response strategy

    Args:
      message: user input that needs to be responded to 
    Returns:
      a dictionary containing various response strategies

    '''
    # analyze the message
    nlu = NLU(message, self.dialogue_tag_model)
    if self.verbose:
      print("Analysis of Message:")
      print(nlu)
    
    # break down the message and save to memory
    ner = nlu.named_entities
    subject = nlu.dependencies["subject"]
    verb = nlu.dependencies["verb"]
    direct_object = nlu.dependencies["object"]
    memory_type = "What_the_user_said"
    new_memory = Memory(ner=ner,text=message,type_of_memory = memory_type,subj=subject,verb=verb,obj=direct_object)
    self.memory.append(new_memory)

    # invoke helper methods and come up with a response strategy
    eliza_grammar,eliza_variable = self.eliza_transformation(nlu)
    extracted_info_grammar,extracted_info_variable = self.refer_to_extracted_information(nlu)
    response_strategy = {
      "memory" : self.memory,
      "resolve_obligation" : self.resolve_obligation(nlu),
      "keyphrase_trigger" : self.keyphrase_trigger(nlu),
      "eliza" : eliza_grammar,
      "eliza_variable" : eliza_variable,
      "extracted_info" : extracted_info_grammar,
      "extracted_info_variable" : extracted_info_variable,
      "markov_chain" : self.markov_chain(nlu),
      "address_profanity" : self.address_profanity(nlu)
    }
    return response_strategy

  # Maanya
  def resolve_obligation(self, nlu):
    '''
    Helper method to resolve a given obligation

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      tuple containing 
        1) a string representing dialogue tag detected from the message, 
        2) a string representing the head of the appropriate response rule from general_conversation.txt 
           = dialogue tag + sentiment + subjectivity
    '''
    obligation_choice = ""

    # If the detected dialogue tag is a Wh-Question, different possible answers need to be given
    # depending on the keyword present in the message
    if nlu.dialogue_tag == "Wh-Question":
      if "what" in nlu.message.lower():
        obligation_choice = "What-Answer"
      elif "who" in nlu.message.lower():
        obligation_choice = "Who-Answer"
      elif "where" in nlu.message.lower():
        obligation_choice = "Where-Answer"
      elif "how" in nlu.message.lower():
        obligation_choice = "How-Answer"
      elif "why" in nlu.message.lower():
        obligation_choice = "Why-Answer"
      elif "when" in nlu.message.lower():
        obligation_choice = "When-Answer"
    
    # given the detected dialogue tag, choose the appropriate response obligation
    obligations_list = Obligations(self.dialogue_tag_model).get_appropriate_response_obligations(nlu.dialogue_tag)
    resolved_obligation = None
    if len(obligations_list) > 0:
      if obligation_choice == "": # if obligation choice has not been decided yet
        obligation_choice = random.choice(obligations_list)
      # consider the sentiment and subjectivity of the user message as well
      resolved_obligation = obligation_choice + "-" + self.address_sentiment(nlu) + "-" + self.address_subjectivity(nlu)
      general_grammar = GrammarEngine("component6/grammar/general_conversation.txt")
      if resolved_obligation not in general_grammar.grammar.grammar.keys():
        resolved_obligation = "general-response"
    return (nlu.dialogue_tag, resolved_obligation)

  # Nicole
  def address_sentiment(self, nlu):
    '''
    Helper method to address the sentiment of the user message 
    
    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      a string representing the sentiment of the message
    '''
    if nlu.sentiment[0] < 0:
      return "negative"
    elif nlu.sentiment[0] > 0:
      return "positive"
    else:
      return "neutral"
  
  # Sue
  def address_subjectivity(self, nlu):
    '''
    Helper method to address the subjectivity of the user message

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      a string representing the subjectivity of the message
    '''
    if nlu.sentiment[1] < 0:
      return "objective"
    elif nlu.sentiment[1] > 0:
      return "subjective"
    else:
      return "neutral"
  
  # Yemi 
  def eliza_transformation(self, nlu):
    '''
    Helper method to perform eliza transformation and choose the appropriate grammar rule
    depending on the user sentiment.

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      1) a string representing the head of the appropriate grammar rule to use from general_conversation.txt
      2) a string containing eliza-transformed user message (which will fill the <fact> slot in the grammar)
    '''
    if nlu.eliza == True:
      eliza = Eliza()
      message = nlu.message
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
    '''
    Helper method to refer to extracted information from the user input

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      1) a string representing the head of the appropriate grammar rule to use from general_conversation.txt
      2) a string containing the extracted information from previous user input (which will fill the <fact> slot in the grammar)
    '''
    message = nlu.message
    parsed_message = self.nlp(message)
    extracted_info_fact = ""
    for ent in parsed_message.ents:
      for item in self.memory:
        if item.ner == ent.label_ and item.type_of_memory == "What_the_user_said": 
          extracted_info_fact = item.text

    # choose the appropriate grammar rule from general_conversation.txt
    if extracted_info_fact != "":
      if nlu.sentiment[0] > 0.5:
        return "express-gladness-at-fact", extracted_info_fact
      elif nlu.sentiment[0] < -0.3:
        return random.choice(["express-anger-at-fact", "express-sadness-at-fact", "question-extracted-info"]), extracted_info_fact
      else:
        return random.choice(["question-about-extracted-info", "acknowledge-extracted-info"]), extracted_info_fact
    
    return None, None

  # Yemi
  def keyphrase_trigger(self, nlu):
    '''
    Helper method to choose the appropriate response to a triggered keyphrase

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      a string containing the appropriate keyphrase response
    '''
    if nlu.detected_keyphrase != None:
      response = nlu.detected_keyphrase + "-Response"
      if response in nlu.keyphrases.keyphrase_responses:
        '''
        nlu.keyphrases is a Keyphrases object
        keyphrase_responses is an instance variable of Keyphrases object 
        that refers to a dictionary mapping keyphrase type to a list of appropriate responses
        '''
        return nlu.keyphrases.keyphrase_responses[response]
    return None
  
  # Nicole
  def markov_chain(self, nlu):
    '''
    Helper method to perform markov chain string generation

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      Markov-generated string (Markov Model is trained on an actual guilty interrogation transcript excerpt)
    '''
    if self.suspect_identity.lower() == "guilty":
      model = MarkovModel(corpus_filename = "component6/grammar/interrogation_guilty.txt", level = "word", order = 3, pos = False)
      string = model.generate(20, "I")
      no_new_line = string.replace("\n"," ") # remove newline
      return no_new_line
    return None
  
  # Nicole
  def address_profanity(self, nlu):
    '''
    Helper method to address profanity in the user message 

    Args:
      nlu: a NLU object containing different analyses of a message
    Returns:
      a string representing the head of the appropriate grammar rule from general_conversation.txt
    '''
    if nlu.profanity == True:
      if self.suspect_identity.lower() == "guilty":
        return "profanity-guilty"
      else:
        return "profanity-innocent"
    else:
      return None

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
    Example case_file format:

    $ Innocent
    ner text type_of_memory subject verb obj
    ...

    $ Guilty
    ner text type_of_memory subject verb obj
    ...

    $ Case
    ner text type_of_memory subject verb obj
    ...

    Types of Memory (You can add more if necessary)
    - Location
    - Action
    - Alibi
    - Reason
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
      ner: {self.ner} 
      text: {self.text}
      type of memory: {self.type_of_memory}
      subject: {self.subject}
      verb: {self.verb}
      object: {self.object}
    )
    '''
  
  def fill_in_memory(self, list_of_items):
    self.ner = list_of_items[0].strip()
    self.text = list_of_items[1].strip()
    self.type_of_memory = list_of_items[2].strip()
    self.subject = list_of_items[3].strip()
    self.verb = list_of_items[4].strip()
    self.object = list_of_items[5].strip()