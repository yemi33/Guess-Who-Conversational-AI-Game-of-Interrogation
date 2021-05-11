from NLU import NLU
from dialogue_manager import DialogueManager
from NLG import NLG
import guess_who

"""
pip install better_profanity
pip install -U textblob
python -m textblob.download_corpora
pip install -U pip setuptools wheel
pip install -U spacy
python -m spacy download en_core_web_sm 
pip install DialogTag

"""
"""
Testing NLU functions
"""
def test_nlu_whole():
  suspect = guess_who.Suspect("guilty", None)
  message = "I know you did it. If you come clean now, you won't have to die in prison."
  nlu = NLU(message)
  print(nlu)

'''
Testing Dialogue Manager functions
'''


'''
Testing NLU -> Dialogue Manager -> NLG flow
'''
def test_eliza_effect():
  suspect = guess_who.Suspect("guilty", None)
  dialogue_manager = DialogueManager(suspect)
  message = "I know you did it. If you come clean now, you won't have to die in prison."
  nlu = NLU(message)
  strategy = dialogue_manager.strategize(nlu)
  strategy_related_to_eliza = strategy["eliza"]
  nlg = NLG(dialogue_manager=dialogue_manager, response_strategy=strategy)
  response = nlg.test_single_response("eliza")
  print(response)

def test_marcov_chain():
  suspect = guess_who.Suspect("guilty", None)
  dialogue_manager = DialogueManager(suspect)
  message = "I know you did it. If you come clean now, you won't have to die in prison."
  nlu = NLU(message)
  strategy = dialogue_manager.strategize(nlu)
  marcov_generated_sentence = strategy["marcov_chain"]
  nlg = NLG(dialogue_manager=dialogue_manager, response_strategy=strategy)
  response = nlg.test_single_response("marcov_chain")
  print(response)


if __name__ == "__main__":
  test_nlu_whole()
  # test_eliza_effect()
  # test_marcov_chain()