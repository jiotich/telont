from bs4 import BeautifulSoup
import requests
import urllib.request
import os
from time import sleep
import random

instructions = '''
Para usar a ferramenta, digite o nome e sobrenome mais populares de um pintor, ignorando acentos.
Ex: Vincent Van Gogh, Claude Monet, Egon Schiele, Salvador Dali

Caso haja dúvida quanto ao nome do artista, procure na WikiArt
Ex: wikiart.org/en/joan-miro -> Joan Miro seria o nome correto.

Em caso de erro o programa fecha sem fazer nada.

O programa para ao terminar de baixar todas as obras, mas no caso de ser parado prematuramente (programa é fechado, internet cai, etc)
ele continuará na pintura onde parou, não criandos duplicatas.

A pasta com os arquivos .jpg é criada no diretorio onde o programa foi executado, com o nome do autor.\n\n
'''

def getHtmlSoup(link):
    html = requests.get(link,headers=user)
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

def findWikiImageLinks(soupHtml):
    allLinks = soupHtml.find_all(itemprop="image")
    for link in allLinks:
        return link['src']
    #print(">got image links")

def findAllWikiArtLinks(soupHtml):
    allLinks = soupHtml.find_all("li","painting-list-text-row")
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
    
    if not os.path.isdir(artist.lower().replace(" ", "-")):
        os.mkdir(artist.lower().replace(" ", "-"))
        
    for link in allPaintingPages:
        pathway = "%s/%s.jpg" % (artist.lower().replace(" ", "-"),link)
        if not os.path.isfile(pathway):
            print(f"[{c}/{len(allPaintingPages)}] Downloading {link}")
            sleep(random.randrange(0,4))
            
            with requests.get(allPaintingPages[link],headers=user) as req:
                soup = BeautifulSoup(req.text, 'html.parser')
                imageLinks[link] = findWikiImageLinks(soup)
                
                try:
                    urllib.request.urlretrieve(imageLinks[link],pathway)
                except Exception as e:
                    print(">Error:",e)
                    pass
        else:
            print(f"\n>{link} already downloaded")
        c+=1
    #print(">got images themselves")

    return imageLinks

def wikiArtGetArtist(name):
    name = name.lower().replace(" ", "-")
    url = f"https://www.wikiart.org/en/{name}/all-works/text-list"
    return url

print(instructions)
input("Pressione enter para proceder.\n")
user = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"}
artist = str(input("Nome do artista: "))
linkAndTitleDict = findAllWikiArtLinks(getHtmlSoup(wikiArtGetArtist(artist)))