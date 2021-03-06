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
    # removed 'utilize_dependency_structure': None, 
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
  response = dialogue_manager.test_single_respond(message, "extracted_info")
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
'''
List of techniques
      "resolve_obligation" : (0.0,0.4),
      "keyphrase_trigger" : (0.4,0.6),
      "eliza" : (0.6,0.7),
      "extracted_info" : (0.7,0.8),
      "markov_chain" : (0.8,0.9),
      "address_profanity" : (0.9,1.0)
      # removed "utilize_dependency_structure" : (0.8,0.9),
      # changed "marcov_chain" : (0.9,0.95),
      # changed "address_profanity" : (0.95,1.0)
'''
def test_guess_who():
  guess_who = GuessWho()
  dialogue_manager = guess_who.dialogue_manager
  message = "What was your relationship with Tyler?"
  response = dialogue_manager.test_single_respond(message, "keyphrase_trigger") # plug in a technique and test to see if the output is reasonable
  print(response)

if __name__ == "__main__":
  # test_nlu()
  # test_dialogue_manager()
  test_nlg()