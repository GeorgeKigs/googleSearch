import concurrent.futures
from apiclient import discovery

class SearchUrls():

    def __init__(self):
        
        self.USERNAME=''
        self.PASSWORD='AIzaSyA1qSTh9OGLTrZOAFhjtmHCUiCZBm0BXiA'
        self.YOUTUBE_SERVICE_API='youtube'
        self.YOUTUBE_API_VERSION='v3'
        self.YOUTUBE_OBJECT=discovery.build(
            self.YOUTUBE_SERVICE_API,
            self.YOUTUBE_API_VERSION,
            developerKey=self.PASSWORD
            )
        self.max_results=5


    def search_keyword(self,query):

        searchKeyWord=self.YOUTUBE_OBJECT.search().list(
            q=query,
            part='id,snippet',
            regionCode='US',
            type='playlist',
            relevanceLanguage='en',
            maxResults=self.max_results,
            order='viewCount'
            ).execute()

        self.results=searchKeyWord.get('items',{})
        
        videos=[]

        for results in self.results:
            
            kind=results['id']['kind']

            if kind == 'youtube#video':
                videos.append(f'https://www.youtube.com/watch?v={results["id"]["videoId"]}')

            if kind == "youtube#playlist":
                videos += self.playlist(results["id"]["playlistId"])
            
        return videos

    def playlist(self, playlistId):

        videoId=[]

        self.res = self.YOUTUBE_OBJECT.playlistItems().list(
            part="snippet",
            playlistId=playlistId,
            maxResults=50
        ).execute()

        nextPage=self.res.get('nextPageToken')
        for content in self.res['items']:
            videoId.append(f'https://www.youtube.com/watch?v={content["snippet"]["resourceId"]["videoId"]}')
    
        while 'nextPageToken' in self.res:
            playList=self.YOUTUBE_OBJECT.playlistItems().list(
                part='snippet',
                playlistId=playlistId,
                maxResults=50,
                pageToken=nextPage
            ).execute()

            for content in playList['items']:
                videoId.append(f'https://www.youtube.com/watch?v={content["snippet"]["resourceId"]["videoId"]}')

            if 'nextPageToken' not in playList:
                self.res.pop('nextPageToken',None)
            else:
                nextPage=playList['nextPageToken']

        return videoId
            
            

if __name__ == "__main__":
    
    search=SearchUrls()
        
    results=search.search_keyword('python basics')        
    print('videos: ', results[0])
    print('playlist: ', results[1])
