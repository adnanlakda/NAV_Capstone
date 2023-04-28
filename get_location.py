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

    """
    This function extracts GPE (geopolitical entities) and LOC (locations) from text data and returns a dataframe
    with these entities as columns.
    
    Parameters:
    -----------
    pravda_df : pandas dataframe
        The dataframe containing text data.
        
    Returns:
    --------
    pravda_df : pandas dataframe
        The original dataframe with new columns for GPE and LOC.
    """

    output_gpe = []  # GPE
    output_loc = []  # LOC

    #for txt in df.iloc[:,3]:
    txt = txt.replace('"','')
    doc = nlp(txt)
    
    entities = [] #GPE
    entity = [] #LOC
    
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
    # LOC column usually will be less than 10
    # Append the output to the list of outputs
    output_gpe.append(GPE)

    for ent in doc.ents:
        if ent.label_ == "LOC":
            entity.append(ent.text)
            
    LOC = ", ".join(entity)
    
    output_loc.append(LOC)
    
    return [output_gpe, output_loc]
    # Add a new column named the GPE & LOC


# Printing the final output
#print(pravda_df)








#### DID NOT RUN AFTER THIS #####
# create final polished for download ##########################
