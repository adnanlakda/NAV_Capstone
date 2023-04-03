#!/usr/bin/python
import spacy
from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
import asyncio
from usp.tree import sitemap_tree_for_homepage
import spacy
from spacy import displacy 
from spacy.lang.en.stop_words import STOP_WORDS
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from get_category import *
from get_sub_category import *
from get_location import *
from get_date import *

import numpy as np
import os
import sys
import nltk
import pandas as pd


# download text preprocessing information 

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
#def(get_pravda)
# determine treemap of website urls ###########################
# TODO: what if this fails, can the code be made more robust here?
# try/except logic? probably just exit gracefully
existings_urls_file = pd.read_csv("master_urls_pravda.csv") # TODO: file with existing URLs -- does it exist, is it accurate?
print(existings_urls_file[0:])
#kw_file = Path(__file__).parent / "kws.csv"
#subkw_file = Path(__file__).parent / "sub_kws.csv"
existing_df = existings_urls_file
existing_urls = existing_df['url'].to_list()
existing_urls = [*set(existing_urls)]
print(existing_urls[0:1])
tree = sitemap_tree_for_homepage('https://www.pravda.com.ua/'); ##### TAKES FOREVER
urls = [page.url for page in tree.all_pages()];
urls = [*set(urls)]
print(urls[0:9])

# define dataframe for storing gathered urls ##################
# TODO: what if this fails, can the code be made more robust here?
# try/except logic? fall back to full scrape if this fails?
df = pd.DataFrame(urls)
df = df.rename(columns={0: 'url'})
print(df[0:1])
print(df[1100:1161])
#df.to_csv('master_urls_pravda.csv', index = False, header = True) 
# # TODO ERROR TypeError: __init__() got an unexpected keyword argument 'line_terminator'
df['title'] = ''
df['text'] = ''
df['incident_type'] = ''

df = df[~df["url"].isin(existing_urls)] # remove previously scraped sites from list

# TODO: why? what does it do?
df = df[df["url"].str.contains("/eng/")==True]
print(df)
df = df[df["url"].str.contains("/news/")==True] # removes urls from the df that have /news/ in their url
print(df)
df = df[(df["url"].str.contains("2023")==True)]
df.head() ## 


