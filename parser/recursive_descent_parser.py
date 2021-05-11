class RecursiveDescentParser:
    """A recursive-descent parser."""

    def __init__(self, grammar, verbose=False):
        """Initialize a RecursiveDescentParser object.

        Args:
          grammar:  A grammar satisfying the requirements given in
                    Component 4 of Homework 3, plus an additional
                    requirement that I will give here. The grammar
                    should be a class that has a find() method that
                    accepts a 'symbol_name' and returns the NonterminalSymbol
                    object with the given name. As in Homework 3, each
                    NonterminalSymbol object should have a 'rules' attribute
                    that is structured as a list of ProductionRule objects.
          verbose:  If True, a partial parse will be printed out at each step.
                    Turn this on to debug, and to see all the backtracking!
        """
        self.grammar = grammar
        self.verbose = verbose

    def parse(self, string, start_symbol_name):
        """Return a parse for the given string, if any.

        Args:
          string:               The string to be parsed.
          start_symbol_name:    The name of the nonterminal symbol that the
                                parser should start from in its process. This
                                comes in handy for island parsing! Though, in
                                that case, you may also want to pass in a
                                partial string.

        Returns:
          The full parse string, if parsing was successful, otherwise None.
        """
        # Retrieve the NonterminalSymbol object for the start symbol
        start_symbol = self.grammar.find(symbol_name=start_symbol_name)
        # Attempt to parse
        remaining, goals, parse, failed = self.descend(
            remaining=string,
            goals=[start_symbol],
            parse=''
        )
        # Pass on the result
        if failed:
            if self.verbose:
                print("\nCould not parse entire string...")
            return None
        if self.verbose:
            print("\nSuccessfully parsed string!")
        return parse

    def descend(self, remaining, goals, parse):
        """Carry out the next step in the recursive descent.

        Args:
          remaining:  The remainder of the string that is yet to be
                      successfully parsed. This shrinks across recursive
                      calls, as parsing is successful, and grows back as
                      backtracking occurs.
          goals:      A list of goals that are to pursued, ordered such
                      that earlier indices hold the goals that are to be
                      pursued soonest.
          parse:      The current partial parse string. This grows across
                      recursive calls, as parsing is successful, and shrinks
                      back down as backtracking occurs.
        Returns:
          This returns modified remaining, goals, and parse values, to
          support the recursive structure, and additionally it returns
          a "failed" boolean value. This is set to False if parsing fails
          at any point, so that the failure signal can be propagated back
          through the recursive call structure to drive backtracking.
        """
        # If verbose mode has been engaged, print out the current partial parse
        if self.verbose:
            print(parse)
        # First, we need to make copies of this list, since if we backtrack,
        # we'll need to revert to our earlier goals. If we don't make a copy,
        # our changes here will also alter the earlier version of our goals,
        # because lists are mutable.
        goals = list(goals)
        # Now it's time to carry out the next step. Let's retrieve our next goal.
        next_goal = goals.pop(0)
        # If the next "goal" is a closing parenthesis (marked by the special
        # string "_)_"), add a closing parenthesis to the parse.
        while next_goal == "_)_":
            parse += ')'
            # If there's no more goals but still remaining input, we need
            # to backtrack.
            if (not goals) and remaining:
                failed = True
                return remaining, goals, parse, failed
            # If there's no more goals and no remaining input, the parse has
            # been successful!
            if (not goals) and (not remaining):
                failed = False
                return remaining, goals, parse, failed
            # Otherwise, retrieve the next goal and continue
            next_goal = goals.pop(0)
        # If the next goal is a terminal symbol, try to match it to the
        # beginning of the remainder of the input string.
        if type(next_goal) == str:
            if not remaining.startswith(next_goal):
                # It didn't match, so propagate a failed signal
                failed = True
                return remaining, goals, parse, failed
            # If we get to here, we matched, so we can consume this part
            # of the input and add it to our parse string.
            remaining = remaining[len(next_goal):]
            parse = parse + next_goal
            return self.descend(remaining=remaining, goals=goals, parse=parse)
        # If we get to here, the next goal is a nonterminal symbol, which we
        # can add to the parse (along with a leading open parenthesis)
        parse += f"({next_goal.name} "
        # Now we need to iterate over this symbol's production rules, one by one
        # and in order, to see if executing one of them will ultimately lead to
        # a successful parse.
        for rule in next_goal.rules:
            # Temporarily execute the rule to produce a new list of goals with
            # the current next_goal replaced with this rule's body.
            temp_goals = rule.body + ["_)_"] + goals
            new_remaining, new_goals, new_parse, failed = self.descend(
                remaining=remaining,
                goals=temp_goals,
                parse=parse
            )
            if failed:
                continue  # Try the next rule
            # If we get to here, this rule worked! Return the results.
            failed = False
            return new_remaining, new_goals, new_parse, failed
        # If we get to here, we exhausted all the rules for this nonterminal
        # symbol, so we need to return a failed signal.
        failed = True
        return remaining, goals, parse, failed
