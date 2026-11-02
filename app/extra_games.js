/* Two original arcade games, sharing UI/rendering infrastructure, never simulation. */
(()=>{
'use strict';
const DT=1/120,clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function emit(s,name){if(s.events.length<24)s.events.push(s.game+'_'+name)}
function brick(s,id){const col=id%10,row=Math.floor(id/10),w=(s.width-72)/10;return{id,x:36+(col+.5)*w,y:66+row*28,w:w-5,h:20,hp:row<2?2:1,row}}
function serve(s){s.balls=[{x:s.paddle.x,y:s.height-59,vx:185,vy:-270}];s.launched=false;s.shots=[]}
function createBreaker(width=900,height=540){const s={game:'breaker',width,height,score:0,lives:3,level:1,time:0,started:false,over:false,events:[],bricks:[],balls:[],shots:[],drops:[],kills:0,wait:0,wide:0,laser:0,fire:0,paddle:{x:width/2,w:110}};s.bricks=Array.from({length:50},(_,i)=>brick(s,i));serve(s);return s}
function power(s,type){if(type==='wide')s.wide=12;else if(type==='laser')s.laser=12;else for(const b of [...s.balls]){if(s.balls.length>=6)break;const speed=Math.hypot(b.vx,b.vy);s.balls.push({...b,vx:-b.vx||140,vy:-Math.sqrt(Math.max(10000,speed*speed-b.vx*b.vx))})}emit(s,'power')}
function damage(s,b){b.hp--;s.score+=10;if(b.hp<=0){s.bricks=s.bricks.filter(v=>v!==b);s.score+=20;s.kills++;if(s.kills%7===0)s.drops.push({x:b.x,y:b.y,type:['wide','multi','laser'][Math.floor(s.kills/7)%3]})}emit(s,'hit')}
function breakerStep(s,input,dt){
 s.wide=Math.max(0,s.wide-dt);s.laser=Math.max(0,s.laser-dt);s.fire=Math.max(0,s.fire-dt);s.paddle.w=s.wide?166:110;
 const p=s.paddle;p.x=clamp(Number.isFinite(input.pointerX)?input.pointerX:p.x+(Number(!!input.right)-Number(!!input.left))*520*dt,p.w/2+8,s.width-p.w/2-8);
 if(s.wait>0){s.wait-=dt;if(s.wait<=0){s.level++;s.bricks=Array.from({length:50},(_,i)=>brick(s,i));s.drops=[];serve(s)}return}
 if(!s.launched){s.balls[0].x=p.x;s.balls[0].y=s.height-59;if(input.fire){s.launched=true;emit(s,'launch')}else return}
 if(s.laser&&input.fire&&s.fire<=0){s.shots.push({x:p.x-35,y:s.height-48},{x:p.x+35,y:s.height-48});s.fire=.24;emit(s,'laser')}
 for(const ball of s.balls){
  const old={x:ball.x,y:ball.y};ball.x+=ball.vx*dt;ball.y+=ball.vy*dt;
  if(ball.x<6){ball.x=6;ball.vx=Math.abs(ball.vx)}if(ball.x>s.width-6){ball.x=s.width-6;ball.vx=-Math.abs(ball.vx)}if(ball.y<32){ball.y=32;ball.vy=Math.abs(ball.vy);emit(s,'bounce')}
  if(ball.vy>0&&old.y+6<=s.height-39&&ball.y+6>=s.height-39&&Math.abs(ball.x-p.x)<=p.w/2+5){const speed=Math.min(520,Math.hypot(ball.vx,ball.vy)+3),offset=clamp((ball.x-p.x)/(p.w/2),-.85,.85);ball.y=s.height-45;ball.vx=speed*offset;ball.vy=-Math.sqrt(speed*speed-ball.vx*ball.vx);emit(s,'bounce')}
  const hit=s.bricks.find(b=>Math.abs(ball.x-b.x)<=b.w/2+6&&Math.abs(ball.y-b.y)<=b.h/2+6);
  if(hit){if(old.y<=hit.y-hit.h/2-5||old.y>=hit.y+hit.h/2+5){ball.vy*=-1;ball.y=hit.y+(ball.vy<0?-1:1)*(hit.h/2+6.1)}else{ball.vx*=-1;ball.x=hit.x+(ball.vx<0?-1:1)*(hit.w/2+6.1)}damage(s,hit)}
 }
 for(const shot of s.shots){shot.y-=650*dt;const hit=s.bricks.find(b=>Math.abs(shot.x-b.x)<b.w/2&&Math.abs(shot.y-b.y)<b.h/2+5);if(hit){damage(s,hit);shot.dead=true}}s.shots=s.shots.filter(v=>!v.dead&&v.y>25).slice(-12);
 for(const drop of s.drops){drop.y+=125*dt;if(drop.y>=s.height-52&&drop.y<=s.height-25&&Math.abs(drop.x-p.x)<p.w/2+10){power(s,drop.type);drop.dead=true}}s.drops=s.drops.filter(d=>!d.dead&&d.y<s.height).slice(-16);
 s.balls=s.balls.filter(b=>b.y<s.height+10);
 if(!s.balls.length){s.lives--;emit(s,'death');if(!s.lives)s.over=true;else{s.wide=s.laser=0;serve(s)}}
 if(!s.over&&!s.bricks.length){s.score+=200*s.level;s.wait=2;emit(s,'win')}
}
function pad(s){return{x:s.width*.72,y:s.height-55,w:Math.max(70,140-s.level*8)}}
function terrain(s){const p=pad(s);return[{x:0,y:s.height-25},{x:s.width*.14,y:s.height-85},{x:s.width*.29,y:s.height-39},{x:s.width*.43,y:s.height-110},{x:p.x-p.w/2-25,y:s.height-30},{x:p.x-p.w/2,y:p.y},{x:p.x+p.w/2,y:p.y},{x:p.x+p.w/2+30,y:s.height-26},{x:s.width,y:s.height-75}].sort((a,b)=>a.x-b.x)}
function ground(s,x){const points=terrain(s);for(let i=1;i<points.length;i++)if(x<=points[i].x){const a=points[i-1],b=points[i];return a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x)}return points.at(-1).y}
function ceiling(s,x){if(s.level<3||x<s.width*.34||x>s.width*.61)return 0;return 90+Math.sin((x/s.width-.34)/.27*Math.PI)*65}
function launchLander(s){s.explosion=null;s.ship={x:s.width*.18,y:55,vx:18,vy:0,angle:0,fuel:100};s.engine=0;s.wait=0;s.landed=false}
function createLander(width=900,height=540){const s={game:'lander',width,height,score:0,lives:3,level:1,time:0,started:false,over:false,events:[],ship:null,engine:0,wait:0,landed:false};launchLander(s);return s}
function landerStep(s,input,dt){
 if(s.explosion){s.explosion.age+=dt;for(const p of s.explosion.particles){p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=38*dt;p.angle+=p.spin*dt}}
 if(s.wait>0){s.wait-=dt;if(s.wait<=0){if(s.landed)s.level++;launchLander(s)}return}
 const p=s.ship;s.engine=Math.max(0,s.engine-dt);
 let thrust=input.thrust?1:0;
 if(Number.isFinite(input.pointerX)&&Number.isFinite(input.pointerY)){
  // Position/velocity feedback keeps inertia and brakes before reaching the cursor.
  const tx=clamp(input.pointerX,22,s.width-22),ty=clamp(input.pointerY,20,ground(s,tx)-11);
  const ax=clamp((tx-p.x)*.65-p.vx*1.7,-52,52),ay=clamp((ty-p.y)*.65-p.vy*1.8,-60,25);
  const target=clamp(Math.atan2(ax,28-ay),-.8,.8);
  p.angle+=clamp(target-p.angle,-1.8*dt,1.8*dt);
  thrust=input.thrust?clamp(Math.hypot(ax,28-ay)/96,0,1):0;
 }else p.angle=clamp(p.angle+(Number(!!input.right)-Number(!!input.left))*1.2*dt,-.8,.8);
 p.firing=thrust>0&&p.fuel>0;p.vy+=28*dt;
 if(p.firing){p.fuel=Math.max(0,p.fuel-5*thrust*dt);p.vx+=Math.sin(p.angle)*96*thrust*dt;p.vy-=Math.cos(p.angle)*96*thrust*dt;if(s.engine<=0){emit(s,'thrust');s.engine=.22}}
 p.vx+=Math.sin(s.time*.6)*Math.min(3,s.level-1)*dt;p.vx=clamp(p.vx,-125,125);p.vy=clamp(p.vy,-115,160);p.x+=p.vx*dt;p.y+=p.vy*dt;
 if(p.x<14){p.x=14;p.vx=Math.abs(p.vx)*.35}if(p.x>s.width-14){p.x=s.width-14;p.vx=-Math.abs(p.vx)*.35}if(p.y<35){p.y=35;p.vy=Math.max(0,p.vy)}
 const platform=pad(s);if(p.y-33<=ceiling(s,p.x)||p.y+13>=Math.min(ground(s,p.x-11),ground(s,p.x),ground(s,p.x+11))){
  const safe=Math.abs(p.x-platform.x)<=platform.w/2-13&&Math.abs(p.vx)<=22&&Math.abs(p.vy)<=32&&Math.abs(p.angle)<=.18;
  if(safe){s.landed=true;p.y=platform.y-13;s.score+=Math.round(200*s.level+p.fuel*3);emit(s,'land')}else{s.explosion={x:p.x,y:p.y,age:0,particles:Array.from({length:32},(_,i)=>{const a=i*Math.PI*2/32,speed=35+(i*47%125);return{x:p.x,y:p.y,vx:Math.cos(a)*speed+p.vx*.2,vy:Math.sin(a)*speed-30,angle:a,spin:(i%2?1:-1)*(2+i%5),life:.55+(i%7)*.13,size:i%4===0?5:2+i%3,fragment:i%4===0}})};p.firing=false;s.lives--;emit(s,'death');if(!s.lives)s.over=true}
  p.vx=p.vy=0;s.wait=2;
 }
}
function step(s,input={},dt=DT){if(!s.started||!Number.isFinite(dt)||dt<=0)return;if(s.over){if(s.explosion){const t=Math.min(.1,dt);s.explosion.age+=t;for(const p of s.explosion.particles){p.x+=p.vx*t;p.y+=p.vy*t;p.vy+=38*t;p.angle+=p.spin*t}}return;}let left=Math.min(.1,dt);while(left>1e-9&&!s.over){const part=Math.min(DT,left);s.time+=part;(s.game==='breaker'?breakerStep:landerStep)(s,input,part);left-=part}s.score=Math.min(2147483647,s.score)}
function resizeState(s,width,height){if(s.width===width&&s.height===height)return;const sx=width/s.width,sy=height/s.height;if(s.game==='breaker'){s.paddle.x*=sx;for(const list of [s.balls,s.shots,s.drops])for(const o of list){o.x*=sx;o.y*=sy}s.width=width;s.height=height;s.bricks=s.bricks.map(b=>({...brick(s,b.id),hp:b.hp}));if(!s.launched)serve(s)}else{s.ship.x*=sx;s.ship.y*=sy;if(s.explosion){s.explosion.x*=sx;s.explosion.y*=sy;for(const p of s.explosion.particles){p.x*=sx;p.y*=sy;p.vx*=sx;p.vy*=sy}}s.width=width;s.height=height}}
if(typeof module!=='undefined'&&module.exports){module.exports={createBreaker,createLander,step,resizeState,pad,ground,DT};return}
function render(ctx,s,width,height,dpr,view,hud=true){
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#080d18';ctx.fillRect(0,0,width,height);ctx.save();ctx.translate(view.x,view.y);ctx.scale(view.scale,view.scale);
 for(let i=0;i<50;i++){ctx.fillStyle='#536583';ctx.fillRect((i*173.7)%s.width,(i*91.3)%s.height,1,1)}
 if(s.game==='breaker'){
  for(const b of s.bricks){ctx.fillStyle=['#f595c4','#b1a0ef','#7cbbe8','#68d9bc','#e9c576'][b.row];ctx.globalAlpha=b.hp===2?1:.78;ctx.fillRect(b.x-b.w/2,b.y-b.h/2,b.w,b.h)}ctx.globalAlpha=1;
  ctx.fillStyle=s.laser?'#ffb4c4':'#a9eaff';ctx.fillRect(s.paddle.x-s.paddle.w/2,s.height-39,s.paddle.w,10);
  ctx.fillStyle='#fff5ce';for(const b of s.balls){ctx.beginPath();ctx.arc(b.x,b.y,6,0,Math.PI*2);ctx.fill()}ctx.fillStyle='#ffb4d2';for(const shot of s.shots)ctx.fillRect(shot.x-2,shot.y-6,4,12);
  for(const d of s.drops){ctx.strokeStyle='#b8f5d8';ctx.strokeRect(d.x-10,d.y-10,20,20);ctx.font='13px monospace';ctx.textAlign='center';ctx.fillStyle='#b8f5d8';ctx.fillText({wide:'W',multi:'M',laser:'L'}[d.type],d.x,d.y+5)}
 }else{
  const points=terrain(s);ctx.fillStyle='#233044';ctx.strokeStyle='#7a91ac';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,s.height);for(const p of points)ctx.lineTo(p.x,p.y);ctx.lineTo(s.width,s.height);ctx.closePath();ctx.fill();ctx.stroke();if(s.level>=3){ctx.beginPath();ctx.moveTo(s.width*.34,0);ctx.lineTo(s.width*.61,0);for(let i=20;i>=0;i--){const x=s.width*(.34+.27*i/20);ctx.lineTo(x,ceiling(s,x))}ctx.closePath();ctx.fill();ctx.stroke()}const platform=pad(s);ctx.strokeStyle='#93f4bc';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(platform.x-platform.w/2,platform.y);ctx.lineTo(platform.x+platform.w/2,platform.y);ctx.stroke();
  const p=s.ship;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.angle);
  if(!s.explosion){
   // Reusable Falcon-inspired returning booster; feet match the landing plane.
   ctx.lineWidth=1.5;ctx.strokeStyle='#a9b8c9';
   const body=ctx.createLinearGradient(-6,0,6,0);body.addColorStop(0,'#9aa8b8');body.addColorStop(.35,'#ffffff');body.addColorStop(1,'#c0ccd8');
   ctx.fillStyle=body;ctx.beginPath();ctx.moveTo(-6,5);ctx.lineTo(-6,-29);ctx.quadraticCurveTo(-6,-32,-3,-33);ctx.lineTo(3,-33);ctx.quadraticCurveTo(6,-32,6,-29);ctx.lineTo(6,5);ctx.closePath();ctx.fill();ctx.stroke();
   ctx.fillStyle='#202a37';ctx.fillRect(-6,-31,12,5);ctx.fillRect(-6,-4,12,9);
   ctx.strokeStyle='#596d80';ctx.lineWidth=1;for(const y of [-18,-8]){ctx.beginPath();ctx.moveTo(-6,y);ctx.lineTo(6,y);ctx.stroke()}
   // Deployable grid fins and four landing legs, shown in side projection.
   ctx.strokeStyle='#b7c9d8';ctx.strokeRect(-11,-25,5,6);ctx.strokeRect(6,-25,5,6);
   ctx.beginPath();for(const x of [-9,-7,8,10]){ctx.moveTo(x,-25);ctx.lineTo(x,-19)}ctx.stroke();
   ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-5,-3);ctx.lineTo(-15,13);ctx.lineTo(-20,13);ctx.moveTo(5,-3);ctx.lineTo(15,13);ctx.lineTo(20,13);ctx.stroke();
   ctx.lineWidth=1;ctx.strokeStyle='#7b91a6';ctx.beginPath();ctx.moveTo(-5,5);ctx.lineTo(-15,13);ctx.moveTo(5,5);ctx.lineTo(15,13);ctx.stroke();
   ctx.fillStyle='#6e8195';ctx.fillRect(-4,5,8,3);
   if(p.firing&&s.wait<=0){const flame=22+Math.sin(s.time*40)*4;ctx.fillStyle='#ff9d48';ctx.beginPath();ctx.moveTo(-4,8);ctx.lineTo(0,flame);ctx.lineTo(4,8);ctx.fill();ctx.fillStyle='#fff2c5';ctx.beginPath();ctx.moveTo(-2,8);ctx.lineTo(0,flame-6);ctx.lineTo(2,8);ctx.fill()}
  }ctx.restore();
  if(s.explosion){const e=s.explosion;ctx.save();if(e.age<.25){ctx.globalAlpha=1-e.age/.25;ctx.fillStyle='#fff0b0';ctx.beginPath();ctx.arc(e.x,e.y,8+e.age*100,0,Math.PI*2);ctx.fill()}for(const part of e.particles){if(e.age>=part.life)continue;ctx.save();ctx.globalAlpha=1-e.age/part.life;ctx.translate(part.x,part.y);ctx.rotate(part.angle);ctx.fillStyle=part.fragment?'#c9eaff':['#ffca70','#ff874d','#ffe8ad'][Math.round(part.life*10)%3];ctx.fillRect(-part.size/2,-part.size/2,part.size,part.fragment?part.size*.55:part.size);ctx.restore()}ctx.restore()}
  if(hud){ctx.fillStyle=Math.abs(p.vy)<=32&&Math.abs(p.vx)<=22?'#a1edbd':'#ffbc91';ctx.font='14px monospace';ctx.textAlign='left';ctx.fillText(uiTr('youtube.lander_telemetry',{fuel:Math.round(p.fuel),vx:Math.round(p.vx),vy:Math.round(p.vy)}),12,27)}
 }
 ctx.restore();if(!hud)return;ctx.textAlign='right';ctx.fillStyle='#e8f2ff';ctx.font='bold 12px system-ui';ctx.fillText(uiTr('youtube.invaders_score',{best:Math.max(s.score,s.best||0),score:s.score,lives:s.lives,wave:s.level}),width-12,25);
 if(!s.started||s.over||s.wait>0){ctx.fillStyle='#080d18dd';ctx.fillRect(0,height/2-28,width,56);ctx.textAlign='center';ctx.fillStyle='#c3edff';ctx.font='bold 15px system-ui';ctx.fillText(uiTr(s.over?'youtube.invaders_over':s.wait>0?(s.game==='lander'?(s.landed?'youtube.lander_landed':'youtube.lander_crash'):'youtube.invaders_wave'):'youtube.'+s.game+'_start'),width/2,height/2+5)}
}
for(const game of ['breaker','lander']){
 const create=game==='breaker'?createBreaker:createLander,panel=$('runner'),canvas=document.createElement('canvas');canvas.id=game+'-canvas';canvas.hidden=true;canvas.tabIndex=0;canvas.setAttribute('role','img');panel.append(canvas);const help=document.createElement('div');help.id=game+'-help';help.hidden=true;panel.append(help);
 const style=document.createElement('style');style.textContent=`#${game}-canvas{position:absolute;inset:0;width:100%;height:100%;outline:none;touch-action:none}#${game}-canvas[hidden],#${game}-help[hidden]{display:none}#${game}-help{position:absolute;left:12px;bottom:10px;max-width:75%;font-size:11px;color:#dceaff;pointer-events:none}`;document.head.append(style);
 const ctx=canvas.getContext('2d'),input={};let s=create(),raf=0,last=0,acc=0,paint=0,blurred=false,view={scale:1,x:12,y:40,width:900,height:540},best=0,lastRecord=0;
 function active(){return window.orbitzGameMode===game}function visible(){return !window.orbitzGamesHome&&active()&&!window.orbitzGamePaused?.()&&!blurred&&!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&$('settings-menu').hidden&&!window.orbitzFeaturesOpen?.()&&document.visibilityState==='visible'}
 function stop(){cancelAnimationFrame(raf);raf=0;last=0;acc=0;for(const k of Object.keys(input))delete input[k];if(s.game==='lander')s.ship.firing=false}
 function save(){if(s.score<=best||s.score===lastRecord)return;lastRecord=s.score;best=s.score;api(game+'-score',{score:best}).catch(()=>{})}
 function draw(){if(window.orbitzGamesHome||!active()||panel.hidden)return;const r=panel.getBoundingClientRect();if(!r.width||!r.height)return;const dpr=Math.min(devicePixelRatio||1,2);if(canvas.width!==Math.round(r.width*dpr)||canvas.height!==Math.round(r.height*dpr)){canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr)}const scale=Math.max(.01,Math.min((r.width-24)/900,(r.height-80)/400));view={scale,x:12,y:40,width:(r.width-24)/scale,height:(r.height-80)/scale};resizeState(s,view.width,view.height);s.best=best;render(ctx,s,r.width,r.height,dpr,view)}
 function tick(now){raf=0;if(!visible()||!s.started||(s.over&&(!s.explosion||s.explosion.age>=1.5)))return;if(last)acc+=Math.min(.1,(now-last)/1000);last=now;while(acc>=DT){step(s,input,DT);acc-=DT;if(s.over&&!s.explosion)break}for(const name of s.events.splice(0)){window.orbitzGameSound?.(name);if(name.endsWith('_win')||name.endsWith('_land'))save()}if(!paint||now-paint>=1000/60-1){draw();paint=now}if(s.over){save();draw();if(s.explosion&&s.explosion.age<1.5)raf=requestAnimationFrame(tick);return}raf=requestAnimationFrame(tick)}
 function ensure(){if(visible()&&s.started&&(!s.over||(s.explosion&&s.explosion.age<1.5))&&!raf){last=0;paint=0;raf=requestAnimationFrame(tick)}}
 window['orbitz'+(game==='breaker'?'Breaker':'Lander')+'Activate']=()=>{canvas.hidden=!active();help.hidden=!active();stop();draw();ensure()};
 function start(){if(s.over)s=create(view.width,view.height);if(!s.started){s.started=true;window.orbitzGameSound?.(game+'_start')}ensure()}
 const keys={arrowleft:'left',a:'left',arrowright:'right',d:'right',arrowup:'thrust',w:'thrust',' ':'fire'};
 document.addEventListener('keydown',e=>{if(!visible()||['INPUT','SELECT','TEXTAREA'].includes(e.target?.tagName)||e.target?.isContentEditable||e.shiftKey||e.altKey||e.ctrlKey||e.metaKey)return;const action=keys[e.key.toLowerCase()];if(!action)return;e.preventDefault();e.stopImmediatePropagation();if(s.over&&e.repeat)return;window.orbitzUnlockGameAudio?.();start();delete input.pointerX;delete input.pointerY;input[action]=true},true);document.addEventListener('keyup',e=>{if(keys[e.key.toLowerCase()])input[keys[e.key.toLowerCase()]]=false});
 function aim(e){const r=canvas.getBoundingClientRect();input.pointerX=clamp((e.clientX-r.left-view.x)/view.scale,22,s.width-22);if(game==='lander')input.pointerY=clamp((e.clientY-r.top-view.y)/view.scale,20,s.height-13)}
 let pointer=null;canvas.addEventListener('pointerdown',e=>{if(!visible()||e.button!==0)return;pointer=e.pointerId;canvas.setPointerCapture(pointer);canvas.focus();window.orbitzUnlockGameAudio?.();start();aim(e);input[game==='breaker'?'fire':'thrust']=true});canvas.addEventListener('pointermove',e=>{if(visible())aim(e)});function release(e){if(pointer===e.pointerId){pointer=null;input.fire=input.thrust=false}}canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',e=>{release(e);delete input.pointerX;delete input.pointerY});canvas.addEventListener('lostpointercapture',release);canvas.addEventListener('pointerleave',()=>{if(pointer===null){delete input.pointerX;delete input.pointerY}});
 new ResizeObserver(draw).observe(panel);new MutationObserver(()=>{if(!visible())stop();else ensure()}).observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','class']});window.addEventListener('blur',()=>{blurred=true;stop()});window.addEventListener('focus',()=>{blurred=false;ensure()});document.addEventListener('visibilitychange',()=>{if(!visible())stop();else ensure()});window.addEventListener('pagehide',()=>{save();stop()});
 window.orbitzGamePreviews[game]=target=>{const {width,height}=window.orbitzPreviewSize(target),scale=Math.min((width-24)/900,(height-20)/400),v={scale,x:12,y:10,width:(width-24)/scale,height:(height-20)/scale},scene=create(v.width,v.height);render(target.getContext('2d'),scene,width,height,1,v,false)};
 const language=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{language?.();help.textContent=uiTr('youtube.'+game+'_help');canvas.setAttribute('aria-label','Orbit '+(game==='breaker'?'Breaker':'Lander'));draw()};window.orbitzRunnerLanguageChanged();api(game+'-score',{}).then(data=>{if(Number.isSafeInteger(data.best))best=Math.max(best,data.best);draw()}).catch(()=>{});
}
})();
