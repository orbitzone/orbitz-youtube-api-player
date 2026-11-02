"""Manual GTK/WebKit geometry smoke: python3 tests/gtk_video_geometry.py [width height] [--runner].
Uses a synthetic iframe; no network, API key or user configuration is accessed.
"""
import ast,json,sys
from pathlib import Path
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,Gdk,GLib,WebKit2
root=Path(__file__).resolve().parents[1]
source=(root/'app/youtube-wrapper.py').read_text();tree=ast.parse(source)
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
activate=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='create_window')
funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('controls_request','player_window_rect')]
funcs += [n for n in activate.body if isinstance(n,ast.FunctionDef) and n.name in ('set_window_state','end_controls_transition')]
runner_mode='--runner' in sys.argv;auto_mode='--auto' in sys.argv;size_args=[arg for arg in sys.argv[1:] if arg not in ('--runner','--auto')]
window=Gtk.Window(title='Teste da área central — temporário');window.set_default_size(*(tuple(map(int,size_args)) if len(size_args)==2 else (524,340)))
results={};failed=[]
ns=dict(Gdk=Gdk,math=__import__('math'),window=window,GLib=GLib,chrome={'hidden':False,'sequence':-1,'geometry':None,'transition':False},resize_state={'target':340,'programmatic':False,'source':0,'page':'player'},window_size_locked=lambda:False,request_page_size=lambda state:None,dispatch_to_gtk=lambda fn,value:fn(value))
exec(compile(ast.Module(body=funcs,type_ignores=[]),'native_geometry','exec'),ns)
manager=WebKit2.UserContentManager();manager.register_script_message_handler('geometry')
view=WebKit2.WebView(user_content_manager=manager);window.add(view)
def receive(_manager,result):
 try:
  data=json.loads(result.get_js_value().to_string())
  if 'action' in data:
   if data['action']=='window-state':ns['set_window_state'](data['body'])
  else:
   rect=data['rect'];ox,oy=view.get_window().get_root_coords(0,0)
   rect['x']=ox+rect.pop('left');rect['y']=oy+rect.pop('top')
   results[data['stage']]=rect
   print(data['stage'],data['rect'],'native_client',window.get_size(),'root',window.get_window().get_root_coords(0,0),'frame',window.get_window().get_frame_extents(),'position',window.get_position(),flush=True)
   if data['stage']=='shown':Gtk.main_quit()
 except Exception as error:
  failed.append(str(error));Gtk.main_quit()
manager.connect('script-message-received::geometry',receive)
page=(root/'app/index.html').read_text();prefix=page.split('<script>',1)[0]
start=page.index('// App controls and settings menu.');end=page.index('function renderResults',start)
script='''const $=id=>document.getElementById(id);let selected='abcdefghijk',uiLocale='pt-BR';function uiTr(key){return key}function uiText(){}function uiErrorText(){}function loadRecommendations(){}function setTab(){}function searchCurrentTab(){}function api(action,body){window.webkit.messageHandlers.geometry.postMessage(JSON.stringify({action,body}));return Promise.resolve({})};'''+page[page.index('let playerResizeMode=false,'):page.index('// Resize overlay end')]+page[start:end]+'''
if(RUNNER_MODE){selected='';$('runner').hidden=false;$('screen').hidden=true;$('runner-help').textContent='Fim de jogo — teste sintético';}else{$('runner').hidden=true;$('screen').hidden=false;$('screen').replaceChildren();const frame=document.createElement('iframe');frame.srcdoc='<html style="background:#126"><body>Vídeo sintético</body></html>';$('screen').append(frame);}
function report(stage){const r=controlsContent().getBoundingClientRect();window.webkit.messageHandlers.geometry.postMessage(JSON.stringify({stage,rect:{left:r.left,top:r.top,width:r.width,height:r.height}}))}
setTimeout(async()=>{
 report('before');
 if(AUTO_MODE){
  await $('auto-controls').onclick();
  window.orbitzAutoPointer({sequence:1,inside:false,x:-1,y:-1});
  setTimeout(()=>{report('hidden');window.orbitzAutoPointer({sequence:1,inside:true,x:.5,y:.5});setTimeout(()=>report('shown'),1100)},2500);
 }else{window.orbitzToggleControls();setTimeout(()=>{window.orbitzFitPlayer();if(!document.body.classList.contains('controls-hidden')||document.getElementById('player-resize-overlay').hidden||document.querySelectorAll('.resize-handle').length!==8)throw Error('resize overlay must preserve hidden mode');window.orbitzFitPlayer();if(!document.getElementById('player-resize-overlay').hidden)throw Error('Ctrl+T must close overlay');report('hidden');window.orbitzToggleControls();setTimeout(()=>report('shown'),600)},600)}
},300);
'''
script='const AUTO_MODE='+('true' if auto_mode else 'false')+';const RUNNER_MODE='+('true' if runner_mode else 'false')+';'+script
view.load_html(prefix+'<script>'+script+'</script>','http://localhost/')
window.show_all();GLib.timeout_add_seconds(8,lambda:Gtk.main_quit() or False);Gtk.main();window.destroy()
if failed or set(results)!={'before','hidden','shown'}:raise SystemExit('SMOKE FAILED '+str(failed)+' '+str(results))
for stage in ('hidden','shown'):
 for dimension in ('x','y','width','height'):
  if abs(results['before'][dimension]-results[stage][dimension])>1:raise SystemExit('Central area size changed: '+str(results))
print('GTK/WebKit geometry smoke PASS: identical central-area screen position and dimensions before/hidden/shown')
