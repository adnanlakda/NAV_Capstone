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
import http.client, urllib.parse #api
import json #api
from datetime import datetime #datetime

import numpy as np
import os
import sys

file_choices = {"yes_use_file" : "Yes", "no_use_file" : "No"} # TODO: defines the buttons yes and no in the shiny app

# defines basic app UI and what you will see in the shiny app ########################################################

app_ui = ui.page_fluid(
    #ui.input_file("original_excel", "Upload excel", accept=".xlsx"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            #ui.input_select("website", "Choose a source:", {"mediastack" : "MediaStack API", "pravda":"Pravda", "[website_name]":"website_name"}),
            ui.input_select("website", "Choose a source:", {"mediastack" : "MediaStack API", "pravda":"Pravda"}),
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

# core of the app functionality ###############################################
        
def server(input, output, session):

    # TODO: improve server function docstring
    # TODO: make code more robust to failures with try/except logic
    # TODO: reduce code repetition by creating functions and external files for key words, etc.
    # TODO: add logging and messages so you know what is happening in the code

    """ Function that defines the Shiny server. More information on Shiny Python available here:
        https://shiny.rstudio.com/py/docs/overview.html.

        For each website:
         - The scrape sub-function first determines if master_urls_<website_name>.csv
           should be used to define prior input information or if a fully new tree of
           website urls is needed. 
         - sitemap_tree_for_homepage is used to determine the tree map of the website. 
         - If previous urls exist, they are not scraped to save time.
         - If no previous urls exist, all urls from the map are scraped.
         - URLS are cached in a pandas dataframe. 
         - Scraping is conducted with beautiful soup, and scraped text is stored in the 
           same dataframe. 
         - External modules get_category, get_date, get_location, and get_sub_category are
           used further categorize information. 
         - For each website, a Pandas dataframe with scraped date, location, and category 
           information is created for download.  
    
        :param input: Likely a Shiny object with various settings that defines server inputs. 
        :param output: Likely a Shiny object that contains various types of outputs. 
        :param session: Likely a Shiny object that ...
        :return: No explicit return. Sub-functions return various Pandas dataframes. 
    
    """
######### WHAT IS THIS ?###########
    @output
    @render.table
    @reactive.event(input.start)
    async def scrape():

        # TODO: needs real doc string

        if input.website() == 'mediastack': # for independent website ########

            if input.use_file != 'no_use_file': # use past website URL information

                existings_urls_file = pd.read_csv("master_urls_api.csv")
                print(existings_urls_file[0:])
                existing_df = existings_urls_file
                existing_urls = existing_df['url'].to_list()
                existing_urls = [*set(existing_urls)]
                print(existing_urls[0:1])
                conn = http.client.HTTPConnection('api.mediastack.com')

                params = urllib.parse.urlencode({
                    'access_key': 'd9babc2a947d03f9b887715a6df56a7a',
                    'categories': 'general',
                    'keywords': 'Ukraine Russian',
                    'languages': 'ar, en, fr, ru, zh',
                    'sort': 'published_desc',
                    'limit': 100,
                    })

                conn.request('GET', "/v1/news?{}".format(params))
                res = conn.getresponse()
                data = res.read()

                import json
                response_dict = json.loads(data.decode('utf-8'))
                for article in response_dict['data']:
                    print(article['author'])
                    print(article['title'])
                    print(article['description'])
                    print(article['url'])
                    print(article['source'])
                    print(article['published_at'])
                    print('-' * 50)

                # create dataframe to store output
                scraped_data = []

                for article in response_dict['data']:
                    # Store the article data in variables
                    url = article['url']
                    title = article['title']
                    text = article['description']
                    author = article['author']
                    source = article['source']
                    date = article['published_at']

                    # Append the scraped data to the list
                    scraped_data.append({
                        'url': url,
                        'title': title,
                        'text': text,
                        'author': author,
                        'source': source,
                        'Date': date
                    })

                # store scraped_data into a dataframe and name it as df
                df = pd.DataFrame(scraped_data)
                print(df)
                df = df[~df["url"].isin(existing_urls)] # remove previously scraped sites from existing url list in this dataframe
                # TODO: why? what does it do?
                #df = df[df["url"].str.contains("/eng/")==True]
                print(df)
                #df = df[df["url"].str.contains("/news/")==True] # removes urls from the df that have /news/ in their url
                #print(df)
                #df = df[(df["url"].str.contains("2023")==True)]
                df.head() ## 
                # #group those articles come from the same source
                df = df.sort_values(by=['source'])

                # create empty columns
                df['incident_type'] = " "
                df['sub_category'] = " "
                df['Latitude'] = " "
                df['Longitude'] = " "


                # update the date format
                # Convert the 'published_at' column to datetime objects and then format them into yyyy-mm-dd strings
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

                # Assuming your dataframe is called df_API, download it into a csv file
                # remember to change path to your desired location

                ## API Chunk#####

                # TODO: determine if this code block is needed
                #df = df[df["url"].str.contains("/national/")==True]
                #df = df[df["url"].str.contains("tag")==False]
                #for url in existing_urls:
                #    df = df.drop(df[df['url'].str.match(url, na=False)].index)
                # print(df)

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
                    for title in soup.find_all("h1"):
                        #for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                        #for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text

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

                nlp = spacy.load('en_core_web_sm') # TODO: what does this do?

                # attempt to determine category ###############################
                # this can fail, and when it does you might see "Divide by zero" in the log
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
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False] # TODO: what does this do?
                print(df)
                # attempt to determine category ###############################
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    main_category = row[3]
                    title = row[1]
                    text = row[2]
                    #try:   
                    sub_category_info = get_sub_category(main_category, title, text)
                    row[4] = sub_category_info
                # call out to get_location module
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                #print(applied_df)

                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                df['Date'] = df['url'].apply(get_date)
                print(df)

                # create final polished for download ##########################
                final_df = pd.DataFrame()
                final_df['url'] = df['url']
                final_df['title'] = df['title']
                final_df['text'] = df['text']
                final_df['author'] = df['author']
                final_df['source'] = df['source']
                final_df['Date'] = df['Date']
                final_df['Latitude'] = df['Latitude']
                final_df['Longitude'] = df['Longitude']
                final_df['Incident_type'] = df['incident_type']
                final_df['Incident_sub_type'] = df['sub_category']

                final_df.to_excel("new_mediastack.xlsx",sheet_name="mediastack_Scraped")

                ##check if latitude is not default
                #final_df = final_df[final_df['Latitude'] != 11.100000]
                #Display full final_df
                pd.set_option('display.max_columns', None)
                pd.set_option('display.max_rows', None)
                print(final_df.columns)

                original_list = pd.read_csv("total_api_news.csv")
                total = pd.concat([original_list, final_df])#combine scraped urls to the url database
                total = total.drop_duplicates()
                total.to_csv('total_api_news.csv', index=False) #update total_api_news file
                ###update master_urls
                existing_df = existings_urls_file.merge(total[['url']], on='url', how='outer')
                existing_df.to_csv('master_urls_api.csv', index=False) #update master_urls_api file
                return final_df # return df with category, date, and location information


            
            elif input.use_file == 'no_use_file': # do NOT use past website URL information

                existings_urls_file = pd.read_csv("master_urls_api.csv")
                print(existings_urls_file[0:])
                existing_df = existings_urls_file
                existing_urls = existing_df['url'].to_list()
                existing_urls = [*set(existing_urls)]
                print(existing_urls[0:1])
                conn = http.client.HTTPConnection('api.mediastack.com')

                params = urllib.parse.urlencode({
                    'access_key': 'd9babc2a947d03f9b887715a6df56a7a',
                    'categories': 'general',
                    'keywords': 'Ukraine Russian',
                    'languages': 'ar, en, fr, ru, zh',
                    'sort': 'published_desc',
                    'limit': 100,
                    })

                conn.request('GET', "/v1/news?{}".format(params))
                res = conn.getresponse()
                data = res.read()

                import json
                response_dict = json.loads(data.decode('utf-8'))
                for article in response_dict['data']:
                    print(article['author'])
                    print(article['title'])
                    print(article['description'])
                    print(article['url'])
                    print(article['source'])
                    print(article['published_at'])
                    print('-' * 50)

                # create dataframe to store output
                scraped_data = []

                for article in response_dict['data']:
                    # Store the article data in variables
                    url = article['url']
                    title = article['title']
                    text = article['description']
                    author = article['author']
                    source = article['source']
                    date = article['published_at']

                    # Append the scraped data to the list
                    scraped_data.append({
                        'url': url,
                        'title': title,
                        'text': text,
                        'author': author,
                        'source': source,
                        'Date': date
                    })

                # store scraped_data into a dataframe and name it as df
                df = pd.DataFrame(scraped_data)
                print(df)
                df = df[~df["url"].isin(existing_urls)] # remove previously scraped sites from existing url list in this dataframe
                # TODO: why? what does it do?
                #df = df[df["url"].str.contains("/eng/")==True]
                print(df)
                #df = df[df["url"].str.contains("/news/")==True] # removes urls from the df that have /news/ in their url
                #print(df)
                #df = df[(df["url"].str.contains("2023")==True)]
                df.head() ## 
                # #group those articles come from the same source
                df = df.sort_values(by=['source'])

                # create empty columns
                df['incident_type'] = " "
                df['sub_category'] = " "
                df['Latitude'] = " "
                df['Longitude'] = " "


                # update the date format
                # Convert the 'published_at' column to datetime objects and then format them into yyyy-mm-dd strings
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

                # Assuming your dataframe is called df_API, download it into a csv file
                # remember to change path to your desired location

                ## API Chunk#####

                # TODO: determine if this code block is needed
                #df = df[df["url"].str.contains("/national/")==True]
                #df = df[df["url"].str.contains("tag")==False]
                #for url in existing_urls:
                #    df = df.drop(df[df['url'].str.match(url, na=False)].index)
                # print(df)

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
                    for title in soup.find_all("h1"):
                        #for title in soup.find_all('h1', attrs={"class":"newsTitle"}):
                        title_text = (title.get_text())
                        row[1] = title_text
                    for para in soup.find_all('div', attrs={"id":"content", "class":"post_single__content__15w2r"}):
                        #for para in soup.find_all('div', attrs={"class":"newsText"}):
                        para_text = (para.get_text())
                        row[2] += para_text

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

                nlp = spacy.load('en_core_web_sm') # TODO: what does this do?

                # attempt to determine category ###############################
                # this can fail, and when it does you might see "Divide by zero" in the log
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
                        row[3] = 'none'

                df = df[df["incident_type"].str.contains("none")==False] # TODO: what does this do?
                print(df)
                # attempt to determine category ###############################
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?

                for index, row in tqdm(df.iterrows(), desc="Loading..."):
                    main_category = row[3]
                    title = row[1]
                    text = row[2]
                    #try:   
                    sub_category_info = get_sub_category(main_category, title, text)
                    row[4] = sub_category_info
                # call out to get_location module
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand')
                #print(applied_df)

                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                df['Date'] = df['url'].apply(get_date)
                print(df)

                # create final polished for download ##########################
                final_df = pd.DataFrame()
                final_df['url'] = df['url']
                final_df['title'] = df['title']
                final_df['text'] = df['text']
                final_df['author'] = df['author']
                final_df['source'] = df['source']
                final_df['Date'] = df['Date']
                final_df['Latitude'] = df['Latitude']
                final_df['Longitude'] = df['Longitude']
                final_df['Incident_type'] = df['incident_type']
                final_df['Incident_sub_type'] = df['sub_category']

                final_df.to_excel("new_mediastack.xlsx",sheet_name="mediastack_Scraped")

                ##check if latitude is not default
                #final_df = final_df[final_df['Latitude'] != 11.100000]
                #Display full final_df
                pd.set_option('display.max_columns', None)
                pd.set_option('display.max_rows', None)
                print(final_df.columns)

                original_list = pd.read_csv("total_api_news.csv")
                total = pd.concat([original_list, final_df])#combine scraped urls to the url database
                total = total.drop_duplicates()
                total.to_csv('total_api_news.csv', index=False) #update total_api_news file
                ###update master_urls
                existing_df = existings_urls_file.merge(total[['url']], on='url', how='outer')
                existing_df.to_csv('master_urls_api.csv', index=False) #update master_urls_api file
                return final_df # return df with category, date, and location information

        elif input.website() == 'pravda': # pravda website

            if input.use_file != 'no_use_file': # use past website URL information
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
                df['Latitude'] = " "
                df['Longitude'] = " "

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
                df.loc[df['incident_type'] == 'none'] 


                df = df[df["incident_type"].str.contains("none")==False] # removing all of the incidents with "none"
                print(df)#then we have around 30% left (4/4/2023)
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
                #df['Latitude'] = 1.12 ## 1.12 is a filler value and we do not need these columns
                #df['Longitude'] = 1.12 ### 1.12 is a filler value and we do not need these columns
                df['Date'] = ''
                ##df['City'] = ''
                #df['Oblast'] = ''
                #df['Country'] = ''

                # call out to get_location module
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?

                #### This is where we call the get_location function to get lat/long, oblast, city, country info
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error?
                # if error, why? make more robust

                # attempt to determine date ###################################
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                df['Date'] = df['url'].apply(get_date)
                print(df["Date"])

                #Get_location
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error?
                
                
                # create final polished for download ##########################
                final_df = pd.DataFrame()
                final_df['url'] = df['url']
                final_df['title'] = df['title']
                final_df['text'] = df['text']
                final_df['Latitude'] = df['Latitude']
                final_df['Longitude'] = df['Longitude']
                final_df['Incident_type'] = df['incident_type']
                final_df['Incident_sub_type'] = df['sub_category']
                final_df['Date'] = df['Date']

                ##check if latitude is not default
                #final_df = final_df[final_df['Latitude'] != 11.100000]
                #Display full final_df
                pd.set_option('display.max_columns', None)
                pd.set_option('display.max_rows', None)
                print(final_df.columns)

                final_df.to_excel("new_pravda.xlsx",sheet_name="Pravda_Scraped")


                original_list = pd.read_csv("total_pravda_news.csv")
                total = pd.concat([original_list, final_df])#combine scraped urls to the url database
                total = total.drop_duplicates()
                total.to_csv('total_pravda_news.csv', index=False) #update total_api_news file
                ###update master_urls
                existing_df = existings_urls_file.merge(total[['url']], on='url', how='outer')
                existing_df.to_csv('master_urls_pravda.csv', index=False) #update master_urls_api file
                return final_df # return df with category, date, and location information

            elif input.use_file == 'no_use_file':  # do NOT use past website URL information
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
                df['Latitude'] = " "
                df['Longitude'] = " "

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
                df.loc[df['incident_type'] == 'none'] 


                df = df[df["incident_type"].str.contains("none")==False] # removing all of the incidents with "none"
                print(df)#then we have around 30% left (4/4/2023)
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
                #df['Latitude'] = 1.12 ## 1.12 is a filler value and we do not need these columns
                #df['Longitude'] = 1.12 ### 1.12 is a filler value and we do not need these columns
                df['Date'] = ''
                ##df['City'] = ''
                #df['Oblast'] = ''
                #df['Country'] = ''

                # call out to get_location module
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?

                #### This is where we call the get_location function to get lat/long, oblast, city, country info
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error?
                # if error, why? make more robust

                # attempt to determine date ###################################
                # can this fail? probably ... 
                # TODO: try/except?
                # what should the value be in the dataframe if this fails?
                df['Date'] = df['url'].apply(get_date)
                print(df["Date"])

                #Get_location
                #applied_df = df.apply(lambda row: pd.Series(get_location(row.url, row.title)), axis=1, result_type='expand') ## Error?
                
                
                # create final polished for download ##########################
                final_df = pd.DataFrame()
                final_df['url'] = df['url']
                final_df['title'] = df['title']
                final_df['text'] = df['text']
                final_df['Latitude'] = df['Latitude']
                final_df['Longitude'] = df['Longitude']
                final_df['Incident_type'] = df['incident_type']
                final_df['Incident_sub_type'] = df['sub_category']
                final_df['Date'] = df['Date']

                ##check if latitude is not default
                #final_df = final_df[final_df['Latitude'] != 11.100000]
                #Display full final_df
                pd.set_option('display.max_columns', None)
                pd.set_option('display.max_rows', None)
                print(final_df.columns)

                final_df.to_excel("new_pravda.xlsx",sheet_name="Pravda_Scraped")


                original_list = pd.read_csv("total_pravda_news.csv")
                total = pd.concat([original_list, final_df])#combine scraped urls to the url database
                total = total.drop_duplicates()
                total.to_csv('total_pravda_news.csv', index=False) #update total_api_news file
                ###update master_urls
                existing_df = existings_urls_file.merge(total[['url']], on='url', how='outer')
                existing_df.to_csv('master_urls_pravda.csv', index=False) #update master_urls_api file
                return final_df # return df with category, date, and location information
        
        # place holder for new websites #######################################
        #elif input.website() == 'custom':
        #    return 'tbd'

    # function for downloading results files ##################################
    # files have names like total_<website_name>.csv
    @session.download()
    def download_final():

        # TODO: real doc string

        path = os.path.join(os.path.dirname(__file__), 'total.csv')
        
        urls = [...]  # list of URLs to download

        def parse(self): 
            self.throw_if_not_downloaded_verbose() 

        for url in urls:
            try:
                article = newspaper.Article(url)
                article.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
                article.parse()
                article.nlp()
                article.download()
                # process the article
            except newspaper.article.ArticleException as e:
                print(f'Skipping URL {url}: {str(e)}')
                continue

        return path

# executes app ################################################################

app = App(app_ui, server, debug=False)

