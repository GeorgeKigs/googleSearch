import youtube_dl as yt
import concurrent.futures 
import time
import os
import sys
import re
import datetime
import json
from search import SearchUrls
from pathlib import Path
import logging



class Logger(object):
    
    def warning(self,msg):
        print(msg)
        pass
    def error(self,msg):
        if 'Unable to download ' in msg:
            sys.exit(1)
        
    def debug(self,msg):
        if 'has already been downloaded' in msg:
            print('page has been downloaded')
        


class VideoDownloader():
    
    def __init__(self,urls):

        print('init')
        
        try:
            with open('config.json','r') as file:
                self.option=json.load(file)
            self.output_path=self.option['outtmpl']
            
        except FileNotFoundError:
            self.option={}
            self.output_path=f'{Path.home()}\\Downloads\\Youtube\\%(title)s.%(ext)s'

        self.max_workers=10
        self.urls=urls
        self.info=1
        if 'list=' in self.urls:
            self.info=self.get_number(self.urls.split('list=')[1])
            self.output_path=f'{Path.home()}\\Downloads\\Youtube\\%(playlist)s\\%(title)s.%(ext)s'

        self.concurrency()

    def options(self,start,stop):
        
        self.option.update({
            'playliststart':start,
            'outtmpl':f'{self.output_path}',
            'playliststop':stop,
            'logger':Logger()
        })
        # print(self.option)
        return self.option

    
    def get_number(self,playlistId):
        youtubeData=SearchUrls().YOUTUBE_OBJECT.playlistItems().list(
            part="snippet",
            playlistId=playlistId,
            maxResults=1
        ).execute()
        return youtubeData['pageInfo']['totalResults']


    def download(self,url,start,stop):
        options=self.options(start,stop)
        # print(options)
        
        with yt.YoutubeDL(options) as ytdl:
            info=ytdl.extract_info(url=url,download=True)
        with open('crawled.txt','a') as file:
            file.write(f'{url}\n')

    def concurrency(self):
        print('start')
        no_in_playlist=self.info

        if no_in_playlist>1:
            list_of_playlist=[i for i in range(0,no_in_playlist,no_in_playlist//self.max_workers)]
            if no_in_playlist not in list_of_playlist:
                list_of_playlist.append(no_in_playlist)
            start_list=[[list_of_playlist[i-1],j] for i,j in enumerate(list_of_playlist) if i>0]

            print(f' downloading {self.max_workers} concurrently')

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for no in start_list:
                    executor.submit(self.download,self.urls,no[0],no[1])
            
            return True
        
        print('downloading single file')
        print(self.urls)
        self.download(self.urls,1,1)



def main(urlList=[]):
    start=time.time()
    if len(sys.argv)>1 or len(urlList)>0:
        
        words=[word for word in sys.argv if word!=sys.argv[0]]
        words=[word for word in urlList]

    else:
        print(' Enter the urls and keywords you want to download. \n \
            seperated by a space\n\n to continue with your last downloads press enter\\n')
        words=input('Search in youTube: ')
        if words=='':
            waiting=set()
            crawled=set()
            try:
                with open('waiting.txt','r') as file:
                    for link in file.readlines():
                        waiting.add(link.split('\n')[0])
                        words=[link for link in waiting if link not in crawled]
                
            except Exception as e:
                print('error',e)
                pass
        else:
            words=words.split(' ')

        
    for file in words:
        if file.endswith('.txt'):
            with open(file,'r') as target:
                for line in target.readlines():
                    words.append(line.split('\n')[0])
    
    search=SearchUrls()
    
    urls=[url for url in words if url.split(':')[0]=='https']

    keyword=[url for url in words if url not in urls and not url.endswith('.txt')]

    for word in keyword:
        urls+=search.search_keyword(word)


    with open('waiting.txt','w') as file:
        file.writelines(f'{link}\n' for link in urls)

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as target:
    
        target.map(VideoDownloader,urls)
            
    print(f'Download complete after: {time.time()-start}')
    


if __name__ == "__main__":
    main()
## store in a file  
