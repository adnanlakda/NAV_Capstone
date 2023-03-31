#!/usr/bin/python
import spacy

nlp = spacy.load("en_core_web_sm")

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_sm")
    doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)
