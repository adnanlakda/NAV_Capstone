# TODO: Add doc string to describe module
# TODO: add comments throughout file to describe what it does

from newspaper import Article
from newspaper import Config
import newspaper
import locationtagger
import geopy
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
from geopy import geocoders 
import nltk
from nltk.tokenize import word_tokenize
import string
import re
import pandas as pd


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

def get_location(url, title):
    
    lat = float(11.10)
    lon = float(11.10)
    #date = 'NA'
    city = 'NA'
    oblast = 'NA'
    country = 'NA'
    
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

    config = Config()
    config.browser_user_agent = user_agent
    config.request_timeout = 20

    article = Article(url,config=config)
    article.download()
    article.parse()
    article.nlp()
    article_summary = article.summary
    
    article_summary = re.sub(r'[^\w\s]', ' ', article_summary)
    
    #print(article_summary)
    
    possible_locs = []
    location_dict = {}
    i_index = 0
    locations = []
    geolocator = GoogleV3('AIzaSyDF3wKwT3Eov1bu-1_J5Tf4rJJkd8TEu58')

    place_entity = locationtagger.find_locations(url = url)
    possible_locs += place_entity.cities
    possible_locs += place_entity.other

    place_entity = locationtagger.find_locations(text = article_summary)
    possible_locs += place_entity.cities
    possible_locs += place_entity.other

    place_entity = locationtagger.find_locations(text = title)
    possible_locs += place_entity.cities
    possible_locs += place_entity.other
            
    title_tokens = word_tokenize(title)
    summary_tokens = word_tokenize(article_summary)

    if 'the' in summary_tokens:
        summary_tokens.remove('the')

    if 'The' in summary_tokens:
        summary_tokens.remove('The')
    
    if 'capital' in summary_tokens:
        summary_tokens.remove('capital')
        
    if 'of' in summary_tokens:
        summary_tokens.remove('of')
        
    possible_locs = [*set(possible_locs)]
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for i in possible_locs:
        if '-' in i:
            possible_locs.remove(i)
        elif i in months:
            possible_locs.remove(i)
        elif 'Seven' in i:
            possible_locs.remove(i)
        elif 'Russia' in i:
            possible_locs.remove(i)
            
    if 'Donbas' in possible_locs and title_tokens:
        locations.append('Donbas')
    
    for i in possible_locs:
        if i in summary_tokens:
            summary_index = summary_tokens.index(i)
            #if summary_index+1 > 
            if summary_index+1 < len(summary_tokens):
                if summary_tokens[summary_index-1] == 'in':
                    locations.append(i)
                    #print(i)
                elif summary_tokens[summary_index+1] == 'to':
                    pass
                elif summary_tokens[summary_index-1] == 'In':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'On':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'on':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'toward':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'attacks':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'city':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'town':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'streets':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'as':
                    locations.append(i)
                elif summary_tokens[summary_index+1] == 'villages':
                    locations.append(i)
                elif summary_tokens[summary_index-1] == 'of':
                    locations.append(i)
                elif summary_tokens[summary_index] == 0:
                    locations.append(i)
                else:
                    pass
        elif i in title_tokens:
            title_index = title_tokens.index(i)
            if title_tokens[title_index-1] == 'in':
                locations.append(i)
            elif title_tokens[title_index-1] == 'to':
                locations.append(i)
            elif title_tokens[title_index] == 0:
                locations.append(i)
            elif title_tokens[title_index-1] == 'In':
                locations.append(i)
            elif title_tokens[title_index-1] == 'on':
                locations.append(i)
            elif title_tokens[title_index-1] == 'On':
                locations.append(i)
            elif title_tokens[title_index-1] == 'attacks':
                locations.append(i)
            elif title_tokens[title_index-1] == 'of':
                locations.append(i)
            else:
                pass
        else:
            pass
    
    locations = [*set(locations)]
    
    for i in locations:
        if '-' in i:
            locations.remove(i)
        elif i in months:
            locations.remove(i)
    
    #precise_loc = ''
    
    #print(locations)
    #print(article_summary)
    
    for i in locations:
        try:
            location = geolocator.geocode(i)
            if 'sublocality' in location.raw['types']:
                break
            elif 'locality' in location.raw['types']:
                #precise_loc = i
                break
            elif 'colloquial_area' in location.raw['types']:
                #precise_loc = i
                pass
            else:
                #pass
                break
        except:
            locations.remove(i)
            pass
    
    if len(locations) > 0:
        
        lat = float(1.1)
        lon = float(1.1)
        #date = 'NA'
        city = 'NA'
        oblast = 'NA'
        country = 'NA'
        
        if type(location) == geopy.location.Location:
            #print(type(location))
            for i in location.raw['address_components']:
                print(i)
                if 'country' in i['types']:
                    country = i['short_name']
                elif 'administrative_area_level_1' in i['types']:
                    oblast = i['short_name']
                elif 'administrative_area_level_2' in i['types']:
                    oblast = i['short_name']
                elif 'colloquial_area' in i['types']:
                    oblast = i['short_name']
                elif 'locality' in i['types']:
                    city = i['long_name']
                else:
                    pass
            
            
            lat = float(location.raw['geometry']['location']['lat'])
            lon = float(location.raw['geometry']['location']['lng'])
            #print(pd.Series([lat, lon, city, oblast, country]), url)
            return [lat, lon, city, oblast, country]
            
        else:
            lat = float(1.1)
            lon = float(1.1)
            #date = 'NA'
            city = 'NA'
            oblast = 'NA'
            country = 'NA'
    
            #lat = float(location.raw['geometry']['location']['lat'])
            #lon = float(location.raw['geometry']['location']['lng'])
            #print(pd.Series([lat, lon, city, oblast, country]), url)
            return [lat, lon, city, oblast, country]
    
    else:
        
        lat = float(11.10)
        lon = float(11.10)
        #date = 'NA'
        city = 'NA'
        oblast = 'NA'
        country = 'NA'
        
        print(pd.Series([lat, lon, city, oblast, country]), url)
        return [lat, lon, city, oblast, country]



#get_location(url='https://kyivindependent.com/news-feed/russia-bombardment-of-ukraine-kills-6-injures-36', title="Russia's bombardment of Ukraine kills 6, injures 36")