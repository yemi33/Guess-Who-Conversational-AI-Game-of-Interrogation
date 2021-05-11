from component6.parser.recursive_descent_parser import RecursiveDescentParser
from component6.grammar.grammar_engine import GrammarEngine

class IslandParser:
  def __init__(self, grammar, verbose = False):
    self.parser = RecursiveDescentParser(grammar = grammar, verbose = verbose)
    self.grammar = grammar
    self.partial_parses = list()

  def parse(self, string):
    '''
    Basic idea
    1. take out the unparsable parts (not stored as terminals in the grammar)
    2. create a list of substrings which consist of terminals only
    3. call parse_substring() to parse each substring
    '''
    # split the input string into tokens
    fragments = string.split()

    # create a list of all symbols appear in the right-hand side of the grammar
    symbol_set = []
    for symbol in self.grammar.grammar.values():
      for rule in symbol.rules:
        for token in rule.body:
          if type(token) == str:
            symbol_set.append(token)

    length = len(fragments)
    index = 0
    subset = []
    valid_set = []
    # check each token and see if it appears in the grammar
    while index < length:
      # if the current token is valid, append it to a subset so that we can keep the adjecent valid tokens together
      if fragments[index] in symbol_set:
        subset.append(fragments[index])
      # if the current token is not valid, check if the subset has some tokens already and append the non-empty subset to the valid_set
      elif len(subset) > 0:
        valid_set.append(subset)
        subset = []
      # move on to the next token
      index += 1
    for sets in valid_set:
      print(sets)
    
    # convert the sub_set inside the valid_set into string and store it in the substring_set
    substring_set = []
    for item in valid_set:
      sub_string = " ".join(item)
      substring_set.append(sub_string)

    # parse each string in substring_set
    for string in substring_set:
      self.parse_substring(string)
    
    # return the list of partial parses sorted in descending order of length
    self.partial_parses.sort(key = lambda x: len(x), reverse = True)
    return self.partial_parses

  def parse_substring(self, sub_string):
    '''
    Basic idea 
    1. fragment the string
    2. attempt to parse this string 
    3. if there is a successful parse, check this partial parse is a subset of some parse, if yes, discard, if no keep
    '''
    
    # split the input string into tokens
    fragments = sub_string.split()
    # length of the substring
    length = len(sub_string)

    # while the length of the substring is greater than or equal to 1
    while length >= 1:
      start = 0
      while start <= len(fragments) - length:
        # get the substring
        substring = " ".join(fragments[start:start + length])
        # parse the substring
        for symbol in self.grammar.grammar.keys(): # try out all symbols
          result = self.parser.parse(string = substring, start_symbol_name = symbol)
          parse_already_exists = False
          # if the result is not None, that means there was a successful parse
          if result != None:
            # check if the result is a subset of some other partial parse
            for parse in self.partial_parses:
              if result in parse:
                parse_already_exists = True
            # if it's not a subset of any of the existing parses, add it to the list
            if not parse_already_exists:
              self.partial_parses.append(result)
        # move the window
        start += 1
      # decrease the length of the expected substring
      length -= 1
    
if __name__ == "__main__":
  grammar = GrammarEngine("component4.txt").grammar
  parser = IslandParser(grammar = grammar, verbose = False)
  string = "Hello, I am Yemi, a senior CS  major. I live in Cassat. A usual day looks like this for me: I wake up at 11  and go to work  after having ramen  for breakfast. After that, I drop my stuff in Cassat, have lunch in LDC, and then work in Little Joy." 
  print(parser.parse(string = string))