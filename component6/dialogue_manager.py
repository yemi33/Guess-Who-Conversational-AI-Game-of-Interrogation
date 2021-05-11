import random

class DialogueManager:
  def __init__(self, nlu, suspect):
    '''
    Args:
      nlu:
        nlu module containing all necessary information extracted from user input
      suspect:
        suspect object containing the suspect's memory
    '''
    # nlu object containing all nlu components
    self.nlu = nlu
    # the suspect that this dialogue will act as a brain for 
    self.suspect = suspect
    '''
    Every function call potentially modifies self.response_strategy dictionary 
    (modifies an entry or returns none)
    Each function call should return a string, so it can be inserted into the value slot in the corresponding dictionary entry
    '''
    # list of nonterminals we would like to use as "origin" in generating the response. 
    self.response_strategy = [
      self.resolve_obligation(),
      self.address_sentiment(),
      self.address_subjectivity(), 
      self.keyphrase_trigger(),
      self.utilize_dependency_structure(),
      self.markov_chain(),
      self.address_profanity(),
      self.address_other_feature()
    ]

    # keyword 'fact' 
    self.fact = {
      "eliza" : self.refer_to_extracted_information()
      "extracted_info" : self.refer_to_extracted_information()
  
  # Maanya
  def resolve_obligation(self):
    '''
    Reply in a coherent manner. If it's a question, answer the question. If it's a statement, make a comment about the statement.
    '''
    pass
  
  # Nicole
  def address_sentiment(self):
    '''
    - If the interrogator is expressing negative sentiment, how does an innocent person react? How does a guilty person react? 
    - Usually, guilty people tend to try to protect or defend themselves first, instead of focusing on the case or the subject itself. 
    - Innocent people tend to focus on the case and try their best to be helpful in providing as much info as possible.
    '''
    #negative
    if self.nlu.sentiment[0] < 0:
      return "negative"
    #positive
    elif self.nlu.sentiment[0] > 0:
      return "positive"
    #neutral
    else:
      return "neutral"
  
  # Sue
  def address_subjectivity(self):
    '''
    React differently if the user input is subjective (a hypothetical claim, such as "I think you killed him") vs objective (from the point of view of the case file, is it a "recorded" fact, such as body was found in the garage, etc)
    '''
    #objective
    if self.nlu.sentiment[1] < 0:
      return "objective"
    #subjective
    elif self.nlu.sentiment[1] > 0:
      return "subjective"
    #neutral
    else:
      return "neutral"
  
  # Yemi
  def eliza_transformation(self):
    '''
    Apply Eliza style transformation as necessary.
    '''
    if self.nlu.eliza == True:
      eliza = component4.Eliza()
      message = self.nlu.message
      return eliza.swap_pronoun(message)
    else:
      return None
  
  # Yemi
  def refer_to_extracted_information(self):
    '''
    - If the user said previously "Eliza was found dead in the garage." 
    - Later put out a reply such as "How was Eliza when she was found in the garage?" etc
    
    Pseudocode:
    - suspect's memory could be labeled with NER tag 
    - identify the NER tag of the user input 
    - if there's a matching NER tag in the suspect's memory, pull out that memory
    '''
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = sys.maxsize
    message = self.nlu.message
    parsed_message = nlp(message)
    for ent in parsed_message.ents:
      for item in self.suspect.memory:
        if item.ner == ent.label_: # extend to compare the type of infor
          return item.text

    return random.choice(self.suspect.memory).text
    
  # Maanya
  def keyphrase_trigger(self):
    '''
    - Again, as mentioned previously, if the user says something like "What were you doing that night?" the keyword would be "what were you doing?" 
    - For a guilty bot, in the entry for "action that night", there might be "killing Eliza." But you don't want to say that. So choose randomly from a pool of actions and say that instead aka "lie". 
    '''
    pass
  
  #Sue
  def utilize_dependency_structure(self):
    '''
    Rephrasing the sentence the user used so that other functions can use this sentence and make the bot answer in a more natural way.
    '''
    new_verb = self.nlu.dependencies(3)
    return new_verb
    
  
  # Nicole
  def markov_chain(self):
    '''
    Pretty general. We can use our MarcovModel to train the model on some transcripts and source some lines from some suspect quotes and use that here. 

    Note: can't find any transcripts from innocent person
    '''
    if self.suspect.identity.lower() == "guilty":
      model = MarcovModel(corpus_filename = "../grammar/interrogation_guilty.txt", level = "word", order = 2, pos = False, hybrid = False)
      return model.generate(20, "I")
    return None
  
  # Nicole
  def address_profanity(self):
    '''
    Also pretty general. Prepare some lines we can use in cases where the user uses profanity.

    Returns string if profanity is in user input, otherwise empty string
    '''
    if self.nlu.profanity == True:
      if self.suspect.identity.lower() == "guilty":
        return "profanity-guilty"
      else:
        return "profanity-innocent"
    else:
      return None
  
  def address_other_feature(self):
    pass