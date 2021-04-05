#################################
##### Name: Shao-Wen
##### Uniqname: Chang
#################################

from bs4 import BeautifulSoup
import requests
import json
import time
import secrets # file that contains your API key

state_list = ['alaska', 'alabama', 'arkansas', 'american samoa', 'arizona', 'california', 'colorado', 'connecticut', 'district of columbia', 'delaware', 'florida', 'georgia', 'guam', 'hawaii', 'iowa', 'idaho', 'illinois', 'indiana', 'kansas', 'kentucky', 'louisiana', 'massachusetts', 'maryland', 'maine', 'michigan', 'minnesota', 'missouri', 'northern mariana islands', 'mississippi', 'montana', 'national', 'north carolina', 'north dakota', 'nebraska', 'new hampshire', 'new jersey', 'new mexico', 'nevada', 'new york', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'puerto rico', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'virginia', 'virgin islands', 'vermont', 'washington', 'wisconsin', 'west virginia', 'wyoming']
CACHE_FILE_NAME = 'cacheSI_proj2.json'
CACHE_DICT = {}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        return "{} ({}): {} {}".format(self.name, self.category, self.address, self.zipcode)

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

# Load the cache, save in global variable
CACHE_DICT = load_cache()

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    BASE_URL = 'https://www.nps.gov/index.htm'
    np_site_url = BASE_URL
    response = make_url_request_using_cache(np_site_url, CACHE_DICT)

    soup = BeautifulSoup(response, 'html.parser')

    dropdown_button = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    dropdown_button_li = dropdown_button.find_all('li')

    state_url_dict = {}
    for state_li in dropdown_button_li:
        dropdown_button_a = state_li.find('a')
        state = state_li.text.strip().lower()
        state_url_dict[state]= 'https://www.nps.gov' + dropdown_button_a.get('href')
    return state_url_dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''

    response = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')

    category = soup.find('span', class_='Hero-designation').text.strip()
    name = soup.find('a', class_='Hero-title').text.strip()
    
    area = soup.find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
    region = soup.find('span', attrs={'itemprop': 'addressRegion'}).text.strip()
    address = area + ', ' + region
    
    zipcode = soup.find('span', attrs={'itemprop': 'postalCode'}).text.strip()
    phone = soup.find('span', attrs={'itemprop': 'telephone'}).text.strip()
    return NationalSite(category, name, address, zipcode, phone)


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = make_url_request_using_cache(state_url, CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
    
    site_list_parent_ul = soup.find('ul', id = 'list_parks')
    site_lists_li = site_list_parent_ul('li', class_ = 'clearfix')

    nationalsite_object_list = []

    for site in site_lists_li:
        site_tag = site.find('a')
        site_path = site_tag['href']
        national_site_url = "https://www.nps.gov" + site_path + "index.htm"
        #print(national_site_url)
        nationalsite_instance = get_site_instance(national_site_url)
        nationalsite_object_list.append(nationalsite_instance)

    return nationalsite_object_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    baseurl = 'http://www.mapquestapi.com/search/v2/radius?'
    params = f"key={secrets.API_KEY}&origin={site_object.zipcode}&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json"
    url = baseurl + params
    
    response = make_url_request_using_cache(url, CACHE_DICT)
    result = json.loads(response)
    
    return result
    

if __name__ == "__main__":

    CACHE_DICT = load_cache()
    state_input = input("Enter a state name (e.g. Michigan, michigan) or \"exit\":")
    state_input_lower = state_input.lower()
    while state_input_lower != "exit":
    
        if state_input_lower not in state_list:
            print("[Error] Enter Proper State Name")
            state_input = input("Enter a state name (e.g. Michigan, michigan) or \"exit\":")

    
        else:
            dict_state_site = build_state_url_dict()
            state_url = dict_state_site[state_input_lower]
            national_park_state = get_sites_for_state(state_url)
            print('----------------')
            print(f'List of national sites in {state_input_lower}')
            print('----------------')
        
            n = 0
            for nationalsite_instance in national_park_state:
                n = n + 1
                print(f"[{n}] {nationalsite_instance.info()}")  
            
            num_nearbyplaces_input = input("Choose the number for detailed search or \"exit\" or \"back\": ")

            while num_nearbyplaces_input != "exit":
                if num_nearbyplaces_input == 'back':
                    state_input = input("Enter a state name (e.g. Michigan, michigan) or \"exit\":")
                    break
                else:
                    num_nearbyplaces_input = int(num_nearbyplaces_input)
                    if num_nearbyplaces_input in range(len(national_park_state)): 
                        num_nearbyplaces_input = int(num_nearbyplaces_input) - 1
                        places_dict = get_nearby_places(national_park_state[num_nearbyplaces_input])['searchResults']
                        print('----------------------------------------')
                        print(f"Places near {national_park_state[num_nearbyplaces_input].name}")
                        print('----------------------------------------')
                        for result in places_dict:
                            name = result['name']
                            if len(result['fields']['group_sic_code_name']) == 0:
                                category = 'no category'
                            else:
                                category = result['fields']['group_sic_code_name']

                            if len(result['fields']['address']) == 0:
                                street_address = 'no address'
                            else:
                                street_address = result['fields']['address']
                
                            if len(result['fields']['city']) == 0:
                                city = 'no city'
                            else:
                                city = result['fields']['city']

                            print(f"- {name} ({category}): {street_address}, {city}")
                        num_nearbyplaces_input = input('Choose number for detail search or \"exit\" or \"back\"\n:')
