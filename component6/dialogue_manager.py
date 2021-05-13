import random
from eliza import Eliza
from markov_model import MarcovModel
from grammar_engine import GrammarEngine

class DialogueManager:
  def __init__(self, suspect_identity):
    self.memory = []
    self.variables = {
      "eliza" : None,
      "extracted_info" : None
    }
    self.suspect_identity = suspect_identity
    self.keyphrases = GrammarEngine("grammar/keyphrases.txt")
    self.keyphrase_responses = GrammarEngine("grammar/keyphrases_trigger.txt")
  
  def strategize(self, nlu):
    self.memory.append(nlu.message)
    response_strategy = {
      "resolve_obligation" : self.resolve_obligation(nlu),
      "address_sentiment" : self.address_sentiment(nlu),
      "address_subjectivity" : self.address_subjectivity(nlu), 
      "keyphrase_trigger" : self.keyphrase_trigger(nlu),
      "eliza" : self.eliza_transformation(nlu),
      "extracted_info" : self.refer_to_extracted_information(nlu),
      "utilize_dependency_structure" : self.utilize_dependency_structure(nlu),
      "marcov_chain" : self.marcov_chain(nlu),
      "address_profanity" : self.address_profanity(nlu),
      "address_other_feature" : self.address_other_feature(nlu)
    }
    return response_strategy

  # Maanya
  def resolve_obligation(self, nlu):
    obligations_list = nlu.obligations
    option = random.randint(0, length(obligations_list)-1)
    obligation_choice = obligations_list[option]
    resolved_obligation = obligation_choice.lower() + "-" + self.address_sentiment(nlu) + "-" + self.address_subjectivity(nlu)
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
      self.variables["eliza"] = eliza.swap_pronouns(message)
      if nlu.sentiment[0] > 0.5:
        return "congratulating-eliza"
      elif nlu.sentiment[0] < -0.3:
        return "empathetic-eliza"
      else:
        return "neutral-eliza"
    else:
      return None
  
  # Yemi
  def refer_to_extracted_information(self, nlu):
    extracted_info_grammar_rules = ["question-about-extracted-info", "acknowledge-extracted-info", "question-extracted-info", "express-anger-at-fact", "express-sadness-at-fact", "express-gladness-at-fact"]

    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = sys.maxsize
    message = nlu.message
    parsed_message = nlp(message)
    for ent in parsed_message.ents:
      for item in self.memory:
        if item.ner == ent.label_: 
          self.variables["extracted_info"] = item.text
    # set the value of the keyword "fact" to be used in the grammar
    self.variables["extracted_info"] = random.choice(self.memory).text
    
    if nlu.sentiment[0] > 0.5:
        return "express-gladness-at-fact"
    elif nlu.sentiment[0] < -0.3:
      return random.choice(["express-anger-at-fact", "express-sadness-at-fact", "question-extracted-info"])
    else:
      return random.choice(["question-about-extracted-info", "acknowledge-extracted-info"])
    
  # Maanya
  def keyphrase_trigger(self, nlu):
    grammar = self.keyphrases.grammar
    message = nlu.message
    for nonterminal in grammar.keys():
      nonterminal_object = grammar[nonterminal]
      for rule in nonterminal_object.rules:
        if rule.body in message:
          return nonterminal + "-Response"
  
  #Sue
  def utilize_dependency_structure(self, nlu):
    new_sentence = nlu.dependencies(3)
    return new_sentence
    
  # Nicole
  def marcov_chain(self, nlu):
    if self.suspect.identity.lower() == "guilty":
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