from grammar.grammar_engine import GrammarEngine 

class NLG:
  def __init__(self, dialogue_manager):
    self.dialogue_manager = dialogue_manager
    self.variables = self.dialogue_manager.variables
    self.keyphrase_trigger = self.dialogue_manager.keyphrase_responses
    self.grammar_engine = GrammarEngine("component6/grammar/general_conversation.txt") 
  
  def general_respond(self, response_strategy):
    response = ""
    # go through each of the response strategy, save variables when applicable
    for strategy in response_strategy.keys():
      if strategy == "eliza":
        self.grammar_engine.set_variable("fact", self.variables["eliza"])
      elif strategy == "extracted_info":
        self.grammar_engine.set_variable("fact", self.variables["extracted_info"])
      # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
      elif strategy == "marcov_chain":
        response += "\n" + response_strategy[strategy]
        continue
      elif strategy == "keyphrase_trigger":
        keyphrase = response_strategy[strategy]
        response += "\n" + self.keyphrase_trigger[keyphrase]
      origin = response_strategy[strategy] # retrieve the origin nonterminal 
      response += "\n" + self.grammar_engine.generate(origin) # concatenate the generated text to the overall response

    return response
  
  def test_single_response(self, response_strategy, strategy):
    if strategy == "eliza":
        self.grammar_engine.set_variable("fact", self.variables["eliza"])
    elif strategy == "extracted_info":
      self.grammar_engine.set_variable("fact", self.variables["extracted_info"])
    # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
    elif strategy == "marcov_chain":
      return response_strategy[strategy]
    elif strategy == "keyphrase_trigger":
      keyphrase = response_strategy[strategy]
      return self.keyphrase_trigger[keyphrase]
    origin = response_strategy[strategy] # retrieve the origin nonterminal 
    return self.grammar_engine.generate(origin) # concatenate the generated text to the overall response