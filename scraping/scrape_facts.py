# import requ
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
    

page = requests.get('https://funfactz.com/tags/') # we use this website to scrape all of the facts
page.raise_for_status()
soup = BeautifulSoup(page.content, 'html.parser')

topics_temp = soup.findAll('ul',{'class':"topics cf"}) 

topics_temp = [_.findChildren("li") for _ in topics_temp]

topics = []

for _ in topics_temp:
    topics.extend(_)

counts = [int(i.span.text[1:-1])//8+1 for i in topics] # the count of facts in each topic and then divide it by 8 as each page has atmost 8 facts
print("topics saved...")

url_data = {}
for _ in topics:
    url_data[_.a.get("title")] = _.a.get("href") 

data = shelve.open("data", writeback = True)
items_left=len(url_data)
i=0                                                     # to run counts list with the dict 
for title,url  in url_data.items():
    print("saving for title \"" + str(title)+"\"")
    for count in range(counts[i]):
        if count!=0:                                    # http://url.com/tag/topic/1 is not a valid url, 
            new_url = url+str(count+1)
        else:
            new_url = url                               # http://url.com/tag/topic/2 is a valid url
        data.setdefault(title.casefold(),[])            # save a list by default
        data[title.casefold()].extend(parse(new_url))   # extend the parsed list into this list
        print("saved: ", len(data[title.casefold()]))
    i+=1                                                # increment to keep counts list in sync with the loop
    print("Progress: {:.3f}%".format(i/items_left*100)) # progress

data.close()


