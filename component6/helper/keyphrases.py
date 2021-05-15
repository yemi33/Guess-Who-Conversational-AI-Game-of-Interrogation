from grammar.grammar_engine import GrammarEngine
from helper.dependency import Dependency

class Keyphrases:
  def __init__(self):
    self.keywords = self.parse_keyword_file()
    self.keyphrases = self.generate_keyphrases()
    self.keyphrase_responses = self.generate_keyphrase_responses()
  
  def detect_keyphrase(self, message):
    if len(message) > 0 and message.strip()[-1] == "?":
      message = message[:-1]
    
    for keyphrase_type in self.keyphrases.keys():
      keyphrases = self.keyphrases[keyphrase_type]
      for keyphrase in keyphrases:
        if keyphrase in message or keyphrase.capitalize() in message or message in keyphrase or message.capitalize() in keyphrase:
          return keyphrase_type 
    
    return None 
  
  def parse_keyword_file(self):
    lines = open("component6/grammar/keywords.txt").read().split("\n")
    keyword_dictionary = dict()
    for line in lines:
      if line == "" or line == " ":
        continue
      key_val = line.split(":")
      keyword_type, keyword = key_val[0], key_val[1]
      keyword_dictionary[keyword_type.strip()] = keyword.strip()
    
    return keyword_dictionary
  
  def generate_keyphrases(self):
    lines = []
    keyword_types = self.keywords.keys()

    file_string = open('component6/grammar/keyphrases.txt').read()
    for nonterminal in keyword_types:
      if f"<{nonterminal}>" in file_string:
        string = f"<{nonterminal}>"
        for keyword_type in self.keywords.keys():
          if keyword_type == nonterminal:
            file_string = file_string.replace(string,self.keywords[keyword_type])

    keyphrases = dict()
    for line in file_string.split("\n"):
      key_val = line.split("->")
      key, values = key_val[0].strip(), key_val[1].strip()
      questions = list(map(lambda s : s.strip(),values.split("|")))
      keyphrases[key] = questions

    return keyphrases 
  
  def generate_keyphrase_responses(self):
    keyword_types = self.keywords.keys()
    grammar_engine = GrammarEngine("component6/grammar/keyphrases_trigger.txt")
   
    for keyword_type in self.keywords.keys():
      value = self.keywords[keyword_type]
      if keyword_type == "Alibi" or keyword_type == "Action":
        chunk = Dependency().find_actionable_chunk(value)
        value = chunk["verb"] + " " + chunk["object"]
      grammar_engine.set_variable(keyword_type, value)
    
    keyphrase_responses = dict()
    for nonterminal in grammar_engine.grammar.grammar.keys():
      keyphrase_responses[nonterminal] = grammar_engine.generate(nonterminal)
    return keyphrase_responses

if __name__ == "__main__":
  keyphrases = Keyphrases()
  print(keyphrases.detect_keyphrase("What happened at blah?"))