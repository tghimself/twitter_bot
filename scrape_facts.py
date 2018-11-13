# import required
try:
    import requests
except:
    raise ModuleNotFoundError("please use \"pip install requests\" to install requests module")

try:
    from bs4 import BeautifulSoup
except:
    raise ModuleNotFoundError("please use \"pip install bs4\" to install requests module")

import shelve

def parse(url):
    '''parse url and save the data in data dict'''
    if "funfactz" in url: # check if the url is complete or not
        pass
    else:
        url = "https://funfactz.com/"+url #if not, complete it
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, 'html.parser')
    return [_.text for _ in soup.findAll("div",{"class":"fact_text"})]
    

page = requests.get('https://funfactz.com/tags/')
page.raise_for_status()
soup = BeautifulSoup(page.content, 'html.parser')

topics_temp = soup.findAll('ul',{'class':"topics cf"})

topics_temp = [_.findChildren("a") for _ in topics_temp]

topics = []

for _ in topics_temp:
    topics.extend(_)
print("topics saved...")
url_data = {}

for _ in topics:
    url_data[_.get("title")] = _.get("href")

data = shelve.open("data")
items_left=len(url_data)
for title,url  in url_data.items():
    print("saving for title \"" + str(title)+"\"\nitems left:", items_left)
    data[title.casefold()] = parse(url)
    items_left-=1

data.close()


