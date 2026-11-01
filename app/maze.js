/* Original maze-chase game: all graphics are drawn locally, no external assets. */
(()=>{
'use strict';
const MAP=[
'###################',
' o.......#.......o ',
'#.##.###.#.###.##.#',
'#.................#',
'#.##.#.#####.#.##.#',
'#....#...#...#....#',
'####.###.#.###.####',
'#......#...#......#',
'#.####.#.#.#.####.#',
'#.................#',
'#.##.#.#####.#.##.#',
'#o.#.#...#...#.#.o#',
'##.#.###.#.###.#.##',
'#.................#',
'#.######.#.######.#',
' ................. ',
'###################'];
const DIRS=[{x:1,y:0},{x:0,y:1},{x:-1,y:0},{x:0,y:-1}];
const key=(x,y)=>x+','+y;
function walkable(x,y,map=MAP){return y>=0&&y<map.length&&x>=0&&x<map[0].length&&map[y][x]!=='#'}
const PORTAL_ROWS=[1,15];
function normalizeX(x){return(x%19+19)%19}
function moves(entity,map=MAP){return DIRS.map((d,i)=>{let x=entity.x+d.x,y=entity.y+d.y;if(PORTAL_ROWS.includes(y)&&(x<0||x>=19))x=normalizeX(x);return{x,y,dir:i}}).filter(p=>walkable(p.x,p.y,map))}
function distanceMap(target,map=MAP){const result=new Map([[key(target.x,target.y),0]]),queue=[target];for(let i=0;i<queue.length;i++){const p=queue[i];for(const next of moves(p,map)){const k=key(next.x,next.y);if(!result.has(k)){result.set(k,result.get(key(p.x,p.y))+1);queue.push(next)}}}return result}
function levelMap(level){const map=MAP.map(row=>[...row]),variant=(level-1)%3;const cuts=variant===1?[[9,5],[9,11],[7,8],[11,8]]:variant===2?[[5,4],[13,4],[9,2],[9,14]]:[];for(const [x,y] of cuts)map[y][x]='.';return map.map(row=>row.join(''))}
const PLAYER_SPEED=1/.14;
const FIXED_DT=1/120;
function actor(x,y,dir){return{x,y,dir,tx:null,ty:null,turns:0}}
function createState(level=1){const map=levelMap(level),dots=new Map();map.forEach((row,y)=>[...row].forEach((c,x)=>{if(c==='.'||c==='o')dots.set(key(x,y),c)}));dots.delete(key(9,15));return{map,level,levelWait:0,cherry:null,cherryWait:16,dots,player:actor(9,15,2),wanted:2,ghosts:[actor(8,7,0),actor(10,7,2),actor(9,9,3)],soundEvents:[],chomp:0,score:0,lives:3,power:0,grace:1.5,over:false,won:false,time:0,travel:0,dotRevision:0,steps:0}}
function resetActors(s){s.player=actor(9,15,2);s.wanted=2;s.ghosts=[actor(8,7,0),actor(10,7,2),actor(9,9,3)];s.power=0;s.grace=1.5;s.routeKey=null}
function centered(entity){return entity.tx==null}
function requestDirection(s,direction){
 if(!Number.isInteger(direction)||direction<0||direction>3)return;
 s.wanted=direction;
 const p=s.player;
 // Reversal happens in the current corridor immediately, without finishing a tile.
 if(!centered(p)&&direction===(p.dir+2)%4){
  const old=DIRS[p.dir];p.tx-=old.x;p.ty-=old.y;p.dir=direction;
 }
}
function moveActor(entity,distance,choose,arrive){
 let remaining=distance;
 while(remaining>1e-9){
  if(centered(entity)){
   const direction=choose(entity);
   if(direction==null)break;
   const d=DIRS[direction];entity.dir=direction;entity.tx=entity.x+d.x;entity.ty=entity.y+d.y;
  }
  const length=Math.abs(entity.tx-entity.x)+Math.abs(entity.ty-entity.y),amount=Math.min(remaining,length),d=DIRS[entity.dir];
  entity.x+=d.x*amount;entity.y+=d.y*amount;remaining-=amount;
  if(length-amount<1e-9){entity.x=entity.tx;entity.y=entity.ty;if(PORTAL_ROWS.includes(entity.y))entity.x=normalizeX(entity.x);entity.tx=null;entity.ty=null;entity.turns=(entity.turns||0)+1;arrive?.(entity)}
  else break;
 }
 return distance-remaining;
}
function soundEvent(s,name){if(s.soundEvents.length<16)s.soundEvents.push(name)}
function collect(s){
 const p=s.player;if(!centered(p))return;
 if(s.cherry&&p.x===s.cherry.x&&p.y===s.cherry.y){s.score+=100*Math.min(s.level,5);s.cherry=null;s.cherryWait=22;soundEvent(s,'maze_cherry')}
 const k=key(p.x,p.y),dot=s.dots.get(k);
 if(dot){s.dots.delete(k);s.dotRevision++;s.score+=dot==='o'?50:10;if(dot==='o'){s.power=Math.max(3,7-(s.level-1)*.45);soundEvent(s,'maze_power')}else{soundEvent(s,s.chomp++%2?'maze_chomp_b':'maze_chomp_a')}}
}
function ghostContact(s){
 for(let i=0;i<s.ghosts.length;i++){
  const ghost=s.ghosts[i];
  if(ghost.cooldown>0||Math.hypot(Math.min(normalizeX(ghost.x-s.player.x),normalizeX(s.player.x-ghost.x)),ghost.y-s.player.y)>.62)continue;
  if(s.power){soundEvent(s,'maze_ghost');s.score+=200;s.ghosts[i]={...actor(9,7,0),cooldown:.8}}
  else if(!s.grace){soundEvent(s,'maze_death');s.lives--;if(!s.lives)s.over=true;else resetActors(s);return true}
 }
 return false;
}
function simulate(s,dt){
 s.time+=dt;
 if(s.cherry){s.cherry.remaining-=dt;if(s.cherry.remaining<=0){s.cherry=null;s.cherryWait=22}}
 else{s.cherryWait-=dt;if(s.cherryWait<=0)s.cherry={x:9,y:9,remaining:8}}
s.power=Math.max(0,s.power-dt);s.grace=Math.max(0,s.grace-dt);s.steps++;
 collect(s);if(ghostContact(s))return;
 s.travel+=moveActor(s.player,PLAYER_SPEED*(1+Math.min(.18,(s.level-1)*.025))*dt,p=>{
  const options=moves(p,s.map);return (options.find(p=>p.dir===s.wanted)||options.find(next=>next.dir===p.dir))?.dir;
 },()=>collect(s));
 const target={x:normalizeX(Math.round(s.player.x)),y:Math.round(s.player.y)},routeKey=key(target.x,target.y);
 if(s.routeKey!==routeKey){s.routeKey=routeKey;s.routes=distanceMap(target,s.map)}
 for(let i=0;i<s.ghosts.length;i++){
  const ghost=s.ghosts[i];ghost.cooldown=Math.max(0,(ghost.cooldown||0)-dt);if(ghost.cooldown)continue;
  moveActor(ghost,(s.power?4.4:6.1+Math.min(1.7,(s.level-1)*.15))*dt,g=>{
   let options=moves(g,s.map),forward=options.filter(p=>p.dir!==(g.dir+2)%4);if(forward.length)options=forward;
   options.sort((a,b)=>{const da=s.routes.get(key(a.x,a.y))??999,db=s.routes.get(key(b.x,b.y))??999;return s.power?db-da:da-db});
   return options[i===2&&g.turns%4===3?g.turns%options.length:0]?.dir;
  });
 }
 ghostContact(s);if(!s.over&&!s.dots.size&&!s.won){s.won=true;s.levelWait=2;s.cherry=null;soundEvent(s,'maze_win')}
}
function advanceLevel(s){const {score,lives,soundEvents}=s;Object.assign(s,createState(s.level+1),{score,lives,soundEvents});soundEvent(s,'maze_start')}
function step(s,dt=.14){
 if(!Number.isFinite(dt)||dt<=0)return;
 let remaining=Math.min(dt,.25);
 while(remaining>1e-9&&!s.over){const slice=Math.min(FIXED_DT,remaining);if(s.won){s.levelWait-=slice;if(s.levelWait<=0)advanceLevel(s)}else simulate(s,slice);remaining-=slice}
}
if(typeof module!=='undefined'&&module.exports){module.exports={MAP,walkable,moves,distanceMap,createState,step,requestDirection,PLAYER_SPEED,FIXED_DT,levelMap,PORTAL_ROWS};return}
const panel=$('runner'),runnerCanvas=$('runner-canvas'),runnerHelp=$('runner-help');
const canvas=document.createElement('canvas');canvas.id='maze-canvas';canvas.tabIndex=0;canvas.setAttribute('role','img');canvas.hidden=true;panel.append(canvas);
const help=document.createElement('div');help.id='maze-help';help.hidden=true;panel.append(help);
const switchHint=document.createElement('div');switchHint.id='game-switch-hint';panel.append(switchHint);
const status=document.createElement('div');status.className='sr-only';status.setAttribute('role','status');status.setAttribute('aria-live','polite');panel.append(status);
const style=document.createElement('style');style.textContent='#maze-canvas{position:absolute;inset:0;width:100%;height:100%;outline:none;background:#080d18}#maze-canvas[hidden],#maze-help[hidden]{display:none}#maze-help{position:absolute;left:12px;bottom:10px;font-size:12px;color:#dceaff;pointer-events:none}#game-switch-hint{z-index:1;position:absolute;left:12px;top:8px;font-size:11px;color:#c4cdd8;pointer-events:none}';document.head.append(style);
let mode='runner',state=createState(),raf=0,last=0,accumulator=0,playing=false,width=0,height=0,blurred=false,lastPaint=0,best=0,savedBest=0,recordTimer=0;
const mazeCache={};
const ctx=canvas.getContext('2d');
function visible(){return !window.orbitzGamesHome&&!window.orbitzGamePaused?.()&&mode==='maze'&&!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&!window.orbitzFeaturesOpen?.()&&$('settings-menu').hidden&&document.visibilityState==='visible'&&!blurred}
function stop(){cancelAnimationFrame(raf);raf=0;last=0;lastPaint=0;accumulator=0}
function announce(){status.textContent=uiTr(state.won?'youtube.maze_win':state.over?'youtube.maze_over':'youtube.maze_label')}
function persistBest(){clearTimeout(recordTimer);recordTimer=0;const score=Math.max(best,state.score);if(score<=savedBest)return;savedBest=score;best=score;api('maze-score',{score}).then(data=>{best=Math.max(best,data.best);savedBest=Math.max(savedBest,data.best)}).catch(()=>{savedBest=0})}
function renderMazeScene(ctx,canvas,state,width,height,dpr,cache,showHud=true){
 ctx.setTransform(dpr,0,0,dpr,0,0);
 const board=state.map||MAP;
 const tile=Math.max(1,Math.min((width-24)/19,(height-(showHud?98:24))/17)),ox=(width-tile*19)/2,oy=showHud?42:12;
 const cacheKey=[width,height,dpr,state.level,state.dotRevision,state.dots.size].join(':');
 if(cacheKey!==cache.key){
  cache.key=cacheKey;cache.image=document.createElement('canvas');cache.image.width=canvas.width;cache.image.height=canvas.height;
  const bg=cache.image.getContext('2d');bg.setTransform(dpr,0,0,dpr,0,0);bg.fillStyle='#080d18';bg.fillRect(0,0,width,height);bg.translate(ox,oy);
  bg.fillStyle='#101c46';
  for(let y=0;y<board.length;y++)for(let x=0;x<19;x++)if(board[y][x]==='#')bg.fillRect(x*tile,y*tile,tile+.5,tile+.5);
  bg.strokeStyle='#527ae9';bg.lineWidth=Math.max(1,tile*.065);bg.lineJoin='round';bg.beginPath();
  for(let y=0;y<board.length;y++)for(let x=0;x<19;x++)if(board[y][x]==='#'){
   const l=x*tile,t=y*tile,r=l+tile,b=t+tile;
   if(y===0||walkable(x,y-1,board)){bg.moveTo(l,t);bg.lineTo(r,t)}
   if(y===board.length-1||walkable(x,y+1,board)){bg.moveTo(l,b);bg.lineTo(r,b)}
   if(x===0||walkable(x-1,y,board)){bg.moveTo(l,t);bg.lineTo(l,b)}
   if(x===18||walkable(x+1,y,board)){bg.moveTo(r,t);bg.lineTo(r,b)}
  }bg.stroke();
  bg.fillStyle='#f8d7a2';bg.beginPath();
  for(const [position,type] of state.dots){if(type==='o')continue;const [x,y]=position.split(',').map(Number);bg.moveTo((x+.57)*tile,(y+.5)*tile);bg.arc((x+.5)*tile,(y+.5)*tile,tile*.065,0,Math.PI*2)}bg.fill();
 }
 ctx.drawImage(cache.image,0,0,width,height);ctx.save();ctx.translate(ox,oy);ctx.beginPath();ctx.rect(0,0,19*tile,17*tile);ctx.clip();
 for(const [position,type] of state.dots){if(type!=='o')continue;const [x,y]=position.split(',').map(Number);ctx.fillStyle='#ffe4a6';ctx.beginPath();ctx.arc((x+.5)*tile,(y+.5)*tile,tile*(.21+.025*Math.sin(state.time*7)),0,Math.PI*2);ctx.fill()}
 function drawPlayer(p){ctx.save();ctx.translate((p.x+.5)*tile,(p.y+.5)*tile);ctx.rotate(p.dir*Math.PI/2);ctx.fillStyle=state.grace>0?'#ffeaa1':'#ffdc30';ctx.beginPath();ctx.moveTo(0,0);const mouth=.045+.22*(.5+.5*Math.sin(state.travel*7));ctx.arc(0,0,tile*.43,mouth*Math.PI,(2-mouth)*Math.PI);ctx.closePath();ctx.fill();ctx.restore();
}
 for(const dx of [0,...(state.player.x<0?[19]:[]),...(state.player.x>18?[-19]:[])])drawPlayer({...state.player,x:state.player.x+dx});
 function drawGhost(g,i){
  const x=(g.x+.5)*tile,y=(g.y+.5)*tile,r=tile*.4,frightened=state.power>0;
  ctx.fillStyle=frightened?(state.power<2&&Math.sin(state.time*18)>0?'#dce6ff':'#527cf2'):['#ff6689','#65e6de','#ffbd69'][i];
  ctx.beginPath();ctx.arc(x,y,r,Math.PI,0);ctx.lineTo(x+r,y+r*.85);
  for(let j=4;j>=0;j--){const foot=(j%2===0?1:.66)+Math.sin(state.time*14+j+i)*.07;ctx.lineTo(x-r+j*r/2,y+r*foot)}ctx.closePath();ctx.fill();
  ctx.fillStyle='#fff';ctx.beginPath();ctx.ellipse(x-r*.35,y-r*.04,r*.25,r*.31,0,0,Math.PI*2);ctx.ellipse(x+r*.35,y-r*.04,r*.25,r*.31,0,0,Math.PI*2);ctx.fill();
  const gaze=DIRS[g.dir];ctx.fillStyle='#14234c';ctx.beginPath();ctx.arc(x-r*.35+gaze.x*r*.1,y-r*.04+gaze.y*r*.14,r*.12,0,Math.PI*2);ctx.arc(x+r*.35+gaze.x*r*.1,y-r*.04+gaze.y*r*.14,r*.12,0,Math.PI*2);ctx.fill();
 }
 state.ghosts.forEach((g,i)=>{drawGhost(g,i);if(g.x<0)drawGhost({...g,x:g.x+19},i);if(g.x>18)drawGhost({...g,x:g.x-19},i)});
 if(state.cherry){const c=state.cherry,x=(c.x+.5)*tile,y=(c.y+.5)*tile;ctx.strokeStyle='#71bc74';ctx.lineWidth=Math.max(1,tile*.07);ctx.beginPath();ctx.moveTo(x-tile*.15,y);ctx.quadraticCurveTo(x-tile*.1,y-tile*.5,x+tile*.22,y-tile*.4);ctx.lineTo(x+tile*.15,y);ctx.stroke();ctx.fillStyle='#f34c6c';ctx.beginPath();ctx.arc(x-tile*.16,y+tile*.12,tile*.19,0,Math.PI*2);ctx.arc(x+tile*.16,y+tile*.12,tile*.19,0,Math.PI*2);ctx.fill()}ctx.restore();
 if(showHud){
 ctx.fillStyle='#eaf3ff';ctx.font='bold 13px system-ui';ctx.textAlign='right';ctx.fillText(uiTr('youtube.maze_score',{score:state.score,lives:state.lives,level:state.level,best:Math.max(best,state.score)}),width-12,26);
 if(!playing||state.over||state.won){ctx.fillStyle='#080d18dd';ctx.fillRect(0,height/2-26,width,52);ctx.fillStyle='#ffe28a';ctx.textAlign='center';ctx.font='bold 14px system-ui';ctx.fillText(uiTr(state.won?'youtube.maze_win':state.over?'youtube.maze_over':'youtube.maze_start'),width/2,height/2+5)}
 }
}
function draw(){
 if(window.orbitzGamesHome||mode!=='maze'||panel.hidden)return;
 const r=panel.getBoundingClientRect();if(!r.width||!r.height)return;
 const dpr=Math.min(devicePixelRatio||1,2);width=r.width;height=r.height;
 if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr)}
 renderMazeScene(ctx,canvas,state,width,height,dpr,mazeCache);
}
window.orbitzGamePreviews.maze=target=>{const {width,height}=window.orbitzPreviewSize(target);const scene=createState();scene.grace=0;renderMazeScene(target.getContext('2d'),target,scene,width,height,1,{},false)};
function tick(now){
 raf=0;if(!visible()||!playing)return;
 if(last)accumulator+=Math.min((now-last)/1000,.1);last=now;
 while(accumulator>=FIXED_DT){step(state,FIXED_DT);accumulator-=FIXED_DT;if(state.over)break}
 if(state.score>best){best=state.score;if(!recordTimer)recordTimer=setTimeout(persistBest,1500)}
 for(const sound of state.soundEvents.splice(0)){window.orbitzGameSound?.(sound);if(sound==='maze_win'){persistBest();announce();}}
 if(!lastPaint||now-lastPaint>=1000/60-1){draw();lastPaint=now}
 if(state.over){persistBest();playing=false;announce();draw();return}
 raf=requestAnimationFrame(tick);
}
function ensure(){if(visible()&&playing&&!raf){last=0;raf=requestAnimationFrame(tick)}}
window.orbitzMazePauseChanged=()=>{persistBest();stop();draw();ensure()};
const games=['runner','maze','invaders','asteroids','breaker','lander'];
function switchGame(direction=1){if(window.orbitzGamesHome)return;selectGame(games[(games.indexOf(mode)+direction+games.length)%games.length])}
function selectGame(next){
 if(!games.includes(next))return;
 if(panel.hidden||!$('screen').hidden||!$('config').hidden||!$('discovery').hidden||window.orbitzFeaturesOpen?.()||!$('settings-menu').hidden)return;
 if(mode==='maze')persistBest();window.orbitzHideGamesHome?.();mode=next;window.orbitzGameMode=mode;window.orbitzSyncGamePause?.();runnerCanvas.hidden=mode!=='runner';runnerHelp.hidden=mode!=='runner';canvas.hidden=mode!=='maze';help.hidden=mode!=='maze';stop();window.orbitzRunnerGameChanged?.();window.orbitzInvadersActivate?.();window.orbitzAsteroidsActivate?.();window.orbitzBreakerActivate?.();window.orbitzLanderActivate?.();
 $(mode==='runner'?'runner-canvas':mode+'-canvas').focus({preventScroll:true});draw();ensure();language();
}
window.orbitzOpenGame=selectGame;
function language(){switchHint.textContent=uiTr('youtube.game_switch');help.textContent=uiTr('youtube.maze_help');canvas.setAttribute('aria-label',uiTr('youtube.maze_label'));draw()}
function editable(target){return ['INPUT','TEXTAREA','SELECT'].includes(target?.tagName)||target?.isContentEditable}
document.addEventListener('keydown',event=>{
 if(editable(event.target))return;
 if(event.shiftKey&&!event.ctrlKey&&!event.altKey&&!event.metaKey&&['ArrowUp','ArrowDown'].includes(event.key)){event.preventDefault();event.stopImmediatePropagation();if(!event.repeat)switchGame(event.key==='ArrowUp'?1:-1);return}
 if(!visible()||event.shiftKey||event.ctrlKey||event.altKey||event.metaKey)return;
 const direction={ArrowRight:0,ArrowDown:1,ArrowLeft:2,ArrowUp:3}[event.key];
 if(direction===undefined&&event.key!==' ')return;
 window.orbitzUnlockGameAudio?.();
 event.preventDefault();event.stopImmediatePropagation();if(state.over){persistBest();state=createState();announce()}
 if(direction!==undefined)requestDirection(state,direction);if(!playing)window.orbitzGameSound?.('maze_start');playing=true;draw();ensure();
},true);
let touch=null;canvas.addEventListener('pointerdown',event=>{if(!visible())return;touch={x:event.clientX,y:event.clientY};canvas.focus();if(state.over){persistBest();state=createState()};if(!playing)window.orbitzGameSound?.('maze_start');playing=true;draw();ensure()});canvas.addEventListener('pointerup',event=>{if(!visible()){touch=null;return}if(!touch)return;const dx=event.clientX-touch.x,dy=event.clientY-touch.y;touch=null;if(Math.max(Math.abs(dx),Math.abs(dy))>10)requestDirection(state,Math.abs(dx)>Math.abs(dy)?dx>0?0:2:dy>0?1:3)});
new MutationObserver(()=>{if(!visible())stop();else{draw();ensure()}}).observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','class']});
new ResizeObserver(()=>draw()).observe(panel);
window.addEventListener('blur',()=>{blurred=true;stop()});window.addEventListener('focus',()=>{blurred=false;ensure()});document.addEventListener('visibilitychange',()=>{if(!visible())stop();else ensure()});window.addEventListener('pagehide',()=>{persistBest();stop()});
const oldLanguage=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{oldLanguage?.();language()};language();api('maze-score',{}).then(data=>{if(Number.isSafeInteger(data.best)&&data.best>=0){best=Math.max(best,data.best);savedBest=Math.max(savedBest,data.best);draw()}}).catch(()=>{});
})();
