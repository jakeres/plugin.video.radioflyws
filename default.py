import urllib,urllib2,re,xbmc,xbmcplugin,xbmcaddon,xbmcgui,os,sys,commands,HTMLParser,jsunpack,time,json

website = 'http://www.radiofly.ws/';

__version__ = "1.0.6"
__plugin__ = "radiofly.ws" + __version__
__url__ = "www.xbmc.com"
settings = xbmcaddon.Addon( id = 'plugin.video.radioflyws' )

search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )
movies_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies.png' )
movies_hd_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies-hd.png' )
tv_series_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'tv.png' )
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )

try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
cache = StorageServer.StorageServer("990ro", 24)


def ROOT():
    addDir('Filme online','http://www.radiofly.ws/filme-online-gratis.php',1,movies_thumb)
    addDir('Filme online 2014','http://www.radiofly.ws/filme-online-gratis-2014.php',1,movies_thumb)
    addDir('Filme online 2013','http://www.radiofly.ws/filme-online-gratis-2013.php',1,movies_thumb)
    addDir('Desene dublate','http://www.radiofly.ws/desene-online-dublate.php',1,movies_thumb)
    
    xbmc.executebuiltin("Container.SetViewMode(500)")

def FILME(url):
    link=get_url(url)
    match = re.compile('<a href="(.+?)" .+?<img src="(filmepoze|desene)(.+?)" .+? title="(.+?)"', re.IGNORECASE).findall(link)
    for the_link, thumb1, thumb2, name in match:
        the_link = url+"--"+the_link
        image = 'http://www.radiofly.ws/'+urllib.quote(thumb1+thumb2)
        #name = HTMLParser.HTMLParser().unescape(name)
        sxaddLink(name,the_link,image,name,mode=10)
    xbmc.executebuiltin("Container.SetViewMode(500)")


def SXVIDEO_GENERIC_PLAY(sxurls, seltitle, linksource):
    listitem = xbmcgui.ListItem(seltitle)
    listitem.setInfo('video', {'Title': seltitle})
    #print sxurls

    source_link = None
    for u in sxurls:
      if u[0] == linksource:
        source_link = u[1]
        break;
        
    if linksource == "trailer":
      SXVIDEO_PLAY_THIS(source_link, listitem, None)
      
    elif linksource == "movie":
      dialog = xbmcgui.Dialog()
      dialog.notification("Info", "Resolving stream. Please wait...", xbmcgui.NOTIFICATION_WARNING, 8000)
      media_url = get_generic_link(source_link)
      if media_url:
        dialog.notification("Info", "Movie ok. ", xbmcgui.NOTIFICATION_WARNING, 500)
        SXVIDEO_PLAY_THIS(media_url, listitem, None)
      else:
        dialog.notification("Error", "Cant play movie", xbmcgui.NOTIFICATION_WARNING, 500)
      
    return
      
def SXVIDEO_PLAY_THIS(selurl, listitem, source):
    player = xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ) 
    player.play(selurl, listitem)
    
    #print source
    
    #while not player.isPlaying():
    #  time.sleep(1) 

    try:
          print "-"
          player.setSubtitles(source['subtitle'])
    except:
        pass

    #while player.isPlaying:
    #  xbmc.sleep(100);
      
    return player.isPlaying()


def SXSHOWINFO(text):
    #progress = xbmcgui.DialogProgress()
    #progress.create("kml browser", "downloading playlist...", "please wait.")
    print ""
    
def SXVIDEO_FILM_PLAY(url):
    SXSHOWINFO("Getting movie link...")
    dialog = xbmcgui.Dialog()
    dialog.notification("Info", "Getting movie link...", xbmcgui.NOTIFICATION_WARNING, 3000)
    
    getinfourl="http://finperstat.pe.hu/LIVE/radioflyws.php?fromurl="+url
    print "URL"
    print url
    
    SXSHOWINFO("Found video links...")
    jsonlink=get_url(getinfourl)
    #print jsonlink
    jsondata = json.loads(jsonlink)
    print jsondata
    
    dialogList = []
    if ('trailer' in jsondata):
      link_youtube = jsondata['trailer']
      link_video_trailer = youtube_resolve(link_youtube)
      del jsondata['trailer']
      dialogList = [' - Ruleaza trailer']
    else:
      link_video_trailer = None
      dialogList = [' - No trailer']
    
    #no resource to resolve this urls
    if ('ok.ru' in jsondata):
      del jsondata['ok.ru']
    #if ('my.mail.ru' in jsondata):
    #  del jsondata['my.mail.ru']
      
    ret = -1
    movie_title = "";
    
    dialogList.extend(jsondata)
      
    #addLink('Trailer film', link_video_trailer+'?.mp4', thumbnail, movie_title+' (trailer)')
    SXSHOWINFO("Playing trailer...")
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Select', dialogList)
    
    if (ret == 0):
      SXVIDEO_GENERIC_PLAY([("trailer", link_video_trailer)], movie_title, "trailer")
      
    #print sxurls
    if (ret > 0):
      #print ret
      #print dialogList[ret]
      SXVIDEO_GENERIC_PLAY([("movie", jsondata[dialogList[ret]])], movie_title, "movie")
    

