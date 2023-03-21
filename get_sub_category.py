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

air_df = sub_kws[sub_kws["main_category"].str.contains("air")==True]
blast_df = sub_kws[sub_kws["main_category"].str.contains("blast")==True]
land_df = sub_kws[sub_kws["main_category"].str.contains("land")==True]
security_df = sub_kws[sub_kws["main_category"].str.contains("security")==True]
targeted_df = sub_kws[sub_kws["main_category"].str.contains("targeted")==True]


def get_sub_category(main_category, title, text):

    indexed_df = air_df
    sub_category = ''
    weight = 0.0

    #air subcategory scores
    fixed_wing_score = 0
    loitering_munition_score = 0
    rotary_wing_score = 0
    surface_to_air_score = 0
    uav_score = 0
    
    #blast subcategory scores
    ied_score = 0
    landmine_score = 0
    naval_mine_score = 0
    uxo_score = 0
    
    #land subcategory scores
    direct_fire_score = 0
    indirect_fire_score = 0
    
    #security subcategory scores
    arrest_score = 0
    demining_score = 0
    exchange_score = 0
    interdiction_score = 0
    military_exercise_score = 0
    raid_score = 0
    troop_mvmnt_score = 0
    
    #targeted subcategory scores
    abduction_score = 0
    arson_score = 0
    assassination_score = 0
    cyber_attack_score = 0
    execution_score = 0
    intimidation_score = 0
    looting_score = 0
    murder_score = 0
    sabotage_score = 0
    vandalism_score = 0

    title_doc = nlp(title)
    title_tokens=[token.text for token in title_doc]
    
    doc = nlp(text)
    tokens=[token.text for token in doc]
    
    if main_category == 'air':
        for title_token in title_tokens:
            #try:
            indexed_df = air_df[air_df["KW"] == title_token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    #print(row[2])
                    
                    if sub_category == 'loitering_munition':
                        loitering_munition_score = loitering_munition_score + 2 * weight
                    elif sub_category == 'uav':
                        uav_score = uav_score + 2 * weight
                    elif sub_category == 'fixed_wing':
                        fixed_wing_score = fixed_wing_score + 2 * weight
                    elif sub_category == 'rotary_wing':
                        rotary_wing_score = rotary_wing_score + 2 * weight
                    elif sub_category == 'surface_to_air':
                        surface_to_air_score = surface_to_air_score + 2 * weight
            else:
                pass
            #except:
                #main_category = ''
                #weight = 0
                #pass
        for token in tokens:
            #try:
            indexed_df = air_df[air_df["KW"] == token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    
                    if sub_category == 'loitering_munition':
                        loitering_munition_score = loitering_munition_score + 1 * weight
                    elif sub_category == 'uav':
                        uav_score = uav_score + 1 * weight
                    elif sub_category == 'fixed_wing':
                        fixed_wing_score = fixed_wing_score + 1 * weight
                    elif sub_category == 'rotary_wing':
                        rotary_wing_score = rotary_wing_score + 1 * weight
                    elif sub_category == 'surface_to_air':
                        surface_to_air_score = surface_to_air_score + 1 * weight
            #except:
                #main_category = ''
                #weight = 0
                #pass
            else:
                pass
            
        air_scores = {'fixed_wing' : fixed_wing_score, 'loitering_munition' : loitering_munition_score, 'rotary_wing' : rotary_wing_score, 'surface_to_air' : surface_to_air_score, 'uav' : uav_score}
        air_v = list(air_scores.values())
        air_k = list(air_scores.keys())
        #print(air_k[air_v.index(max(air_v))])
        return air_k[air_v.index(max(air_v))]
    
    elif main_category == 'blast':
        for title_token in title_tokens:
            #try:
            indexed_df = blast_df[blast_df["KW"] == title_token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    #print(row[2])
                    
                    if sub_category == 'ied':
                        ied_score = ied_score + 2 * weight
                    elif sub_category == 'landmine':
                        landmine_score = landmine_score + 2 * weight
                    elif sub_category == 'naval_mine':
                        naval_mine_score = naval_mine_score + 2 * weight
                    elif sub_category == 'uxo':
                        uxo_score = uxo_score + 2 * weight
            else:
                pass
            #except:
                #main_category = ''
                #weight = 0
                #pass
        for token in tokens:
            #try:
            indexed_df = blast_df[blast_df["KW"] == token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    
                    if sub_category == 'ied':
                        ied_score = ied_score + 1 * weight
                    elif sub_category == 'landmine':
                        landmine_score = landmine_score + 1 * weight
                    elif sub_category == 'naval_mine':
                        naval_mine_score = naval_mine_score + 1 * weight
                    elif sub_category == 'uxo':
                        uxo_score = uxo_score + 1 * weight
            #except:
                #main_category = ''
                #weight = 0
                #pass
            else:
                pass
            
        blast_scores = {'ied' : ied_score, 'landmine' : landmine_score, 'naval_mine' : naval_mine_score, 'uxo' : uxo_score}
        blast_v = list(blast_scores.values())
        blast_k = list(blast_scores.keys())
        return blast_k[blast_v.index(max(blast_v))]
    
    elif main_category == 'land':
        for title_token in title_tokens:
            indexed_df = land_df[land_df["KW"] == title_token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    if sub_category == 'direct_fire':
                        direct_fire_score = direct_fire_score + 2 * weight
                    elif sub_category == 'indirect_fire':
                        indirect_fire_score = indirect_fire_score + 2 * weight   
            else:
                pass
            
        for token in tokens:
            #try:
            indexed_df = land_df[land_df["KW"] == token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]              
                    if sub_category == 'direct_fire':
                        direct_fire_score = direct_fire_score + 1 * weight
                    elif sub_category == 'indirect_fire':
                        indirect_fire_score = indirect_fire_score + 1 * weight   
            else:
                pass
        
        land_scores = {'direct_fire' : direct_fire_score, 'indirect_fire' : indirect_fire_score}
        land_v = list(land_scores.values())
        land_k = list(land_scores.keys())
        return land_k[land_v.index(max(land_v))]
            
    elif main_category == 'security':
        for title_token in title_tokens:
            indexed_df = security_df[security_df["KW"] == title_token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    if sub_category == 'arrest':
                        arrest_score = arrest_score + 2 * weight
                    elif sub_category == 'demining':
                        demining_score = demining_score + 2 * weight  
                    elif sub_category == 'exchange':
                        exchange_score = exchange_score + 2 * weight
                    elif sub_category == 'interdiction':
                        interdiction_score = interdiction_score + 2 * weight
                    elif sub_category == 'military_exercise':
                        military_exercise_score = military_exercise_score + 2 * weight
                    elif sub_category == 'raid':
                        raid_score = raid_score + 2 * weight
                    elif sub_category == 'troop_movement':
                        troop_mvmnt_score = troop_mvmnt_score + 2 * weight
            else:
                pass
            
        for token in tokens:
            #try:
            indexed_df = land_df[land_df["KW"] == token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]              
                    if sub_category == 'arrest':
                        arrest_score = arrest_score + 1 * weight
                    elif sub_category == 'demining':
                        demining_score = demining_score + 1 * weight  
                    elif sub_category == 'exchange':
                        exchange_score = exchange_score + 1 * weight
                    elif sub_category == 'interdiction':
                        interdiction_score = interdiction_score + 1 * weight
                    elif sub_category == 'military_exercise':
                        military_exercise_score = military_exercise_score + 1 * weight
                    elif sub_category == 'raid':
                        raid_score = raid_score + 1 * weight
                    elif sub_category == 'troop_movement':
                        troop_mvmnt_score = troop_mvmnt_score + 1 * weight
            else:
                pass
        
        security_scores = {'arrest' : arrest_score, 'demining' : demining_score, 'exchange' : exchange_score, 'interdiction' : interdiction_score, 'military_exercise' : military_exercise_score, 'raid' : raid_score, 'troop_mvmnt' : troop_mvmnt_score}
        security_v = list(security_scores.values())
        security_k = list(security_scores.keys())
        return security_k[security_v.index(max(security_v))]
    
    elif main_category == 'targeted':
        for title_token in title_tokens:
            indexed_df = targeted_df[targeted_df["KW"] == title_token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]
                    if sub_category == 'abduction':
                        abduction_score = abduction_score + 2 * weight
                    elif sub_category == 'arson':
                        arson_score = arson_score + 2 * weight
                    elif sub_category == 'assassination':
                        assassination_score = assassination_score + 2 * weight
                    elif sub_category == 'cyber_attack':
                        cyber_attack_score = cyber_attack_score + 2 * weight
                    elif sub_category == 'execution':
                        execution_score = execution_score + 2 * weight
                    elif sub_category == 'intimidation':
                        intimidation_score = intimidation_score + 2 * weight
                    elif sub_category == 'murder':
                        murder_score = murder_score + 2 * weight
                    elif sub_category == 'sabotage':
                        sabotage_score = sabotage_score + 2 * weight
                    elif sub_category == 'vandalism':
                        vandalism_score = vandalism_score + 2 * weight
            else:
                pass
            
        for token in tokens:
            #try:
            indexed_df = land_df[land_df["KW"] == token]
            if len(indexed_df.index) >= 1:
                for index, row in indexed_df.iterrows():
                    sub_category = row[2]
                    weight = row[3]              
                    if sub_category == 'abduction':
                        abduction_score = abduction_score + 1 * weight
                    elif sub_category == 'arson':
                        arson_score = arson_score + 1 * weight
                    elif sub_category == 'assassination':
                        assassination_score = assassination_score + 1 * weight
                    elif sub_category == 'cyber_attack':
                        cyber_attack_score = cyber_attack_score + 1 * weight
                    elif sub_category == 'execution':
                        execution_score = execution_score + 1 * weight
                    elif sub_category == 'intimidation':
                        intimidation_score = intimidation_score + 1 * weight
                    elif sub_category == 'murder':
                        murder_score = murder_score + 1 * weight
                    elif sub_category == 'sabotage':
                        sabotage_score = sabotage_score + 1 * weight
                    elif sub_category == 'vandalism':
                        vandalism_score = vandalism_score + 1 * weight
            else:
                pass
            
        targeted_scores = {'abduction' : abduction_score, 'arson' : arson_score, 'assassination' : assassination_score, 'cyber_attack' : cyber_attack_score, 'execution' : execution_score, 'intimidation' : intimidation_score, 'looting' : looting_score, 'murder' : murder_score, 'sabotage' : sabotage_score, 'vandalism' : vandalism_score}
        targeted_v = list(targeted_scores.values())
        targeted_k = list(targeted_scores.keys())
        return targeted_k[targeted_v.index(max(targeted_v))]
        