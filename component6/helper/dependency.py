import spacy
from grammar.grammar_engine import GrammarEngine 
from parser.island_parser import IslandParser
from helper.eliza import Eliza
import random

class Dependency:
  def find_actionable_chunk(self,message):
    nlp = spacy.load("en_core_web_sm")
    message = nlp(message)
    verb_chunk = self.modified_find_verb_chunk(message)
    output = {
      "subject" : verb_chunk["subject"], #string
      "verb" : verb_chunk["verb"], #string
      "object" :verb_chunk["object"], #string
      "changed_verb" : self.change_verb(message), #string
      # "derived_question" : self.derive_question(message) #string
    }
    return output

  # needs fix
  def modified_find_verb_chunk(self,doc):
    """
    Returns a dictionary representing a simple verb chunk
    with a subject, verb, object.
    """
    verb_chunk = {
      "subject": "",
      "verb": "",
      "object": "",
    }
    for noun_chunk in doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      subj = noun_chunk.root
      verb = subj.head
      if verb.n_rights > 0:
        child = list(verb.rights)[0] # only consider children to the right of this verb
        verb_chunk["subject"] = subj.text
        verb_chunk["verb"] = verb.text
        verb_chunk["object"] = " ".join([child.text for child in child.subtree])
        break

    return verb_chunk
  
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

  def find_subject_chunk(self,doc):
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

  def find_object_chunk(self,doc):
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

  def find_subject(self,doc):
    subj_chunk = dict()
    for noun_chunk in doc.noun_chunks:
      if noun_chunk.root.dep_ != "nsubj":
        continue
      subj = noun_chunk.root
      return subj.text
    return None

  def find_verb(self,doc):
    """
    Returns a dictionary representing the verb.
    """
    for noun_chunk in doc.noun_chunks:
      if noun_chunk.root.dep_ != 'nsubj':
        continue
      verb = noun_chunk.root.head
      return verb.text
    return None

  def find_direct_object(self,doc):
    for noun_chunk in doc.noun_chunks:
      if noun_chunk.root.dep_ != "dobj":
        continue
      dobj = noun_chunk.root
      return dobj.text
    return None
  
  def derive_question(self,doc):
    """
    Return a string that rephrases an action in the
    doc in the form of a question.
    'doc' is expected to be a spaCy doc.
    try except blocks are for cases where there wasn't a successful parsing and the values are default strings ("")
    """
    verb_chunk = self.find_verb_chunk(doc)
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
    swapped_pronoun_question = Eliza().swap_pronouns(question)
    return swapped_pronoun_question

  def change_verb(self,doc):
    '''
    Find the synonym of the verb
    Return the new sentence
    '''
    verb = self.find_verb(doc)
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
  dependency = Dependency()
  message = "I want you to tell me what happened."
  print(dependency.find_actionable_chunk(message))