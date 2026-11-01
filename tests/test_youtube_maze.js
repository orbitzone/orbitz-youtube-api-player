const assert=require('assert');
const {MAP,walkable,distanceMap,createState,step,requestDirection,PLAYER_SPEED}=require('../app/maze.js');
assert(MAP.every(row=>row.length===19));
const s=createState(),distances=distanceMap(s.player);
for(const position of s.dots.keys())assert(distances.has(position),'all dots are reachable: '+position);
for(const ghost of s.ghosts)assert(walkable(ghost.x,ghost.y));
s.player={x:1,y:1,dir:3};s.wanted=3;step(s);assert.equal(s.player.x,1,'walls block movement');assert.equal(s.score,50);assert(s.power>0);
s.player={x:1,y:3,dir:0};s.wanted=0;step(s);assert.equal(s.player.x,2);assert.equal(s.score,70);
const hit=createState();hit.grace=0;hit.player={x:8,y:7,dir:3};hit.wanted=3;hit.ghosts=[{x:8,y:7,dir:0}];step(hit);assert.equal(hit.lives,2,'contact loses one life and resets actors');
const powered=createState();powered.power=3;powered.player={x:1,y:1,dir:2};powered.wanted=2;powered.ghosts=[{x:1,y:1,dir:0}];step(powered);assert(powered.score>=200);assert.equal(powered.lives,3);
const won=createState();won.dots.clear();step(won);assert(won.won);const score=won.score;step(won);assert.equal(won.score,score);
console.log('OK: maze reachability, walls, dots, power, ghost contacts, lives and win state.');

const near=(a,b)=>assert(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const moving=createState();moving.ghosts=[];
step(moving,.07);near(moving.player.x,8.5);near(moving.player.y,15);
requestDirection(moving,0);assert.equal(moving.player.dir,0,'reverse immediately between centers');
step(moving,.035);near(moving.player.x,8.75);near(moving.player.y,15);
step(moving,.035);near(moving.player.x,9);
const turn=createState();turn.ghosts=[];step(turn,.07);requestDirection(turn,3);
near(turn.player.x,8.5);near(turn.player.y,15);
step(turn,.07);near(turn.player.x,8);near(turn.player.y,15);
step(turn,.07);near(turn.player.x,8);near(turn.player.y,14.5);
const blocked=createState();blocked.ghosts=[];requestDirection(blocked,3);
step(blocked,.035);assert(blocked.player.x<9,'invalid buffered turn does not stop forward travel');near(blocked.player.y,15);
const whole=createState(),slices=createState();whole.ghosts=[];slices.ghosts=[];
step(whole,.14);for(let i=0;i<14;i++)step(slices,.01);
near(whole.player.x,slices.player.x);near(whole.player.y,slices.player.y);assert.equal(whole.score,slices.score);
const terminal=createState();terminal.grace=0;terminal.lives=1;terminal.ghosts=[{...terminal.player}];step(terminal,.008);assert(terminal.over);assert.equal(terminal.lives,0);
console.log('OK: fractional movement, instant reversal, buffered center turns, wall rejection, time independence and final life.');

assert(s.soundEvents.includes('maze_power'));assert(s.soundEvents.some(name=>name.startsWith('maze_chomp')));assert(powered.soundEvents.includes('maze_ghost'));assert(terminal.soundEvents.includes('maze_death'));assert(won.soundEvents.includes('maze_win'));

for(const row of [1,15])for(const direction of [0,2]){
 const portal=createState();portal.ghosts=[];portal.player={x:direction===0?18:0,y:row,dir:direction,tx:null,ty:null};portal.wanted=direction;
 step(portal,.07);assert(direction===0?portal.player.x>18:portal.player.x<0,'continuous exit');
 step(portal,.07);near(portal.player.x,direction===0?0:18);near(portal.player.y,row);
}
const reverse=createState();reverse.ghosts=[];reverse.player={x:0,y:1,dir:2,tx:null,ty:null};reverse.wanted=2;step(reverse,.07);requestDirection(reverse,0);step(reverse,.07);near(reverse.player.x,0);
const fruit=createState();fruit.ghosts=[];fruit.player={x:1,y:3,dir:2,tx:null,ty:null};fruit.wanted=2;fruit.cherryWait=.001;step(fruit,.02);assert(fruit.cherry&&fruit.cherry.remaining<=8);fruit.player={x:9,y:9,dir:3,tx:null,ty:null};fruit.wanted=3;const beforeFruit=fruit.score;step(fruit,.01);assert.equal(fruit.cherry,null);assert(fruit.score>=beforeFruit+100);assert(fruit.soundEvents.includes('maze_cherry'));
const expired=createState();expired.ghosts=[];expired.cherry={x:9,y:9,remaining:.001};step(expired,.02);assert.equal(expired.cherry,null);
const next=createState();next.ghosts=[];next.score=500;next.lives=2;next.dots.clear();step(next,.01);assert(next.won);for(let i=0;i<9;i++)step(next,.25);assert.equal(next.level,2);assert.equal(next.lives,2);assert(next.score>=500);assert(next.dots.size>0);assert(!next.won);assert.notDeepEqual(next.map,MAP);
for(const level of [1,2,3,10]){const levelState=createState(level),paths=distanceMap(levelState.player,levelState.map);for(const position of levelState.dots.keys())assert(paths.has(position),'level dots reachable '+level)}
console.log('OK: four portal entrances, smooth traversal/reversal, cherry spawn/expiry/bonus and progressive levels preserving lives and score.');
