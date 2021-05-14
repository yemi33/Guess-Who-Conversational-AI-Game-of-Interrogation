import nltk, re, pprint
import random
from nltk import word_tokenize, regexp_tokenize
import statistics
import spacy
import sys

class MarkovModel:
  def __init__(self, corpus_filename, level, order, pos=bool(False), hybrid=bool(False)):
    '''
    Creates a MarcovModel object.

    Args:
      corpus_filename: 
        string representing the path to a text file containing sample sentences
      level: 
        "character" or "word" (which mode to train the model in)
      order: 
        integer defining the model's order 
    '''
    self.corpus_filename = corpus_filename
    self.corpus, self.testset = self._load_corpus(corpus_filename)
    self.tokens = []
    self.pos = pos
    self.hybrid = hybrid
    if self.pos:
      self.level = "word"
    else:
      self.level = level
    self.order = order
    self.token_to_token_transitions = dict()
    self.pos_to_pos_transitions = dict()
    self.pos_to_token_transitions = dict()
    self.authorship_estimator = (0, 0) # first number represents the mean likelihood value, second value represents the standard deviation 
    self.nlp = spacy.load("en_core_web_sm")
    self.nlp.max_length = sys.maxsize
    self.nlp.select_pipes(enable=["tok2vec", "tagger"])
    self.train()

  # Sue 
  def train(self):
    '''
    Populates 'transitions' dictionary of n-grams, where n is the given order of the model. In addition, calculates authorship_estimator (aka mean and stdev of likelihoods for the second half of the model).
    '''
    split_corpus = self.corpus.split("\n")

    # If the corpus is william shakespeare collected works, just reduce the size of the corpus for now (for future, make the code more efficient by serializing)
    if self.corpus_filename == "william_shakespeare_collected_works.txt":
      self.corpus = "\n".join(split_corpus[:len(split_corpus) // 3])
    else:
      self.corpus = "\n".join(split_corpus[:(len(split_corpus) * 8) // 10])
   
    corpus_to_be_used_for_estimation = split_corpus[((len(split_corpus) * 8) // 10) + 1:]

    '''
    POPULATING (appropriate) TRANSITIONS DICTIONARY portion
    '''
    if self.hybrid:
      self._hybrid_train()
    elif self.pos:
      self._pos_train()
    else:
      self._word_train()

    '''
    CALCULATING AUTHORSHIP ESTIMATOR portion
    '''
    # self.authorship_estimator = self._caculate_authorship_estimator(corpus_to_be_used_for_estimation)
  
  # Yemi
  def _hybrid_train(self):
    self._pos_train()
    self._word_train()

  # Nicole
  def _word_train(self):
    '''
    Trains the model based on token-token transitions (original)
    aka. populates token_to_token_transitions.
    '''
    self.tokens = self._tokenize(self.corpus)

    # puntuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~\t'''
    puntuations = '''\t'''
    # count how many times each token appears when a given n-gram in a nested list
    num = 0 # position of the first word in the n-gram in the corpus
    for token in self.tokens:
      # puntuation does not go into the n-gram
      if token not in puntuations:
        gram = [token] # a list of tokens) that go into the ngram
        cur_order = 1
        word_num = 1 # the length of the n-gram
        # create valid n-gram
        while cur_order < self.order:
          # make sure it is not out of index and the n-gram doesn't have puntuations
          if num+cur_order < len(self.tokens) and self.tokens[num+cur_order] not in puntuations:
            # gram = gram + " " + self.tokens)[num+cur_order]
            gram.append(self.tokens[num+cur_order])
            word_num += 1
          cur_order += 1
        
        gram = self._construct_text(gram).strip()
        
        # make sure n-gram do not contain puntuations and there is at least one more token in the corpus
        if word_num == self.order and num < len(self.tokens)-self.order:
          value = self.tokens[num+self.order] 
          # puntuation does not count as token
          if value not in puntuations:
            # create the dictionary with values in nested lists
            if gram in self.token_to_token_transitions:
              not_added = True
              for item in self.token_to_token_transitions[gram]: # "the" : [["fox", 3], ["bear", 5]]
                if item[0] == value:
                  item[1] += 1
                  not_added = False
              if not_added:
                self.token_to_token_transitions[gram].append([value,1])
            else:
              self.token_to_token_transitions[gram] = [[value,1]]   
      num += 1

    # calculate probablity and convert list to tuple
    
    all_keys = self.token_to_token_transitions.keys()
    for key in all_keys:
      total_appearance = 0
      specific_values = self.token_to_token_transitions[key]
      # calculate the total appearances
      # "the" : [["fox", 3], ["bear", 5]]
      for value in specific_values:
        total_appearance = total_appearance + value[1]
      # calculate the frequency_range for each token and convert the list to tuple
      range_num = 0 # start of a new range
      for value in specific_values:
        value[1] = (range_num, range_num+value[1]/total_appearance)
        range_num = value[1][1] # update lower bound
        # convert the nested list into a tuple
      token_num = 0
      while token_num < len(specific_values):
        specific_values[token_num] = tuple(specific_values[token_num])
        token_num += 1
  
  # Maanya, Nicole
  def _pos_train(self):
    '''
    Trains the model based on pos_tag - pos_tag transitions 
    aka. populates the transitions dictionary based on this scheme.
    '''

    '''
    POPULATING POS_TO_POS DICTIONARY portion
    '''
    self.tokens = self.nlp(self.corpus)
        
    for count in range(len(self.tokens)-self.order+1):
      n_gram = self.tokens[count:count+self.order] #exclusive i.e. l=[1,2,3], l[0:2] = [1,2]
      n_gram_tags = []
      #syntax tags will make up keys, so create list then convert to tuple for each key
      for token in n_gram:
        if "\n" in token.text:
          n_gram_tags.append("NLN")
        else:
          n_gram_tags.append(token.tag_)
      if count != len(self.tokens)-self.order:
        syntax_value = self.tokens[count+self.order].tag_
      else:
        #edge case: n_gram is at the end of the text
        syntax_value = None
      #NOTE: keys can't be mutable, so key is tuple instead of list
      n_gram_tags_tuple = tuple(n_gram_tags)
      if n_gram_tags_tuple not in self.pos_to_pos_transitions.keys():
        if syntax_value == None:
          #NOTE: may need to change assigned value because it may throw some errors depending on generate()
          self.pos_to_pos_transitions[n_gram_tags_tuple] = None
        else:
          self.pos_to_pos_transitions[n_gram_tags_tuple] = [[syntax_value,1]]
      else:
        for value in self.pos_to_pos_transitions[n_gram_tags_tuple]:
          already_a_value = False
          #update dicitonary
          if syntax_value == value[0]:
            value[1]+=1 # increment count
            already_a_value = True
        # if not already a value
        if already_a_value == False:
          self.pos_to_pos_transitions[n_gram_tags_tuple].append([syntax_value,1])
    #update dictionary so values are tuples and percents not numbers
    for key in self.pos_to_pos_transitions.keys():
      value_list = self.pos_to_pos_transitions[key]
      #ex. value_list = [['RB',1],['VBZ',2]]
      total_tag_count = 0
      if value_list == None:
        pass
      else:
        # add up the total count
        for tag in value_list:
          #ex. tag = ['RB',1]
          total_tag_count += tag[1]

        first_value = True
        previous_range = ()
        tuple_to_replace_list = []

        # calculate percentage
        for tag in value_list:
          percent = tag[1]/total_tag_count
          if first_value == True:
            percent_range = tuple((0.0,percent))
            first_value = False
            previous_range = percent_range
          else:
            percent_range = tuple((float(previous_range[1]),float(previous_range[1])+percent))
            previous_range = percent_range

          tuple_to_replace_list.append(tuple((tag[0],percent_range)))
        self.pos_to_pos_transitions[key] = tuple(tuple_to_replace_list)

    '''
    POPULATING POS_TO_TOKEN DICTIONARY portion
    '''
    self._map_pos_to_tokens()

  # Maanya
  def _map_pos_to_tokens(self):
    '''
    Requirements:
      Create a new subroutine in your training procedure that produces a dictionary mapping POS tags to probability ranges over the tokens) to which those tags were attached when the corpus was tagged. For instance, if the tag NP was attached to the token Northfield once
      and to the token Minnesota thrice, the value in this dictionary for the key NP would be
      [(“Northfield”, (0.0, 0.25)), (“Minnesota”, (0.25, 1.0))].

      populate self.pos_to_token_transitions dictionary
    '''
    #["UH": [("Hello", 1)], ".": [(".", 1)]]

    pos_token_list = self.generate_pos_tags(self.corpus)
    for pos_token_pair in pos_token_list:
        if pos_token_pair[0] not in self.pos_to_token_transitions:
            self.pos_to_token_transitions[pos_token_pair[0]] = [(pos_token_pair[1], 1)]
        else:
            present = False
            # token_value = ("Hello", 1)
            # self.pos_to_token_transitions[pos_token_pair[0]] = [("Hello", 1), ("Hey", 1)]
            for token_value in self.pos_to_token_transitions[pos_token_pair[0]]:
                if pos_token_pair[1] == token_value[0]:
                    present = True
                    token_value = list(token_value)
                    token_value[1] += 1
                    token_value = tuple(token_value)
            if present == False:
                self.pos_to_token_transitions[pos_token_pair[0]].append((pos_token_pair[1], 1))

    for key in self.pos_to_token_transitions.keys():
      value_list = self.pos_to_token_transitions[key]
      #ex. value_list = [(“Northfield”, 1), (“Minnesota”, 3)]
      total_tag_count = 0
      if value_list == None:
        pass
      else:
        # add up the total count
        for tag in value_list:
          #ex. tag = (“Northfield”, 1)
          total_tag_count += tag[1]

        first_value = True
        previous_range = ()
        tuple_to_replace_list = []

        # calculate percentage
        for tag in value_list:
          percent = tag[1]/total_tag_count
          if first_value == True:
            percent_range = tuple((0.0,percent))
            first_value = False
            previous_range = percent_range
          else:
            percent_range = tuple((float(previous_range[1]),float(previous_range[1])+percent))
            previous_range = percent_range

          tuple_to_replace_list.append(tuple((tag[0],percent_range)))
          self.pos_to_token_transitions[key] = tuple_to_replace_list
          # print(self.pos_to_token_transitions)

  # Maanya
  def generate_pos_tags(self, corpus):
    # # Load the standard English model suite
    # nlp = spacy.load("en_core_web_sm")
    # # corpus = re.sub('\n', 'newline', corpus)
    
    # # Update the model suite to allow for a long corpus
    # nlp.max_length = len(corpus)
    # # POS-tag the corpus
    # with nlp.select_pipes(enable=["tok2vec", "tagger"]):
    tagged_tokens = self.nlp(corpus)
    # Print out the tagged tokens
    n_gram_tags = []
    for token in tagged_tokens:
        if "\n" in token.text:
            token.tag_ = 'NLN'
        # print(f"{token}/{token.tag_}") 
        n_gram_tags.append((token.tag_, token.text))
    return(n_gram_tags)

  # Maanya
  def _tokenize(self, text):
    '''
    Helper method to tokenize a certain line of sentence.

    Args:
      text: 
        text to be tokenized

    Returns:
      list of tokens)

    Requirements:
      Have to make sure to deal with white space (include newline)
      tokenize at the level of the entire corpus
    '''
    #makes use of the nltk library and regular expressions to tokenize a corpus
    tokens_list = []
    if self.level == "word":
        tokens_list = regexp_tokenize(text,'\w+|\$[\d\.]+|\S+|\n|\r|\t')
    else:
        for char in text:
            tokens_list.append(char)
    #added this for loop and if statement, tabs were still in the list when only remove() was called
    for lists in tokens_list:
      if '\t' in lists:
        tokens_list.remove('\t')
    return tokens_list
  
  # Maanya, Yemi
  @staticmethod
  def _load_corpus(corpus_filename):
    '''
    Returns the contents of a corpus loaded from a corpus file.

    Credit to James (Took from Comp Med HW file)

    Args:
      corpus_filename:
        The filename for the corpus that's to be loaded.

    Returns:
      A single string

    Raises:
      IOError:
        There is no corpus file with the given name in the 'corpora' folder.
    '''
    corpus_text = open(corpus_filename).read()
    return corpus_text[:(len(corpus_text) * 8) // 100], corpus_text[:((len(corpus_text) * 8) // 10) + 1]

  def generate(self, length, prompt="\n"):
    '''
    Generates text based on the statistical language model.
    '''
    if self.hybrid:
      return self._hybrid_generate(length, prompt)
    elif self.pos:
      return self._adapted_pos_generate(length, prompt)
    else:
      return self._original_generate(length, prompt)
  
  # Nicole
  def _original_generate(self, length, prompt="\n"):
    '''
    Generates a text of 'length' tokens which begins with 'prompt' token if given one.

    Args:
      length: 
        length of the text to be generated
      prompt: 
        starting tokens) (default: "\n")
    
    Returns:
      A string containing the generated text
    '''
    gen_text = prompt
    n_gram = ""
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n'''

    tokenized_prompt = self._tokenize(prompt)
    length_of_prompt = len(tokenized_prompt)
    
    #prompt does not have a complete n-gram
    if length_of_prompt < self.order:
      n_gram, gen_text = self._find_n_gram(prompt, tokenized_prompt, length_of_prompt, gen_text, length)
    else: #prompt is longer than or equal to one n-gram, reduce/keep the same
      n_tokens = tokenized_prompt[length_of_prompt - self.order:]
      n_gram = self._construct_text(n_tokens, 1)
      #check if n_gram is in our dictionary
      if n_gram not in self.token_to_token_transitions.keys():
        #find key containing prompt
        n_gram, gen_text = self._find_n_gram(n_gram, self._tokenize(n_gram), len(self._tokenize(n_gram)), gen_text, length)

    while len(self._tokenize(gen_text)) < length:
      values = self.token_to_token_transitions.get(n_gram)
      if values is None:
        n_gram, gen_text = self._find_n_gram(n_gram, self._tokenize(n_gram), len(self._tokenize(n_gram)), gen_text, length)
        values = self.token_to_token_transitions.get(n_gram)
      random_num = random.random()
      # ["the": (("end", (0,.5)), ("fox", (.5,1)))]
      for t in values:
        probability_range = t[1]
        if random_num > probability_range[0] and random_num <= probability_range[1]:
          add_word = t[0]
      if self.level == "character":
        gen_text+=add_word
      else:
        if add_word in punctuations:
          gen_text += add_word
        else:
          gen_text += " " + add_word
      #get last n token of generated text
      tokenized_text = self._tokenize(gen_text)
      n_gram = self._construct_text(tokenized_text[len(tokenized_text) - self.order:],1)
      
    return gen_text
  
  # Nicole
  def _find_n_gram(self, prompt, tokenized_prompt, length_of_prompt, gen_text, length):
    '''
    Finds the appropriate n-gram based on the conditions given.
    To be used with original_generate method

    Args:
      prompt:
        prompt inputted to the generate method
      tokenized_prompt:
        prompt tokenized by our model's scheme
      length_of_prompt:
        length of prompt
      gen_text:
        part of a generated text
      length:
        desired length of the generated text (goal)
    
    Returns:
      a string representing an n-gram
    '''
    
    keys = self.token_to_token_transitions.keys()
    n_gram = ""
    #find n-gram CONTAINING the prompt or shortened prompt
    x = 0 #variable to decrement token length of prompt (ex. "the brown" not found, then check if some key begins with "brown")
    while n_gram == "":
      for k in keys:
        if prompt == "\n" and "\n" in k:
          n_gram = k
          break
        split_key = self._tokenize(k)
        #see if prompt is the start of key k
        shortened_key = split_key[0:length_of_prompt]
        #store to add to gen_text when valid key is found
        rest_of_key = split_key[length_of_prompt:]
        new_k = self._construct_text(shortened_key,1)
        if new_k == prompt:
          n_gram = k
          gen_text += self._construct_text(rest_of_key, 0)
          #add rest of key to gen_text, ex. key = "brown fox jumps", prompt = "the quick brown", gen_text = "the quick brown fox jumps", n_gram = brown fox jumps
          break #valid dictionary key found
      #if prompt not contained in any n-grams in dictionary, remove first token, check again
      x+=1
      shortened_prompt = tokenized_prompt[x:]
      prompt = self._construct_text(shortened_prompt, 1)
      length_of_prompt = len(shortened_prompt)
      #if no words in the prompt in any dictionary key, choose a random key to start text generation
      if x == len(tokenized_prompt):
        #note: random key not appended to gen_text
        entry_list = list(self.token_to_token_transitions.keys())
        n_gram = random.choice(entry_list)
    if len(self._tokenize(gen_text)) > length:
      less_tokens = self._tokenize(gen_text)[0:self.order]
      gen_text = self._construct_text(less_tokens, 1)
    return n_gram, gen_text

  # Nicole
  def _construct_text(self, tokens, first_token=0):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n'''
    text = ""
    if self.level == "character":
      for token in tokens:
        text+=token
    else:
      for token in tokens:
        if first_token == 1:
          text += token
          first_token+=1
        elif token in punctuations:
          text += token
        elif (self.pos == True or self.hybrid == True) and " " in token:
          text += " "
        else:
          text += " " + token
    return text
  
  # Maanya, Nicole
  def _adapted_pos_generate(self, length, prompt="\n"):
    '''
    Generates a text of 'length' tokens which begins with 'prompt' token if given one.

    Args:
      length: 
        length of the text to be generated
      prompt: 
        starting tokens) (default: "\n")
    
    Returns:
      A string containing the generated text
    '''
    gen_prompt_tags = self.generate_pos_tags(prompt)
    tagged_prompt = []
    for tag in gen_prompt_tags:
      tagged_prompt.append(tag[0])
    tagged_prompt = tuple(tagged_prompt)

    final_tags = list(tagged_prompt)
    n_gram = ""

    length_of_prompt = len(tagged_prompt)
    
    # print(self.pos_to_pos_transitions)
    #prompt does not have a complete n-gram
    if length_of_prompt < self.order:
      n_gram, final_tags = self._find_n_gram_pos(tagged_prompt, final_tags, length_of_prompt, length)
    else: #prompt is longer than or equal to one n-gram, reduce/keep the same
      n_gram = tuple(tagged_prompt[length_of_prompt - self.order:])
      #check if n_gram is in our dictionary
      if n_gram not in self.pos_to_pos_transitions.keys():
        #find key containing prompt
        n_gram, final_tags = self._find_n_gram_pos(tagged_prompt, final_tags, length_of_prompt, length)

    while len(final_tags) < length:
      values = self.pos_to_pos_transitions.get(n_gram)
      if values is None:
        n_gram, final_tags = self._find_n_gram_pos(n_gram, final_tags, length_of_prompt, length)
        values = self.pos_to_pos_transitions.get(n_gram)
      random_num = random.random()
      # ["the": (("end", (0,.5)), ("fox", (.5,1)))]
      for t in values:
        probability_range = t[1]
        if random_num > probability_range[0] and random_num <= probability_range[1]:
          add_tag = t[0]
          final_tags.append(add_tag)
      #get last n token of generated text
      n_gram = tuple(final_tags[len(final_tags) - self.order:])
    
    return self._generate_text_from_tags(tagged_prompt, prompt, final_tags)
  
  # Nicole, Maanya
  def _find_n_gram_pos(self, tagged_prompt, final_tags, length_of_prompt, length):
    keys = self.pos_to_pos_transitions.keys()
    n_gram = ""
    prompt = tagged_prompt
    #find n-gram CONTAINING the prompt or shortened prompt
    x = 0 #variable to decrement token length of prompt (ex. "the brown" not found, then check if some key begins with "brown")
    while n_gram == "":
      for k in keys:
        #see if prompt is the start of key k
        shortened_key = k[0:length_of_prompt]
        #store to add to gen_text when valid key is found
        rest_of_key = list(k[length_of_prompt:])
        if shortened_key == prompt:
          n_gram = k
          for i in rest_of_key:
            final_tags.append(i)
          #add rest of key to gen_text, ex. key = "brown fox jumps", prompt = "the quick brown", gen_text = "the quick brown fox jumps", n_gram = brown fox jumps
          break #valid dictionary key found
      #if prompt not contained in any n-grams in dictionary, remove first token, check again
      x+=1
      prompt = tuple(tagged_prompt[x:])
      length_of_prompt = len(prompt)
      #if no words in the prompt in any dictionary key, choose a random key to start text generation
      if x == len(tagged_prompt):
        #note: random key not appended to gen_text
        entry_list = list(self.pos_to_pos_transitions.keys())
        n_gram = random.choice(entry_list)
    if len(final_tags) > length:
      final_tags = final_tags[0:self.order]
    return n_gram, final_tags

  # Nicole
  def _generate_text_from_tags(self, tagged_prompt, prompt, final_tags):
    gen_text_list = []
    for tag in final_tags[len(tagged_prompt):]:
      if not tag in self.pos_to_token_transitions.keys():
        continue
      values = self.pos_to_token_transitions[tag]
      random_num = random.random()
      for v in values:
        probability_range = v[1]
        if random_num > probability_range[0] and random_num <= probability_range[1]:
          gen_text_list.append(v[0])
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n'''
    last_char_punctuation = False
    for char in prompt:
      if char in punctuations:
        last_char_punctuation = True
    if last_char_punctuation == True:
      beginning = prompt
    else:
      beginning = prompt + " "
    return beginning + self._construct_text(gen_text_list)

  # Yemi
  def _hybrid_generate(self, length, prompt="\n"):
    '''
    Generates texts using a hybrid approach between POS tagging and our original MarcovModel text generation appraoch.

    pos tags to words (self.pos_to_token_transitions)
    pos tags to pos tags (self.transitions)

    pos mode generates more syntactically correct sentences
    regular mode generates more semantically coherent sentences

    Perhaps we can prioritize meaning, then syntax

    Pseudocode:
      generate a text using the original generate method 
      for each n-gram in the generated text, 
        retrieve the pos-tag n-gram
        retrieve the pos-tag of the successor of this n-gram
        see if this pos-tag n-gram exists in the pos_to_pos dictionary
        if it does, check if the successor pos-tag exists in the list of values
          if the successor pos-tag does not exist in the list of values, correct it
            aka. choose probabilistically the new successor pos-tag from the list of values
            use the pos-to-token dictionary to probabilistically choose the next token
          if the successor does exist, great! move on
        if it does not, it means that it most likely is not sytactically correct 
        find a new n-gram that retains parts of the original n-gram, but is syntactically correct (aka exists in the pos_to_pos dictionary)
        check if the successor pos-tag exists in the list of values
          if the successor pos-tag does not exist in the list of values, correct it
            aka. choose probabilistically the new successor pos-tag from the list of values
            use the pos-to-token dictionary to probabilistically choose the next token
          if the successor does exist, great! move on
    '''
    gen_text = self._original_generate(length, prompt).strip()
    # Do some cleaning
    gen_text = gen_text.strip('''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n''')
    gen_text = gen_text.split("\n")
    gen_text = " ".join(gen_text)

    gen_text_tokenized = self.nlp(gen_text)

    start_position = 0
    
    while start_position < (len(gen_text_tokenized) - self.order):
      n_gram = self._construct_text([token.text for token in gen_text_tokenized[start_position:start_position + self.order]])
      n_gram_tags = tuple([token.tag_ for token in gen_text_tokenized[start_position:start_position + self.order]])
      n_gram_successor = gen_text_tokenized[start_position + self.order].text
      n_gram_successor_tag = gen_text_tokenized[start_position + self.order].tag_
      
      # if the n_gram_tags exists, it means that it is a valid syntactical structure
      if n_gram_tags in self.pos_to_pos_transitions.keys():
        # if the n_gram_successor_tag does not exist in the list of values, it does not fit the syntactical structure
        if n_gram_successor_tag not in self.pos_to_pos_transitions[n_gram_tags]:
          gen_text = self._correct_succesor(gen_text, n_gram_tags,start_position + self.order)
          gen_text_tokenized = self.nlp(gen_text) 
      # if the n_gram_tags does not exist, it means that it is NOT a valid syntactical structure
      else:
        new_n_gram_tags = self._find_replacement_n_gram(n_gram_tags)
        gen_text = self._correct_n_gram(gen_text, new_n_gram_tags, start_position, start_position + self.order)

        if n_gram_successor_tag not in self.pos_to_pos_transitions[new_n_gram_tags]:
          gen_text = self._correct_succesor(gen_text, new_n_gram_tags, start_position + self.order)
          gen_text_tokenized = self.nlp(gen_text) 

      start_position += 1 
      
    # do a bit of cleaning
    gen_text = gen_text.strip()
    gen_text = gen_text.strip('''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n''')
    gen_text = gen_text.split("\n")
    gen_text = " ".join(gen_text)
    
    return gen_text
  
  # Yemi
  def _correct_succesor(self, gen_text, n_gram_tags, position_to_correct):
    random_number = random.random()
    new_successor_tag = ""
    
    for successor in self.pos_to_pos_transitions[n_gram_tags]:
      if random_number >= successor[1][0] and random_number < successor[1][1]:
        new_successor_tag = successor[0]
        break

    if new_successor_tag in self.pos_to_token_transitions.keys():
      for token in self.pos_to_token_transitions[new_successor_tag]:
        random_number = random.random()
        if random_number >= token[1][0] and random_number < token[1][1]:
          gen_text_tokenized = [token.text for token in list(self.nlp(gen_text))]
          gen_text_tokenized[position_to_correct] = token[0]
          gen_text = self._construct_text(gen_text_tokenized, 1)
          break
    
    # minor clean-up
    gen_text = gen_text.strip()
    gen_text = gen_text.strip('''!()-[]{};:'"\,<>./?@#$%^&*_~\t\n''')
    return gen_text
  
  # Yemi
  def _correct_n_gram(self, gen_text, n_gram_tags, start_position, end_position):
    random_number = random.random()
    new_n_gram = []
   
    for tag in n_gram_tags:
      for token in self.pos_to_token_transitions[tag]:
        if random_number >= token[1][0] and random_number < token[1][1]:
          new_n_gram.append(token[0])

    gen_text_tokenized = [token.text for token in list(self.nlp(gen_text))]
 
    # replace the specific n-gram portion of the gen_text
    index = 0
    for i in range(start_position,end_position):
      gen_text_tokenized[i] = new_n_gram[index]
      index += 1
    
    updated_gen_text = self._construct_text(gen_text_tokenized)
    return updated_gen_text

  # Yemi
  def _find_replacement_n_gram(self, n_gram_tags):
    start_position = 1

    while (start_position < len(n_gram_tags) - 1):
      fragment = n_gram_tags[start_position:]
      for n_gram_tag in self.pos_to_pos_transitions.keys():
        if fragment in n_gram_tag: # let's see if this takes too long
          return n_gram_tag
      start_position += 1
    
    # if no replace could be found with the fragments, get the random n_gram tag
    random_n_gram_tags = random.choice(list(self.pos_to_pos_transitions.keys()))
    return random_n_gram_tags

  # Yemi
  def estimate(self, text):
    '''
    Returns a single string floating-point value: a (normalized) z-score estimate of the likelihood that this text could have been produced by the model at hand

    Args:
      text: 
        text to be analyzed
    
    Returns:
      A floating point estimate of the likelihood of authorship
    '''
    likelihood_of_this_text = self._calculate_likelihood(text)
    return (likelihood_of_this_text - self.authorship_estimator[0]) / self.authorship_estimator[1]

  # Yemi
  def _caculate_authorship_estimator(self, corpus_to_be_used_for_estimation):
    '''
    Helper method to calculate the authorship estimator for the model.

    Args:
      corpus_to_be_used_for_estimation:
        corpus to be used for estimation
    
    Returns:
      the mean and stdev of the model's likelihood values
    '''
    total = 0
    likelihoods = []
    for line in corpus_to_be_used_for_estimation:
      likelihood = self._calculate_likelihood(line)
      likelihoods.append(likelihood)
    mean = statistics.mean(likelihoods)
    standard_dev = statistics.stdev(likelihoods) 
    
    return (mean, standard_dev)
  
  # Yemi
  def _calculate_likelihood(self, text):
    '''
    Helper method to caculate the likelihood of a given text, based on the transitions dictionary of the trained model.

    Args:
      text:
        text to be analyzed
    
    Returns:
      A single number representing the likelihood (aggregate of probabilities) of this text being authored by the author of the model
    '''
    likelihood = 0

    # word_tokenize the string
    string_to_be_analyzed = self._tokenize(text) # this tokenize function should take care of whether to tokenize it in terms of words or characters depending on the object's level

    actual_successor = ""

    for i in range(len(string_to_be_analyzed) - self.order):
      # get the token according to the order
      # token = " ".join(string_to_be_analyzed[i:i + self.order])
      token = self._construct_text(string_to_be_analyzed[i:i + self.order])
      # retrieve the actual sucessor
      actual_successor = string_to_be_analyzed[i + self.order]
      # retrieve the values from the dictionary if one exists
      if token in self.token_to_token_transitions.keys():
        potential_successors = self.token_to_token_transitions[token]
        # if the actual sucessor of the token is in transitions dictionary, add the corresponding probability to likelihood
        for successor in potential_successors:
          if actual_successor == successor[0]:
            likelihood += successor[1][1] - successor[1][0]
    
    # take the average to account for normalizing with respect to length
    if (len(string_to_be_analyzed) != 0):
      return likelihood / len(string_to_be_analyzed)
    return likelihood

if __name__ == "__main__":
    model = MarkovModel(corpus_filename = "alexander_dumas_collected_works.txt", level = "word", order = 2, pos = False, hybrid = False)
    print(model.generate(20, "I wonder if there"))
