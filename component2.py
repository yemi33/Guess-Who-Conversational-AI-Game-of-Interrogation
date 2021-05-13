#Maanya (working on local terminal but not here)
from dialog_tag import DialogTag
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_VERBOSITY'] = 'critical'

def component2():
  model = DialogTag('distilbert-base-uncased')

  sentence = "I'll probably go to shopping today."
  output = model.predict_tag(sentence)
  print(output)
  # output: 'Statement-non-opinion'

  sentence = "Why are you asking me this question again and again?"
  output = model.predict_tag(sentence)
  print(output)
  # output: 'Wh-Question'

  sentence = "What did you do last night?"
  output = model.predict_tag(sentence)
  print(output)
  # output: 'Wh-Question'

  sentence = "I know you did it."
  output = model.predict_tag(sentence)
  print(output)
  # output: 'Statement-non-opinion'

if __name__ == "__main__":
  component2()

