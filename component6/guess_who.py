import random
from grammar.grammar_engine import GrammarEngine
from dialogue_manager import *

class GuessWho:
  '''
  Class that represents the simulation of the GuessWho game.
  '''
  def __init__(self, verbose = False):
    self.suspect_name = ""
    self.case_file, self.suspect_name, self.suspect_identity, self.suspect_memory = self.generate_scenario("component6/case_file.txt") # a dictionary of facts
    self.dialogue_manager = DialogueManager(self.suspect_identity, self.suspect_memory, verbose)
    self.generate_keywords()

  # Yemi, Sue
  def generate_scenario(self, case_file):
    '''
    Method to generate the game scenario based on case_file.txt

    Args:
      case_file: file containing structured lines that will be parsed into Memory objects 
    Returns:
      1) list of Memory objects corresponding to the Case File (Knowledge available to the user in the beginning of the conversation)
      2) string containing the suspect's name
      3) list of Memory objects corresponding to the suspect's memory (Knowledge available to the suspect in the beginning of the conversation)
    '''
    dictionary = {
      "Innocent": None,
      "Guilty": None,
      "Case": None
    }
    suspect_name = ""
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
        memory = Memory()
        memory.fill_in_memory(items)
        if memory.type_of_memory == "Name":
          suspect_name = memory.text
        list_of_memory.append(memory)
    # for the edge case of the last category not running into another $ sign before hitting end of file
    dictionary[key] = list_of_memory
    
    # choose the suspect
    suspect_identity = random.choice(["Guilty", "Innocent"])
    suspect_memory = dictionary[suspect_identity]

    return dictionary["Case"], suspect_name, suspect_identity, suspect_memory
  
  def generate_keywords(self):
    '''
    Method to generate the keywords based on the suspect's memory

    Returns:
      keywords.txt: file that contains corresponding the keywords that will be used 
                    in the generation of keyphrases and keyphrase responses by Keyphrases module
    '''
    outfile = open("component6/grammar/keywords.txt", "w")
    for memory in self.suspect_memory:
      outfile.write(f"{memory.type_of_memory}:{memory.text}\n")

  # Nicole, Yemi
  def start_game(self):
    '''
    Method to generate the game
    '''
    print("You are an interrogator. You must determine if the person you are interviewing is GUILTY or NOT GUILTY.")
    print("Here is your case file.")
    print_case_file(self.case_file)
    answer = input("Would like to begin questioning? (Yes/No): ")
    if answer.lower() == "yes" or answer.lower() == "y":
      print(f"* {self.suspect_name} enters the room *")
      for i in range(10):
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
          print(f"No. {self.suspect_name} fooled you. They were guilty.")
        else:
          print(f"Yes! {self.suspect_name} was innocent as you have correctly guessed.")

# Sue
def print_case_file(case_file):
  '''
  Method to print the case file.
  '''
  print("------------------------------------------")
  print("------------------ CASE ------------------")
  for item in case_file:
    string = item.type_of_memory + ": " + item.text
    num = 33 - len(string)
    num1 = int((33 - len(string))/2)
    num2 = num - num1
    print("| ", " "*num1, item.type_of_memory, ": ", item.text, " "*num2, "|")
  print("-----------------------------------------")

if __name__ == "__main__":
  guess_who = GuessWho(verbose=True)
  user_answer = input("Would you like to play GuessWho??? (Yes/No): ")
  if user_answer.lower() == "yes" or user_answer.lower() == "y":
    guess_who.start_game()
  else:
    print("Well thanks for coming by anyway. :D")