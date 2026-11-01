const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('app/index.html','utf8');
function setup(){
 const nodes=new Map(),classes=new Set(),actions=[],timers=new Map();let now=0,next=0,hook=null;
 const document={body:{classList:{toggle(n,on){on?classes.add(n):classes.delete(n)},remove(n){classes.delete(n)}}},addEventListener(){},activeElement:null};
 const node=id=>({id,hidden:true,disabled:false,isConnected:true,style:{setProperty(){},removeProperty(){}},attributes:{},events:{},setAttribute(k,v){this.attributes[k]=v},addEventListener(k,fn){this.events[k]=fn},contains(n){return n===this},focus(){document.activeElement=this},getBoundingClientRect(){return this.rect||{left:0,top:60,width:700,height:390}}});
 for(const id of ['runner','screen','config','discovery','settings-menu','settings','new-window','open-settings','auto-controls','auto-controls-check','controls-shortcut','always-above','always-above-check','copy-video-link','config-close','language','save','search','query','key','config-status','player-action-status'])nodes.set(id,node(id));
 nodes.get('screen').hidden=false;
 const context=vm.createContext({document,window:{innerWidth:700,innerHeight:500,addEventListener(){}},$:id=>nodes.get(id),selected:'abcdefghijk',uiText(){},uiLocale:'pt-BR',uiErrorText(){},loadRecommendations(){},searchCurrentTab(){},
 setTimeout(fn,delay){timers.set(++next,{fn,at:now+delay});return next},clearTimeout(id){timers.delete(id)},
 api:async(action,body)=>{actions.push({action,body});return hook?await hook(action,body):{};}});
 vm.runInContext(html.slice(html.indexOf('// App controls and settings menu.'),html.indexOf('function renderResults')),context);
 const advance=ms=>{now+=ms;for(const [id,timer] of [...timers])if(timer.at<=now){timers.delete(id);timer.fn()}};
 const pointer=inside=>context.window.orbitzAutoPointer({sequence:actions.findLast(a=>a.action==='auto-controls').body.sequence,inside,x:.5,y:.4});
 return{nodes,classes,actions,timers,context,advance,pointer,setHook(fn){hook=fn}};
}
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
(async()=>{
 const t=setup(),{nodes,classes,context,advance,pointer,timers,actions}=t;
 await nodes.get('auto-controls').onclick();assert.equal(nodes.get('controls-shortcut').attributes['aria-disabled'],'true');
 context.window.orbitzToggleControls();assert(!classes.has('controls-hidden'),'Ctrl+H disabled with auto on');
 pointer(false);const staleTimer=[...timers.values()][0].fn;advance(1999);assert(!classes.has('controls-hidden'));pointer(true);staleTimer();advance(1);assert(!classes.has('controls-hidden'),'return cancels hide even if the old callback was queued');
 pointer(false);advance(1000);pointer(false);assert.equal(timers.size,1,'same region does not reset the deadline');advance(1000);assert(classes.has('controls-hidden'),'2 seconds outside hides');
 pointer(true);advance(499);assert(classes.has('controls-hidden'));pointer(false);advance(1);assert(classes.has('controls-hidden'),'exit cancels reveal');
 pointer(true);advance(500);assert(!classes.has('controls-hidden'),'500 milliseconds inside reveals');await flush();
 pointer(false);advance(1500);pointer(true);pointer(false);advance(500);assert(!classes.has('controls-hidden'),'new exit restarts full 2 seconds');advance(1500);assert(classes.has('controls-hidden'));
 pointer(true);advance(100);await nodes.get('auto-controls').onclick();advance(10000);assert(!classes.has('controls-hidden'),'disabling cancels timers and restores controls');
 assert.equal(nodes.get('controls-shortcut').attributes['aria-disabled'],'false');context.window.orbitzToggleControls();assert(classes.has('controls-hidden'),'manual shortcut works again');context.window.orbitzToggleControls();await flush();
 await nodes.get('auto-controls').onclick();pointer(false);advance(1000);context.openSettings();advance(5000);assert(!classes.has('controls-hidden'),'modal protects controls');context.closeSettings();advance(1999);assert(!classes.has('controls-hidden'));advance(1);assert(classes.has('controls-hidden'),'closing modal starts a fresh deadline');
 const epoch=actions.findLast(a=>a.action==='auto-controls').body.sequence;
 context.window.orbitzAutoPointer({sequence:epoch-1,inside:true,x:.5,y:.4});advance(500);assert(classes.has('controls-hidden'),'stale epoch cannot show controls');
 pointer(true);assert.equal(timers.size,1);context.window.orbitzAutoPointer({sequence:epoch,inside:true,x:.2,y:.02});advance(500);assert(classes.has('controls-hidden'),'pointer on header is outside video');
 // Hiding moves the content to viewport origin. An old header coordinate
 // must not suddenly be interpreted as a mouse reentry into the video.
 const layout=setup();await layout.nodes.get('auto-controls').onclick();
 const epochLayout=layout.actions.findLast(a=>a.action==='auto-controls').body.sequence;
 layout.context.window.orbitzAutoPointer({sequence:epochLayout,inside:true,x:.5,y:.04});
 layout.advance(2000);assert(layout.classes.has('controls-hidden'));
 layout.nodes.get('screen').rect={left:0,top:0,width:700,height:390};
 layout.context.syncControls();layout.advance(500);
 assert(layout.classes.has('controls-hidden'),'layout change without fresh pointer sample must not reveal header');
 layout.pointer(false);layout.advance(5000);assert(layout.classes.has('controls-hidden'));
 const content=setup();await content.nodes.get('auto-controls').onclick();
 const contentEpoch=content.actions.findLast(a=>a.action==='auto-controls').body.sequence;
 content.nodes.get('screen').rect={left:14,top:60,width:672,height:390};
 content.context.window.orbitzAutoPointer({sequence:contentEpoch,inside:true,x:.005,y:.4});
 content.nodes.get('screen').rect={left:0,top:60,width:700,height:390};
 content.context.window.orbitzRefreshPointer();content.advance(2000);
 assert(!content.classes.has('controls-hidden'),'actual content selection refreshes pointer region once, before transitions');
 // Older request failure must not undo the newest desired state.
 const g=setup();let oldReject;let count=0;
 g.setHook(action=>action==='window-state'&&++count===1?new Promise((resolve,reject)=>{oldReject=reject}):{});
 g.context.window.orbitzToggleControls();g.context.window.orbitzToggleControls();g.context.window.orbitzToggleControls();
 oldReject(Error('old request'));await flush();assert(g.classes.has('controls-hidden'),'stale native failure cannot override latest state');
 const early=setup();early.setHook((action,body)=>{if(action==='auto-controls')early.context.window.orbitzAutoPointer({sequence:body.sequence,inside:false,x:0,y:0});return{}});
 await early.nodes.get('auto-controls').onclick();early.advance(2000);assert(early.classes.has('controls-hidden'),'initial native sample arriving before HTTP acknowledgement is replayed once');
 const h=setup();h.setHook(()=>{throw Error('synthetic preference failure')});
 await h.nodes.get('auto-controls').onclick();assert(!h.nodes.get('auto-controls').disabled);h.context.window.orbitzToggleControls();assert(h.classes.has('controls-hidden'),'failed enable keeps manual shortcut available');
 console.log('OK: auto controls deadlines, cancellation, rapid reentry, iframe/native coordinates, modal protection, epoch rejection and shortcut exclusion.');
})().catch(error=>{console.error(error);process.exitCode=1});
