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

topics_temp = [_.findChildren("li") for _ in topics_temp]

topics = []

for _ in topics_temp:
    topics.extend(_)

counts = [int(i.span.text[1:-1])//8+1 for i in topics]
print("topics saved...")
url_data = {}

for _ in topics:
    url_data[_.a.get("title")] = _.a.get("href")

data = {} # shelve.open("data")
items_left=len(url_data)
i=0
for title,url  in url_data.items():
    print("saving for title \"" + str(title)+"\"")
    for count in range(counts[i]):
        if count!=0:
            new_url = url+str(count+1)
        else:
            new_url = url
        data.setdefault(title.casefold(),[])
        data[title.casefold()].extend(parse(new_url))
        print("saved: ", len(data[title.casefold()]))
        # print(new_url, parse(new_url))
    i+=1
    print("Progress: {:.3f}%".format(i/items_left*100))

data.close()