# for each new url scrape using beautiful soup ################
# store information in Pandas dataframe initialized above
# TODO: what if this fails, can the code be made more robust here?
# try/except logic? probably just fail gracefully 
# TODO: this should be a function and not be repated so many times
current_url = ""
title_text = ""
for index, row in tqdm(df.iterrows(), desc="Loading..."):
    current_url = row[0]
    res = requests.get(current_url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    for title in soup.find_all('h1', attrs={"class":"post_title"}):
        title_text = (title.get_text())
        row[1] += title_text
    for para in soup.find_all('div', attrs={"class":"post_text"}):
        para_text = (para.get_text())
        row[2] += para_text

print(df['title'])
print(df['text'])
print(df['incident_type'])

# use regular expressions to extract key words from scraped text 
# TODO: likely move to an external file so it's easier to add new or remove stale
# this should not be repeated so many times
df = df.replace('\n', '', regex=True)
df = df.replace('shoot down', 'shootdown', regex=True)
df = df.replace('shot down', 'shotdown', regex=True)
df = df.replace('fighter jet', 'fighterjet', regex=True)
df = df.replace('war plane', 'warplane', regex=True)
df = df.replace('kamakazee drone', 'kamakazeedrone', regex=True)
df = df.replace('suicide drone', 'suicidedrone', regex=True)
df = df.replace('naval mine', 'navalmine', regex=True)
df = df.replace('sea mine', 'seamine', regex=True)
df = df.replace('remnants of war', 'remnantsofwar', regex=True)
df = df.replace('unexploded ordance', 'unexplodedordance', regex=True)
df = df.replace('shot at', 'shotat', regex=True)
df = df.replace('cruise missile', 'cruisemissile', regex=True)
df = df.replace('ballistic missile', 'ballisticmissile', regex=True)
df = df.replace('guided missile', 'guidedmissile', regex=True)
df = df.replace('prisoner exchange', 'prisonerexchange', regex=True)
df = df.replace('prisoner swap', 'prisonerswap', regex=True)
df = df.replace('prisoner release', 'prisonerrelease', regex=True)
df = df.replace('special forces', 'specialforces', regex=True)
df = df.replace('strategic withdraw', 'strategicwithdraw', regex=True)
df = df.replace('pull back', 'pullback', regex=True)
df = df.replace('set fire to', 'setfireto', regex=True)
df = df.replace('attempted assassination', 'attemptedassassination', regex=True)
df = df.replace('sentenced to death', 'sentencedtodeath', regex=True)
df = df[df["title"].str.contains("If")==False]
df = df[df["title"].str.contains("What")==False]
df = df[df["title"].str.contains("How")==False]
df = df[df["title"].str.contains("Analysts")==False]
df = df[df["title"].str.contains("visits")==False]

print(df['title'])
print(df['text'])
print(df['incident_type'])

#nlp = spacy.load('en_core_web_sm') # TODO: why, what does it do? we don't call this
#### This code loads a pre-trained statistical model for English language processing from 
# the spaCy library. The en_core_web_sm model is a small, but effective, model for processing
#  English text data that includes tokenization, named entity recognition, part-of-speech tagging, 
# and dependency parsing.

# attempt to determine category ###############################
# this can fail, and when it does you might see "Divide  by zero" in the log
# TODO: could there be a better message for failure?
# what should the value be in the dataframe if this fails?
for index, row in tqdm(df.iterrows(), desc="Loading..."):
    title = row[1]
    text = row[2]
    
    try:   
        category_info = get_category(title, text)
        row[3] = category_info[0]
        #row[4] = np.float64(category_info[1])
    except Exception as e:
        print(e)
        row[3] = 'none' # failed top retrieve this
print(df['incident_type'])
df.loc[df['incident_type'] == 'none'] ## march 10th: 69 rows are not categorized -- can improve

df = df[df["incident_type"].str.contains("none")==False] # removing all of the incidents with "none"
print(df)
df['sub_category'] = ' ' ## adding the column subcategory to the df
print(df['sub_category']) 

for index, row in tqdm(df.iterrows(), desc="Loading..."):
    main_category = row[3]
    title = row[1]
    text = row[2]
    
    #try:   
    sub_category_info = get_sub_category(main_category, title, text)
    row[4] = sub_category_info
        #row[4] = np.float64(category_info[1])
    #except:
        #row[4] = 'none'
print(df['sub_category']) ## updated subcategory 

# attempt to determine location ###############################
# can this fail? probably ... 
# TODO: try/except?
# what should the value be in the dataframe if this fails?
df['Latitude'] = 1.12
df['Longitude'] = 1.12 ### why is this defined?
df['Date'] = ''
df['City'] = ''
df['Oblast'] = ''
df['Country'] = ''

# call out to get_location module
# can this fail? probably ... 
# TODO: try/except?
# what should the value be in the dataframe if this fails?

#### This is where we call the get_location function to get lat/long, oblast, city, country info
applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error?
# if error, why? make more robust

# attempt to determine date ###################################
# can this fail? probably ... 
# TODO: try/except?
# what should the value be in the dataframe if this fails?
df['Date'] = df['url'].apply(get_date)
print(df["Date"])
df.to_excel("pravda.xlsx",sheet_name="Pravda_Scraped")
print(df)


#### DID NOT RUN AFTER THIS #####
# create final polished for download ##########################
final_df = pd.DataFrame()
final_df['Latitude'] = applied_df[0]
final_df['Longitude'] = applied_df[1]
final_df['Date'] = df['Date']
final_df['Town'] = applied_df[2]
final_df['Oblast'] = applied_df[3]
final_df['Country'] = applied_df[4]
final_df['Incident_type'] = df['incident_type']
final_df['Incident_sub_type'] = df['sub_category']
final_df['Source_1'] = df['url']

final_df = final_df[final_df['Latitude'] != 11.100000]
final_df = final_df[final_df["Country"].str.contains("UA")==True]
final_df = final_df[final_df["Oblast"].str.contains("NA")==False]

original_list = pd.read_csv("total_pravda.csv")
total = pd.concat([original_list, final_df])
total = total.drop_duplicates()
total.to_csv('total_pravda.csv', index=False) # always downloads?
print(df)
print(final_df) # return df with category, date, and location information
print(1)
