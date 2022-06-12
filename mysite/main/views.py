from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CreateNewNews
# Create your views here.

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

#for scraping
import requests
from bs4 import BeautifulSoup
import random
import json
from datetime import datetime
from datetime import timedelta

# import quopri

from newsapi import NewsApiClient

def index(request):
    # add source preferences and keyword preferences in arguments
    # scrapeMauritius()
    # scrapeInternational()
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    if request.session.has_key('username'):
        context = {}
        # All resource paths end in .html.
        # Pick out the html file name from the url. And load that template.
        try:

            load_template = request.path.split('/')[-1]

            if load_template == 'admin':
                return HttpResponseRedirect(reverse('admin:index'))
            context['segment'] = load_template

            html_template = loader.get_template('home/' + load_template)
            return HttpResponse(html_template.render(context, request))

        except template.TemplateDoesNotExist:

            html_template = loader.get_template('home/page-404.html')
            return HttpResponse(html_template.render(context, request))

        except:
            html_template = loader.get_template('home/page-500.html')
            return HttpResponse(html_template.render(context, request))
    else:
        return redirect("/login/")


user_agents = [ 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
    ]

# get current date and remove 2 weeks from it
two_weeks_ago = datetime.now().date() - timedelta(days=14)

#mauritius
def scrapeMauritius():
    scrapeLexpress()
    scrapeDefimedia()
    scrapeRadio1()
    scrapeMBC()
    scrapeMauritiustimes()
    scrapeLemauricien()
    scrapeIONnews()

import http.client, urllib.parse, json
from newsdataapi import NewsDataApiClient
def scrapeInternational():

    categories=["business", "entertainment", "general","health","science","sports","technology"]
    # newsapi = NewsApiClient(api_key='5b6b382928fa426f9b2e4912c21617f7')
    for category in categories:

        url = "https://newsapi.org/v2/top-headlines?pageSize=100&"+category+"=business&language=en&sortBy=popularity&apiKey=5b6b382928fa426f9b2e4912c21617f7"
        news = requests.get(url).json()
        with open("main/news-articles/international/"+category+".json", "w", encoding="utf-8") as outfile:
                json.dump(news, outfile, indent = "")



