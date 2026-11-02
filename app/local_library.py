"""Private transactional preferences, bookmarks, queue and last playback position."""
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import threading
import time
from contextlib import contextmanager

DATABASE = Path(os.environ.get('XDG_CONFIG_HOME', Path.home()/'.config'))/'orbitz-youtube-wrapper'/'library.sqlite3'
LOCK = threading.RLock()
MAX_MEDIA_SECONDS = 2_147_483_647
DEFAULTS = dict(game_volume=25,game_sound=False,always_above=False)


def video(value):
    if not isinstance(value, dict) or not isinstance(value.get('id'),str) or not re.fullmatch('[A-Za-z0-9_-]{11}',value['id']):
        raise ValueError('Invalid video')
    title=value.get('title','')
    if not isinstance(title,str) or len(title)>300:raise ValueError('Invalid title')
    channel=value.get('channel','')
    if not isinstance(channel,str) or len(channel)>200:raise ValueError('Invalid channel')
    return dict(id=value['id'],title=title,**({'channel':channel} if channel else {}))


def preferences(value):
    if not isinstance(value,dict) or set(value)-DEFAULTS.keys():raise ValueError('Invalid preferences')
    for key,item in value.items():
        if key in ('always_above','game_sound'):
            if type(item) is not bool:raise ValueError('Invalid preference')
        elif key=='game_volume':
            if type(item) is not int or not 0<=item<=100:raise ValueError('Invalid volume')
    return value


@contextmanager
def connection():
    with LOCK:
        DATABASE.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(DATABASE,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        os.fchmod(fd,0o600);os.close(fd)
        db=sqlite3.connect(DATABASE,timeout=5)
        try:
            db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS bookmarks (kind TEXT,id TEXT,title TEXT,PRIMARY KEY(kind,id))')
            db.execute('CREATE TABLE IF NOT EXISTS queue (qid INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT,title TEXT)')
            with db:yield db
        finally:db.close()


def setting(db,key,default):
    row=db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
    return json.loads(row[0]) if row else default


def put(db,key,value):db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)',(key,json.dumps(value)))


def state(db):
    stored=setting(db,'preferences',{})
    clean={key:value for key,value in stored.items() if key in DEFAULTS}
    if clean!=stored:put(db,'preferences',clean)
    prefs={**DEFAULTS,**clean}
    result=dict(preferences=prefs,resume=setting(db,'resume',None),recommendation_preferences=setting(db,'recommendation_preferences',{'interests':[],'use_recent':True}))
    for kind in ('favorites','later'):
        result[kind]=[dict(id=i,title=t) for i,t in db.execute('SELECT id,title FROM bookmarks WHERE kind=? ORDER BY rowid DESC',(kind,))]
    result['queue']=[dict(qid=q,id=i,title=t) for q,i,t in db.execute('SELECT qid,id,title FROM queue ORDER BY qid')]
    return result


