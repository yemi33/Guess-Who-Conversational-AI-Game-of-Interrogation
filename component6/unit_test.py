from NLU import NLU
from dialogue_manager import DialogueManager
from NLG import NLG
from guess_who import *

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
Testing NLU
"""
def test_nlu():
  messages = ["I know you did it. If you come clean now, you won't have to die in prison.", "What were you doing last night?"]
  for message in messages:
    nlu = NLU(message)
    print(nlu)

'''
Testing Dialogue Manager
'''
def test_dialogue_manager():
  dialogue_manager = DialogueManager(suspect_identity="guilty")
  message = "What were you doing last night?"
  print(dialogue_manager.strategize(message))
  '''
  Sample Output:
  {
    'resolve_obligation': 'statement-non-opinion-neutral-subjective', 
    'address_sentiment': 'neutral', 
    'address_subjectivity': 'subjective', 
    'keyphrase_trigger': 'Activity-Response', 
    'eliza': 'neutral-eliza', 
    'extracted_info': 'question-about-extracted-info', 
    'utilize_dependency_structure': None, 
    'marcov_chain': 'I mean ’? been doing?\n about, What ’s happenin ’?\n one down yeah.,. doing?\n', 
    'address_profanity': None, 
    'address_other_feature': None
  }
  '''

'''
Testing NLU -> Dialogue Manager -> NLG flow
'''

def test_nlg():
  dialogue_manager = DialogueManager(suspect_identity="guilty")
  message = "What were you doing last night?"
  response = dialogue_manager.respond(message)
  print(response)
  '''
  Sample Output:
  {
    'resolve_obligation': 'statement-non-opinion-neutral-subjective', 
    'address_sentiment': 'neutral', 
    'address_subjectivity': 'subjective', 
    'eliza': " I'm glad to know that  What were i doing last night?.", 
    'eliza_variable': 'What were i doing last night?', 
    'extracted_info': 'You know,  You also mentioned before that  What were you doing last night?. ', 
    'extracted_info_variable': 'What were you doing last night?', 
    'marcov_chain': 'I mean what? what? younger, ’? she been\n yeah. younger,?. yeah. about, I'
  }
  '''

'''
Testing NLU -> Dialogue Manager -> NLG -> Guess Who flow
'''

def test_guess_who():
  guess_who = GuessWho()
  dialogue_manager = guess_who.dialogue_manager
  message = "What were you doing last night?"
  response = dialogue_manager.test_single_respond(message, "keyphrase_trigger")
  print(response)

if __name__ == "__main__":
  # test_nlu()
  # test_dialogue_manager()
  # test_nlg()
  test_guess_who()