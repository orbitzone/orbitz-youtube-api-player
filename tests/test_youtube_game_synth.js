const assert=require('assert');
const {patterns,synthesize}=require('../app/game_synth.js');
for(const rate of [44100,48000])for(const [name,notes] of Object.entries(patterns)){
 const data=synthesize(notes,rate);
 assert(data.length>0&&data.length<rate,'short effect: '+name);
 assert(data.every(value=>Number.isFinite(value)&&Math.abs(value)<=1),'no invalid samples/clipping');
 assert(data.some(value=>Math.abs(value)>.01),'audible signal');
 assert.equal(data[0],0);assert(Math.abs(data[data.length-1])<.001,'release avoids final click');
}
assert.notDeepEqual(synthesize(patterns.maze_chomp_a),synthesize(patterns.maze_chomp_b));
console.log('OK: original retro sound synthesis, finite samples, headroom, attack/release and alternating dot timbres.');
