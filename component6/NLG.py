from grammar.grammar_engine import GrammarEngine 

class NLG:
  def __init__(self, response_strategy, suspect, grammar):
    self.response_strategy = response_strategy
    self.grammar = grammar 
    self.suspect = suspect
  
  def general_respond(self):
    '''
    Generate some response to the user's questions
    '''
    grammar_engine = grammar
    
  def lie(self):
    '''
    Generate some lies
    '''
    pass