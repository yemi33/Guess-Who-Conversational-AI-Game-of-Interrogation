from grammar.grammar_engine import GrammarEngine 

class NLG:
  def __init__(self, dialogue_manager, response_strategy):
    self.response_strategy = response_strategy
    self.variables = dialogue_manager.variables
    self.grammar_engine = GrammarEngine("component6/grammar/general_conversation.txt") 
  
  def general_respond(self):
    '''
    Generate some response to the user's questions
    '''
    response = ""
    # go through each of the response strategy, save variables when applicable
    for strategy in self.response_strategy.keys():
      if strategy == "eliza":
        self.grammar_engine.set_variable("fact", self.variables["eliza"])
      elif strategy == "extracted_info":
        self.grammar_engine.set_variable("fact", self.variables["extracted_info"])
      # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
      elif strategy == "marcov_chain":
        response += "\n" + self.response_strategy[strategy]
        continue
      origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
      response += "\n" + self.grammar_engine.generate(origin) # concatenate the generated text to the overall response

    return response
  
  def test_single_response(self, strategy):
    '''
    Tester function to see if the specified strategy is working correctly
    '''

    if strategy == "eliza":
        self.grammar_engine.set_variable("fact", self.variables["eliza"])
    elif strategy == "extracted_info":
      self.grammar_engine.set_variable("fact", self.variables["extracted_info"])
    # if it's a markov chain strategy, don't use grammar engine and just append the markov-generated text to response
    elif strategy == "marcov_chain":
      return self.response_strategy[strategy]
      
    origin = self.response_strategy[strategy] # retrieve the origin nonterminal 
    return self.grammar_engine.generate(origin) # concatenate the generated text to the overall response