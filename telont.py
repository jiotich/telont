from bs4 import BeautifulSoup
import requests
import urllib.request
from urllib.error import HTTPError
import os
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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

class InvaluableArtist:
    def __init__(self,name):
        self.user = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"}
        self.name = name
        self.lastSearch=51
        self.fname = None
        self.lname = None
        self.code = None
        self.aPage = None
        self.linkA = None
        self.linkB = None
        self.revertName()
        self.findArtist()
    
    def seleniumGetHtml(self,link,webd):
        webd.get(link)
        html = webd.page_source
        soup = BeautifulSoup(html,'html5lib')
        print(">Got JS'ed page source")
        return soup
    
    def findArtist(self):
        if self.code is None:
            try:
                self.loadInvArtist()
                return
            except:
                print(">Could not retireve artist page from code.")
                pass
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        prelink = f"https://www.invaluable.com/search?keyword={self.name}"
        soup = self.seleniumGetHtml(prelink,driver)
        target = soup.find("a","item-title text-clamp-2 bold")#primeiro link da pesquisa
        prelink = "https://www.invaluable.com"+target['href']
        soup = self.seleniumGetHtml(prelink,driver)
        target = soup.find("div",class_="pull-right-sm",style="width:188px;")
        c = 1
        x = ""
        for item in target:
            if c == 2:
                x = item
                break
            c+=1
        link = "https://www.invaluable.com"+x['href']
        self.code = link[-11:-1]
        self.aPage = link
        self.linkA = link+"lots-at-auction"
        self.linkB = f"https://www.invaluable.com/catalog/searchLots.cfm?scp=m&artistref={code}&issc=1&ad=DESC&ord=2&shw=50&alf=1&row={self.lastSearch}"
        
        self.saveInvArtist()
        
        soup = self.seleniumGetHtml(link,driver)#CHEGA NA PAGINA DO ARTISTA
        driver.quit()

    def revertName(self,name=None):
        if name is None:
            name = self.name
        fname = ""
        lname = ""
        for n, letter in enumerate(name):
            if letter != " ":
                fname += letter
            else:
                lname = name[n+1:]
                break
        self.fname = fname
        self.lname = lname

    def saveInvArtist(self):
        if not os.path.isdir("data"):
                os.mkdir("data")
        with open(f"data/{self.name}","w") as file:
            file.write(f"{self.code},{self.aPage},{self.linkA},{self.linkB},{self.lastSearch}")

    def loadInvArtist(self,name=None):
        data = []
        if name is None:
            name=self.name
        try:
            with open(f"data/{name}","r") as file:
                data = file.readline().split(",")
        except:
            raise Exception(">No artist data on disk. Gonna need to download it.")
        self.code = data[0]
        self.aPage = data[1]
        self.linkA = data[2]
        self.linkB = data[3]
        self.lastSearch = int(data[4])
        

    def downloadImages(self,links):
        pathway = f"data/{self.lname}-{self.fname}/"
        og_pathway = pathway
        c = 1
        t = 1
        if not os.path.isdir(pathway):
                os.mkdir(pathway)
        for item in links:
            pathway = f"{og_pathway}{item[-20:]}"
            try:
                if not os.path.isfile(pathway):
                    print(f">[{c}/{t}] Downloading {item}")
                    sleep(random.randrange(0,2))
                    
                    with requests.get(item,headers=self.user) as req:
                        try:
                                urllib.request.urlretrieve(item,pathway)
                                c+=1
                            
                        except Exception as e:
                            print(">Error:",e)
                            pass
                else:
                    print(f"\n>{item} already downloaded")
            except Exception as e:
                print(">Error: ",e)
            t+=1

    def getSoldImages(self):
        html = requests.get("%s%s" % (self.linkB[:-2],self.lastSearch),headers=self.user)
        soup = BeautifulSoup(html.text,'html5lib')
        minims = soup.find_all('div',"photo")
        imgs = []
        for item in minims:
            try:
                imgs.append(f"{item.contents[1]['src'][:-8]}.jpg")
            except:
                pass
        self.downloadImages(imgs)
        self.lastSearch+=50
        self.saveInvArtist()
