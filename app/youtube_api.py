#!/usr/bin/python3
"""YouTube Data API access, local key and suggestion cache."""
import html
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

CONFIG_ROOT = Path(os.environ.get('XDG_CONFIG_HOME', Path.home()/'.config'))
CONFIG = CONFIG_ROOT/'orbitz-youtube-wrapper'/'youtube.json'
LEGACY_CONFIG = CONFIG_ROOT/'orbitz-youtube-desktop'/'youtube.json'
RESULT_LIMIT = 20


class MissingAPIKey(ValueError):
    pass


def _valid_key(key):
    return isinstance(key, str) and re.fullmatch(r'[A-Za-z0-9_-]{20,200}', key) is not None


def read_key():
    for path in (CONFIG,LEGACY_CONFIG):
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd) as stream:
                value=json.loads(stream.read(4096))
            if not isinstance(value,dict):
                continue
            key=value.get('key','')
            if _valid_key(key):
                return key
        except (OSError,ValueError,TypeError):
            continue
    return ''


def save_key(key):
    if not _valid_key(key):
        raise ValueError('Formato da chave inválido.')
    CONFIG.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(CONFIG,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as stream:
        os.fchmod(stream.fileno(),0o600)
        json.dump({'key':key},stream)


def search(query=None, mode='videos',locale=None):
    if not isinstance(mode,str) or mode not in ('videos','shorts','live','podcasts'):
        raise ValueError('Filtro de busca inválido.')
    if query is not None and (not isinstance(query,str) or not 0<len(query.strip())<=300 or any(ord(char)<32 for char in query)):
        raise ValueError('Busca inválida.')
    key=read_key()
    if not key: raise MissingAPIKey('Configure uma chave da API ou cole um link do YouTube.')
    options=dict(part='snippet',type='video',maxResults=50,videoEmbeddable='true',key=key)
    if query is None:
        options.update(regionCode='BR',relevanceLanguage='pt',order='viewCount',
            publishedAfter=(datetime.now(timezone.utc)-timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'))
        if mode=='live':options.pop('publishedAfter',None)
        if mode=='podcasts':
            options['q']='podcast';options.pop('publishedAfter',None)
    else:
        options['q']=' | '.join('podcast '+term.strip() for term in query.split('|') if term.strip()) if mode=='podcasts' else query
        # Podcasts are not an official search filter. Prefixing the user's
        # query is an approximate relevance search, not a content guarantee.
        # The API's `short` bucket means videos under four minutes. It is the
        # closest official search filter; YouTube does not expose a Shorts-only
        # search parameter, so some returned videos may not be classified as Shorts.
    if mode=='shorts':options['videoDuration']='short'
    elif mode=='live':options['eventType']='live'
    elif mode=='podcasts':options['videoDuration']='long'
    if locale is not None:
        options.update(regionCode='US' if locale=='en-US' else 'BR',relevanceLanguage='en' if locale=='en-US' else 'pt')
    params=urllib.parse.urlencode(options)
    endpoint='search'
    try:
        with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/'+endpoint+'?'+params,timeout=10) as response:
            raw=response.read(262145)
        if len(raw)>262144: raise ValueError('Resposta muito grande.')
        data=json.loads(raw)
    except urllib.error.HTTPError as error:
        if error.code==403: raise ValueError('Consulta recusada: confira a chave, a ativação da API e a quota diária.') from None
        raise ValueError('O YouTube não conseguiu concluir a busca.') from None
    except (OSError,ValueError):
        raise ValueError('Não foi possível consultar o YouTube. Verifique a conexão.') from None
    items=[]
    seen=set()
    for item in data.get('items',[])[:50]:
        identity=item.get('id',{}).get('videoId','')
        if not re.fullmatch(r'[\w-]{11}',identity):continue
        if identity in seen:continue
        snippet=item.get('snippet',{})
        broadcast=snippet.get('liveBroadcastContent','none')
        if mode=='live':
            if broadcast!='live':continue
        elif broadcast in ('live','upcoming'):continue
        if mode=='podcasts':
            evidence=' '.join(str(snippet.get(name,'')) for name in ('title','channelTitle','description')).casefold()
            if not re.search(r'podcasts?|videocasts?',evidence):continue
            if re.search(r'\b(shorts?|cortes?|clips?)\b',str(snippet.get('title','')),re.I):continue
        seen.add(identity)
        items.append(dict(id=identity,title=html.unescape(snippet.get('title',''))[:300],channel=html.unescape(snippet.get('channelTitle',''))[:200],thumbnail='https://i.ytimg.com/vi/'+identity+'/default.jpg'))
        if len(items)>=RESULT_LIMIT:break
    return items


def recommendations():
    cache_root=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))
    cache_path=cache_root/'orbitz-youtube-wrapper'/'youtube-suggestions.json'
    legacy_cache=cache_root/'orbitz-youtube-desktop'/'youtube-suggestions.json'
    for source in (cache_path,legacy_cache):
        try:
            cached=json.loads(source.read_text())
            if 0<=time.time()-cached['time']<21600 and isinstance(cached['items'],list) and cached['items'] and cached.get('result_limit')==RESULT_LIMIT:
                return cached['items'][:RESULT_LIMIT]
        except (OSError,ValueError,KeyError,TypeError):
            continue
    items=search()
    try:
        cache_path.parent.mkdir(parents=True,exist_ok=True)
        temporary=cache_path.with_name('youtube-suggestions-'+secrets.token_hex(8)+'.tmp')
        temporary.write_text(json.dumps({'time':time.time(),'items':items,'result_limit':RESULT_LIMIT}))
        os.replace(temporary,cache_path)
    except OSError:
        pass
    return items


def video_details(identity):
    """Public metadata through the official videos.list endpoint."""
    if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}',identity):
        raise ValueError('Invalid video')
    key=read_key()
    if not key:raise MissingAPIKey('Configure uma chave da API.')
    params=urllib.parse.urlencode(dict(part='snippet',id=identity,key=key,fields='items(id,snippet(title,channelTitle))'))
    try:
        with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/videos?'+params,timeout=10) as response:
            raw=response.read(16385)
        if len(raw)>16384:raise ValueError('Resposta muito grande.')
        data=json.loads(raw)
        for item in data.get('items',[]):
            if item.get('id')==identity:
                snippet=item.get('snippet',{})
                return dict(id=identity,title=html.unescape(snippet.get('title',''))[:300],channel=html.unescape(snippet.get('channelTitle',''))[:200])
        return {'id':identity,'channel':''}
    except (OSError,ValueError,TypeError):
        raise ValueError('Não foi possível consultar os dados do vídeo.') from None


