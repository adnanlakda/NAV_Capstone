# TODO: Add doc string to describe module
# TODO: add comments throughout file to describe what it does

import spacy
from spacy import displacy 
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
import pandas as pd

nlp = spacy.load('en_core_web_sm')

kws = pd.read_csv('kws.csv')
sub_kws = pd.read_csv('sub_kws.csv')

def get_category(title, text):
    """
        Returns a list containing the main category and the total score of the input text.

        Parameters:
        title (str): A string containing the title of the input text.
        text (str): A string containing the input text.

        Returns:
        list: A list containing the main category and the total score of the input text.
    """

# Initialize scores and variables
    air_score = 0
    blast_score = 0
    land_score = 0
    maritime_score = 0
    missile_score = 0
    security_score = 0
    targeted_score = 0
    title_score = 0
    
    main_category = ''
    weight = 0
    
    title_doc = nlp(title)
    title_tokens=[token.text for token in title_doc]
    
    for title_token in title_tokens:
        try:
            main_category = kws.loc[kws['KW']==title_token]['Category'].values[0]
            weight = kws.loc[kws['KW']==title_token]['Weight'].values[0]
            #print(main_category)
        except:
            #print('Not a KW!')
            main_category = ''
            weight = 0
        
        if main_category != '':
            if main_category == 'air':
                air_score = air_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'blast':
                blast_score = blast_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'land':
                land_score = land_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'maritime':
                maritime_score = maritime_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'missile':
                missile_score = missile_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'security':
                security_score = security_score + 4 * weight
                title_score = title_score + 1
            if main_category == 'targeted':
                targeted_score = targeted_score + 4 * weight
                title_score = title_score + 1

    # Tokenize the input text using spaCy           
    doc = nlp(text)
    tokens=[token.text for token in doc]
    # Loop through each token in the input text and check if it's a keyword
    for token in tokens:
        try:
            main_category = kws.loc[kws['KW']==token]['Category'].values[0]
            weight = kws.loc[kws['KW']==token]['Weight'].values[0]
            #print(main_category)
        except:
            #print('Not a KW!')
            main_category = ''
            weight = 0
        # Update scores based on the main category
        if main_category != '':
            if main_category == 'air':
                air_score = air_score + 1 * weight
            if main_category == 'blast':
                blast_score = blast_score + 1 * weight
            if main_category == 'land':
                land_score = land_score + 1 * weight
            if main_category == 'maritime':
                maritime_score = maritime_score + 1 * weight
            if main_category == 'missile':
                missile_score = missile_score + 1 * weight
            if main_category == 'security':
                security_score = security_score + 1 * weight
            if main_category == 'targeted':
                targeted_score = targeted_score + 1 * weight
    
    total_score = air_score + blast_score + land_score + maritime_score + missile_score + security_score + targeted_score 
    print('get_category.py line 92')
    scores = {'air_score': air_score/total_score, 'blast_score': blast_score/total_score, 'land_score': land_score/total_score, 'maritime_score': maritime_score/total_score, 'missile_score': missile_score/total_score, 'security_score': security_score/total_score, 'targeted_score': targeted_score/total_score}
    # error here means total_score = 0, why? because there aee no other scores , why? 
    print('get_category.py line 94')
    v = list(scores.values())
    k = list(scores.keys())
    highest = k[v.index(max(v))]
    
    if total_score >= 4:
        if highest == 'air_score':
            return ['air', total_score]
        elif highest == 'blast_score':
            return ['blast', total_score]
        elif highest == 'land_score':
            return ['land', total_score]
        elif highest == 'maritime_score':
            return ['maritime', total_score]
        elif highest == 'missile_score':
            return ['missile', total_score]
        elif highest == 'security_score':
            return ['security', total_score]
        elif highest == 'targeted_score':
            return ['targeted', total_score]