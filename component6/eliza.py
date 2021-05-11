import spacy
import component3
import random

class Eliza: 
  def __init__(self):
    self.nlp = spacy.load("en_core_web_sm")
    self.memory = []

  def swap_pronouns(self, string):
    '''
    Identify the usages of pronouns (I, me, my, myself, you, your, yourself) and if they're (I, me, myself), swap it for (you, your, yourself) and vice versa
    '''
    special_pronouns = ["i", "me", "my", "myself", "you", "your", "yourself"]
    special_verbs = ["am", "'m", "are"]
    doc = self.nlp(string)
    token_list = [token.text for token in doc]
    for i, token in enumerate(doc):
      if token.text.lower() in special_pronouns or token.text.lower() in special_verbs:
        self.swap(i, token, token_list)
    punctuation = "!.?,\"\':;-"
    return_string = ""
    first = True
    for t in token_list:
      if t in punctuation:
        return_string += t
      else:
        if first:
          return_string += t
          first = False
        else:
          return_string += " " + t
    return return_string.capitalize()
  
  def swap(self, index, token, token_list):
    dictionary = {
      "i" : "you",
      "me": "you",
      "my" : "your",
      "myself" : "yourself",
      "you-subj" : "i",
      "you-obj" : "me",
      "your" : "my",
      "yourself" : "myself",
      "'m" : "are",
      "am" : "are",
      "are" : "am",
      "'re" : "am"
    }

    token_str = token.text.lower()
    if token_str == "you":
      if token.dep_ == "nsubj":
        token_list[index] = dictionary[token_str + "-subj"]
      else:
        token_list[index] = dictionary[token_str + "-obj"]
    else:
      token_list[index] = dictionary[token_str]
  
  def do_you_say_for_a_special_reason(self, string):
    content = self.swap_pronouns(string).lower()
    return "Do you say " + content + " for a special reason?"
  
  def you_seem_quite(self, string):
    if "yes" in string or "Yes" in string or "YES" in string:
      return "You seem to be quite positive."
    elif "no" in string or "No" in string or "NO" in string:
      return "You seem to be quite negative."
    else:
      return "I see."
  
  def deposit_memory(self, string):
    doc = self.nlp(string)
    verb_chunk = component3.find_verb_chunk(doc)
    
    memory = ""
    if verb_chunk != None:
      memory = " ".join([verb_chunk["subject"].text,verb_chunk["verb"].text,verb_chunk["object"].text])
      memory = self.swap_pronouns(memory)
    
    if memory != "":
      self.memory.append(memory.lower())
    else:
      memory = self.swap_pronouns(string)
      if memory[-1] == ".":
        memory = memory[:-1]
      self.memory.append(memory.lower())

  def ask_about_memory(self, string):
    if len(self.memory) > 0:
      return "Does that have anything to do with the fact that " + random.choice(self.memory) + "?"
    else:
      return "I see."
      self.deposit_memory(string)

if __name__ == "__main__":
  eliza = Eliza()
  result = eliza.swap_pronouns("He says I'm depressed.")
  result2 = eliza.do_you_say_for_a_special_reason("I'm sad")
  result3 = eliza.you_seem_quite("I'm telling you, I am sad.")
  result4 = eliza.deposit_memory("He says I'm depressed.")
  result5 = eliza.deposit_memory("Autonomous fast cars shift insurance liability toward manufacturers")
  result5 = eliza.ask_about_memory("I don't know what to do.")
  print(result)
  print(result2)
  print(result3)
  print(result5)

