from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.error import HTTPError
import os
from time import sleep
import random

class WikiArtArtist:
    def __init__(self,name):
        self.user = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"}
        self.name = name
        self.url = self.wikiArtGetArtist(self.name)
        self.supper = self.getHtmlSoup(self.url)
        

    def wikiArtGetArtist(self,name):
        name = name.lower().replace(" ", "-")
        url = f"https://www.wikiart.org/en/{name}/all-works/text-list"
        return url
    
    def getHtmlSoup(self,link):
        html = requests.get(link,headers=self.user)
        #print(html.request.headers)
        soup = BeautifulSoup(html.text, 'html.parser')
        #print(">got soup")
        '''if not soup.find("li","painting-list-text-row"):
            link = link[27:]
            link = link.split("/",1)[0]
            newLink = f"https://www.wikiart.org/en/Search/{link}"
            html = requests.get(newLink,headers=user)
            soup = BeautifulSoup(html.text, 'html.parser')
            #print(soup.find_all("div", {'class':'artist-name'}))
            print(soup)'''
        return soup
    
    def findWikiImageLinks(self,soupHtml):
        allLinks = soupHtml.find_all(itemprop="image")
        for link in allLinks:
            return link['src']
        #print(">got image links")
    
    def findAndDownload(self,soupHtml=None,highRes=True):
        if soupHtml is None:
            soupHtml = self.supper
        allLinks = soupHtml.find_all("li","painting-list-text-row")
        pathway = "%s_high_res" % (self.name.lower().replace(" ", "-")) if highRes else "%s" % (self.name.lower().replace(" ", "-"))
        pathway_og = pathway
        allPaintingPages = {}
        imageLinks = {}
        c = 1
        if not allLinks:
            print("Erro 404. O nome do artista provavelmente não está adequado.")
            return
        for link in allLinks:
            #print(f"{(link.contents[1]['href']}\n")#links
            #print(f"{link.contents[1].contents}\n")#titulos
            allPaintingPages[link.contents[1].contents[0]]=f"http://wikiart.org{link.contents[1]['href']}"
        #print(">links to images")
        print(pathway)
        if not os.path.isdir(pathway):
                os.mkdir(pathway)
            
        for link in allPaintingPages:
            pathway = f"{pathway_og}/{link}.jpg"
            if not os.path.isfile(pathway):
                print(f"[{c}/{len(allPaintingPages)}] Downloading {link}")
                sleep(random.randrange(0,4))
                
                with requests.get(allPaintingPages[link],headers=self.user) as req:
                    soup = BeautifulSoup(req.text, 'html.parser')
                    imageLinks[link] = self.findWikiImageLinks(soup)
                    
                    try:
                        if highRes:
                            urllib.request.urlretrieve(imageLinks[link][:len(imageLinks[link])-10],pathway)
                        else:
                            urllib.request.urlretrieve(imageLinks[link],pathway)
                        c+=1
                    except HTTPError as e:
                        if not os.path.isfile(pathway):
                            urllib.request.urlretrieve(imageLinks[link],pathway)
                            c+=1
                        
                    except Exception as e:
                        print(">Error:",e)
                        pass
            else:
                print(f"\n>{link} already downloaded")
                c+=1

        return imageLinks

art = WikiArtArtist(input("Artista: "))
art.findAndDownload(highRes=False)
