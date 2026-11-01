/* Original vector space game. All shapes and physics are local. */
(()=>{
'use strict';
const DT=1/120,TAU=Math.PI*2;
const wrap=(value,size)=>(value%size+size)%size;
function delta(a,b,size){let d=a-b;if(d>size/2)d-=size;if(d<-size/2)d+=size;return d}
function distance(a,b,s){return Math.hypot(delta(a.x,b.x,s.width),delta(a.y,b.y,s.height))}
function random(s){s.seed=(Math.imul(s.seed,1664525)+1013904223)>>>0;return s.seed/4294967296}
function sound(s,name){if(s.events.length<20)s.events.push(name)}
function rock(s,x,y,size=3){const angle=random(s)*TAU,speed=(26+random(s)*30)*(1+(3-size)*.45+s.level*.045);return{x,y,size,r:[0,12,23,39][size],vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,angle:random(s)*TAU,spin:(random(s)-.5)*1.3,shape:Array.from({length:10},()=>.7+random(s)*.3)}}
function newWave(s){s.rocks=[];for(let i=0;i<Math.min(12,3+s.level);i++){let x,y;do{x=random(s)*s.width;y=random(s)*s.height}while(distance({x,y},s.ship,s)<Math.min(140,s.width*.2,s.height*.25));s.rocks.push(rock(s,x,y))}s.waveWait=0;s.ufo=null;s.ufoWait=12;s.ship.grace=Math.max(s.ship.grace,2)}
function createState(width=900,height=540){const s={width,height,seed:271828,level:1,score:0,lives:3,started:false,over:false,time:0,events:[],rocks:[],shots:[],enemyShots:[],particles:[],waveWait:0,ufo:null,ufoWait:12,ship:{x:width/2,y:height/2,vx:0,vy:0,angle:-Math.PI/2,cooldown:0,grace:2,thrust:false}};newWave(s);return s}
function resizeState(s,width,height){if(s.width===width&&s.height===height)return;const sx=width/s.width,sy=height/s.height;for(const item of [s.ship,...s.rocks,...s.shots,...s.enemyShots,...s.particles,...(s.ufo?[s.ufo]:[])]){item.x*=sx;item.y*=sy}s.width=width;s.height=height}
function burst(s,x,y,color){for(let i=0;i<16;i++){const angle=random(s)*TAU,speed=35+random(s)*120;s.particles.push({x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,life:.5,color})}s.particles=s.particles.slice(-120)}
function hitShip(s){if(s.ship.grace>0||s.over)return;s.lives--;burst(s,s.ship.x,s.ship.y,'#8cecff');sound(s,'asteroids_death');if(s.lives<=0){s.over=true;return}s.ship={x:s.width/2,y:s.height/2,vx:0,vy:0,angle:-Math.PI/2,cooldown:.3,grace:3,thrust:false};s.enemyShots=[]}
function splitRock(s,index){const target=s.rocks[index];s.rocks.splice(index,1);s.score+=[0,100,50,20][target.size];burst(s,target.x,target.y,'#d3dfe7');sound(s,'asteroids_hit');if(target.size>1)for(let i=0;i<2;i++)s.rocks.push(rock(s,target.x,target.y,target.size-1))}
function simulate(s,input,dt){
 if(!s.started||s.over)return;s.time+=dt;const ship=s.ship;
 ship.grace=Math.max(0,ship.grace-dt);ship.cooldown=Math.max(0,ship.cooldown-dt);
 ship.angle+=(Number(!!input.right)-Number(!!input.left))*3.8*dt;ship.thrust=!!input.thrust;
 if(ship.thrust){ship.vx+=Math.cos(ship.angle)*235*dt;ship.vy+=Math.sin(ship.angle)*235*dt}
 const drag=Math.exp(-.14*dt);ship.vx*=drag;ship.vy*=drag;const speed=Math.hypot(ship.vx,ship.vy);if(speed>340){ship.vx*=340/speed;ship.vy*=340/speed}
 ship.x=wrap(ship.x+ship.vx*dt,s.width);ship.y=wrap(ship.y+ship.vy*dt,s.height);
 if(input.fire&&ship.cooldown<=0&&s.waveWait<=0){s.shots.push({x:wrap(ship.x+Math.cos(ship.angle)*18,s.width),y:wrap(ship.y+Math.sin(ship.angle)*18,s.height),vx:Math.cos(ship.angle)*490+ship.vx*.4,vy:Math.sin(ship.angle)*490+ship.vy*.4,life:1.15});ship.cooldown=.19;sound(s,'asteroids_shot')}
 for(const p of s.particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt}s.particles=s.particles.filter(p=>p.life>0);
 if(s.waveWait>0){s.waveWait-=dt;if(s.waveWait<=0){s.level++;newWave(s)}return}
 for(const target of s.rocks){target.x=wrap(target.x+target.vx*dt,s.width);target.y=wrap(target.y+target.vy*dt,s.height);target.angle+=target.spin*dt}
 s.ufoWait-=dt;if(!s.ufo&&s.ufoWait<=0){s.ufo={x:0,y:60+random(s)*(s.height-120),vx:85,fire:1.2};s.ufoWait=15+random(s)*8;sound(s,'asteroids_ufo')}
 if(s.ufo){const u=s.ufo;u.x+=u.vx*dt;u.fire-=dt;if(u.fire<=0){const angle=Math.atan2(delta(ship.y,u.y,s.height),delta(ship.x,u.x,s.width));s.enemyShots.push({x:u.x,y:u.y,vx:Math.cos(angle)*195,vy:Math.sin(angle)*195,life:2.6});u.fire=Math.max(.6,1.5-s.level*.04)}if(u.x>s.width+25)s.ufo=null}
 for(const shot of s.shots){shot.x=wrap(shot.x+shot.vx*dt,s.width);shot.y=wrap(shot.y+shot.vy*dt,s.height);shot.life-=dt;if(shot.life<=0)continue;
  if(s.ufo&&distance(shot,s.ufo,s)<22){s.score+=200;burst(s,s.ufo.x,s.ufo.y,'#ff9fdd');s.ufo=null;shot.life=0;sound(s,'asteroids_hit');continue}
  const index=s.rocks.findIndex(target=>distance(shot,target,s)<target.r+2);if(index>=0){splitRock(s,index);shot.life=0}
 }
 s.shots=s.shots.filter(shot=>shot.life>0).slice(-16);
 for(const shot of s.enemyShots){shot.x=wrap(shot.x+shot.vx*dt,s.width);shot.y=wrap(shot.y+shot.vy*dt,s.height);shot.life-=dt;if(distance(shot,s.ship,s)<12){shot.life=0;hitShip(s)}}s.enemyShots=s.enemyShots.filter(shot=>shot.life>0).slice(-12);
 if(s.rocks.some(target=>distance(s.ship,target,s)<target.r+10)||(s.ufo&&distance(s.ship,s.ufo,s)<29))hitShip(s);
 if(!s.rocks.length&&!s.over){s.score+=s.level*150;s.waveWait=2;s.shots=[];s.enemyShots=[];s.ufo=null;sound(s,'asteroids_win')}
 s.score=Math.min(2147483647,s.score);
}
function step(s,input={},dt=DT){if(!Number.isFinite(dt)||dt<=0)return;let remaining=Math.min(.1,dt);while(remaining>1e-9){const slice=Math.min(DT,remaining);simulate(s,input,slice);remaining-=slice;if(s.over)break}}
if(typeof module!=='undefined'&&module.exports){module.exports={createState,resizeState,step,splitRock,distance,wrap,DT};return}
const panel=$('runner'),canvas=document.createElement('canvas');canvas.id='asteroids-canvas';canvas.tabIndex=0;canvas.hidden=true;canvas.setAttribute('role','img');panel.append(canvas);
const help=document.createElement('div');help.id='asteroids-help';help.hidden=true;panel.append(help);
const style=document.createElement('style');style.textContent='#asteroids-canvas{position:absolute;inset:0;width:100%;height:100%;outline:none;touch-action:none}#asteroids-canvas[hidden],#asteroids-help[hidden]{display:none}#asteroids-help{position:absolute;left:12px;bottom:10px;font-size:12px;color:#dceaff;pointer-events:none}@media(max-width:500px){#asteroids-help{max-width:68%;font-size:10px}}';document.head.append(style);
const ctx=canvas.getContext('2d'),input={};let state=createState(),best=0,raf=0,last=0,acc=0,lastPaint=0,blurred=false,layout={scale:1,x:12,y:40,width:900,height:540},lastRecord=0;
const stars=Array.from({length:70},(_,i)=>({x:(i*.618033)%1,y:(i*.414214)%1,r:i%5===0?1.2:.6}));
function active(){return window.orbitzGameMode==='asteroids'}
function visible(){return !window.orbitzGamesHome&&active()&&!window.orbitzGamePaused?.()&&!blurred&&!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&$('settings-menu').hidden&&!window.orbitzFeaturesOpen?.()&&document.visibilityState==='visible'}
function stop(){cancelAnimationFrame(raf);raf=0;last=0;acc=0;for(const key of Object.keys(input))delete input[key];state.ship.thrust=false}
function saveRecord(){if(state.score<=best||state.score===lastRecord)return;lastRecord=state.score;best=state.score;api('asteroids-score',{score:best}).then(data=>{if(Number.isSafeInteger(data.best))best=Math.max(best,data.best)}).catch(()=>{})}
function renderAsteroidsScene(ctx,state,width,height,dpr,layout,showHud=true){
ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#080d18';ctx.fillRect(0,0,width,height);ctx.save();ctx.translate(layout.x,layout.y);ctx.scale(layout.scale,layout.scale);
 for(const star of stars){ctx.fillStyle='#506583';ctx.fillRect(star.x*state.width,star.y*state.height,star.r,star.r)}
 ctx.strokeStyle='#c6d5df';ctx.lineWidth=1.7;
 for(const target of state.rocks){ctx.save();ctx.translate(target.x,target.y);ctx.rotate(target.angle);ctx.beginPath();target.shape.forEach((r,i)=>{const a=i/10*TAU,x=Math.cos(a)*target.r*r,y=Math.sin(a)*target.r*r;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.closePath();ctx.stroke();ctx.restore()}
 const ship=state.ship;if(!state.over&&(ship.grace<=0||Math.floor(state.time*12)%2===0)){ctx.save();ctx.translate(ship.x,ship.y);ctx.rotate(ship.angle);ctx.strokeStyle='#a8efff';ctx.beginPath();ctx.moveTo(17,0);ctx.lineTo(-12,11);ctx.lineTo(-7,0);ctx.lineTo(-12,-11);ctx.closePath();ctx.stroke();if(ship.thrust){ctx.strokeStyle='#ffd184';ctx.beginPath();ctx.moveTo(-10,-5);ctx.lineTo(-21-Math.sin(state.time*45)*5,0);ctx.lineTo(-10,5);ctx.stroke()}ctx.restore()}
 if(state.ufo){const u=state.ufo;ctx.strokeStyle='#ffabe4';ctx.beginPath();ctx.ellipse(u.x,u.y,22,8,0,0,TAU);ctx.moveTo(u.x-11,u.y-5);ctx.lineTo(u.x-6,u.y-14);ctx.lineTo(u.x+6,u.y-14);ctx.lineTo(u.x+11,u.y-5);ctx.stroke()}
 for(const shot of state.shots){ctx.fillStyle='#dcfbff';ctx.fillRect(shot.x-2,shot.y-2,4,4)}for(const shot of state.enemyShots){ctx.fillStyle='#ffb079';ctx.beginPath();ctx.arc(shot.x,shot.y,3,0,TAU);ctx.fill()}
 for(const p of state.particles){ctx.globalAlpha=Math.max(0,p.life/.5);ctx.fillStyle=p.color;ctx.fillRect(p.x-1,p.y-1,2,2)}ctx.globalAlpha=1;ctx.restore();if(showHud){ctx.fillStyle='#e5f1ff';ctx.textAlign='right';ctx.font='bold 12px system-ui';ctx.fillText(uiTr('youtube.invaders_score',{score:state.score,best,lives:state.lives,wave:state.level}),width-12,25);
 if(!state.started||state.over||state.waveWait>0){ctx.fillStyle='#080d18dc';ctx.fillRect(0,height/2-30,width,60);ctx.fillStyle='#bcecff';ctx.textAlign='center';ctx.font='bold 16px system-ui';ctx.fillText(uiTr(state.over?'youtube.invaders_over':state.waveWait>0?'youtube.invaders_wave':'youtube.asteroids_start'),width/2,height/2+5)}
}
}
function draw(){
 if(window.orbitzGamesHome||!active()||panel.hidden)return;const rect=panel.getBoundingClientRect();if(!rect.width||!rect.height)return;
 const width=rect.width,height=rect.height,dpr=Math.min(devicePixelRatio||1,2);if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr)}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#080d18';ctx.fillRect(0,0,width,height);
 const scale=Math.max(.01,Math.min((width-24)/900,(height-80)/360));layout={scale,x:12,y:40,width:(width-24)/scale,height:(height-80)/scale};resizeState(state,layout.width,layout.height);
 renderAsteroidsScene(ctx,state,width,height,dpr,layout);
}
window.orbitzGamePreviews.asteroids=target=>{const {width,height}=window.orbitzPreviewSize(target);const scene=createState();scene.started=true;scene.ship.grace=0;const scale=Math.min((width-24)/900,(height-20)/360),view={scale,x:12,y:10,width:(width-24)/scale,height:(height-20)/scale};resizeState(scene,view.width,view.height);renderAsteroidsScene(target.getContext('2d'),scene,width,height,1,view,false)};
function tick(now){raf=0;if(!visible()||!state.started||state.over)return;if(last)acc+=Math.min(.1,(now-last)/1000);last=now;while(acc>=DT){step(state,input,DT);acc-=DT;if(state.over)break}for(const event of state.events.splice(0))window.orbitzGameSound?.(event);if(!lastPaint||now-lastPaint>=1000/60-1){draw();lastPaint=now}if(state.over){saveRecord();draw();return}raf=requestAnimationFrame(tick)}
function ensure(){if(visible()&&state.started&&!state.over&&!raf){last=0;lastPaint=0;raf=requestAnimationFrame(tick)}}
window.orbitzAsteroidsActivate=()=>{canvas.hidden=!active();help.hidden=!active();stop();draw();ensure()};
function start(){if(state.over)state=createState(layout.width,layout.height);if(!state.started){state.started=true;window.orbitzGameSound?.('asteroids_start')}ensure()}
const keys={arrowleft:'left',a:'left',arrowright:'right',d:'right',arrowup:'thrust',w:'thrust',' ':'fire'};
document.addEventListener('keydown',event=>{if(!visible()||['INPUT','TEXTAREA','SELECT'].includes(event.target?.tagName)||event.target?.isContentEditable||event.shiftKey||event.ctrlKey||event.altKey||event.metaKey)return;const action=keys[event.key.toLowerCase()];if(!action)return;event.preventDefault();event.stopImmediatePropagation();if(state.over&&event.repeat)return;window.orbitzUnlockGameAudio?.();start();input[action]=true},true);
document.addEventListener('keyup',event=>{const action=keys[event.key.toLowerCase()];if(action)input[action]=false});
let pointer=null;canvas.addEventListener('pointerdown',event=>{if(!visible()||event.button!==0)return;pointer=event.pointerId;canvas.setPointerCapture(pointer);canvas.focus();window.orbitzUnlockGameAudio?.();start();input.fire=true;input.thrust=true});canvas.addEventListener('pointermove',event=>{if(pointer!==event.pointerId||!visible())return;state.ship.angle=Math.atan2((event.clientY-canvas.getBoundingClientRect().top-40)/layout.scale-state.ship.y,(event.clientX-canvas.getBoundingClientRect().left-12)/layout.scale-state.ship.x)});function release(event){if(pointer===event.pointerId){pointer=null;input.fire=input.thrust=false}}canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
new ResizeObserver(()=>draw()).observe(panel);new MutationObserver(()=>{if(!visible())stop();else ensure()}).observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','class']});window.addEventListener('blur',()=>{blurred=true;stop()});window.addEventListener('focus',()=>{blurred=false;ensure()});document.addEventListener('visibilitychange',()=>{if(!visible())stop();else ensure()});window.addEventListener('pagehide',()=>{saveRecord();stop()});
const language=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{language?.();help.textContent=uiTr('youtube.asteroids_help');canvas.setAttribute('aria-label',uiTr('youtube.asteroids_label'));draw()};window.orbitzRunnerLanguageChanged();api('asteroids-score',{}).then(data=>{if(Number.isSafeInteger(data.best)&&data.best>=0)best=Math.max(best,data.best);draw()}).catch(()=>{});
})();