def action(data):
    op=data.get('op','get')
    with connection() as db:
        if op=='preferences':put(db,'preferences',{**{key:value for key,value in setting(db,'preferences',{}).items() if key in DEFAULTS},**preferences(data.get('values'))})
        elif op in ('save','remove'):
            kind=data.get('kind')
            if kind not in ('favorites','later'):raise ValueError('Invalid list')
            item=video(data.get('video'))
            if op=='save':
                if db.execute('SELECT count(*) FROM bookmarks WHERE kind=?',(kind,)).fetchone()[0]>=1000 and not db.execute('SELECT 1 FROM bookmarks WHERE kind=? AND id=?',(kind,item['id'])).fetchone():raise ValueError('Library full')
                db.execute('INSERT OR REPLACE INTO bookmarks VALUES (?,?,?)',(kind,item['id'],item['title']))
            else:db.execute('DELETE FROM bookmarks WHERE kind=? AND id=?',(kind,item['id']))
        elif op=='queue-add':
            item=video(data.get('video'))
            if db.execute('SELECT count(*) FROM queue').fetchone()[0]>=200:raise ValueError('Queue full')
            db.execute('INSERT INTO queue(id,title) VALUES (?,?)',(item['id'],item['title']))
        elif op in ('queue-remove','queue-up','queue-down'):
            qid=data.get('qid')
            if type(qid) is not int or qid<=0:raise ValueError('Invalid queue item')
            if op=='queue-remove':db.execute('DELETE FROM queue WHERE qid=?',(qid,))
            else:
                rows=list(db.execute('SELECT qid,id,title FROM queue ORDER BY qid'))
                index=next((i for i,row in enumerate(rows) if row[0]==qid),-1)
                other=index+(-1 if op=='queue-up' else 1)
                if index>=0 and 0<=other<len(rows):
                    a,b=rows[index],rows[other]
                    db.execute('UPDATE queue SET id=?,title=? WHERE qid=?',(b[1],b[2],a[0]))
                    db.execute('UPDATE queue SET id=?,title=? WHERE qid=?',(a[1],a[2],b[0]))
        elif op=='queue-next':
            row=db.execute('SELECT qid,id,title FROM queue ORDER BY qid LIMIT 1').fetchone()
            if row:
                db.execute('DELETE FROM queue WHERE qid=?',(row[0],))
                result=state(db);result['next']=dict(id=row[1],title=row[2]);return result
        elif op in ('remember','progress'):
            item=video(data.get('video'));position=data.get('position',0);duration=data.get('duration',0)
            if any(type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=MAX_MEDIA_SECONDS for n in (position,duration)):raise ValueError('Invalid playback position')
            live=data.get('live',False);restart=data.get('restart',False)
            if type(live) is not bool or type(restart) is not bool:raise ValueError('Invalid playback flags')
            start=0 if live or restart or not duration or duration>172800 or position>=duration else position
            put(db,'resume',{**item,'position':start,'duration':duration,'live':live})
            return {'saved':True}
        elif op=='recommendation-settings':
            values=data.get('values')
            if not isinstance(values,dict) or set(values)!={'interests','use_recent'}:raise ValueError('Invalid recommendation preferences')
            interests=values['interests']
            if type(values['use_recent']) is not bool or not isinstance(interests,list) or len(interests)>10:raise ValueError('Invalid recommendation preferences')
            normalized=[]
            for term in interests:
                if not isinstance(term,str) or not 0<len(term.strip())<=80 or any(ord(char)<32 for char in term):raise ValueError('Invalid interest')
                term=' '.join(term.split())
                if term.casefold() not in [item.casefold() for item in normalized]:normalized.append(term)
            put(db,'recommendation_preferences',dict(interests=normalized,use_recent=values['use_recent']))
            put(db,'recommendation_revision',setting(db,'recommendation_revision',0)+1)
        elif op=='clear-searches':
            put(db,'recent_searches',[]);put(db,'recommendation_revision',setting(db,'recommendation_revision',0)+1)
        elif op=='resume-metadata':
            item=video(data.get('video'));previous=setting(db,'resume',None)
            if previous and previous['id']==item['id']:
                put(db,'resume',{**previous,**item})
        elif op=='clear-resume':put(db,'resume',None)
        elif op!='get':raise ValueError('Invalid library action')
        return state(db)


def export_library():
    with connection() as db:
        value=state(db)
        return dict(version=1,favorites=value['favorites'],later=value['later'])


def import_library(value):
    if not isinstance(value,dict) or type(value.get('version')) is not int or value['version']!=1:raise ValueError('Invalid library format')
    validated={}
    for kind in ('favorites','later'):
        rows=value.get(kind,[])
        if not isinstance(rows,list) or len(rows)>1000:raise ValueError('Invalid library size')
        validated[kind]=[video(row) for row in rows]
    with connection() as db:
        for kind,rows in validated.items():
            for item in rows:db.execute('INSERT OR REPLACE INTO bookmarks VALUES (?,?,?)',(kind,item['id'],item['title']))
        if db.execute('SELECT count(*) FROM bookmarks').fetchone()[0]>2000:raise ValueError('Library full')
        return state(db)


def recommendation_profile():
    with connection() as db:
        now=time.time()
        rows=setting(db,'recent_searches',[])
        fresh=[item for item in rows if 0<=now-item['at']<30*86400][:30]
        if fresh!=rows:put(db,'recent_searches',fresh)
        return dict(preferences=setting(db,'recommendation_preferences',{'interests':[],'use_recent':True}),recent=fresh,favorites=[dict(id=row[0],title=row[1]) for row in db.execute("SELECT id,title FROM bookmarks WHERE kind='favorites' ORDER BY rowid DESC LIMIT 3")],revision=setting(db,'recommendation_revision',0))


def record_search(query,mode,revision):
    if mode not in ('videos','shorts','live','podcasts') or not isinstance(query,str) or not 0<len(query.strip())<=300 or any(ord(char)<32 for char in query):raise ValueError('Invalid search history')
    if re.match(r'https?://',query,re.I):return
    with connection() as db:
        prefs=setting(db,'recommendation_preferences',{'interests':[],'use_recent':True})
        if not prefs['use_recent'] or revision!=setting(db,'recommendation_revision',0):return
        now=time.time();query=' '.join(query.split())
        rows=[item for item in setting(db,'recent_searches',[]) if 0<=now-item['at']<30*86400 and not(item['mode']==mode and item['query'].casefold()==query.casefold())]
        put(db,'recent_searches',[dict(query=query,mode=mode,at=now)]+rows[:29])
