const assert=require('assert');
const {createState,step,viewportLayout,resizeState,W,H,DT}=require('../app/invaders.js');
const fresh=()=>{const s=createState();s.started=true;return s};
let s=createState();assert.equal(s.enemies.length,45);assert(s.bunkers.length>100);step(s,{fire:true},.1);assert.equal(s.time,0,'idle has no simulation');
s=fresh();step(s,{left:true},.1);assert(s.player.x<W/2);assert(s.player.x>W/2-35);s.player.x=24;step(s,{left:true},.1);assert.equal(s.player.x,24);
s=fresh();step(s,{fire:true},DT);assert.equal(s.bullets.length,1);assert(s.events.includes('invaders_shot'));step(s,{fire:true},.1);assert.equal(s.bullets.length,1,'cooldown prevents excessive firing');
s=fresh();s.player.double=5;step(s,{fire:true},DT);assert.equal(s.bullets.length,2);
s=fresh();s.enemies=[{x:400,y:200,w:30,h:24,row:0,col:0}];s.bullets=[{x:400,y:210,w:4,h:12}];step(s,{},DT);assert.equal(s.enemies.length,0);assert(s.score>=50);assert(s.waveWait>0);assert(s.events.includes('invaders_win'));for(let i=0;i<21;i++)step(s,{},.1);assert.equal(s.level,2);assert.equal(s.enemies.length,45);
s=fresh();const block=s.bunkers[0];s.bullets=[{x:block.x,y:block.y+4,w:4,h:12}];const count=s.bunkers.length;step(s,{},DT);assert(s.bunkers.length<count,'bunkers are destructible');
s=fresh();s.player.invulnerable=0;s.enemyBullets=[{x:s.player.x,y:s.player.y-5,w:5,h:13}];step(s,{},DT);assert.equal(s.lives,2);assert(s.player.invulnerable>0);
s=fresh();s.player.invulnerable=0;s.player.shield=true;s.enemyBullets=[{x:s.player.x,y:s.player.y-5,w:5,h:13}];step(s,{},DT);assert.equal(s.lives,3);assert(!s.player.shield);
s=fresh();s.drops=[{x:s.player.x,y:s.player.y,w:18,h:18,type:'double'}];step(s,{},DT);assert(s.player.double>10);assert(s.events.includes('invaders_power'));
s=fresh();s.enemies=[{x:100,y:s.player.y,w:30,h:24,row:0,col:0}];step(s,{},DT);assert(s.over);assert.equal(s.lives,0);
s=fresh();s.enemies[0].x=W-22;const y=s.enemies[0].y;step(s,{},DT);assert(s.enemies[0].y>y&&s.enemies[0].y<y+2,'descent is animated, not a tile jump');
s=fresh();s.ufo={x:400,y:43,w:42,h:18};s.bullets=[{x:400,y:52,w:4,h:12}];step(s,{},DT);assert.equal(s.ufo,null);assert.equal(s.score,150);
console.log('OK: invaders movement, firing/cooldown, waves, bunkers, power-ups, lives, invasion, UFO and continuous descent.');

for(const [w,h] of [[360,220],[700,450],[1920,1080],[2560,480],[480,1000]]){
 const view=viewportLayout(w,h);
 assert(Math.abs(view.x+view.width*view.scale-(w-12))<1e-7,'fills available width');
 assert(Math.abs(view.y+view.height*view.scale-(h-40))<1e-7,'fills available height');
 assert(view.height>=360-1e-6&&view.width>=W-1e-6,'playable world bounds');
 const game=fresh();game.score=123;game.bunkers.splice(0,10);const remaining=game.bunkers.length;
 resizeState(game,view.width,view.height);assert.equal(game.bunkers.length,remaining);assert.equal(game.score,123);assert.equal(game.lives,3);
 assert.equal(game.player.y,view.height-36);assert(game.player.x>=24&&game.player.x<=view.width-24);
 for(const block of game.bunkers)assert(block.x>0&&block.x<view.width&&block.y<game.player.y);
}
s=fresh();s.enemies=[{x:200,y:s.player.y-40,w:30,h:24,row:0,col:0}];resizeState(s,1600,360);step(s,{},DT);assert(!s.over,'resize does not turn a safe approach into invasion');
console.log('OK: responsive landscape/portrait/ultrawide layout, full-area coverage, persistent damage/score and safe resize.');
