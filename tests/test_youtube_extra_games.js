const assert=require('assert');const {createBreaker,createLander,step,pad,resizeState,DT}=require('../app/extra_games.js');
let s=createBreaker();step(s,{fire:true},.1);assert.equal(s.time,0);s.started=true;step(s,{fire:true},DT);assert(s.launched);assert(s.balls[0].vy<0);
s=createBreaker();s.started=s.launched=true;s.balls=[{x:20,y:100,vx:-300,vy:0}];step(s,{},.1);assert(s.balls[0].vx>0);
s=createBreaker();s.started=s.launched=true;const b=s.bricks[0];s.balls=[{x:b.x,y:b.y,vx:0,vy:-200}];step(s,{},DT);assert.equal(b.hp,1);assert(s.events.includes('breaker_hit'));
s=createBreaker();s.started=s.launched=true;s.balls=[{x:450,y:600,vx:0,vy:200}];step(s,{},DT);assert.equal(s.lives,2);assert(!s.launched);
for(const type of ['wide','multi','laser']){s=createBreaker();s.started=s.launched=true;s.drops=[{x:s.paddle.x,y:s.height-50,type}];step(s,{},DT);assert(type==='wide'?s.wide>0:type==='laser'?s.laser>0:s.balls.length>1)}
s=createBreaker();s.started=s.launched=true;s.bricks=[];step(s,{},DT);assert(s.wait>0);for(let i=0;i<21;i++)step(s,{},.1);assert.equal(s.level,2);assert.equal(s.bricks.length,50);
s=createLander();s.started=true;const fuel=s.ship.fuel;step(s,{thrust:true},.1);assert(s.ship.fuel<fuel);assert(s.ship.vy<0);step(s,{},DT);assert(!s.ship.firing);
s=createLander();s.started=true;let p=pad(s);Object.assign(s.ship,{x:p.x,y:p.y-13,vx:0,vy:0,angle:0});step(s,{},DT);assert(s.landed);assert.equal(s.lives,3);assert(s.score>0);for(let i=0;i<21;i++)step(s,{},.1);assert.equal(s.level,2);assert.equal(s.ship.fuel,100);
for(const unsafe of [{vy:80},{angle:.5},{vx:40}]){s=createLander();s.started=true;p=pad(s);Object.assign(s.ship,{x:p.x,y:p.y-13,vx:0,vy:0,angle:0},unsafe);step(s,{},DT);assert.equal(s.lives,2);assert(!s.landed)}
s=createLander();s.started=true;s.ship.fuel=0;step(s,{thrust:true},.1);assert(s.ship.vy>0);assert.equal(s.ship.fuel,0);
s=createBreaker();s.bricks[0].hp=1;s.bricks.splice(1,4);s.score=55;resizeState(s,1300,700);assert.equal(s.bricks.length,46);assert.equal(s.bricks[0].hp,1);assert.equal(s.score,55);
console.log('OK: Breaker physics, damage, powers, waves and Lander fuel, safe/unsafe landings, missions and resize.');

s=createLander();s.started=true;s.level=3;Object.assign(s.ship,{x:s.width*.45,y:50});step(s,{},DT);assert.equal(s.lives,2,'cave roof is an obstacle on advanced missions');
