import yt_dlp
import re

ytdlopts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'logtostderr': False,
    'no_warnings': False, 
    'source_address': '0.0.0.0'
    # 'default_search': 'auto',
    # 'quiet': True, 
    # 'nocheckcertificate': True,
    # 'ignoreerrors': False,
    # 'restrictfilenames': True,
}



class Song:
    def __init__(self, keyword):
        self.extract(keyword)

    def get_url(self,content):
        regex = re.compile(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if re.search(regex, content):
            result = regex.search(content)
            url = result.group(0)
            return url
        else:
            return None
        #Check if user input is a link


    def extract(self,url):
        global songInfo

        vidURL = self.get_url(url)
        
        with yt_dlp.YoutubeDL(ytdlopts) as ydl:
            if vidURL is None:    
                r = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
            else: 
                r = ydl.extract_info(url, download=False)
        

        self.videocode = r.get('id')
        if vidURL is not None :
            self.videolink = url
        else:
            self.videolink = 'https://www.youtube.com/watch?v='+self.videocode

        self.audio = r.get('url')
        self.uploader = r.get('uploader')
        self.title = r.get('title')
        self.thumbnail = r.get('thumbnail')

        seconds = r.get('duration') % (24 * 3600)
        # duration_MS = seconds*10
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        if hour > 0:
            self.duration = "%d:%02d:%02d" % (hour, minutes, seconds)
        else:
            self.duration = "%02d:%02d" % ( minutes, seconds)

        self.date = r.get('upload_date')
        self.views = r.get('view_count')
        self.likes = r.get('like_count')
        self.dislikes = r.get('dislike_count')