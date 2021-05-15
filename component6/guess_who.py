import random
from grammar.grammar_engine import GrammarEngine
from dialogue_manager import *

class GuessWho:
  '''
  Class that represents the game simulation.
  '''
  def __init__(self):
    self.suspect_name = ""
    self.case_file, self.suspect_name, self.suspect_identity, self.suspect_memory = self.generate_scenario("component6/case_file.txt") # a dictionary of facts
    self.dialogue_manager = DialogueManager(self.suspect_identity, self.suspect_memory)
    self.generate_keyphrases()

  # Yemi, Sue
  def generate_scenario(self, case_file):
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
    outfile = open("component6/grammar/keywords.txt", "w")
    for memory in self.suspect_memory:
      outfile.write(f"{memory.type_of_memory}:{memory.text}\n")

  # Nicole, Yemi
  def start_game(self):
    '''
    Code to generate the game
    '''
    print("You are an interrogator. You must determine if the person you are interviewing is GUILTY or NOT GUILTY.")
    print("Here is your case file.")
    print_case_file(self.case_file)
    answer = input("Would like to begin questioning? (Yes/No): ")
    if answer.lower() == "yes" or answer.lower() == "y":
      print(f"*{self.suspect_name} enters the room*")
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
  print("----------------------------------")
  print("-------------- CASE --------------")
  for item in case_file:
    string = item.type_of_memory + ": " + item.text
    num = 25 - len(string)
    num1 = int((25 - len(string))/2)
    num2 = num - num1
    print("| ", " "*num1, item.type_of_memory, ": ", item.text, " "*num2, "|")
  print("---------------------------------")

if __name__ == "__main__":
  guess_who = GuessWho()
  user_answer = input("Would you like to play GuessWho??? (Yes/No): ")
  if user_answer.lower() == "yes" or user_answer.lower() == "y":
    guess_who.start_game()
  else:
    print("Well thanks for coming by anyway. :D")