"""Local-interest recommendations with bounded per-category caches and single flight."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import re
import threading
import time
import youtube_api
import local_library

MODES=('videos','shorts','live','podcasts')
LOCKS={mode:threading.Lock() for mode in MODES}


def plan(mode,locale='pt-BR'):
    if mode not in MODES:raise ValueError('Invalid recommendation filter')
    profile=local_library.recommendation_profile()
    prefs=profile['preferences'];recent=profile['recent'] if prefs['use_recent'] else []
    same=[item['query'] for item in recent if item['mode']==mode]
    other=[item['query'] for item in recent if item['mode']!=mode]
    candidates=[]
    # Combine an explicit interest with category-specific and global recent intent.
    interests=prefs['interests']
    if interests:
        offset=(int(time.time()//21600)+MODES.index(mode))%len(interests)
        interests=interests[offset:]+interests[:offset]
        candidates.append(interests[0])
    candidates+=same[:2]
    if len(candidates)<3:candidates+=other[:3-len(candidates)]
    if len(candidates)<3:candidates+=interests[1:1+3-len(candidates)]
    if not candidates:
        for favorite in profile['favorites']:
            topic=re.split(r'\|| — | - ',favorite['title'],1)[0]
            topic=re.sub(r'\[[^]]*\]|\([^)]*\)',' ',topic).strip()[:70]
            if topic and topic!=favorite['id']:candidates.append(topic)
    terms=[]
    for value in candidates:
        value=' '.join(re.sub(r'[\x00-\x1f\x7f]',' ',value).replace('|',' ').replace('"',' ').split())[:85]
        if value and value.casefold() not in [term.casefold() for term in terms]:terms.append(value)
        if len(terms)==3:break
    # OR avoids requiring unrelated interests to occur together in one video.
    query=' | '.join(terms) or None
    basis='personalized' if terms else 'popular'
    identity=hashlib.sha256(json.dumps([3,mode,locale,query,youtube_api.RESULT_LIMIT]).encode()).hexdigest()
    return dict(mode=mode,locale=locale,query=query,terms=terms,basis=basis,key=identity)


def recommend(mode='videos',locale='pt-BR'):
    if not isinstance(mode,str) or mode not in MODES:raise ValueError('Invalid recommendation filter')
    with LOCKS[mode]:
        selected=plan(mode,locale)
        root=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'orbitz-youtube-wrapper'
        path=root/('recommendations-'+mode+'.json')
        ttl=300 if mode=='live' else 21600
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd) as stream:cached=json.loads(stream.read(1048577))
            if cached.get('key')==selected['key'] and isinstance(cached['items'],list) and 0<=time.time()-cached['time']<(ttl if cached['items'] else min(ttl,300)):
                return dict(items=cached['items'][:youtube_api.RESULT_LIMIT],basis='popular' if cached.get('fallback') else selected['basis'],terms=[] if cached.get('fallback') else selected['terms'],mode=mode)
        except (OSError,ValueError,TypeError,KeyError,AttributeError):pass
        items=youtube_api.search(selected['query'],mode,locale=locale)
        basis=selected['basis'];terms=selected['terms']
        if not items and selected['query']:
            items=youtube_api.search(None,mode,locale=locale)
            basis='popular';terms=[]
        try:
            root.mkdir(parents=True,exist_ok=True,mode=0o700)
            temporary=root/('.recommendations-'+secrets.token_hex(8)+'.tmp')
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:
                with os.fdopen(fd,'w') as stream:json.dump(dict(key=selected['key'],time=time.time(),items=items,fallback=bool(selected['query'] and basis=='popular')),stream)
                os.replace(temporary,path)
            finally:
                try:temporary.unlink()
                except FileNotFoundError:pass
        except OSError:pass
        return dict(items=items,basis=basis,terms=terms,mode=mode)
