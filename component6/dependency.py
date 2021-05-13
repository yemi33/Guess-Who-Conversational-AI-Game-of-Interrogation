import spacy
from grammar.grammar_engine import GrammarEngine 
from parser.island_parser import IslandParser
import random
# pip install -U pip setuptools wheel
# pip install -U spacy
# python -m spacy download en_core_web_sm

def find_verb_chunk(doc):
  """
  Returns a dictionary representing a simple verb chunk
  with a subject, verb, object.
  """
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != 'nsubj':
      continue
    subj = noun_chunk.root
    verb = subj.head
    for child in verb.children:
      obj = child
      if child.dep_ == 'dobj':
        verb_chunk = {
          "subject": subj,
          "verb": verb,
          "object": obj
        }
        return verb_chunk
  return None

def find_subject_chunk(doc):
  '''
  Returns a dictionary representing the subject noun phrase with adverb, adjective, and noun
  '''
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != "nsubj":
      continue
    subj = noun_chunk.root
    subj_chunk = dict()
    subj_chunk["adjective"] = []
    subj_chunk["adverb"] = []
    for child in subj.children:
      if child.dep_ == "amod":
        subj_chunk["adjective"].append(child)
      elif child.dep_ == "advmod":
        subj_chunk["adverb"].append(child)
    subj_chunk["subject"] = subj
    return subj_chunk
  return None

def find_object_chunk(doc):
  '''
  Returns a dictionary representing the object noun phrase with adverb, adjective, and noun
  '''
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != "dobj":
      continue
    obj = noun_chunk.root
    obj_chunk = dict()
    obj_chunk["adjective"] = []
    obj_chunk["adverb"] = []
    for child in obj.children:
      if child.dep_ == "amod":
        obj_chunk["adjective"].append(child)
      elif child.dep_ == "advmod":
        obj_chunk["adverb"].append(child)
    obj_chunk["object"] = obj
    return obj_chunk
  return None

def find_subject(doc):
  subj_chunk = dict()
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != "nsubj":
      continue
    subj = noun_chunk.root
    return subj.text
  return None

def find_verb(doc):
  """
  Returns a dictionary representing the verb.
  """
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != 'nsubj':
      continue
    verb = noun_chunk.root.head
    return verb.text
  return None

def find_direct_object(doc):
  dobj_chunk = dict()
  for noun_chunk in doc.noun_chunks:
    if noun_chunk.root.dep_ != "dobj":
      continue
    dobj = noun_chunk.root
    return dobj.text
  return None

def derive_question(doc):
  """
  Return a string that rephrases an action in the
  doc in the form of a question.
  'doc' is expected to be a spaCy doc.
  """
  verb_chunk = find_verb_chunk(doc)
  if not verb_chunk:
      return None
  subj = verb_chunk['subject'].text
  obj = verb_chunk['object'].text
  if verb_chunk['verb'].tag_ != 'VB':
      # If the verb is not in its base form ("to ____" form),
      # use the spaCy lemmatizer to convert it to such
      verb = verb_chunk['verb'].lemma_
  else:
      verb = verb_chunk['verb'].text
  question = f"Why did {subj} {verb} {obj}?"
  return question

def change_verb(doc):
  '''
  Find the synonym of the verb
  Return the new sentence
  '''
  verb = find_verb(doc)
  grammar = GrammarEngine("component6/grammar/general_conversation.txt").grammar
  try:
    rule = grammar.find(verb).rules
  except:
    return None
  index = random.randint(0, len(rule)-1)
  new_verb = str(rule[index])[7:-3]
  new_sentence = ""
  for word in doc:
    if word.text == verb:
      new_sentence = new_sentence + " " + new_verb
    elif len(new_sentence) > 0:
      new_sentence = new_sentence + " " + word.text
    else:
      new_sentence = word.text
  return new_sentence


if __name__ == "__main__":
  nlp = spacy.load("en_core_web_sm")
  doc = nlp("Autonomous fast cars shift insurance liability toward manufacturers")
  #doc = nlp("Where were you last night?")
  #doc1 = nlp("Autonomous fast cars shift insurance liability toward manufacturer")
  # print(doc.similarity(doc1))
  #doc = nlp("I would like to know more about science.")

  # for chunk in doc.noun_chunks:
  #    print("text: ", chunk.text, "| root text: ", chunk.root.text, "| dep: ", chunk.root.dep_, "| root head: ", chunk.root.head.text)

  print("verb chunk: ", find_verb_chunk(doc))
  print("subject chunk: ", find_subject_chunk(doc))
  print("object chunk: ", find_object_chunk(doc))
  print("S: ", find_subject(doc))
  print("V: ", find_verb(doc))
  print("DO: ", find_direct_object(doc))
  print(derive_question(doc))
  print(change_verb(doc))
