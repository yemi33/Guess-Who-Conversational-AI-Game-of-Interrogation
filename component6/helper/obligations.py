import logging
logging.disable(logging.CRITICAL)
from dialog_tag import DialogTag

class Obligations:
    '''
    Sub module responsible for recognizing and responding to dialogue tags
    '''
    def __init__(self,model):
        self.model = model
        self.list_of_obligations = self.parse_obligation()
    
    def get_dialogue_tag(self, message):
        '''
        Method to get the dialogue tag of the message

        Args:
            message: message to be analyzed
        Returns:
            a string containing the predicted tag
        '''
        return self.model.predict_tag(message)
    
    def get_appropriate_response_obligations(self, tag):
        '''
        Method to get the appropriate response obligation

        Args:
            tag: name of the tag we're responding to
        Returns:
            list of possible response obligation tags
        '''
        obligations_list = []
        if tag in self.list_of_obligations.keys():
            obligations_list = self.list_of_obligations[tag]
        return obligations_list

    def parse_obligation(self):
        '''
        Method to parse obligations.txt 

        Returns:
            dictionary mapping a dialogue tag to a list of appropriate response tags
        '''
        obligations = {}
        obligations_list = [] # list for a given dialog act
        file = open("component6/grammar/obligations.txt", "r").read().split("\n")
        for line in file:
            if line == "" or line == "\n" or line == " ":
                continue
            dialogue_acts = line.split(":")
            act = dialogue_acts[0]
            responses = dialogue_acts[1].replace("\n", "")
            responses = responses.split(",")
            obligations[act] = responses
        return obligations 
