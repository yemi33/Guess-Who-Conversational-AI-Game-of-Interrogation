from NLU import NLU 
from dialogue_manager import DialogueManager
from NLG import NLG 
from dialog_tag import DialogTag

def analyze_expected_input(file):
  infile = open(file).read().split("\n")
  outfile = open("component6/grammar/analyzed_inputs.txt", "w")
  model = DialogTag('distilbert-base-uncased')
  for line in infile:
    nlu = NLU(line, model)
    outfile.write(f"{nlu.message}:{nlu.obligations} \n")

if __name__ == "__main__":
  analyze_expected_input("component6/corpora/expected_inputs.txt")
    