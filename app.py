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

file_choices = {"yes_use_file" : "Yes", "no_use_file" : "No"}

app_ui = ui.page_fluid(
    #ui.input_file("original_excel", "Upload excel", accept=".xlsx"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            #ui.input_select("website", "Choose a website:", {"independent" : "Kyiv Independent", "inform":"UKInform", "pravda":"Pravda", "[website_name]":"website_name"}),
            ui.input_select("website", "Choose a website:", {"independent" : "Kyiv Independent", "inform":"UKInform", "pravda":"Pravda"}),
            ui.input_radio_buttons("use_file", "Use pre-existing data?", file_choices),
            ui.input_action_button("start", "Start"),
            ui.download_button("download_final", "Download", class_="btn-primary")
        ),
        ui.panel_main(
            #ui.output_text_verbatim("scrape", placeholder=True)
            ui.output_table("scrape")
        )
    )
    #ui.output_table("table")
)


def server(input, output, session):
    
    @output
    @render.table
    @reactive.event(input.start)
    async def scrape():
        if input.website() == 'independent':
            if input.use_file != 'no_use_file':

                nltk.download('punkt')
                nltk.download('averaged_perceptron_tagger')
                nltk.download('maxent_ne_chunker')
                nltk.download('words')

                existings_urls_file = Path(__file__).parent / "master_urls_independent.csv"
                #kw_file = Path(__file__).parent / "kws.csv"
                #subkw_file = Path(__file__).parent / "sub_kws.csv"
                existing_df = pd.read_csv(existings_urls_file)
                existing_urls = existing_df['url'].to_list()
                existing_urls = [*set(existing_urls)]
                tree = sitemap_tree_for_homepage('https://kyivindependent.com/');
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]
                
                print(existing_df)

                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df.to_csv('master_urls_independent.csv', index=False)
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''

                df = df[~df["url"].isin(existing_urls)]

                df = df[df["url"].str.contains("/national/")==True]
                #df = df[df["url"].str.contains("tag")==False]

                #for url in existing_urls:
                #    df = df.drop(df[df['url'].str.match(url, na=False)].index)

                print(df)

                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    current_url = row[0]
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    for title in soup.find_all("h1"):
                        #for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                        #for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text

                print('line 100')

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

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0]
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print(e)
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                print(applied_df)

                df['Date'] = df['url'].apply(get_date)

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

                print(final_df)

                original_list = pd.read_csv("total_independent.csv")
                total = pd.concat([original_list, final_df])
                total = total.drop_duplicates()
                total.to_csv('total_independent.csv', index=False)

                return final_df
            
            elif input.use_file == 'no_use_file':

                tree = sitemap_tree_for_homepage('https://kyivindependent.com/');
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]
                
                print('line 204')
                print(existing_df)

                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''
                df = df[df["url"].str.contains("/national/")==True]

                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    current_url = row[0]
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    for title in soup.find_all("h1"):
                        #for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                        #for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text
                
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

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0]
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print(e)
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                print(applied_df)

                df['Date'] = df['url'].apply(get_date)

                print('line 300')

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

                final_df.to_csv('new_independent.csv', index=False)

                return final_df

        
        elif input.website() == 'inform':
            if input.use_file != 'no_use_file':
                print('!= no_use_file') # use pre-existing data = yes

                nltk.download('punkt')
                nltk.download('averaged_perceptron_tagger')
                nltk.download('maxent_ne_chunker')
                nltk.download('words')

                existings_urls_file = Path(__file__).parent / "master_urls_inform.csv"
                #kw_file = Path(__file__).parent / "kws.csv"
                #subkw_file = Path(__file__).parent / "sub_kws.csv"
                existing_df = pd.read_csv(existings_urls_file)
                existing_urls = existing_df['url'].to_list()
                existing_urls = [*set(existing_urls)]
                tree = sitemap_tree_for_homepage('https://www.ukrinform.net/'); # builds site tree using package, takes time
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]
                
                print(existing_urls)

                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df.to_csv('master_urls_inform.csv', index=False)
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''

                print(df)

                #df = df.loc[:3, :]
                #df = df[~df["url"].isin(existing_urls)] # entire dataframe disappears, all found rows have existing URLs in master_url_inform.csv -- why does that matter?? 

                print(df)

                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."): # for rows in the dataframe (but dataframe has no rows??)
                    current_url = row[0] # likely causes KeyError
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    #for title in soup.find_all("h1"):
                    for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    if row[1] == '':
                        for noPic_title in soup.find_all('div', attrs={"class":"newsNoPicture"}):
                            noPic_titleText = (noPic_title.get_text())
                            row[1] = noPic_titleText
                    #for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                    for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text


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
                
                print('line 400') # runs to here with 3 row dataset 
                
                df = df.replace('sentenced to death', 'sentencedtodeath', regex=True)
                df = df[df["title"].str.contains("If")==False]
                df = df[df["title"].str.contains("What")==False]
                df = df[df["title"].str.contains("How")==False]
                df = df[df["title"].str.contains("Analysts")==False]
                df = df[df["title"].str.contains("visits")==False]

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0] # keyerror 0?
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print('line 423')
                        print(e) # currently failing here 
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                print(applied_df) #empty? 

                df['Date'] = df['url'].apply(get_date)

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

                print('line 469')
                print(final_df)
                
                original_list = pd.read_csv("total_inform.csv")
                total = pd.concat([original_list, final_df])
                total = total.drop_duplicates()
                total.to_csv('total_inform.csv', index=False)

                return final_df

            elif input.use_file == 'no_use_file':

                print('== no_use_file')

                tree = sitemap_tree_for_homepage('https://www.ukrinform.net/');
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]
                
                print(existing_df)

                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''

                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    current_url = row[0]
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    #for title in soup.find_all("h1"):
                    for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    if row[1] == '':
                        for noPic_title in soup.find_all('div', attrs={"class":"newsNoPicture"}):
                            noPic_titleText = (noPic_title.get_text())
                            row[1] = noPic_titleText
                    #for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                    for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text
                
                print('line 500')

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

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0]
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print(e)
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                print(applied_df)

                df['Date'] = df['url'].apply(get_date)

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

                final_df.to_csv('new_inform.csv', index=False)

                return final_df

            print('line 600')

        elif input.website() == 'pravda':
            if input.use_file != 'no_use_file':

                nltk.download('punkt')
                nltk.download('averaged_perceptron_tagger')
                nltk.download('maxent_ne_chunker')
                nltk.download('words')

                existings_urls_file = Path(__file__).parent / "master_urls_pravda.csv"
                #kw_file = Path(__file__).parent / "kws.csv"
                #subkw_file = Path(__file__).parent / "sub_kws.csv"
                existing_df = pd.read_csv(existings_urls_file)
                existing_urls = existing_df['url'].to_list()
                existing_urls = [*set(existing_urls)]
                tree = sitemap_tree_for_homepage('https://www.pravda.com.ua/');
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]

                
                #print(existing_urls)
                #print(urls)


                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df.to_csv('master_urls_pravda.csv', index=False)
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''

                df = df[~df["url"].isin(existing_urls)]

                df = df[df["url"].str.contains("/eng/")==True]
                df = df[df["url"].str.contains("/news/")==True]
                df = df[(df["url"].str.contains("2022")==True) | (df["url"].str.contains("2023")==True)]

                print(df)

                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    current_url = row[0]
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    for title in soup.find_all('h1', attrs={"class":"post_title"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"class":"post_text"}):
                        para_text = (para.get_text())
                        row[2] += para_text


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

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0]
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print(e)
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

                print('line 700')

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error 
                print(applied_df)

                df['Date'] = df['url'].apply(get_date)

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

                print(final_df)

                original_list = pd.read_csv("total_pravda.csv")
                total = pd.concat([original_list, final_df])
                total = total.drop_duplicates()
                total.to_csv('total_pravda.csv', index=False)

                return final_df

            elif input.use_file == 'no_use_file':

                tree = sitemap_tree_for_homepage('https://www.pravda.com.ua/');
                urls = [page.url for page in tree.all_pages()];
                urls = [*set(urls)]
                print(existing_df)

                df = pd.DataFrame(urls)
                df = df.rename(columns={0: 'url'})
                df['title'] = ''
                df['text'] = ''
                df['incident_type'] = ''
                df = df[df["url"].str.contains("/eng/")==True]
                df = df[df["url"].str.contains("/news/")==True]
                df = df[(df["url"].str.contains("2022")==True) | (df["url"].str.contains("2023")==True)]


                current_url = ""
                title_text = ""
                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    current_url = row[0]
                    res = requests.get(current_url)
                    html_page = res.content
                    soup = BeautifulSoup(html_page, 'html.parser')
                    for title in soup.find_all('h1', attrs={"class":"post_title"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"class":"post_text"}):
                        para_text = (para.get_text())
                        row[2] += para_text
                
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
                
                print('line 800')
                
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

                nlp = spacy.load('en_core_web_sm')

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    title = row[1]
                    text = row[2]
                    
                    try:   
                        category_info = get_category(title, text)
                        row[3] = category_info[0]
                        #row[4] = np.float64(category_info[1])
                    except Exception as e:
                        print(e)
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False]
                df['sub_category'] = ' '

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

                df['Latitude'] = 1.12
                df['Longitude'] = 1.12
                df['Date'] = ''
                df['City'] = ''
                df['Oblast'] = ''
                df['Country'] = ''

                applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                print(applied_df)

                df['Date'] = df['url'].apply(get_date)

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

                final_df.to_csv('new_pravda.csv', index=False)

                return final_df
        
        #elif input.website() == 'custom':
        #    return 'tbd'

    @session.download()
    def download_final():
        path = os.path.join(os.path.dirname(__file__), 'total.csv')
        return path

app = App(app_ui, server, debug=False)

