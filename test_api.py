import http.client, urllib.parse
import json
import pandas as pd

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
    author = article['author']
    title = article['title']
    description = article['description']
    url = article['url']
    source = article['source']
    published_at = article['published_at']

    # Append the scraped data to the list
    scraped_data.append({
        'author': author,
        'title': title,
        'description': description,
        'url': url,
        'source': source,
        'published_at': published_at
    })

df_API = pd.DataFrame(scraped_data)
#df = df[df['title'].isin(['Ukrain', 'Russian'])]

df_API.head() #display dataframe

# update the date format
# Convert the 'published_at' column to datetime objects and then format them into yyyy-mm-dd strings
df_API['published_at'] = pd.to_datetime(df_API['published_at']).dt.strftime('%Y-%m-%d')

# Assuming your dataframe is called df_API
df_API.to_csv('API_news.csv', encoding = 'utf-8-sig',index=False)

import os
import shutil

# Specify the path and filename of the CSV file you want to download
src_file = os.path.join('path/to/CSV', 'API_news.csv')

# Specify the path and filename where you want to save the CSV file
dst_file = os.path.join('C:\\', 'API_news.csv')

# Copy the CSV file to the specified location
shutil.copy(src_file, dst_file)