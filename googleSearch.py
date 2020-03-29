import re
import json
import sys
import requests
import subprocess
import threading
import shutil
from googleapiclient.discovery import build
import concurrent.futures

class GoogleSearch():
    def __init__(self):
        self.PASSWORD=''
        self.CSE_ID=''
        self.query_service=build('customsearch','v1',developerKey=self.PASSWORD)
    
    def search(self,query,images=False,limit=0):
        items=[]
        images='image' if images else None
        limit=int(limit) if limit>0 else 50
        for i in range(0,limit,10):
            self.query_result=self.query_service.cse().list(
                q=query,
                cx=self.CSE_ID,
                searchType=images,
                num=10,
                start=i,
                safe= 'off'
                ).execute()
            
            items+=self.query_result['items']
            try:
                if  self.query_result['queries']['nextPage'][0]:
                    pass
            except:
                break

        return items
        


def runSherlock(userName):
    context={}
    context['socialMedia']=[]
    hello=subprocess.Popen(['py','sherlock.py',f'{userName}'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8')
    results=[i.split(': ')[-1] for i in hello.communicate()[0].split('\n') if i.split(': ')[-1].startswith('http')] 
    for i in results:
        context['socialMedia'].append({
                i.split('/')[2]:i
            })
    with open(f'file_.json','a') as file:
        json.dump(context,file,indent=4)
    return results


def searchImages(query):
    images_links=[]
    search=GoogleSearch()
    query_images=search.search(query,images=True,limit=5)
    images=[]
    for i in query_images:
        images.append({
            i['title']:{
                'link':i['link']
            }
        })
        images_links.append(i['link'])
    return images_links,images

def writeFiles(files):
    file_download=requests.get(files,stream=True,)
    with open(f'{files.split("/")[-1]}','wb') as file:
        file.write(file)


def validate_nos(choiceInput):
    if choiceInput=='':
        return True
    elif choiceInput=='n':
        return False
    numbers=[]
    for i in choiceInput.split(','):
        if '-' in i:
            start=int(i.split('-')[0])-1
            stop=int(i.split('-')[1])
            for i in range(start,stop):
                numbers.append(i)
        else:
            numbers.append(int(i))
    return numbers


def download(videos_links=[],images_links=[],files_links=[]):
    cont=input(' do you wish to download: ')
    if cont=='y' or cont=='Y':

        print(' Select what you want to download, seperated by a comma. Eg. 1,3,8\n\
        Or a range of numbers. Eg 1-5,8-12: \
        to download all the content in a given category. Press Enter: \
            if none press n: ')

        for i,j in enumerate(videos_links):
            print(i+1,' : ',j)
        for i in validate_nos(input(' Videos: ')):
            if i ==True:
                videos_input=videos_links
                break
            if i==False:
                videos_input=[]
            else:
                videos_input=[videos_links[i]]
    

        for i,j in enumerate(images_links):
            print(i+1,' : ',j)
        for i in validate_nos(input('Images: ')):
            if i ==True:
                images_input=images_links
                break
            if i==False:
                images_input=[]
            else:
                images_input=[images_links[i] ]

        for i,j in enumerate(files_links):
            print(i+1,' : ',j)
        for i in validate_nos(input('Files: ')):
            if i ==True:
                files_input=files_links
                break
            if i==False:
                files_input=[]
            else:
                files_input=[files_links[i] ]


        from youtubeApp import main as ytMain

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as submit:
            submit.submit(ytMain,videos_input)
            submit.map(writeFiles,images_input+files_input)
        
    elif cont=='n' or cont=='N':
        pass

def main(query=''):
    search=GoogleSearch()
    
    context={}
    

    context['articles']=[]
    context['videos']=[]
    videos_links=[]
    files_links=[]
    
    context['images']=[i for i in searchImages(query)[1]]
    context['files']=[]
    socialMediaLinks=set()
    context['social Media Acc']=[]
    with concurrent.futures.ThreadPoolExecutor() as execute:
        image=execute.submit(searchImages,query).result()
        context['images']=[i for i in image[1]]
        images_links=[i for i in image[0]]
        query=execute.submit(search.search,query).result()

    
    with open('filex.json','w') as file:
        json.dump(query,file,indent=4)

    for i in query:
        #videos
        try:
            if "video" in i['pagemap']['metatags'][0]['og:type']:
                videos_links.append(i['link'])
                context['videos'].append({
                    i['title']:{
                        'link':i['link'],
                        'site':i['displayLink']
                        }
                    })
            
        except:
            pass

        #articles
        try:
            if i['pagemap']['metatags'][0]["og:type"]=='article' or i['pagemap']['metatags'][0]["og:type"]=='website':
                
                
                context['articles'].append({
                    f"{i['pagemap']['metatags'][0]['og:title']}":{
                        'description':f"{i['pagemap']['metatags'][0]['og:description']}",
                        'url':f"{i['link']}"
                    }
                })
        except:
            pass
        
        #files
        try:
            if 'fileFormat' in i:
                files_links.append(i['link'])
                context['files'].append({
                    i['title']:{
                        'link':i['link'],
                        'author':i['pagemap']['metatags'][0]['author']}
                    })
        except:
            pass

        #social Media
        try:
            if i["displayLink"]== "www.facebook.com":
                userName=i['link'].split('/')[-2]
                    
        except:
            pass
        
        try:
            if i["displayLink"]== "www.instagram.com":
                userName=i['link']('/')[-1]
                
        except:
            pass
        try:
            if i["displayLink"]== "twitter.com":
                userName=(i['link'].split('/')[-1]).split('?')[0]
  
        except:
            pass
    with open('file_.json','w') as file:
        json.dump(context,file,indent=4)
    print(userName)
    thread1=threading.Thread(target=download,args=(videos_links,images_links,files_links)) 
    thread2=threading.Thread(target=runSherlock,args=[userName])
    thread1.start()
    thread2.start()
    thread2.join()
    thread1.join()
        

if __name__ == "__main__":
    try:
        main(input('enter your Search Query: '))
    except Exception as e:
        print('Connection not established')
        print(e)


        