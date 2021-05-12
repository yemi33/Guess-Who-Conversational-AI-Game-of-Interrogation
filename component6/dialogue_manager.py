import random
from eliza import Eliza
import MarcovModel

class DialogueManager:
  def __init__(self, suspect):
    '''
    Args:
      nlu:
        nlu module containing all necessary information extracted from user input
      suspect:
        suspect object containing the suspect's memory
    '''
    self.memory = []
    self.variables = {
      "eliza" : None,
      "extracted_info" : None
    }
    self.suspect = suspect
  
  def strategize(self, nlu):
    '''
    Every function call potentially modifies self.response_strategy dictionary 
    (modifies an entry or returns none)
    Each function call should return a string, so it can be inserted into the value slot in the corresponding dictionary entry
    '''
    self.memory.append(nlu.message)
    # response_strategy = {
    #   "resolve_obligation" : self.resolve_obligation(nlu),
    #   "address_sentiment" : self.address_sentiment(nlu),
    #   "address_subjectivity" : self.address_subjectivity(nlu), 
    #   "keyphrase_trigger" : self.keyphrase_trigger(nlu),
    #   "eliza" : self.eliza_transformation(nlu),
    #   "extracted_info" : self.refer_to_extracted_information(nlu),
    #   "utilize_dependency_structure" : self.utilize_dependency_structure(nlu),
    #   "marcov_chain" : self.marcov_chain(nlu),
    #   "address_profanity" : self.address_profanity(nlu),
    #   "address_other_feature" : self.address_other_feature(nlu)
    # }
    response_strategy = {
      "eliza" : self.eliza_transformation(nlu),
      "marcov_chain" : self.marcov_chain(nlu)
    }
    return response_strategy

  # Maanya
  def resolve_obligation(self, nlu):
    '''
    Reply in a coherent manner. If it's a question, answer the question. If it's a statement, make a comment about the statement.
    '''
    pass
    
  
  # Nicole
  def address_sentiment(self, nlu):
    #use more as helper function to get correct nonterminal
    '''
    - If the interrogator is expressing negative sentiment, how does an innocent person react? How does a guilty person react? 
    - Usually, guilty people tend to try to protect or defend themselves first, instead of focusing on the case or the subject itself. 
    - Innocent people tend to focus on the case and try their best to be helpful in providing as much info as possible.
    '''
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
    #use more as helper function to get correct nonterminal
    '''
    React differently if the user input is subjective (a hypothetical claim, such as "I think you killed him") vs objective (from the point of view of the case file, is it a "recorded" fact, such as body was found in the garage, etc)
    '''
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
    '''
    Apply Eliza style transformation as necessary. 
    '''
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
    '''
    - If the user said previously "Eliza was found dead in the garage." 
    - Later put out a reply such as "How was Eliza when she was found in the garage?" etc
    
    Pseudocode:
    - suspect's memory could be labeled with NER tag 
    - identify the NER tag of the user input 
    - if there's a matching NER tag in the suspect's memory, pull out that memory
    '''
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
    '''
    - Again, as mentioned previously, if the user says something like "What were you doing that night?" the keyword would be "what were you doing?" 
    - For a guilty bot, in the entry for "action that night", there might be "killing Eliza." But you don't want to say that. So choose randomly from a pool of actions and say that instead aka "lie". 
    '''
    pass
  
  #Sue
  def utilize_dependency_structure(self, nlu):
    '''
    Rephrasing the sentence the user used so that other functions can use this sentence and make the bot answer in a more natural way.
    '''
    new_sentence = nlu.dependencies(3)
    return new_sentence
    
  # Nicole
  def marcov_chain(self, nlu):
    '''
    Pretty general. We can use our MarcovModel to train the model on some transcripts and source some lines from some suspect quotes and use that here. 

    Note: can't find any transcripts from innocent person
    '''
    if self.suspect.identity.lower() == "guilty":
      model = MarcovModel.MarcovModel(corpus_filename = "component6/grammar/interrogation_guilty.txt", level = "word", order = 2, pos = False, hybrid = False)
      return model.generate(20, "I")
    
    return None
  
  # Nicole
  def address_profanity(self, nlu):
    '''
    Also pretty general. Prepare some lines we can use in cases where the user uses profanity.

    Returns string if profanity is in user input, otherwise empty string
    '''
    if nlu.profanity == True:
      if self.suspect.identity.lower() == "guilty":
        return "profanity-guilty"
      else:
        return "profanity-innocent"
    else:
      return None
  
  def address_other_feature(self, nlu):
    pass