def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False

def fastupload_resolve(legatura):
    link = get_url(legatura)
    match = re.compile("(http://(fastupload.rol|superweb|superweb.rol).ro/video/.+?.html)", re.IGNORECASE).findall(link)
    try:
        fu_link = match[0][0]
    except:
        return {'url': '', 'referer': ''}
    
    #print fu_link
    fu_source = get_url(fu_link)
    if fu_source == False:
        return {'url': '', 'referer': ''}
    # fastupload flv url
    match=re.compile("&flv=(.+?\.(mp4|flv))&getvar=", re.IGNORECASE).findall(fu_source)
    #print "FUL"
    
    try:
      url_flv = match[0][0]
      url_ext = match[0][1]
    except IndexError:
      match=re.compile("'(http://.+?\.(mp4|flv))'", re.IGNORECASE).findall(fu_source)
      #print match
      url_flv = match[0][0]
      url_ext = match[0][1]
    
    #req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    
    if (url_ext == "mp4"):
      url_flv = url_flv+'|User-Agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3|referer='+fu_link
    elif (url_ext == "flv"):
      url_flv = url_flv+'|User-Agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3|referer='+fu_link
    
 
    #prepare
    fu = {}
    fu['url']       = url_flv
    fu['url_ext']   = url_ext
    fu['referer']   = fu_link 
    fu['subtitle']  = None
    
    #print fu
    
    match=re.compile("'captions.file': '(.+?)',", re.IGNORECASE).findall(fu_source)
    #print "FULSRT"
    #print match
    if match:
        url_srt = match[0]
        fu['subtitle']  = url_srt 
    
    return fu


def get_generic_link(legatura):
    #attempt to resolve
    print legatura
    
    match = re.compile("(fastupload|superweb|superweb.rol)", re.IGNORECASE).findall(legatura)
    if match:
      m = fastupload_resolve(legatura)
      media_url = m['url']
    elif re.compile("(mail.ru)", re.IGNORECASE).findall(legatura):
      media_url = mailru_resolve(legatura)
    else:  
      import urlresolver
      media_url = urlresolver.resolve(legatura) 

    print media_url
    
    return media_url
    
def get_search(keyword):
    url = 'http://www.990.ro/functions/search3/live_search_using_jquery_ajax/search.php'
    params = {'kw': keyword}
    req = urllib2.Request(url, urllib.urlencode(params))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def youtube_resolve(url):
    print "YOUTUBE: " + url
    import urlresolver
    
    media_url = urlresolver.resolve(url) 
    print media_url
    
    return media_url

def mailru_resolve(url):
    try:
        usr = re.compile('/mail/(.+?)/').findall(url)[0]
        vid = re.compile('(\d*)[.]html').findall(url)[0]
        urljson = 'http://videoapi.my.mail.ru/videos/mail/%s/_myvideo/%s.json?ver=0.2.60' % (usr, vid)

        items = []
        quality = "???"
        req = urllib2.Request(urljson)
        resp = urllib2.urlopen(req)
        data = resp.read()
        cookie = resp.headers.get('Set-Cookie')
        #print data

        h = "|Cookie=%s" % urllib.quote(cookie)
        u = json.loads(data)['videos']
        
        url = []
        try: url += [[{'quality': '1080p', 'url': i['url'] + h} for i in u if i['key'] == '1080p'][0]]
        except: pass
        try: url += [[{'quality': 'HD', 'url': i['url'] + h} for i in u if i['key'] == '720p'][0]]
        except: pass
        try: url += [[{'quality': 'SD', 'url': i['url'] + h} for i in u if not (i['key'] == '1080p' or i ['key'] == '720p')][0]]
        except: pass

        #print url
        
        if url == []: return
        return url[0]['url']

    except:
        return

# returns the steam url
def mailru_resolve2(url):
    m1 = re.search('http://.+?mail\.ru.+?<param.+?value=\"movieSrc=(?P<url>[^\"]+)', url, re.IGNORECASE | re.DOTALL)
    m2 = re.search('http://video\.mail\.ru\/(?P<url>.+?)\.html', url, re.IGNORECASE | re.DOTALL)
    
    m = m1 or m2
    print m
    if m:
        
        return items
    
def sxaddLink(name,url,iconimage,movie_name,mode=4):
        ok=True
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": movie_name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

def addLink(name,url,iconimage,movie_name):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": movie_name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addNext(name,page,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
        
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        ROOT()

elif mode==1:
        FILME(url)
              
elif mode==2:
        DESENE_DUBLATE(url)
 
elif mode==3:
        CAUTA(url)

elif mode==4:
        VIDEO(url,name)

elif mode==10:
        SXVIDEO_FILM_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
