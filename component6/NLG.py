from grammar.grammar_engine import GrammarEngine
import random
from helper.keyphrases import Keyphrases
from helper.dependency import Dependency

class NLG:
  '''
  Class representing the Natural Language Generation module.
  '''
  def __init__(self,response_strategy):
    '''
    Constructor for NLG class

    self.grammar_engine: grammar engine containg grammar from general_conversation.txt
    self.response_strategy: dictionary containing various response strategies (given by the dialogue manager)

    '''
    self.grammar_engine = GrammarEngine("component6/grammar/general_conversation.txt") 
    self.response_strategy = response_strategy

  def general_respond(self):
    '''
    Method that generates a single string containing the appropriate response
    '''
    # weighted probabilites for each technique that uses the grammar engine 
    # keyphrase_trigger, and markov_chain does not use the grammar engine
    probabilities = {
      "resolve_obligation" : (0.0,0.5),
      "eliza" : (0.5,0.7),
      "extracted_info" : (0.7,0.8),
      "markov_chain" : (0.8,0.9),
      "address_profanity" : (0.9,1.0)
    }
    
    # prioritize keyphrase trigger
    if self.response_strategy["keyphrase_trigger"] != None:
      return self.response_strategy["keyphrase_trigger"]

    # then prioritize obligations that are responses to Wh-Question 
    # because these grammar actually need content 
    # and you need to set variables in the grammar engine before starting to generate texts.
    elif self.response_strategy["resolve_obligation"][0] == "Wh-Question":
      keywords = Keyphrases().keywords
      for word in keywords.keys():
        if word == "Alibi" or word == "Action":
          # use dependency module to break apart the sentence
          chunk = Dependency().find_actionable_chunk(keywords[word])
          value = chunk["verb"] + " " + chunk["object"]
        self.grammar_engine.set_variable(word, keywords[word])
    
    responses = {}
    origin = ""
    # go through each of the response strategy, save variables when applicable
    for strategy in self.response_strategy.keys():
      if strategy == "eliza" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["eliza_variable"])
      elif strategy == "extracted_info" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["extracted_info_variable"])
      # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
      elif strategy == "markov_chain" and self.response_strategy[strategy] != None:
        responses[strategy] = self.response_strategy[strategy]
        continue
      elif strategy == "resolve_obligation":
        # remember, self.response_strategy["resolve_obligation"] is a tuple 
        # with 1) detected dialogue tag, 2) name of the appropriate obligation tag
        origin = self.response_strategy[strategy][1]
      elif strategy == "memory": 
        continue
  
      response_strategies_that_are_not_grammar_rules = ["keyphrase_trigger", "eliza_variable", "extracted_info_variable", "markov_chain", "address_other_feature"]
      if origin == "":
        origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
      if self.response_strategy[strategy] != None and not self.response_strategy[strategy] in response_strategies_that_are_not_grammar_rules:
        responses[strategy] = self.grammar_engine.generate(origin) # concatenate the generated text to the overall response

    # choose the string that will be returned as the response
    random_num = random.random()
    for strategy in probabilities.keys():
      if probabilities[strategy][0] <= random_num and random_num < probabilities[strategy][1]:
        chosen_strategy = strategy
        if chosen_strategy in responses.keys():
          return responses[chosen_strategy]

    # default behavior
    response = random.choice(list(responses.keys()))
    return responses[response]

  def single_respond(self, strategy):
      '''
      Test method to test out a specific strategy

      Args:
        strategy: name of the strategy you want to test 
      Returns:
        a string containing the appropriate response 
      '''

      # strategies that need special treatment
      if strategy == "eliza" and self.response_strategy[strategy] != None:
          self.grammar_engine.set_variable("fact", self.response_strategy["eliza_variable"])
      elif strategy == "extracted_info" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["extracted_info_variable"])
      # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
      elif strategy == "markov_chain" and self.response_strategy[strategy] != None:
        return self.response_strategy[strategy]
      elif strategy == "keyphrase_trigger" and self.response_strategy[strategy] != None:
        return self.response_strategy[strategy]
      
      response_strategies_that_are_not_grammar_rules = ["keyphrase_trigger", "eliza_variable", "extracted_info_variable", "markov_chain", "address_other_feature"]
      if self.response_strategy[strategy] != None and not self.response_strategy[strategy] in response_strategies_that_are_not_grammar_rules:
        origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
        return self.grammar_engine.generate(origin) # concatenate the generated text to the overall response