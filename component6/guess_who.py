class Suspect:
  '''
  Class that represents the suspect bot that will chat with the user
  '''
  def __init__(self, identity, dialogue_manager):
    self.identity = identity
    self.dialogue_manager = dialogue_manager
    '''
    Suspect Memory Architecture:
    suspect's self.memory is a list of Memory objects

    Memory object consists of:
      NER tag
      text
      type of memory (set of rigid categories)
      if type of memory == action:
        subject (who did)
        verb (what)
        object (to whom)
    '''

class Memory:
  '''
  Struct representing a memory unit
  '''
  def __init__(self, ner, text, type_of_memory, subject = None, verb = None, obj = None):
    self.ner = ner
    self.text = text
    self.type_of_memory = type_of_memory
    '''
    Location
    Action
    Residence 
    Relationship 
    Age 
    '''
    self.subject = subject
    self.verb = verb
    self.object = obj

class GuessWho:
  '''
  Class that represents the game simulation.
  '''
  def __init__(self):
    self.case_file, self.suspect_identity,
    self.suspect_memory = self.generate_scenario() # a dictionary of facts
    self.bot = Suspect(self.suspect_identity,self.suspect_memory)
    self.random_facts = []

  def generate_scenario(self):
    '''
    Generate a random crime scenario
    - create a case case_file
    - create a suspect who has either innocent or guilty identity and a dictionary of memory 
    '''
    pass
  
  def start_game(self):
    '''
    Code to generate the game
    - utilize NLU, Dialogue Manager, NLG to have a conversation (aka chatbot)
    '''
    pass