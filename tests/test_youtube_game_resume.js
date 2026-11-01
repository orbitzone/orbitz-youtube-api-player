const fs=require('fs'),vm=require('vm'),assert=require('assert');
const nodes=new Map(),handlers=[];let forwarded=0;
function node(id){return{id,hidden:!['runner'].includes(id),classList:{toggle(){}},setAttribute(){},append(){},focus(){},dispatchEvent(event){forwarded++;for(const handler of handlers)handler(event)}}}
for(const id of ['runner','screen','config','discovery','settings-menu','runner-canvas','maze-canvas','invaders-canvas','asteroids-canvas','breaker-canvas','lander-canvas'])nodes.set(id,node(id));
const context={window:{},$:id=>nodes.get(id),uiTr:k=>k,KeyboardEvent:class{constructor(type,data){Object.assign(this,data);this.type=type;this.target={tagName:'CANVAS'}}preventDefault(){}stopImmediatePropagation(){}},document:{createElement:()=>node('new'),head:{append(){}},addEventListener:(name,fn)=>handlers.push(fn)}};
vm.createContext(context);vm.runInContext(fs.readFileSync('app/game_controls.js','utf8'),context);
const press=(key,options={})=>{const event={key,target:{tagName:'CANVAS'},preventDefault(){},stopImmediatePropagation(){},...options};handlers[0](event)};
const controls={runner:[' ','ArrowUp'],maze:[' ','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'],invaders:[' ','ArrowLeft','ArrowRight','a','d'],asteroids:[' ','ArrowLeft','ArrowRight','ArrowUp','a','d','w'],breaker:[' ','ArrowLeft','ArrowRight','a','d'],lander:[' ','ArrowLeft','ArrowRight','ArrowUp','a','d','w']};
for(const [game,keys] of Object.entries(controls))for(const key of keys){context.window.orbitzGameMode=game;press('Escape');assert(context.window.orbitzGamePaused());press('x');assert(context.window.orbitzGamePaused());press(key,{repeat:true});assert(context.window.orbitzGamePaused());const previous=forwarded;press(key);assert(!context.window.orbitzGamePaused(),game+' '+key);assert.equal(forwarded,previous+1,'control forwarded once')}
press('Escape');press(' ',{target:{tagName:'INPUT'}});assert(context.window.orbitzGamePaused());press(' ',{shiftKey:true});assert(context.window.orbitzGamePaused());press('Escape');
console.log('OK: every real control resumes each of six games once; repeat, modifiers and inputs excluded.');
