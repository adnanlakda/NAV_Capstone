
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
    sub_category_info = get_sub_category(main_category, title, text) # call out to get_sub_category module
    row[4] = sub_category_info
print(df)
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

