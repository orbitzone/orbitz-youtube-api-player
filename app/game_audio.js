/* Short local effects: decoded once after opt-in; no delayed gameplay callbacks. */
(()=>{
'use strict';
const files={jump:'phaseJump1.ogg',shot:'laser1.ogg',ufo:'laser5.ogg',hit:'spaceTrash1.ogg',over:'lowDown.ogg'};
const panel=$('runner'),button=document.createElement('button');button.id='game-sound';button.type='button';
const controls=document.createElement('div');controls.id='game-audio-controls';
const slider=document.createElement('input');slider.type='range';slider.id='game-volume';slider.min='0';slider.max='100';slider.step='1';slider.value='0';slider.setAttribute('aria-orientation','vertical');
controls.append(button,slider);panel.append(controls);
const style=document.createElement('style');style.textContent="@font-face{font-family:Orbitron;src:url('fonts/Orbitron.ttf') format('truetype');font-weight:400 900;font-display:swap}#game-audio-controls{position:absolute;right:14px;top:38px;display:flex;flex-direction:column;align-items:center;gap:7px;z-index:2}#runner-brand{position:absolute;right:14px;bottom:0;height:34px;display:flex;align-items:center;font-family:Orbitron,system-ui,sans-serif;font-size:12px;font-weight:500;line-height:26px;white-space:nowrap;z-index:2}#game-sound{width:26px;height:26px;padding:3px;display:flex;align-items:center;justify-content:center;background:transparent;border:0;color:#dceaff;border-radius:4px}#game-sound svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}#game-volume{appearance:none;-webkit-appearance:none;writing-mode:vertical-lr;direction:rtl;width:22px;height:88px;padding:0;margin:0;flex:0 0 88px;background:transparent;border:0;cursor:pointer;accent-color:#9bcfff}#game-volume::-webkit-slider-runnable-track{width:3px;border-radius:3px;background:linear-gradient(to top,#9bcfff 0%,#9bcfff var(--volume,0%),#637080 var(--volume,0%),#637080 100%)}#game-volume::-webkit-slider-thumb{-webkit-appearance:none;width:10px;height:10px;margin-left:-3.5px;border-radius:50%;background:#dceaff;border:0}#game-volume:focus,#game-volume:focus-visible{outline:none;box-shadow:none}#game-sound:focus-visible{outline:2px solid #77bff0;outline-offset:3px}@media(max-width:500px){#game-audio-controls{right:8px;gap:5px}#runner-brand{font-size:10px}#game-volume{height:65px;flex-basis:65px}}";document.head.append(style);
let volume=0,previousVolume=25,saveTimer=0;
let enabled=false,context=null,master=null,loading=null,revision=0,alive=true,focused=true,soundMode=window.orbitzGameMode;
const variation=new Map();
const buffers=new Map(),voices=new Set(),lastPlayed=new Map();
function visible(){return !window.orbitzGamesHome&&!window.orbitzGamePaused?.()&&alive&&focused&&document.visibilityState==='visible'&&!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&$('settings-menu').hidden&&!window.orbitzFeaturesOpen?.()}
function stop(){for(const voice of voices){try{voice.stop()}catch{}voice.disconnect()}voices.clear();lastPlayed.clear()}
function render(){
 const label=uiTr(enabled?'youtube.game_sound_disable':'youtube.game_sound_enable');button.title=label;button.setAttribute('aria-label',label);button.setAttribute('aria-pressed',String(enabled));button.hidden=false;slider.value=String(volume);slider.style.setProperty('--volume',volume+'%');slider.setAttribute('aria-label',uiTr('youtube.game_volume'));slider.setAttribute('aria-valuetext',volume+'%');slider.title=uiTr('youtube.game_volume')+': '+volume+'%';
 button.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4z"/>'+(enabled?'<path d="M17 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>':'<path d="m17 9 5 6m0-6-5 6"/>')+'</svg>';
}
function unlock(){
 if(!enabled||!visible())return;
 try{
  if(!context){const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return;context=new Audio();master=context.createGain();master.gain.value=volume/100;master.connect(context.destination);for(const [name,buffer] of window.orbitzCreateMazeSounds?.(context)||[])buffers.set(name,buffer);for(const [name,source] of Object.entries({invaders_power:'maze_power',invaders_win:'maze_win',invaders_start:'maze_start',invaders_death:'maze_death'}))buffers.set(name,buffers.get(source))}
  if(context.state==='suspended')context.resume().catch(()=>{});
  if(!loading){loading=Promise.all(Object.entries(files).map(async([name,file])=>{try{
   const response=await fetch(location.pathname+'audio/'+file);if(!response.ok)return;
   const buffer=await context.decodeAudioData(await response.arrayBuffer());if(alive){buffers.set(name,buffer);const aliases={shot:'invaders_shot',hit:'invaders_hit',ufo:'invaders_ufo'};if(aliases[name]){buffers.set(aliases[name],buffer);}}
  }catch{}}));}
 }catch{} // Audio support or permission never blocks the game.
}
window.orbitzUnlockGameAudio=unlock;
window.orbitzGameSound=name=>{
 const prefix=name.split('_')[0],game=['maze','invaders','asteroids','breaker','lander'].includes(prefix)?prefix:'runner';if(game!==(window.orbitzGameMode||'runner'))return;
 const original=name;const variants={asteroids_shot:4,asteroids_hit:3};if(variants[name]){const index=variation.get(name)||0;variation.set(name,index+1);name+='_'+index%variants[name]}
 if(!enabled||!visible()||!buffers.has(name)||context?.state!=='running')return;
 const now=context.currentTime;if(now-(lastPlayed.get(original)??-1)<.065)return;lastPlayed.set(original,now);
 if(voices.size>=6){const oldest=voices.values().next().value;try{oldest.stop()}catch{}oldest.disconnect();voices.delete(oldest)}
 const voice=context.createBufferSource();voice.buffer=buffers.get(name);voice.connect(master);voices.add(voice);voice.onended=()=>{voices.delete(voice);voice.disconnect()};voice.start();
};
let saveChain=Promise.resolve();
function saveVolume(){clearTimeout(saveTimer);const value=volume;saveChain=saveChain.catch(()=>{}).then(()=>api('local-state',{op:'preferences',values:{game_sound:value>0,game_volume:value}})).catch(()=>{})}
function setVolume(value){
 revision++;volume=Math.max(0,Math.min(100,Math.round(Number(value)||0)));enabled=volume>0;if(enabled)previousVolume=volume;
 if(master){master.gain.cancelScheduledValues(context.currentTime);master.gain.setTargetAtTime(volume/100,context.currentTime,.01)}
 if(!enabled)stop();render();unlock();clearTimeout(saveTimer);saveTimer=setTimeout(saveVolume,180);
}
button.onclick=()=>{setVolume(enabled?0:previousVolume);saveVolume()};
slider.oninput=()=>setVolume(slider.value);slider.onchange=saveVolume;
let volumePointer=null;
slider.addEventListener('pointerdown',event=>{if(event.button!==0)return;volumePointer=event.pointerId;slider.setPointerCapture?.(event.pointerId)});
function releaseVolume(event){
 if(volumePointer!==event.pointerId)return;volumePointer=null;saveVolume();
 const game=$(window.orbitzGameMode&&window.orbitzGameMode!=='runner'?window.orbitzGameMode+'-canvas':'runner-canvas');
 if(!panel.hidden&&$('screen').hidden&&$('config').hidden&&$('discovery').hidden&&!window.orbitzFeaturesOpen?.())game?.focus({preventScroll:true});
 else slider.blur();
}
document.addEventListener('pointerup',releaseVolume);document.addEventListener('pointercancel',releaseVolume);

document.addEventListener('pointerdown',unlock,true);document.addEventListener('keydown',unlock,true);
new MutationObserver(()=>{if(soundMode!==window.orbitzGameMode){soundMode=window.orbitzGameMode;stop()}if(!visible())stop()}).observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','class']});
window.addEventListener('blur',()=>{focused=false;stop()});window.addEventListener('focus',()=>{focused=true});document.addEventListener('visibilitychange',()=>{if(!visible())stop()});
window.addEventListener('pagehide',()=>{alive=false;clearTimeout(saveTimer);stop();context?.close().catch(()=>{})});
const oldLanguage=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{oldLanguage?.();render()};
render();const requested=revision;api('local-state',{}).then(state=>{if(requested!==revision||!alive)return;const stored=state.preferences.game_volume;previousVolume=Number.isInteger(stored)&&stored>0&&stored<=100?stored:25;volume=state.preferences.game_sound===true?previousVolume:0;enabled=volume>0;render()}).catch(()=>{});
})();
