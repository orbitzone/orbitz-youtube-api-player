"""Manual GTK/WebKit responsive-filter smoke; synthetic content, no network/user data."""
import json
from pathlib import Path
import gi
gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,GLib,WebKit2
root=Path(__file__).resolve().parents[1]
cases=[(568,320,'pt-BR'),(980,500,'en-US'),(360,280,'pt-BR')];results=[];errors=[]
manager=WebKit2.UserContentManager();manager.register_script_message_handler('layout')
view=WebKit2.WebView(user_content_manager=manager);window=Gtk.Window(title='Teste de filtros — temporário');window.add(view)
window.set_default_size(*cases[0][:2])
page=(root/'app/index.html').read_text().split('<script>',1)[0]
catalogs={locale:json.loads((root/'i18n'/(locale+'.json')).read_text()) for locale in ('pt-BR','en-US')}
script='''const catalogs='''+json.dumps(catalogs)+''';
function measure(locale){
 const catalog=catalogs[locale];
 for(const node of document.querySelectorAll('[data-i18n]'))node.textContent=catalog[node.dataset.i18n]||'';
 for(const attribute of ['aria-label','title'])for(const node of document.querySelectorAll('[data-i18n-'+attribute+']'))node.setAttribute(attribute,catalog[node.getAttribute('data-i18n-'+attribute)]||'');
 document.getElementById('discovery').hidden=false;
 const tabs=[...document.querySelectorAll('#view-tabs [role="tab"]')],rail=document.getElementById('view-tabs'),panel=document.getElementById('discovery');
 window.webkit.messageHandlers.layout.postMessage(JSON.stringify({width:innerWidth,height:innerHeight,tabs:tabs.map(tab=>({id:tab.id,label:tab.getAttribute('aria-label'),title:tab.title,labelDisplay:getComputedStyle(tab.querySelector('.filter-label')).display,iconWidth:tab.querySelector('svg').getBoundingClientRect().width})),rail:{width:rail.getBoundingClientRect().width,bottom:rail.getBoundingClientRect().bottom,scrollHeight:rail.scrollHeight,clientHeight:rail.clientHeight},panelBottom:panel.getBoundingClientRect().bottom,comments:document.getElementById('comments-tab')!==null}));
}
'''
def evaluate():
 locale=cases[len(results)][2];view.run_javascript('measure('+json.dumps(locale)+');',None,None,None);return False

def receive(_manager,value):
 try:
  data=json.loads(value.get_js_value().to_string());expected=cases[len(results)]
  assert data['width']==expected[0],data
  assert len(data['tabs'])==4 and not data['comments'],data
  compact=data['width']<=640
  assert data['rail']['width']==(44 if compact else 112),data
  assert data['rail']['bottom']<=data['panelBottom'],data
  for tab in data['tabs']:
   assert tab['label'] and tab['title']==tab['label'],tab
   assert tab['iconWidth']==24,tab
   assert (tab['labelDisplay']=='none')==compact,tab
  print('PASS',expected,'rail width',data['rail']['width'],'names hidden',compact,flush=True)
  results.append(data)
  if len(results)==len(cases):Gtk.main_quit()
  else:window.resize(*cases[len(results)][:2]);GLib.timeout_add(250,evaluate)
 except Exception as error:errors.append(str(error));Gtk.main_quit()
manager.connect('script-message-received::layout',receive)
view.connect('load-changed',lambda _view,event:GLib.timeout_add(250,evaluate) if event==WebKit2.LoadEvent.FINISHED else None)
view.load_html(page+'<script>'+script+'</script>','http://localhost/');window.show_all()
GLib.timeout_add_seconds(8,lambda:Gtk.main_quit() or False);Gtk.main();window.destroy()
if errors or len(results)!=len(cases):raise SystemExit('SMOKE FAILED '+str(errors))
print('GTK filter layout PASS: small/large/narrow viewport, labels, icons and rail containment')
