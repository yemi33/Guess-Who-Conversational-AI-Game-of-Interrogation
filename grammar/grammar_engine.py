import random

class Grammar:
  def __init__(self, grammar):
    self.grammar = grammar
  
  def __repr__(self):
    return str(self.grammar)
  
  def find(self, symbol_name):
    '''
    The grammar
    should be a class that has a find() method that
    accepts a 'symbol_name' and returns the NonterminalSymbol
    object with the given name.
    '''
    return self.grammar[symbol_name]
  

class GrammarEngine:
  def __init__(self, path_to_file):
    self.grammar_file = self._load_corpus(path_to_file)
    self.grammar = Grammar(self.parse_grammar(self.grammar_file))
    self.variables = dict()
  
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
    corpus_text = open(f"{corpus_filename}").read()
    return corpus_text
  
  # Yemi, Maanya
  def parse_grammar(self, grammar_file):
    '''
    parse the grammar file to create a bunch of NonterminalSymbol objects and ProductionRule objects.

    Syntax:
    greeting -> <greeting word> <#name> <punct> blah
    greeting -> Hello
    greeting word -> Hello|Hey|Hi|Yo
    name -> <first name> <last name> | <first name>
    first name -> Abdul|Betty|Caesar
    last name -> Xavier|Yi|Zimmer
    punct -> .|! 
    
    dictionary
    key: nonterminal_symbol
    value: a list of production rules for which this symbol is the head

    {greeting: [Object([<greeting word>,<name>,<punct>]), Object([Hello])]}
    '''
    punctuations_for_parse = '''!()-[]{};:'"\,./?@#$%^&*_~\t'''
    dictionary = dict()
    dictionary_of_nonterminal_symbols = dict()
    grammar = grammar_file.split("\n")
    is_comment = False 

    for line in grammar:
      # deal with comments
      if line == "'''":
        if is_comment:
          is_comment = False
          continue
        else:
          is_comment = True
      if is_comment:
        continue

      split_text = line.split("->")
      head, body = split_text[0].strip(), split_text[1].strip()
      if head not in dictionary_of_nonterminal_symbols:
        head_nonterminal = NonterminalSymbol(name = head)
        dictionary_of_nonterminal_symbols[head] = head_nonterminal
      if head not in dictionary:
        dictionary[head] = list()
    
      list_of_symbols = list()
      if "<" in body:
        index = 0
        while index < len(body):
          if body[index] == "<":
            index += 1
            savable = False
            if body[index] == "#":
              savable = True
              index += 1
            index_of_end_symbol = body.index(">", index) # start looking for the symbol from index
            nonterminal_symbol = NonterminalSymbol(name = body[index:index_of_end_symbol], savable = savable)
            dictionary_of_nonterminal_symbols[nonterminal_symbol.name] = nonterminal_symbol
            list_of_symbols.append(nonterminal_symbol)
            index = index_of_end_symbol + 1
          elif body[index] == "|":
            dictionary[head].append(list_of_symbols)
            list_of_symbols = list()
            index += 1
          # deal with the case of loading in corpora
          elif body[index] == "$":
            index_of_next_delimeter = body.find("|", index)
            corpus_filename = ""
            if index_of_next_delimeter == -1:
              corpus_filename = body[index + 1:]
              index = len(body)
            else:
              corpus_filename = body[index + 1:index_of_next_delimeter]
              index = index_of_next_delimeter
            corpus_values = self._load_corpus(corpus_filename=f"corpora/{corpus_filename}").split("\n")
            for item in corpus_values:
              dictionary[head].append([item.strip()])
          else:
            string = ""
            while index < len(body) and body[index] != "<" and body[index] != "|" and body[index] != "$":
              string += body[index]
              index += 1
            list_of_symbols.append(string)
  
        dictionary[head].append(list_of_symbols)
      else:
        split_string = body.split("|") 
        for item in split_string:
          dictionary[head].append([item.strip()])
      list_of_symbols = list()

    for key in dictionary.keys():
      list_of_production_rules = list()
      for value in dictionary[key]:
        production_rule = ProductionRule(key, value)
        list_of_production_rules.append(production_rule)
      nonterminal_symbol = dictionary_of_nonterminal_symbols[key]
      nonterminal_symbol.rules = list_of_production_rules
    
    for key in dictionary_of_nonterminal_symbols.keys():
      updated_list_of_rules = list()
      for production_rule in dictionary_of_nonterminal_symbols[key].rules:
        updated_rule = list()
        for token in production_rule.body:
          updated_token = token
          if type(token) != str and token.name in dictionary_of_nonterminal_symbols.keys():
            updated_token = dictionary_of_nonterminal_symbols[token.name]
          updated_rule.append(updated_token)
        
        # remove leading or trailing white space
        if updated_rule[0] == " ":
          updated_rule = updated_rule[1:]
        if len(updated_rule) > 0 and updated_rule[len(updated_rule) - 1] == " ":
          updated_rule = updated_rule[:-1]
        
        updated_list_of_rules.append(ProductionRule(production_rule.head, updated_rule))
      dictionary_of_nonterminal_symbols[key].rules = updated_list_of_rules

    # for key in dictionary_of_nonterminal_symbols.keys():
    #   print(f"symbol: {key} / rules: {dictionary_of_nonterminal_symbols[key].rules}")
    return dictionary_of_nonterminal_symbols
  
  # Sue
  def generate(self,start_symbol):
    '''
    while there is at least one nonterminal symbol in the intermediate output, rewrite the leftmost nonterminal symbol in that intermediate output; once you have only terminal symbols (strings), concatenate them to form your final output. 
    '''
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~\t'''
    intermediate_list = [start_symbol]
    symbols_list = self._rewrite_symbols(intermediate_list, 0)
    concatenated_string = ""
    for item in symbols_list:
      if item not in punctuations and len(concatenated_string) != 0 and item[0] not in punctuations:
        concatenated_string = concatenated_string + " " + item
      else:
        concatenated_string = concatenated_string + item
    return concatenated_string

  def _rewrite_symbols(self, intermediate_list, curr_index): 
    while curr_index < len(intermediate_list):
      curr_symbol = intermediate_list[curr_index]
      if curr_symbol in self.variables.keys():
        intermediate_list.insert(curr_index + 1, self.variables[curr_symbol])
        intermediate_list.remove(curr_symbol)
        self._rewrite_symbols(intermediate_list, curr_index)
      elif curr_symbol in self.grammar.grammar.keys():
        random_rule = random.choice(self.grammar.grammar[curr_symbol].rules)
        if self.grammar.grammar[curr_symbol].savable:
          self.set_variable(curr_symbol, random_rule.body[0])
        insert_index = curr_index
        for symbol in random_rule.body:
          insert_index += 1
          intermediate_list.insert(insert_index, str(symbol))
        intermediate_list.remove(curr_symbol)
        self._rewrite_symbols(intermediate_list, curr_index)
      curr_index += 1
    return intermediate_list

  # Nicole
  def set_variable(self, key, value):
    '''
    accepts a key and value, and makes an entry in the self.variables dictionary
    '''
    self.variables[key] = value

class NonterminalSymbol:
  def __init__(self, name, production_rules = list(), savable = False):
    '''
    Each NonterminalSymbol object will have a rules instance variable, which stores a list of ProductionRule objects where this symbol is the head
    '''
    self.name = name
    self.rules = production_rules
    self.savable = savable
  
  def __repr__(self):
    return f"{self.name}"

class ProductionRule:
  def __init__(self, head, body):
    '''
    Each ProductionRule object will have a head instance variable, which stores the NonterminalSymbol object associated with the symbol on the left-hand side of the rule, and a body instance variable, which stores the body of the rule (i.e., the right-hand side of the rule); the body should be represented as a list of NonterminalSymbol objects and strings (the latter being the terminal symbols). 
    '''
    self.head = head
    self.body = body
  
  def __repr__(self):
    return f"rule({self.body})"

if __name__ == "__main__":
  grammar_engine = GrammarEngine("grammar/test_grammar.txt")
  grammar = grammar_engine.grammar

  for nonterminal in grammar.grammar:
    print(nonterminal)
    print(grammar.find(nonterminal).rules)