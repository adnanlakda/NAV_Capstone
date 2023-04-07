import spacy
from collections import Counter
import en_core_web_sm
nlp = en_core_web_sm.load()
import matplotlib as mpl


import pandas as pd
pravda_df = pd.read_excel("april4_pravda.xlsx")
pravda_df.head(10)


outputs = []


for txt in pravda_df.iloc[:,3]:
    txt = txt.replace('"','')
    doc = nlp(txt)
    
    entities = []
    
    for ent in doc.ents:
        if ent.label_ == "GPE" or ent.label_ == "LOC":
            entities.append(ent.text)
    
    # Join the entities into a string
    output = ", ".join(entities)
    
    # Append the output to the list of outputs
    outputs.append(output)

# Add a new column named the output
pravda_df['output'] = outputs

print(pravda_df)