"""MPRIS session-bus integration; driven by player events, with no polling."""
import json
import time
from local_library import MAX_MEDIA_SECONDS
from gi.repository import Gio, GLib

NAME='org.mpris.MediaPlayer2.orbitz_youtube_wrapper'
PATH='/org/mpris/MediaPlayer2'
ROOT='org.mpris.MediaPlayer2'
PLAYER=ROOT+'.Player'
XML='''<node><interface name="org.mpris.MediaPlayer2">
<method name="Raise"/><method name="Quit"/>
<property name="CanQuit" type="b" access="read"/><property name="CanRaise" type="b" access="read"/>
<property name="HasTrackList" type="b" access="read"/><property name="Identity" type="s" access="read"/>
<property name="DesktopEntry" type="s" access="read"/><property name="SupportedUriSchemes" type="as" access="read"/>
<property name="SupportedMimeTypes" type="as" access="read"/></interface>
<interface name="org.mpris.MediaPlayer2.Player">
<method name="Next"/><method name="Previous"/><method name="Pause"/><method name="PlayPause"/><method name="Stop"/><method name="Play"/>
<method name="Seek"><arg direction="in" type="x"/></method>
<method name="SetPosition"><arg direction="in" type="o"/><arg direction="in" type="x"/></method>
<property name="PlaybackStatus" type="s" access="read"/><property name="LoopStatus" type="s" access="readwrite"/>
<property name="Rate" type="d" access="readwrite"/><property name="Shuffle" type="b" access="readwrite"/>
<property name="Metadata" type="a{sv}" access="read"/><property name="Volume" type="d" access="readwrite"/>
<property name="Position" type="x" access="read"/><property name="MinimumRate" type="d" access="read"/>
<property name="MaximumRate" type="d" access="read"/><property name="CanGoNext" type="b" access="read"/>
<property name="CanGoPrevious" type="b" access="read"/><property name="CanPlay" type="b" access="read"/>
<property name="CanPause" type="b" access="read"/><property name="CanSeek" type="b" access="read"/>
<property name="CanControl" type="b" access="read"/><signal name="Seeked"><arg type="x"/></signal>
</interface></node>'''


