import random
from grammar.grammar_engine import GrammarEngine
from dialogue_manager import DialogueManager

# pip install -U spacy
# python -m spacy download en_core_web_sm

class Memory:
  '''
  Struct representing a memory unit
  '''
  def __init__(self, ner = "", text = "", type_of_memory = "", subject = None, verb = None, obj = None):
    self.ner = ner
    self.text = text
    self.type_of_memory = type_of_memory
    self.subject = subject
    self.verb = verb
    self.object = obj
    '''
    Example file format:

    $ Innocent
    ner text type_of_memory subject verb obj

    $ Guilty
    ner text type_of_memory subject verb obj

    $ Case
    ner text type_of_memory subject verb obj

    Types of Memory (You can add more if necessary)
    - Location
    - Action
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
    return f"Memory({self.ner} | {self.text} | {self.type_of_memory} | {self.subject} | {self.verb} | {self.object})"
  
  def fill_in_memory(self, list_of_items):
    self.ner = list_of_items[0]
    self.text = list_of_items[1]
    self.type_of_memory = list_of_items[2]
    self.subject = list_of_items[3]
    self.verb = list_of_items[4]
    self.object = list_of_items[5]

class GuessWho:
  '''
  Class that represents the game simulation.
  '''
  def __init__(self):
    self.case_file, self.suspect_identity, self.suspect_memory = self.generate_scenario("component6/case_file.txt") # a dictionary of facts
    self.dialogue_manager = DialogueManager(self.suspect_identity)
    self.dialogue_manager.memory = self.suspect_memory
    #self.nlg = NLG(self.dialogue_manager)

  # Yemi, Sue
  def generate_scenario(self, case_file):
    '''
    Generate a random crime scenario
    - create a case case_file
    - create a suspect who has either innocent or guilty identity and a dictionary of memory 
    '''
    dictionary = {
      "Innocent": None,
      "Guilty": None,
      "Case": None
    }
    case_file_text = open(case_file).read().split("\n")
    list_of_memory = list()
    key = ""
    for line in case_file_text:
      if line == "" or line == " ":
        continue
      if line[0] == "$":
        dictionary[key] = list_of_memory
        key = line.replace("$", "").strip()
        list_of_memory = list()
        continue
      else:
        items = line.split("|")
        # def __init__(self, ner, text, type_of_memory, subject = None, verb = None, obj = None)
        memory = Memory()
        memory.fill_in_memory(items)
        list_of_memory.append(memory)
    # for the edge case of the last category not running into another $ sign before hitting end of file
    dictionary[key] = list_of_memory
    
    suspect_identity = random.choice(["Guilty", "Innocent"])
    suspect_memory = dictionary[suspect_identity]
    return dictionary["Case"], suspect_identity, suspect_memory
  
  # Sue, Yemi
  def generate_trigger_responses(self):
    '''
    add the randomly generated suspect's memory into the grammar as savable variable
    
    Format:
    General-Response -> I think it was <Person to be Blamed> who did it. <Scared>.
    Person to be Blames -> ...
    '''
    memory_type_list = ["Alibai", "Residence", "Relationship", "Name",  "Company", "Memory with Victim", "Person to be Blamed", "Location"]
    grammar_engine = self.dialogue_manager.keyphrase_responses
    for item in self.suspect_memory:
      if item.type_of_memory in memory_type_list:
        grammar_engine.set_variables(item.type_of_memory, item.text)
    
    populated_keyphrase_triggers = dict()
    for nonterminal in grammar_engine.grammar.grammar.keys():
      populated_keyphrase_triggers[nonterminal] = grammar.generate(nonterminal)
  
    self.dialogue_manager.keyphrase_responses = populated_keyphrase_triggers
    
  def start_game(self):
    '''
    Code to generate the game
    - utilize NLU, Dialogue Manager, NLG to have a conversation (aka chatbot)
    '''
    # print("Would you like to play Guilty as Charged???")
    # yes/no
    # print("You are an interrogator. You must determine if the person you are interviewing is GUILTY or NOT GUILTY.")
    # Here is your case file:
    # print case file
    # Would like to begin questioning?
    # yes/no
    # print("*NAME enters the room*")
    # for i in range 25 (? how many rounds do we want)
    #   nlu(input())
    #   dialogemanager.strategize(response)
    #   nlg(dialogemanager)
    #   print(nlg.general_respond)

if __name__ == "__main__":
  guess_who = GuessWho()
  