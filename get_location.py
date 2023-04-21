# TODO: Add doc string to describe module
# TODO: add comments throughout file to describe what it does
## for get location imports
import spacy
from collections import Counter
#import en_core_web_sm
#nlp = en_core_web_sm.load()
import pandas as pd
import numpy as np

def get_location(nlp,txt):
#pravda_df = pd.read_excel("april4_pravda.xlsx")
#pravda_df.head(10)
### GET LOCATION ### how do we combine this into the full?
    output_1s = []  # GPE
    output_2s = []  # LOC

    #for txt in df.iloc[:,3]:
    txt = txt.replace('"','')
    doc = nlp(txt)
    
    entities = []
    entity = []
    
    for ent in doc.ents:
        if ent.label_ == "GPE":
            entities.append(ent.text)
    
    # removing duplicates
    res = np.unique(entities)
    
    
    # Join the entities into a string
    GPE = ", ".join(res)
    
    # Check if the number of locations listed in the GPE column is more than 10
    if len(res) > 10:
        GPE = 'Read article'
    
    # Append the output to the list of outputs
    output_1s.append(GPE)

    for ent in doc.ents:
        if ent.label_ == "LOC":
            entity.append(ent.text)
            
    LOC = ", ".join(entity)
    
    output_2s.append(LOC)
    
    return output_1s, output_2s
    # Add a new column named the GPE & LOC

#df['GPE'] = output_1s
#df['LOC'] = output_2s

# Printing the final output
#print(pravda_df)








#### DID NOT RUN AFTER THIS #####
# create final polished for download ##########################
