/* Per-game manual pause. No simulation time is recovered after resuming. */
(()=>{
'use strict';
const paused={runner:false,maze:false,invaders:false,asteroids:false,breaker:false,lander:false};
const panel=$('runner'),overlay=document.createElement('div');overlay.id='game-pause';overlay.hidden=true;overlay.setAttribute('role','status');overlay.setAttribute('aria-live','polite');panel.append(overlay);
const style=document.createElement('style');style.textContent='#game-pause{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#080d1877;color:#ffe6a3;font-weight:700;text-align:center;padding:24px;pointer-events:none;z-index:1}#game-pause[hidden]{display:none}';document.head.append(style);
const mode=()=>['maze','invaders','asteroids','breaker','lander'].includes(window.orbitzGameMode)?window.orbitzGameMode:'runner';
window.orbitzGamePaused=()=>paused[mode()]||Boolean(window.orbitzResizeActive?.());
window.orbitzSyncGamePause=()=>{
 const value=paused[mode()];panel.classList.toggle('game-paused',value);overlay.hidden=window.orbitzGamesHome||!value;overlay.textContent=uiTr('youtube.game_paused');
};
document.addEventListener('keydown',event=>{
 if(event.ctrlKey||event.altKey||event.metaKey||event.shiftKey)return;
 const controls={runner:[' ','arrowup'],maze:[' ','arrowup','arrowdown','arrowleft','arrowright'],invaders:[' ','arrowleft','arrowright','a','d'],asteroids:[' ','arrowleft','arrowright','arrowup','a','d','w'],breaker:[' ','arrowleft','arrowright','a','d'],lander:[' ','arrowleft','arrowright','arrowup','a','d','w']};
 const escape=event.key==='Escape',resume=paused[mode()]&&controls[mode()].includes(event.key.toLowerCase());
 if(!escape&&!resume)return;
 if(window.orbitzGamesHome||panel.hidden||!$('screen').hidden||!$('config').hidden||!$('discovery').hidden||!$('settings-menu').hidden||window.orbitzFeaturesOpen?.())return;
 if(['INPUT','TEXTAREA','SELECT'].includes(event.target?.tagName)||event.target?.isContentEditable)return;
 event.preventDefault();event.stopImmediatePropagation();if(event.repeat)return;
 paused[mode()]=!paused[mode()];window.orbitzSyncGamePause();
 window.orbitzRunnerGameChanged?.();window.orbitzMazePauseChanged?.();window.orbitzInvadersActivate?.();window.orbitzAsteroidsActivate?.();window.orbitzBreakerActivate?.();window.orbitzLanderActivate?.();
 if(!paused[mode()])window.orbitzUnlockGameAudio?.();
 if(resume&&!escape){const canvas=$(mode()==='runner'?'runner-canvas':mode()+'-canvas');canvas?.focus({preventScroll:true});canvas?.dispatchEvent(new KeyboardEvent('keydown',{key:event.key,code:event.code,location:event.location,bubbles:true,cancelable:true}))}
},true);
const language=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{language?.();window.orbitzSyncGamePause()};window.orbitzSyncGamePause();
})();
