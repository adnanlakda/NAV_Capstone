import http.client, urllib.parse
import json
import pandas as pd
from datetime import datetime

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

# store scraped_data into a dataframe and name it as df_API
df_API = pd.DataFrame(scraped_data)

# #group those articles come from the same source
df_API = df_API.sort_values(by=['source'])

# create empty columns
df_API['incident_type'] = " "
df_API['sub_category'] = " "
df_API['Latitude'] = " "
df_API['Longitude'] = " "


# update the date format
# Convert the 'published_at' column to datetime objects and then format them into yyyy-mm-dd strings
df_API['Date'] = pd.to_datetime(df_API['Date']).dt.strftime('%Y-%m-%d')

# Assuming your dataframe is called df_API, download it into a csv file
# remember to change path to your desired location
df_API.to_csv('/Users/grace/Downloads/API_news.csv', encoding = 'utf-8-sig', index=False)

import os
import shutil

# Specify the path and filename of the CSV file you want to download
src_file = os.path.join('path/to/CSV', 'API_news.csv')

# Specify the path and filename where you want to save the CSV file
dst_file = os.path.join('C:\\', 'API_news.csv')

# Copy the CSV file to the specified location
shutil.copy(src_file, dst_file)