class MediaControls:
    def __init__(self,window,view,instance=0):
        self.window,self.view=window,view
        self.state=dict(id='',title='',position=0,duration=0,status='Stopped',volume=1.0,next=False,rate=1.0,live=False,restart=False)
        self.updated=time.monotonic();self.connection=None;self.registrations=[]
        self.private_connection=None
        if instance:
            address=Gio.dbus_address_get_for_bus_sync(Gio.BusType.SESSION,None)
            self.private_connection=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
            name=NAME+'.window'+str(instance)
            self.acquired(self.private_connection,name)
            self.owner=Gio.bus_own_name_on_connection(self.private_connection,name,Gio.BusNameOwnerFlags.NONE,None,None)
        else:
            self.owner=Gio.bus_own_name(Gio.BusType.SESSION,NAME,Gio.BusNameOwnerFlags.NONE,self.acquired,None,None)
        window.connect('destroy',self.destroyed)

    def command(self,name,value=None):
        self.view.run_javascript('window.orbitzMediaCommand && window.orbitzMediaCommand('+json.dumps(name)+','+json.dumps(value)+');',None,None,None)

    def acquired(self,connection,_name):
        self.connection=connection
        for interface in Gio.DBusNodeInfo.new_for_xml(XML).interfaces:
            self.registrations.append(connection.register_object(PATH,interface,self.call,self.get,self.set))

    def call(self,_conn,_sender,_path,interface,method,parameters,invocation):
        args=parameters.unpack()
        if interface==ROOT:
            if method=='Raise':self.window.present()
            elif method=='Quit':self.window.close()
        elif method=='Next':self.command('next',{'keepPaused':self.state['status']!='Playing'})
        elif method=='Stop':
            self.state.update(status='Stopped',position=0,restart=True);self.updated=time.monotonic();self.command('stop')
        elif method=='Previous':pass
        elif method=='Seek':self.command('seek',args[0]/1_000_000)
        elif method=='SetPosition':
            if args[0]=='/io/orbitz/track/'+self.state['id'].encode().hex() and 0<=args[1]/1_000_000<=self.state['duration']:self.command('position',args[1]/1_000_000)
        else:self.command(method.lower())
        invocation.return_value(None)

    def properties(self,interface):
        V=GLib.Variant;s=self.state
        if interface==ROOT:
            return {k:V(t,v) for k,t,v in [('CanQuit','b',True),('CanRaise','b',True),('HasTrackList','b',False),('Identity','s','YouTube API Player - By Orbitz'),('DesktopEntry','s','io.orbitz.YouTubeDesktop'),('SupportedUriSchemes','as',[]),('SupportedMimeTypes','as',[])]}
        metadata={}
        if s['id']:
            metadata={'mpris:trackid':V('o','/io/orbitz/track/'+s['id'].encode().hex()),'xesam:title':V('s',s['title']),'xesam:url':V('s','https://www.youtube.com/watch?v='+s['id']),'mpris:length':V('x',round(s['duration']*1_000_000))}
        position=s['position']+((time.monotonic()-self.updated)*s.get('rate',1.0) if s['status']=='Playing' else 0)
        if s['duration']:position=min(position,s['duration'])
        values=[('PlaybackStatus','s',s['status']),('LoopStatus','s','None'),('Rate','d',s.get('rate',1.0)),('Shuffle','b',False),('Metadata','a{sv}',metadata),('Volume','d',s['volume']),('Position','x',round(position*1_000_000)),('MinimumRate','d',.25),('MaximumRate','d',2.0),('CanGoNext','b',s['next']),('CanGoPrevious','b',False),('CanPlay','b',bool(s['id'])),('CanPause','b',bool(s['id'])),('CanSeek','b',bool(s['id'])),('CanControl','b',True)]
        return {k:V(t,v) for k,t,v in values}

    def get(self,_conn,_sender,_path,interface,name):return self.properties(interface).get(name)

    def set(self,_conn,_sender,_path,_interface,name,value):
        if name in ('LoopStatus','Shuffle'):return value.unpack()=={'LoopStatus':'None','Shuffle':False}[name]
        if name=='Rate':
            rate=value.unpack()
            if not .25<=rate<=2:return False
            self.command('rate',rate);return True
        if name!='Volume':return False
        self.command('volume',max(0.0,min(1.0,value.unpack())));return True

    def update(self,data):
        import math,re
        if not isinstance(data.get('id'),str) or (data['id'] and not re.fullmatch('[A-Za-z0-9_-]{11}',data['id'])):raise ValueError('Invalid track')
        if data.get('status') not in ('Playing','Paused','Stopped') or type(data.get('next')) is not bool:raise ValueError('Invalid playback state')
        if not isinstance(data.get('title'),str) or len(data['title'])>300:raise ValueError('Invalid title')
        for key in ('position','duration','volume'):
            value=data.get(key)
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=(1 if key=='volume' else MAX_MEDIA_SECONDS):raise ValueError('Invalid media value')
        rate=data.get('rate',1.0)
        if type(rate) not in (int,float) or not math.isfinite(rate) or not .25<=rate<=4:raise ValueError('Invalid playback rate')
        for key in ('live','restart'):
            if type(data.get(key,False)) is not bool:raise ValueError('Invalid playback flags')
        self.state={key:data.get(key,1.0) if key=='rate' else data.get(key,False) if key in ('live','restart') else data[key] for key in self.state};self.updated=time.monotonic()
        if self.connection:
            changed=self.properties(PLAYER);changed.pop('Position')
            self.connection.emit_signal(None,PATH,'org.freedesktop.DBus.Properties','PropertiesChanged',GLib.Variant('(sa{sv}as)',(PLAYER,changed,[])))
            if data.get('seeked') is True:self.connection.emit_signal(None,PATH,PLAYER,'Seeked',GLib.Variant('(x)',(round(data['position']*1_000_000),)))

    def destroyed(self,*_):
        Gio.bus_unown_name(self.owner)
        if self.connection:
            for registration in self.registrations:self.connection.unregister_object(registration)
        if self.private_connection:self.private_connection.close_sync(None)
