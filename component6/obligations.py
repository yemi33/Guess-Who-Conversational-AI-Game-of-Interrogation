import logging
logging.disable(logging.CRITICAL)
from dialog_tag import DialogTag

class Obligations:
    def __init__(self):
        self.list_of_obligations = self.parse_obligation()

    def get_appropriate_response_obligations(self, message, model):
        output = model.predict_tag(message)
        obligations_list = []
        if output in self.list_of_obligations.keys():
            obligations_list = self.list_of_obligations[output]
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

if __name__ == "__main__":
    obligations = Obligations()
    message = "I want you to tell me what you did that night."
    print(obligations.get_appropriate_response_obligations(message))