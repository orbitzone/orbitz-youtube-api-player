/* Original space-defense arcade game. Fixed-step simulation, local canvas graphics. */
(()=>{
'use strict';
const W=896,H=504,DT=1/120;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const overlap=(a,b)=>Math.abs(a.x-b.x)<((a.w||4)+(b.w||4))/2&&Math.abs(a.y-b.y)<((a.h||12)+(b.h||12))/2;
function random(s){s.seed=(Math.imul(s.seed,1664525)+1013904223)>>>0;return s.seed/4294967296}
function event(s,name){if(s.events.length<20)s.events.push(name)}
function shields(width=W,height=H){const result=[];for(let group=0;group<4;group++)for(let row=0;row<5;row++)for(let col=0;col<9;col++){if((row===0&&(col<2||col>6))||(row>=3&&col>=3&&col<=5))continue;result.push({group,row,col,x:(group+1)*width/5+(col-4)*6,y:height-112+row*6,w:6,h:6})}return result}
function viewportLayout(width,height){const availableWidth=Math.max(1,width-24),availableHeight=Math.max(1,height-80),scale=Math.max(.001,Math.min(availableWidth/W,availableHeight/360));return{scale,x:12,y:40,width:availableWidth/scale,height:availableHeight/scale}}
function resizeState(s,width,height){
 if(s.width===width&&s.height===height)return;
 const sx=width/s.width,sy=(height-60)/(s.height-60);
 for(const objects of [s.enemies,s.bullets,s.enemyBullets,s.drops,s.particles])for(const object of objects){object.x*=sx;object.y*=sy}
 if(s.ufo){s.ufo.x*=sx;s.ufo.y*=sy}
 s.player.x=clamp(s.player.x*sx,24,width-24);s.player.y=height-36;
 for(const block of s.bunkers){block.x=(block.group+1)*width/5+(block.col-4)*6;block.y=height-112+block.row*6}
 s.width=width;s.height=height;
}
function wave(s){s.enemies=[];for(let row=0;row<5;row++)for(let col=0;col<9;col++)s.enemies.push({x:s.width/2-232+col*58,y:Math.min(90,s.height*.15)+row*Math.min(38,(s.height-200)/5),w:30,h:24,row,col});s.direction=1;s.descent=0;s.fireWait=1.1;s.waveWait=0;s.bullets=[];s.enemyBullets=[];s.drops=[];s.ufo=null;s.ufoWait=9;s.player.invulnerable=1.5}
function createState(){const s={width:W,height:H,seed:314159,time:0,score:0,lives:3,level:1,kills:0,started:false,over:false,events:[],particles:[],bunkers:shields(),direction:1,fireWait:1,ufoWait:9,waveWait:0,player:{x:W/2,y:468,w:30,h:22,cooldown:0,invulnerable:1.5,double:0,shield:false}};wave(s);return s}
function burst(s,x,y,color){for(let i=0;i<12;i++){const angle=random(s)*Math.PI*2,speed=40+random(s)*120;s.particles.push({x,y,vx:Math.cos(angle)*speed,vy:Math.sin(angle)*speed,life:.4,color})}s.particles=s.particles.slice(-96)}
function loseLife(s){if(s.player.invulnerable>0||s.over)return;if(s.player.shield){s.player.shield=false;s.player.invulnerable=1;event(s,'invaders_power');return}s.lives--;burst(s,s.player.x,s.player.y,'#79e5ff');event(s,'invaders_death');if(s.lives<=0){s.over=true;return}s.player.x=s.width/2;s.player.invulnerable=2;s.enemyBullets=[];s.player.double=0}
function bunkerHit(s,bullet){const target=s.bunkers.find(block=>overlap(block,bullet));if(!target)return false;s.bunkers=s.bunkers.filter(block=>Math.hypot(block.x-target.x,block.y-target.y)>9);return true}
function simulate(s,input,dt){
 if(!s.started||s.over)return;
 s.time+=dt;const p=s.player;p.invulnerable=Math.max(0,p.invulnerable-dt);p.double=Math.max(0,p.double-dt);p.cooldown=Math.max(0,p.cooldown-dt);
 p.x=clamp(p.x+(Number(!!input.right)-Number(!!input.left))*340*dt,24,s.width-24);
 if(Number.isFinite(input.pointerX))p.x=clamp(input.pointerX,24,s.width-24);
 if(input.fire&&p.cooldown<=0&&s.waveWait<=0){const offsets=p.double>0?[-9,9]:[0];for(const offset of offsets)s.bullets.push({x:p.x+offset,y:p.y-18,w:4,h:12});p.cooldown=p.double>0?.16:.23;event(s,'invaders_shot')}
 for(const particle of s.particles){particle.x+=particle.vx*dt;particle.y+=particle.vy*dt;particle.life-=dt}s.particles=s.particles.filter(particle=>particle.life>0);
 if(s.waveWait>0){s.waveWait-=dt;if(s.waveWait<=0){s.level++;if(s.level%3===1)s.bunkers=shields(s.width,s.height);wave(s)}return}
 if(s.enemies.length){
  const speed=22+Math.min(65,s.level*5)+(45-s.enemies.length)*1.35,dx=s.direction*speed*dt;
  const edge=s.descent<=0&&s.enemies.some(e=>e.x+dx<22||e.x+dx>s.width-22);
  if(edge){s.direction*=-1;s.descent=17}
  const down=Math.min(s.descent,95*dt);s.descent-=down;
  for(const enemy of s.enemies){if(down>0)enemy.y+=down;else enemy.x+=dx}
  s.bunkers=s.bunkers.filter(block=>!s.enemies.some(enemy=>overlap(block,enemy)));
  if(s.enemies.some(enemy=>enemy.y+12>=p.y-12)){s.lives=0;s.over=true;event(s,'invaders_death');return}
  s.fireWait-=dt;if(s.fireWait<=0){
   const columns=[...new Set(s.enemies.map(e=>e.col))],column=columns[Math.floor(random(s)*columns.length)],enemy=s.enemies.filter(e=>e.col===column).reduce((a,b)=>a.y>b.y?a:b);
   s.enemyBullets.push({x:enemy.x,y:enemy.y+16,w:5,h:13,vx:s.level>=4?clamp((p.x-enemy.x)*.12,-35,35):0});
   s.fireWait=Math.max(.23,1.1-s.level*.065)*( .75+random(s)*.5 );
  }
 }
 s.ufoWait-=dt;if(!s.ufo&&s.ufoWait<=0){s.ufo={x:-35,y:43,w:42,h:18};s.ufoWait=14+random(s)*7;event(s,'invaders_ufo')}
 if(s.ufo){s.ufo.x+=105*dt;if(s.ufo.x>s.width+35)s.ufo=null}
 for(const bullet of s.bullets){
  bullet.y-=610*dt;if(bullet.dead||bullet.y<0)continue;
  if(bunkerHit(s,bullet)){bullet.dead=true;continue}
  if(s.ufo&&overlap(bullet,s.ufo)){s.score+=150;burst(s,s.ufo.x,s.ufo.y,'#ff9ddb');s.ufo=null;bullet.dead=true;event(s,'invaders_hit');continue}
  const index=s.enemies.findIndex(enemy=>overlap(enemy,bullet));
  if(index>=0){const enemy=s.enemies[index];s.score+=(5-enemy.row)*10;s.kills++;burst(s,enemy.x,enemy.y,['#ff9ad6','#bca2ff','#7fe5df'][enemy.row%3]);s.enemies.splice(index,1);bullet.dead=true;event(s,'invaders_hit');if(s.kills%8===0)s.drops.push({x:enemy.x,y:enemy.y,w:18,h:18,type:s.kills%16===0?'shield':'double'})}
 }
 s.bullets=s.bullets.filter(b=>!b.dead&&b.y>-15).slice(-16);
 for(const bullet of s.enemyBullets){bullet.y+=(195+Math.min(150,s.level*13))*dt;bullet.x+=(bullet.vx||0)*dt;if(bunkerHit(s,bullet))bullet.dead=true;else if(overlap(bullet,p)){bullet.dead=true;loseLife(s)}}
 s.enemyBullets=s.enemyBullets.filter(b=>!b.dead&&b.y<s.height+15).slice(-24);
 for(const drop of s.drops){drop.y+=100*dt;if(overlap(drop,p)){if(drop.type==='shield')p.shield=true;else p.double=11;drop.dead=true;s.score+=25;event(s,'invaders_power')}}s.drops=s.drops.filter(d=>!d.dead&&d.y<s.height);
 if(!s.enemies.length&&!s.over){s.score+=s.level*200;s.waveWait=2;s.enemyBullets=[];s.bullets=[];event(s,'invaders_win')}
 s.score=Math.min(2147483647,s.score);
}
function step(s,input={},dt=DT){if(!Number.isFinite(dt)||dt<=0)return;let remaining=Math.min(.1,dt);while(remaining>1e-9){const slice=Math.min(DT,remaining);simulate(s,input,slice);remaining-=slice;if(s.over)break}}
if(typeof module!=='undefined'&&module.exports){module.exports={createState,step,overlap,shields,viewportLayout,resizeState,W,H,DT};return}
const panel=$('runner'),canvas=document.createElement('canvas');canvas.id='invaders-canvas';canvas.tabIndex=0;canvas.hidden=true;canvas.setAttribute('role','img');panel.append(canvas);
const help=document.createElement('div');help.id='invaders-help';help.hidden=true;panel.append(help);
const live=document.createElement('div');live.className='sr-only';live.setAttribute('role','status');live.setAttribute('aria-live','polite');panel.append(live);
const style=document.createElement('style');style.textContent='#invaders-canvas{position:absolute;inset:0;width:100%;height:100%;outline:none;touch-action:none}#invaders-canvas[hidden],#invaders-help[hidden]{display:none}#invaders-help{position:absolute;left:12px;bottom:10px;font-size:12px;color:#dceaff;pointer-events:none}@media(max-width:500px){#invaders-help{max-width:65%;font-size:10px}}';document.head.append(style);
const ctx=canvas.getContext('2d'),input={left:false,right:false,fire:false};let state=createState(),best=0,raf=0,last=0,accumulator=0,lastPaint=0,blurred=false,layout={scale:1,x:0,y:0},lastRecord=0;
const sprites=[['00111100','01111110','11011011','11111111','00100100','01011010'],['00100100','01111110','11111111','11011011','11111111','01000010'],['00011000','00111100','01111110','11011011','11111111','10100101']].map((rows,index)=>[0,1].map(frame=>{const c=document.createElement('canvas');c.width=32;c.height=24;const g=c.getContext('2d');g.fillStyle=['#ff9ad6','#bca2ff','#7fe5df'][index];rows.forEach((line,y)=>[...line].forEach((pixel,x)=>{if(pixel==='1')g.fillRect((y===5&&frame?7-x:x)*4,y*4,4,4)}));return c}));
const stars=Array.from({length:65},(_,i)=>({x:(i*173.3)%W,y:(i*97.7)%H,r:i%4===0?1.5:.7}));
function active(){return window.orbitzGameMode==='invaders'}
function visible(){return !window.orbitzGamesHome&&active()&&!window.orbitzGamePaused?.()&&!blurred&&!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&$('settings-menu').hidden&&!window.orbitzFeaturesOpen?.()&&document.visibilityState==='visible'}
function clearInput(){input.left=input.right=input.fire=false;delete input.pointerX}
function stop(){cancelAnimationFrame(raf);raf=0;last=0;accumulator=0;clearInput()}
function saveRecord(){if(state.score<=best||state.score===lastRecord)return;lastRecord=state.score;best=state.score;api('invaders-score',{score:best}).then(data=>{if(Number.isSafeInteger(data.best))best=Math.max(best,data.best)}).catch(()=>{})}
function renderInvadersScene(ctx,state,width,height,dpr,layout,showHud=true){
ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#080d18';ctx.fillRect(0,0,width,height);ctx.save();ctx.translate(layout.x,layout.y);ctx.scale(layout.scale,layout.scale);
 for(const star of stars){ctx.fillStyle=star.r>1?'#7894c1':'#3b4c6c';ctx.fillRect(star.x/W*state.width,star.y/H*state.height,star.r,star.r)}
 for(const block of state.bunkers){ctx.fillStyle='#65cc9a';ctx.fillRect(block.x-3,block.y-3,5.6,5.6)}
 for(const enemy of state.enemies)ctx.drawImage(sprites[enemy.row%3][Math.floor(state.time*3)%2],enemy.x-16,enemy.y-12);
 if(state.ufo){const u=state.ufo;ctx.fillStyle='#ff9ad6';ctx.beginPath();ctx.ellipse(u.x,u.y,23,7,0,0,Math.PI*2);ctx.fill();ctx.fillStyle='#c3edff';ctx.beginPath();ctx.arc(u.x,u.y-4,10,Math.PI,0);ctx.fill()}
 for(const bullet of state.bullets){ctx.fillStyle='#c8fbff';ctx.fillRect(bullet.x-2,bullet.y-7,4,14)}
 for(const bullet of state.enemyBullets){ctx.fillStyle='#ffb477';ctx.fillRect(bullet.x-2,bullet.y-7,4,14)}
 for(const drop of state.drops){ctx.strokeStyle=drop.type==='shield'?'#7fdcff':'#ffe681';ctx.lineWidth=2;ctx.strokeRect(drop.x-10,drop.y-10,20,20);ctx.fillStyle=ctx.strokeStyle;ctx.font='bold 15px monospace';ctx.textAlign='center';ctx.fillText(drop.type==='shield'?'S':'Ⅱ',drop.x,drop.y+5)}
 const p=state.player;if(!state.over&&(p.invulnerable<=0||Math.floor(state.time*12)%2===0)){ctx.fillStyle='#a8f1ff';ctx.beginPath();ctx.moveTo(p.x,p.y-18);ctx.lineTo(p.x+17,p.y+11);ctx.lineTo(p.x,p.y+5);ctx.lineTo(p.x-17,p.y+11);ctx.closePath();ctx.fill();ctx.fillStyle='#ffcb65';ctx.fillRect(p.x-4,p.y+10,8,4+Math.sin(state.time*35)*2);if(p.shield){ctx.strokeStyle='#72deff';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,25,0,Math.PI*2);ctx.stroke()}}
 for(const particle of state.particles){ctx.globalAlpha=Math.max(0,particle.life/.4);ctx.fillStyle=particle.color;ctx.fillRect(particle.x-2,particle.y-2,4,4)}ctx.globalAlpha=1;
 ctx.restore();if(showHud){ctx.textAlign='right';ctx.font='bold 12px system-ui';ctx.fillStyle='#e5f1ff';ctx.fillText(uiTr('youtube.invaders_score',{score:state.score,best,lives:state.lives,wave:state.level}),width-12,25);
 if(!state.started||state.over||state.waveWait>0){ctx.fillStyle='#080d18dc';ctx.fillRect(0,height/2-32,width,64);ctx.fillStyle='#bcecff';ctx.textAlign='center';ctx.font='bold 17px system-ui';ctx.fillText(uiTr(state.over?'youtube.invaders_over':state.waveWait>0?'youtube.invaders_wave':'youtube.invaders_start'),width/2,height/2+5)}
}
}
function draw(){
 if(window.orbitzGamesHome||!active()||panel.hidden)return;const rect=panel.getBoundingClientRect();if(!rect.width||!rect.height)return;
 const dpr=Math.min(devicePixelRatio||1,2),width=rect.width,height=rect.height;
 if(canvas.width!==Math.round(width*dpr)||canvas.height!==Math.round(height*dpr)){canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr)}
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#080d18';ctx.fillRect(0,0,width,height);
 layout=viewportLayout(width,height);const {scale}=layout;if(Number.isFinite(input.pointerX))input.pointerX*=layout.width/state.width;resizeState(state,layout.width,layout.height);
 renderInvadersScene(ctx,state,width,height,dpr,layout);
}
window.orbitzGamePreviews.invaders=target=>{const {width,height}=window.orbitzPreviewSize(target);const scene=createState();scene.started=true;scene.player.invulnerable=0;const scale=Math.min((width-24)/W,(height-20)/360),view={scale,x:12,y:10,width:(width-24)/scale,height:(height-20)/scale};resizeState(scene,view.width,view.height);scene.enemies=scene.enemies.filter(enemy=>Math.abs(view.x+enemy.x*scale-width/2)>180+16*scale||Math.abs(view.y+enemy.y*scale-height/2)>30+12*scale);renderInvadersScene(target.getContext('2d'),scene,width,height,1,view,false)};
function tick(now){raf=0;if(!visible()||!state.started||state.over)return;if(last)accumulator+=Math.min(.1,(now-last)/1000);last=now;
 while(accumulator>=DT){step(state,input,DT);accumulator-=DT;if(state.over)break}
 for(const name of state.events.splice(0))window.orbitzGameSound?.(name);
 if(!lastPaint||now-lastPaint>=1000/60-1){draw();lastPaint=now}
 if(state.over){saveRecord();live.textContent=uiTr('youtube.invaders_over');draw();return}raf=requestAnimationFrame(tick);
}
function ensure(){if(visible()&&state.started&&!state.over&&!raf){last=0;lastPaint=0;raf=requestAnimationFrame(tick)}}
window.orbitzInvadersActivate=()=>{canvas.hidden=!active();help.hidden=!active();stop();draw();ensure()};
function start(){if(state.over){state=createState();resizeState(state,layout.width||W,layout.height||H);}if(!state.started){state.started=true;window.orbitzGameSound?.('invaders_start')}ensure()}
function editable(target){return ['INPUT','TEXTAREA','SELECT'].includes(target?.tagName)||target?.isContentEditable}
document.addEventListener('keydown',event=>{if(!visible()||editable(event.target)||event.shiftKey||event.ctrlKey||event.altKey||event.metaKey)return;const key=event.key.toLowerCase();if(!['arrowleft','arrowright','a','d',' '].includes(key))return;event.preventDefault();event.stopImmediatePropagation();if(state.over&&event.repeat)return;window.orbitzUnlockGameAudio?.();start();if(['arrowleft','a'].includes(key))input.left=true;if(['arrowright','d'].includes(key))input.right=true;if(key===' ')input.fire=true},true);
document.addEventListener('keyup',event=>{const key=event.key.toLowerCase();if(['arrowleft','a'].includes(key))input.left=false;if(['arrowright','d'].includes(key))input.right=false;if(key===' ')input.fire=false});
let pointer=null;canvas.addEventListener('pointerdown',event=>{if(!visible()||event.button!==0)return;pointer=event.pointerId;canvas.setPointerCapture(pointer);canvas.focus();window.orbitzUnlockGameAudio?.();start();input.fire=true});canvas.addEventListener('pointermove',event=>{if(pointer!==event.pointerId||!visible())return;input.pointerX=(event.clientX-canvas.getBoundingClientRect().left-layout.x)/layout.scale});function release(event){if(pointer!==event.pointerId)return;pointer=null;clearInput()}canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',release);
new ResizeObserver(()=>draw()).observe(panel);new MutationObserver(()=>{if(!visible())stop();else ensure()}).observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','class']});
window.addEventListener('blur',()=>{blurred=true;stop()});window.addEventListener('focus',()=>{blurred=false;ensure()});document.addEventListener('visibilitychange',()=>{if(!visible())stop();else ensure()});window.addEventListener('pagehide',()=>{saveRecord();stop()});
const oldLanguage=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{oldLanguage?.();help.textContent=uiTr('youtube.invaders_help');canvas.setAttribute('aria-label',uiTr('youtube.invaders_label'));draw()};window.orbitzRunnerLanguageChanged();api('invaders-score',{}).then(data=>{if(Number.isSafeInteger(data.best)&&data.best>=0)best=Math.max(best,data.best);draw()}).catch(()=>{});
})();
