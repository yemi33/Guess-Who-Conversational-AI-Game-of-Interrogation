import logging
logging.disable(logging.CRITICAL)
from dialog_tag import DialogTag

class Obligations:
    def __init__(self,model):
        self.model = model
        self.list_of_obligations = self.parse_obligation()
    
    def get_dialogue_tag(self, message):
        return self.model.predict_tag(message)
    
    def get_appropriate_response_obligations(self, tag):
        obligations_list = []
        if tag in self.list_of_obligations.keys():
            obligations_list = self.list_of_obligations[tag]
        return obligations_list

    def parse_obligation(self):
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
