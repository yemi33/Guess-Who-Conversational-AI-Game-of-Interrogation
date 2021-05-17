import spacy

class Ner:
    '''
    Sub module responsible for recognizing named entities in user inputs.
    '''
    def find_named_entities(self, message):
        named_entities = {}
        nlp = spacy.load("en_core_web_sm")
        parsed_msg = nlp(message)
        for ent in parsed_msg.ents:
            named_entities[ent.label_] = ent
        return named_entities

if __name__ == "__main__":
    ner = Ner()
    message = "I know what you did to Taylor that night."
    print(ner.find_named_entities(message))