def scrapeLexpress():
    months=["jan", "fév","mar", "avr", "mai","jun","jul","août", "sep", "oct", "nov", "déc" ]
    # id=0

    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}
    # create array for all category links
    categories = [["politics","politique"], ["miscellaneous","societe/faits-divers"], ["police-and-justice","societe/police-et-justice"], ["solidarity","societe/solidarite"], ["education","societe/education"], ["infrastructure","societe/infrastructures"], ["environment","societe/environnement"], ["health","societe/sante"],["who-cares","societe/who-cares%3F"],["ephemeris", "societe/ephemeride"], ["business","economie/entreprises"], ["real-estate","economie/immobilier"], ["job","economie/emploi"],["practical-information","economie/infos-pratiques"], ["tourism","economie/tourisme"], ["sport","sport/sport-local"], ["turf","sport/turf"],["north","regions/nord"],["south","regions/sud"],["east","regions/est"],["west","regions/ouest"],["rodrigues","regions/rodrigues"],["editorial","idees/editorial"],["court","idees/tribune"],["opinion","idees/opinions"],["focus","idees/focus"],["blog","idees/blogs"]]

    id=0
    for category in categories:
        print(category)

        current_page_articles=[]

        response = requests.get('https://www.lexpress.mu/'+category[1], headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        page_links=[]
        
        # i=0
        # code to get all the subpages' links and store them into an array
        sublinks = soup.find_all("div", {"class": "pagination-slide-wrapper"})
        for div in sublinks:
            for a in div.find_all('a'):
                page_links.append(a['href'])
                # print (links[i])
                # i+=1

        # get sub links of each category page
        for i in range(0,15):
            stri = "https://www.lexpress.mu/"+category[1]+ "/"+ str(i+1)
            page_links.append(stri)
            # print (links[i])
            # i+=1

        outdated_flag = False
        for j in range(0,15):
            if outdated_flag == True:
                break
            # get article links
            response = requests.get(page_links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")
            heading = soup.find_all("div", {"class": "heading"})
            # code to get all links to main article
            article_links=[]
            for div in heading:
                # print (div.a['href'])
                article_links.append(div.a['href'])

            # get data from each article link in current page to put into json(14 links in a page)
            
            for i in range(14):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                heading = soup.find_all("div", {"class": "metadata-wrapper"})
                heading = soup.find_all("span", {"class": "icon"})
                for content in heading:
                    if content.find('a') != None:
                        # if string not empty(contain only spaces)
                        if (not content.find('a').text) == False:
                            # remove excess whitespaces from beg and end of string
                            date = content.find('a').text.lower()
                            split = date.split()
                            dd = split[0]
                            mm = months.index(split[1])+1
                            yy = split[2]
                            a_date = dd+" "+str(mm)+" "+yy
                            article_date = datetime.strptime(a_date, '%d %m %Y').date()
                            if article_date<two_weeks_ago:
                                outdated_flag = True

                if outdated_flag == True:
                    break
                # get title of article
                heading = soup.find_all("div", {"class": "lx-block-header"})
                for content in heading:
                    if content.find('h1') != None:
                        title = content.find('h1')
                        title = str(title.text)
                        # print("title: "+ title)


                # get image link
                heading = soup.find_all("div", {"class": "main-image-wrapper"})
                for content in heading:
                    # if content has image tag
                    if content.find('img') != None:
                        image=content.find('img')['src']

                # get content of article
                article_content=""
                heading = soup.find_all("div", {"class": "article-content"})
                for content in heading:
                    for p in content.find_all('p'):
                        article_content += " "+ p.text
                    

                dictionary ={
                "id" : "",
                "source" : "lexpress",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1

        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/lexpress/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
        
    
def scrapeDefimedia():
    months=["janvier", "février","mars", "avril", "mai","juin","juillet","août", "septembre", "octobre", "novembre", "décembre" ]
    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}
    # create array for all category links
    categories=[["news","actualites"],["miscellaneous","faits-divers"],["explikouka","explikouka"],["defi-zen","defi-zen"],["politics","politique"],["people","people"],["magazine","magazine"],["news-sunday","news-sunday"],["technology","techno"],["budget","budget"]]
    for category in categories:
        print(category)
        current_page_articles=[]
        response = requests.get('https://defimedia.info/categorie/'+ category[1], headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0
        
        # get sub links of each category page
        for i in range(0,15):
            stri = "https://defimedia.info/categorie/"+category[1]+ "?page="+ str(i)
            links.append(stri)
            # print (links[i])
            i+=1
        outdated_flag = False
        for j in range(0,15):
            if outdated_flag == True:
                break
            # get article links for each page untill longer than 2 weeks
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            mydivs = soup.find_all("div", {"class": "article-img"})
            # print(mydivs)
            article_links=[]
            for div in mydivs:
                article_links.append("https://defimedia.info/"+ str(div.a['href']))

            # get data from each article link in current page to put into json
            
            # outdated_flag = False
            for i in range(11):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                heading = soup.find_all("div", {"class": "submitted"})
                for content in heading:
                    # remove excess whitespaces from beg and end of string
                    date = content.text.lower()
                    split = date.split()
                    dd = split[0]
                    mm = months.index(split[1])+1
                    yy = split[2]
                    a_date = dd+" "+str(mm)+" "+yy
                    # print("date: "+ a_date)
                    article_date = datetime.strptime(a_date, '%d %m %Y').date()
                    if article_date<two_weeks_ago:
                        outdated_flag = True

                if outdated_flag == True:
                    break

                # get title of article
                heading = soup.find_all("h1", {"class": "page-header"})
                # print(heading)
                for content in heading:
                    title = content.text
                    # print("title: "+ title)

                # get image link
                heading = soup.find_all("div", {"class": "field--name-field-main-picture"})
                for content in heading:
                    # if content has image tag
                    # break because there were many img links and we need first only
                    if content.find('img') != None:
                        image=content.find('img')['src']
                        # print("image link: "+ image)
                        break

                # get content of article
                article_content=""
                heading = soup.find_all("div", {"class": "content"})
                for content in heading:
                    for divs in content.find_all("div", {"class": "field--type-text-with-summary"}):
                        for p in divs.find_all('p'):
                            article_content += " "+ p.text
                # print(article_content)
                dictionary ={
                "id" : "",
                "source" : "defimedia",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1

        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/defimedia/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
        

    
    # ONLY "ACTU" tab contains updated news articles


    # # create array for all category links
    # categories=[["actualities","actu"],["consumption","conso"],["job","emploi"],["entrepreneur","entrepreneur"],["better understand","mieux-comprendre"]]
    # months=["janvier", "février","mars", "avril", "mai","juin","juillet","august", "september", "october", "november", "december" ]
    # for category in categories:
    #     print(category)
    #     response = requests.get('https://defieconomie.defimedia.info/'+ category[1], headers=headers)
    #     content = response.text
    #     soup=BeautifulSoup(content, "html.parser")
    #     links=[]
        
    #     # get sub links of each category page
    #     for i in range(0,11):
    #         stri = "https://defieconomie.defimedia.info/"+category[1]+ "?page="+ str(i)
    #         links.append(stri)
    #         # print (links[i])
    #         i+=1


    #     # get article links for each page untill longer than 2 weeks
    #     response = requests.get(links[0], headers=headers)
    #     content = response.text
    #     soup=BeautifulSoup(content, "html.parser")

    #     # code to get all links to main article
    #     main = soup.find_all("div", {"class": "categories-view-content view-content-wrap"})
    #     # print(main)
    #     for divs in main:
    #         # print(divs.find_all('a'))
    #         mydivs = divs.find_all("h3",{"class": "post-title"})
    #         # print(mydivs)

    #         article_links=[]
    #         for div in mydivs:
    #             # print(div.a['href'])
    #             article_links.append("https://defieconomie.defimedia.info/"+ str(div.a['href']))
    #         mydivs = divs.find_all("div",{"class": "post-title"})
    #         for div in mydivs:
    #             # print(div.a['href'])
    #             article_links.append("https://defieconomie.defimedia.info/"+ str(div.a['href']))
    #     # print(article_links)

    #     # get data from each article link in current page to put into json
    #     current_page_articles=[]
    #     outdated_flag = False
    #     for i in range(len(article_links)):

    #         response = requests.get(article_links[i], headers=headers)
    #         content = response.text
    #         soup=BeautifulSoup(content, "html.parser")

    #         # get date of article, if article is older than 2 weeks, stop scraping
    #         heading = soup.find_all("div", {"id": "page-main-content"})
    #         for content in heading:
    #             d = content.find("span", {"class": "post-created"})
    #             # remove excess whitespaces from beg and end of string
    #             date = d.text.lower()
    #             split = date.split()
    #             dd = split[0]
    #             mm = months.index(split[1])+1
    #             yy = split[2]
    #             a_date = dd+" "+str(mm)+" "+yy
    #             # print("date: "+ a_date)
    #             article_date = datetime.strptime(a_date, '%d %m %Y').date()
    #             # print(article_date)
    #             if article_date<two_weeks_ago:
    #                 outdated_flag = True

    #         if outdated_flag == True:
    #             break

    #         # get title of article
    #         heading = soup.find_all("h1", {"class": "post-title"})
    #         # print(heading)
    #         for content in heading:
    #             title = content.text
    #             # print("title: "+ title)

    #         # get image link
    #         heading = soup.find_all("div", {"id": "page-main-content"})
    #         for content in heading:
    #             # print(content)
    #             img = content.find_all("div", {"class": "field--name-field-image"})
    #             # print(img)
    #             # if content has image tag
    #             # break because there were many img links and we need first only
    #             for data in img:
    #                 if data.find('img') != None:
    #                     image="https://defieconomie.defimedia.info"+data.find('img')['data-src']
    #                     # print("image link: "+ image)
    #                     break

    #         # get content of article
    #         article_content=""
    #         heading = soup.find_all("div", {"id": "page-main-content"})
    #         for content in heading:
    #             for divs in content.find_all("div", {"class": "field--type-text-with-summary"}):
    #                 for p in divs.find_all('p'):
    #                     article_content += " "+ p.text
    #         # print(article_content)
    #         dictionary ={
    #         "id" : "",
    #         "source" : "defimedia",
    #         "title" : "",
    #         "article_link" : "",
    #         "image_link" : "",
    #         "date" : "",
    #         "summary" : "",
    #         "article_content" : ""
    #         }
    #         dictionary["id"]= id
    #         dictionary["title"]= title
    #         dictionary["article_link"]= article_links[i]
    #         dictionary["image_link"]= image
    #         dictionary["date"]= a_date
    #         dictionary["article_content"]= article_content
    #         # print(dictionary)
    #         current_page_articles.append(dictionary)

    #         # Serializing json 
    #         json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
    #         # Writing to sample.json
    #         with open("main/news-articles/mauritius/defimedia/"+category[0]+".json", "w", encoding="utf-8") as outfile:
    #             outfile.write(json_object)
    #         id+=1


def scrapeRadio1():
    months=["janv.", "févr.","mars", "avril", "mai","juin","juil.","août", "sept.", "oct.", "nov.", "déc." ]
    
    categories= [["politics","politique"],["miscellaneous","fait-divers"],["economy","economie"],["health","sante"],["environment","environnement"],["science and technology","technologie"],["regional","regionale"],["sports","sports"],["people","people"],["infrastructure","infrastructures"],["society","societe"],["rodrigues","rodrigues"],["court","judiciaire"],["culture","culture"],["education","education"],["entertainment","cinema-et-musique"],["meteo","meteo"],["Obituary","avis-de-deces"]]

    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}

    for category in categories:
        current_page_articles=[]
        print(category)

        response = requests.get('https://www.r1.mu/actu/'+category[1], headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0

        # get sub links of each category page
        for i in range(0,15):
            stri = "https://www.r1.mu/actu/"+category[1]+ "&page="+ str(i)
            links.append(stri)
            # print (links[i])
            # i+=1

        outdated_flag = False
        for j in range(0,15):
            if outdated_flag == True:
                break

            # get article links for each page untill longer than 2 weeks
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            mydivs = soup.find_all("article", {"class": "large-up-3"})
            # print(mydivs)
            article_links=[]
            for div in mydivs:
                for a in div.find_all('a'):
                    article_links.append(a['href'])

            # get data from each article link in current page to put into json
            
            
            for i in range(29):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")
            
                # get date of article, if article is older than 2 weeks, stop scraping
                content = soup.find("p", {"class": "date-published"})
                # print(heading)
                # remove excess whitespaces from beg and end of string
                date = content.text.lower()
                split = date.split()
                dd = split[0]
                mm = months.index(split[1])+1
                yy = split[2]
                a_date = dd+" "+str(mm)+" "+yy
                # print("date: "+ a_date)
                article_date = datetime.strptime(a_date, '%d %m %Y').date()
                if article_date<two_weeks_ago:
                    outdated_flag = True

                if outdated_flag == True:
                    break

                # get title of article
                heading = soup.find("figcaption")
                title = heading.find('h1').text
                # print("title: "+ title)

                # get image link
                # heading = soup.find("figure")
                content = soup.find("div", {"class": "preview"})
                # print(content.find('img')['data-src'])
                if content.find('img') != None:
                    image=content.find('img')['data-src']
                    # print("image link: "+ image)
                
                # get content of article
                article_content=""
                for content in heading.find_all('p'):
                    # print(content)
                    article_content += " "+ content.text
                
                # print(article_content)

                # print(article_content)
                dictionary ={
                "id" : "",
                "source" : "radio1",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1  
        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/radio1/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
            


def scrapeMBC():
    months=["jan", "feb","mar", "apr", "may","jun","jul","aug", "sep", "oct", "nov", "dec" ]
    categories= [["local","local"],["world","world"],["rodrigues","rodrigues"],["business","business"],["culinary","culinary"],["culture","culture"],["discovery","discovery"],["entertainment","entertainment"],["health","health"],["music","music"],["politics","politics"],["religion","religion"],["society","society"],["technology","technology"],["miscellaneous","faits-divers"],["people","people"]]
    
    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}

    for category in categories:
        current_page_articles=[]
        print(category)

        response = requests.get('https://mbcradio.tv/news/'+category[1], headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0

        # get sub links of each category page
        for i in range(0,15):
            stri = "https://mbcradio.tv/news/"+category[1]+ "?page="+ str(i)
            links.append(stri)
            # print (links[i])
            # i+=1

        outdated_flag = False
        for j in range(0,15):
            if outdated_flag == True:
                break

            # get article links for each page untill longer than 2 weeks
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            heading = soup.find_all("div", {"class": "view-id-news_term_page"})
            counter = 0
            article_links=[]
            for divs in heading:
                for contents in divs.find_all("div", {"class": "views-field-title"}):
                    if counter==6:
                        break
                    article_links.append("https://mbcradio.tv/"+contents.find('a')['href'])
                    counter +=1

            # get data from each article link in current page to put into json
            
            
            for i in range(6):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                heading = soup.find_all("time", {"class": "full-format"})
                for content in heading:
                    # remove excess whitespaces from beg and end of string
                    date = content.text.lower()
                    split = date.split()
                    dd = split[1].strip(',')
                    mm = months.index(split[0])+1
                    yy = split[2]
                    a_date = dd+" "+str(mm)+" "+yy
                    # print("date: "+ a_date)
                    article_date = datetime.strptime(a_date, '%d %m %Y').date()
                    # print(article_date)
                    if article_date<two_weeks_ago:
                        outdated_flag = True

                if outdated_flag == True:
                    break

                # get title of article
                heading = soup.find("h1", {"id": "page-title"})
                # print(heading.text)
                title = heading.text

                # get image link
                heading = soup.find_all("div", {"class": "field-name-field-image"})
                for content in heading:
                    # if content has image tag
                    # break because there were many img links and we need first only
                    if content.find('img') != None:
                        image=content.find('img')['src']
                        # print("image link: "+ image)
                        break

                # get content of article
                #span paragraph was not the same for articles with video included,
                #try for exception was needed to try another way
                article_content=""
                heading = soup.find_all("p", {"class": "rtejustify"})
                for content in heading:
                    for divs in content:
                        try:
                            for span in divs.find_all('span'):
                                article_content += " "+ span.text
                        except:
                            # print(divs)
                            try:
                                # print(divs.find('span').text)
                                # print(content)
                                article_content+=divs.find('span').text
                            except:
                                # print(divs.text)
                                # print(content)
                                article_content+=divs.text
                # print(article_content)

                dictionary ={
                "id" : "",
                "source" : "mbc",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1
        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/mbc/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
            
def scrapeMauritiustimes():
    months=["january", "february","march", "april", "may","june","july","august", "september", "october", "november", "december" ]
    categories= [["editorials","editorials"],["interviews","interviews"],["reports-and-publications","reports-and-publications"],["culture","culture"],["politics","politics"],["economy","economy"],["history","history"],["education","education"],["society","society"],["language","language"],["sports","sports"],["entertainment","entertainment"],["wellness","wellness"]]

    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}

    for category in categories:
        current_page_articles=[]
        print(category)

        response = requests.get('http://www.mauritiustimes.com/mt/category/features/'+category[1]+"/", headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0

        # get sub links of each category page
        for i in range(0,15):
            stri = "http://www.mauritiustimes.com/mt/category/features/"+category[1]+ "/page/"+ str(i)+"/"
            links.append(stri)
            # print (links[i])
            # i+=1

        outdated_flag = False
        for j in range(0,15):
            if outdated_flag == True:
                break
            # get article links for each page untill longer than 2 weeks
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            heading = soup.find_all("div", {"class": "article"})
            article_links=[]
            for divs in heading:
                for contents in divs.find_all("article", {"class": "post excerpt"}):
                    article_links.append(contents.find('a')['href'])
                    # print(contents.find('a')['href'])

            # get data from each article link in current page to put into json
            
            
            for i in range(15):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                content = soup.find("span", {"class": "thetime"})
                # print ( heading)
                # remove excess whitespaces from beg and end of string
                date = content.text.lower()
                split = date.split()
                dd = split[1].strip(',')
                mm = months.index(split[0])+1
                yy = split[2]
                a_date = dd+" "+str(mm)+" "+yy
                # print("date: "+ a_date)
                article_date = datetime.strptime(a_date, '%d %m %Y').date()
                # print(article_date)
                if article_date<two_weeks_ago:
                    outdated_flag = True

                if outdated_flag == True:
                    break

                # get title of article
                heading = soup.find("h1", {"class": "single-title"})
                # print(heading.text)
                title = heading.text

                # get image link
                heading = soup.find_all("div", {"class": "post-single-content"})
                
                for content in heading:
                    # print(content)
                    # some articles don't have image, hence, image=""
                    if content.find('img') != None:
                        image=content.find('img')['src']
                        # print("image link: "+ image)
                        # break
                    else:
                        image=""

                # get content of article
                article_content=""
                for data in heading:
                    for p in data.find_all('p'):
                        # print(p.text)
                        article_content+=p.text

                dictionary ={
                "id" : "",
                "source" : "mauritiustimes",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1
        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/mauritiustimes/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
            

def scrapeLemauricien():
    months=["jan", "fév","mar", "avr", "mai","juin","juil","août", "sep", "oct", "nov", "déc" ]
    categories= [["politique","politique"],["economie","economie"],["faits-divers","faits-divers"],["societe","societe"],["forum","forum"],["opinions","opinions"],["technologie","technologie"],["sports","sports"],["magazine","magazine"],["turf","turf"],["week-end","week-end"],["scope","scope"]]

    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}

    for category in categories:
        # put a counter to iterate for more that 1 page, in case data from2 weeks is in second page, line 110
        current_page_articles=[]
        print(category)

        response = requests.get('https://www.lemauricien.com/category/'+category[1]+"/", headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0

        # get sub links of each category page
        for i in range(0,9):
            stri = "https://www.lemauricien.com/category/actualites/"+category[1]+ "/page/"+ str(i+1)+"/"
            links.append(stri)
            # print (links[i])
            i+=1

        # get article links for each page untill longer than 2 weeks

        outdated_flag = False
        for j in range(0,9):
            if outdated_flag == True:
                break
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            heading = soup.find_all("div", {"class": "tdb-category-loop-posts"})
            # print(heading.a['href'])
            article_links=[]
            for divs in heading:
                for contents in divs.find_all("h3", {"class": "td-module-title"}):
                    # print(contents.find('a')['href'])
                    article_links.append(contents.find('a')['href'])


            # get data from each article link in current page to put into json
            
            for i in range(10):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                content = soup.find("time", {"class": "td-module-date"})
                # print ( heading)
                # remove excess whitespaces from beg and end of string
                date = content.text.lower()
                split = date.split()
                dd = split[0]
                mm = months.index(split[1])+1
                yy = split[2]
                a_date = dd+" "+str(mm)+" "+yy
                # print("date: "+ a_date)
                article_date = datetime.strptime(a_date, '%d %m %Y').date()
                # print(article_date)
                if article_date<two_weeks_ago:
                    outdated_flag = True

                if outdated_flag == True:
                    break

                # get title of article
                heading = soup.find("h1", {"class": "tdb-title-text"})
                # print(heading.text)
                if heading != None:
                    title = heading.text

                # get image link
                image=""
                heading = soup.find_all("div", {"class": "tdb_single_featured_image"})
                for content in heading:
                    if content.find('a') != None:
                        # print(content.find('a')['href'])
                        image = content.find('a')['href']
                # for article with video instead of image
                else:
                    heading = soup.find_all("div", {"class": "_3fnx _1jto _4x6d _8yzm _3htz"})
                    for content in heading:
                        # print(content.find('img')['src'])
                        image = content.find('a')['href']

                # get content of article
                heading = soup.find_all("div", {"class": "tdb-block-inner"})
                article_content=""
                for data in heading:
                    # print(data.p)
                    for p in data.find_all('p'):
                        # print(p.text)
                        article_content+=p.text

                dictionary ={
                "id" : "",
                "source" : "lemauricien",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1
        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/lemauricien/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
                


def scrapeIONnews():
    months=["jan", "feb","mar", "apr", "may","jun","jul","aug", "sep", "oct", "nov", "dec" ]
    
    categories= [["societe","societe"],["politique","politique"],["economie","economie"],["tribune","tribune"],["business","business"],["sport","sport"],["lifestyle","lifestyle"]]

    id=0
    user_agent = random.choice(user_agents) 
    headers = {'User-Agent': user_agent}

    for category in categories:
        current_page_articles=[]
        print(category)

        response = requests.get('https://ionnews.mu/category/'+category[1]+"/", headers=headers)
        content = response.text
        soup=BeautifulSoup(content, "html.parser")
        links=[]
        i=0

        # get sub links of each category page
        for i in range(0,15):
            stri = "https://ionnews.mu/category/"+category[1]+ "/page/"+ str(i+1)+"/"
            links.append(stri)
            # print (links[i])
            # i+=1

        # get article links for each page untill longer than 2 weeks
        outdated_flag = False

        for j in range(0,15):
            if outdated_flag == True:
                break
            response = requests.get(links[j], headers=headers)
            content = response.text
            soup=BeautifulSoup(content, "html.parser")

            # code to get all links to main article
            heading = soup.find_all("h2", {"class": "entry-title"})
            article_links=[]
            for h in heading:
                # print(h.a['href'])
                article_links.append(h.a['href'])

            # get data from each article link in current page to put into json
            
            for i in range(10):

                response = requests.get(article_links[i], headers=headers)
                content = response.text
                soup=BeautifulSoup(content, "html.parser")

                # get date of article, if article is older than 2 weeks, stop scraping
                content = soup.find("span", {"class": "published"})
                # print ( heading)
                # remove excess whitespaces from beg and end of string
                date = content.text.lower()
                split = date.split()
                dd = split[1].strip(',')
                mm = months.index(split[0])+1
                yy = split[2]
                a_date = dd+" "+str(mm)+" "+yy
                # print("date: "+ a_date)
                article_date = datetime.strptime(a_date, '%d %m %Y').date()
                # print(article_date)
                if article_date<two_weeks_ago:
                    outdated_flag = True

                if outdated_flag == True:
                    break

               # get title of article
                heading = soup.find("h1", {"class": "entry-title"})
                # print(heading.text)
                if heading != None:
                    title = heading.text 

                # get image link
                image=""
                heading = soup.find("img", {"class": "alignnone"})
                if heading != None:
                    # print(heading['src'])
                    image = heading['src']

                # get content of article
                heading = soup.find_all("div", {"class": "entry-content"})
                article_content=""
                for data in heading:
                    for p in data.find_all('p'):
                        # print(p.text)
                        article_content+=p.text

                dictionary ={
                "id" : "",
                "source" : "ionnews",
                "title" : "",
                "article_link" : "",
                "image_link" : "",
                "date" : "",
                "summary" : "",
                "article_content" : ""
                }
                dictionary["id"]= id
                dictionary["title"]= title
                dictionary["article_link"]= article_links[i]
                dictionary["image_link"]= image
                dictionary["date"]= a_date
                dictionary["article_content"]= article_content
                # print(dictionary)
                current_page_articles.append(dictionary)
                id+=1

        # Serializing json 
        json_object = json.dumps(current_page_articles, indent = "",  ensure_ascii=False)
        # Writing to sample.json
        with open("main/news-articles/mauritius/ionnews/"+category[0]+".json", "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
            