# Small, bounded session cache; no background refresh while watching a video.
import threading
_LIKES_LOCK = threading.Lock()
_LIKES_CACHE = {}


def video_likes(identities):
    if not isinstance(identities,list) or not 1<=len(identities)<=50 or any(not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}',identity) for identity in identities):
        raise ValueError('Invalid videos')
    identities=list(dict.fromkeys(identities))
    with _LIKES_LOCK:
        now=time.monotonic()
        missing=[identity for identity in identities if identity not in _LIKES_CACHE or now-_LIKES_CACHE[identity][0]>=300]
        if missing:
            key=read_key()
            if not key:raise MissingAPIKey('Configure uma chave da API.')
            params=urllib.parse.urlencode(dict(part='statistics',id=','.join(missing),key=key,fields='items(id,statistics(likeCount))'))
            try:
                with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/videos?'+params,timeout=10) as response:
                    raw=response.read(32769)
                if len(raw)>32768:raise ValueError('Resposta muito grande.')
                data=json.loads(raw)
                counts=dict.fromkeys(missing)
                for item in data.get('items',[]):
                    count=item.get('statistics',{}).get('likeCount')
                    if item.get('id') in counts and isinstance(count,str) and re.fullmatch(r'[0-9]{1,20}',count):
                        counts[item['id']]=count
                for identity,count in counts.items():_LIKES_CACHE[identity]=(now,count)
                while len(_LIKES_CACHE)>200:_LIKES_CACHE.pop(next(iter(_LIKES_CACHE)))
            except (OSError,ValueError,TypeError):
                raise ValueError('Não foi possível consultar as curtidas.') from None
        return {identity:_LIKES_CACHE[identity][1] for identity in identities}
