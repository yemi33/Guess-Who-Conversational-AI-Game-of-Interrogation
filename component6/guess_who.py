import random
from grammar.grammar_engine import GrammarEngine
from dialogue_manager import *

# pip install -U spacy
# python -m spacy download en_core_web_sm

class GuessWho:
  '''
  Class that represents the game simulation.
  '''
  def __init__(self):
    self.suspect_name = ""
    self.case_file, self.suspect_name, self.suspect_identity, self.suspect_memory = self.generate_scenario("component6/case_file.txt") # a dictionary of facts
    self.dialogue_manager = DialogueManager(self.suspect_identity)
    self.dialogue_manager.memory = self.suspect_memory
    self.dialogue_manager.keyphrases = self.generate_keyphrases()
    print(self.dialogue_manager.keyphrases)
    self.dialogue_manager.keyphrase_responses = self.generate_trigger_responses()

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

    # Retrieve suspect's name
    suspect_name = ""
    for memory in suspect_memory:
      if memory.type_of_memory == "Name":
        suspect_name = memory.text
  
    return dictionary["Case"], suspect_name, suspect_identity, suspect_memory
  
  def generate_keyphrases(self):
    lines = []
    memory_type_list = ["Alibi", "Action", "Residence", "Relationship", "Name", "Name Of Victim", "Company", "Memory with Victim", "Person to be Blamed", "Location"]
    with open('component6/grammar/keyphrases.txt') as f:
      file_string = f.read()
      for nonterminal in memory_type_list:
        if nonterminal in file_string:
          for memory in self.suspect_memory:
            if memory.type_of_memory == nonterminal:
              print("hello")
              file_string = file_string.replace(nonterminal,memory.text)
      
      lines = file_string.split("\n")
      print(lines)

    populated_keyphrases = dict()
    for line in lines:
      key_val = line.split("->")
      key, values = key_val[0].strip(), key_val[1].strip()
      questions = values.split("|") # list
      populated_keyphrases[key] = questions

    return populated_keyphrases 

  # Sue, Yemi
  def generate_trigger_responses(self):
    '''
    add the randomly generated suspect's memory into the grammar as savable variable
    
    Format:
    General-Response -> I think it was <Person to be Blamed> who did it. <Scared>.
    Person to be Blames -> ...
    '''
    memory_type_list = ["Alibi", "Action", "Residence", "Relationship", "Name", "Victim", "Company", "Memory with Victim", "Person to be Blamed", "Location"]
    grammar_engine = GrammarEngine("component6/grammar/keyphrases_trigger.txt")
    for item in self.suspect_memory:
      if item.type_of_memory in memory_type_list:
        text = item.text
        if item.type_of_memory == "Alibi" or item.type_of_memory == "Action":
          text = item.verb + " " + item.object
        grammar_engine.set_variable(item.type_of_memory, text)
    
    populated_keyphrase_triggers = dict()
    for nonterminal in grammar_engine.grammar.grammar.keys():
      populated_keyphrase_triggers[nonterminal] = grammar_engine.generate(nonterminal)
  
    return populated_keyphrase_triggers
  
  # Nicole, Yemi
  def start_game(self):
    '''
    Code to generate the game
    '''
    print("You are an interrogator. You must determine if the person you are interviewing is GUILTY or NOT GUILTY.")
    print("Here is your case file.")
    print (self.case_file)
    answer = input("Would like to begin questioning? (Yes/No): ")
    if answer.lower() == "yes" or answer.lower() == "y":
      print(f"*{self.suspect_name} enters the room*")
      for i in range(5):
        user_input = input("You: ")
        print(f"{self.suspect_name}: {self.dialogue_manager.respond(user_input)}")
      
      final_verdict = input(f"Now, make a guess. Is {self.suspect_name} guilty or not? (Guilty/Not Guilty): ")
      if final_verdict == "Guilty":
        if self.suspect_identity == "Guilty":
          print(f"You have correctly guessed. {self.suspect_name} was indeed guilty.")
        else:
          print(f"Nope. {self.suspect_name} was actually innocent.")
      else:
        if self.suspect_identity == "Guilty":
          print(f"No. {self.suspect_name} fooled you. She was guilty.")
        else:
          print(f"Yes! {self.suspect_name} was innocent as you have correctly guessed.")

if __name__ == "__main__":
  guess_who = GuessWho()

  print("Would you like to play GuessWho??? (Yes/No)")
  user_answer = input()
  if user_answer.lower() == "yes" or user_answer.lower() == "y":
    guess_who.start_game()
  else:
    print("Well thanks for coming by anyway. :D")