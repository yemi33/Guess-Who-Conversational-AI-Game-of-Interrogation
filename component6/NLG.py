from grammar.grammar_engine import GrammarEngine
import random

class NLG:
  def __init__(self,response_strategy):
    self.grammar_engine = GrammarEngine("component6/grammar/general_conversation.txt") 
    self.response_strategy = response_strategy

  def single_respond(self, strategy):
    if strategy == "eliza" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["eliza_variable"])
    elif strategy == "extracted_info" and self.response_strategy[strategy] != None:
      self.grammar_engine.set_variable("fact", self.response_strategy["extracted_info_variable"])
    # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
    elif strategy == "markov_chain" and self.response_strategy[strategy] != None:
      return self.response_strategy[strategy]
    elif strategy == "keyphrase_trigger" and self.response_strategy[strategy] != None:
      return self.response_strategy[strategy]
    
    response_strategies_that_are_not_grammar_rules = ["keyphrase_trigger", "eliza_variable", "extracted_info_variable", "marcov_chain", "address_other_feature"]
    if self.response_strategy[strategy] != None and not self.response_strategy[strategy] in response_strategies_that_are_not_grammar_rules:
      origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
      return self.grammar_engine.generate(origin) # concatenate the generated text to the overall response

  def general_respond(self):
    ''' 
    remove utilize_dependency_structure
    '''
    probabilities = {
      "resolve_obligation" : (0.0,0.5),
      "eliza" : (0.5,0.7),
      "extracted_info" : (0.7,0.8),
      "markov_chain" : (0.8,0.9),
      "address_profanity" : (0.9,1.0)
    }
    
    if self.response_strategy["keyphrase_trigger"] != None:
      return self.response_strategy["keyphrase_trigger"]
    
    responses = {}
    # go through each of the response strategy, save variables when applicable
    for strategy in self.response_strategy.keys():
      # If there's a keyword trigger, prioritize that.
      # if strategy == "keyphrase_trigger" and self.response_strategy[strategy] != None:
      #   return self.response_strategy[strategy]
      # All other cases
      if strategy == "eliza" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["eliza_variable"])
      elif strategy == "extracted_info" and self.response_strategy[strategy] != None:
        self.grammar_engine.set_variable("fact", self.response_strategy["extracted_info_variable"])
      # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
      elif strategy == "markov_chain" and self.response_strategy[strategy] != None:
        responses[strategy] = self.response_strategy[strategy]
        continue
        
      response_strategies_that_are_not_grammar_rules = ["keyphrase_trigger", "eliza_variable", "extracted_info_variable", "marcov_chain", "address_other_feature"]
      if self.response_strategy[strategy] != None and not self.response_strategy[strategy] in response_strategies_that_are_not_grammar_rules:
        origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
        responses[strategy] = self.grammar_engine.generate(origin) # concatenate the generated text to the overall response

    random_num = random.random()
    for strategy in probabilities.keys():
      if probabilities[strategy][0] <= random_num and random_num < probabilities[strategy][1]:
        chosen_strategy = strategy
        if chosen_strategy in responses.keys():
          return responses[chosen_strategy]

    response = random.choice(list(responses.keys()))
    return responses[response]