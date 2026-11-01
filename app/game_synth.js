/* Original retro timbres, generated locally. No samples or melodies from Pac-Man. */
(()=>{
'use strict';
const patterns={
 maze_cherry:[[.07,660,880],[.08,990,1320],[.09,1100,1540]],
 asteroids_shot_0:[[.085,1800,150]],asteroids_shot_1:[[.07,1500,210]],asteroids_shot_2:[[.09,2100,240]],asteroids_shot_3:[[.06,1200,120]],
 asteroids_hit_0:[[.035,170,65],[.09,80,27]],asteroids_hit_1:[[.045,230,85],[.11,95,32]],asteroids_hit_2:[[.025,120,45],[.13,65,22]],
 asteroids_death:[[.12,180,60],[.22,95,30],[.25,45,22]],asteroids_start:[[.06,220,280],[.08,330,440]],asteroids_win:[[.09,260,390],[.1,520,650],[.13,780,520]],asteroids_ufo:[[.09,180,380],[.09,380,180]],
 breaker_bounce:[[.045,500,360]],breaker_hit:[[.055,850,1150]],breaker_launch:[[.08,350,700]],breaker_power:[[.08,440,660],[.1,880,1100]],breaker_laser:[[.06,1500,600]],breaker_death:[[.15,260,100],[.16,100,60]],breaker_win:[[.1,400,600],[.1,800,1000],[.12,1200,900]],breaker_start:[[.07,300,450],[.08,600,750]],
 lander_thrust:[[.065,65,85]],lander_land:[[.12,260,390],[.12,520,780]],lander_death:[[.12,110,40],[.2,70,24]],lander_start:[[.1,200,300],[.1,400,500]],

 maze_chomp_a:[[.065,650,220]],
 maze_chomp_b:[[.065,230,720]],
 maze_power:[[.08,330,440],[.08,440,590],[.10,590,880],[.10,880,660]],
 maze_ghost:[[.09,260,620],[.08,620,1050],[.08,1050,1400]],
 maze_death:[[.16,620,450],[.16,450,280],[.20,280,170],[.26,170,65]],
 maze_win:[[.11,330,330],[.11,440,440],[.11,550,550],[.13,660,660],[.24,880,660]],
 maze_start:[[.08,260,330],[.09,390,440],[.13,520,660]]
};
function synthesize(notes,sampleRate=44100){
 const length=Math.ceil(notes.reduce((sum,n)=>sum+n[0],0)*sampleRate),samples=new Float32Array(length);
 let offset=0,phase=0;
 notes.forEach(([duration,from,to])=>{
  const count=Math.round(duration*sampleRate);
  for(let i=0;i<count&&offset+i<length;i++){
   const progress=i/Math.max(1,count-1),frequency=from*Math.pow(to/from,progress);
   phase=(phase+frequency/sampleRate)%1;
   // Soft pulse with filtered harmonics and short attack/release, avoiding clicks.
   const wave=(Math.sin(phase*Math.PI*2)+.22*Math.sin(phase*Math.PI*6)+.08*Math.sin(phase*Math.PI*10))/.95;
   const envelope=Math.min(1,i/(sampleRate*.004),(count-1-i)/(sampleRate*.012));
   samples[offset+i]=wave*Math.max(0,envelope)*.22;
  }
  offset+=count;
 });return samples;
}
function createBuffers(context){return Object.entries(patterns).map(([name,notes])=>{const samples=synthesize(notes,context.sampleRate),buffer=context.createBuffer(1,samples.length,context.sampleRate);buffer.getChannelData(0).set(samples);return[name,buffer]})}
if(typeof module!=='undefined'&&module.exports){module.exports={patterns,synthesize};return}
window.orbitzCreateMazeSounds=createBuffers;
})();
