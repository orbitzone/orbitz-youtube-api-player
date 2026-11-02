/* One-shot miniature scenes using the live games’ own renderers. No simulation, timers, input or audio. */
(()=>{
'use strict';
const panel=$('runner'),home=document.createElement('section');home.id='games-home';home.setAttribute('aria-labelledby','games-home-title');panel.append(home);
const style=document.createElement('style');style.textContent=`
#games-home{position:absolute;inset:0;z-index:3;overflow:auto;display:flex;flex-direction:column;padding:16px 18px;background:#101720;gap:12px}#games-home[hidden]{display:none}
#games-home #feature-resume{position:static;max-width:none;width:100%;margin:0;flex:0 0 auto}.keep-watching{flex:0 0 auto}.keep-watching h2{font-size:18px;margin:0 0 10px}.games-home-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}.games-home-head h2{margin:0;font-size:18px}.games-home-head p{margin:0;color:#aebcce;font-size:12px}
.games-home-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(3,minmax(110px,1fr));gap:12px;flex:1;min-height:360px}
.game-card{position:relative;display:block;min-width:0;min-height:110px;width:100%;height:100%;padding:0;border:1px solid #35465c;border-radius:12px;background:#080d18;overflow:hidden;box-shadow:none}.game-card:hover{border-color:#8acfff}.game-card:focus-visible{outline:2px solid #8acfff;outline-offset:2px}.game-card canvas{position:absolute;inset:0;display:block;width:100%;height:100%;pointer-events:none;background:#171b20}.game-card-copy{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:12px;pointer-events:none;text-align:center;background:transparent}.game-card strong{display:block;width:calc(100% + 24px);flex:0 0 calc(100% + 24px);padding:10px 12px;background:rgba(0,0,0,.55);font-family:Orbitron,system-ui,sans-serif;font-size:clamp(18px,2.4vw,30px);font-weight:600;line-height:1.3;color:#f0f7ff;text-shadow:none}

.games-support{display:flex;align-items:center;gap:12px;flex:0 0 auto;padding:10px 16px;border:1px solid #354c69;border-radius:12px;background:linear-gradient(115deg,#162638,#171d28)}.games-support-orbit{display:flex;align-items:center;justify-content:center;width:34px;height:34px;flex:0 0 34px;border-radius:50%;background:#8acfff18;color:#8acfff;font-size:21px}.games-support-copy{flex:1;min-width:0}.games-support h2{margin:0 0 2px;font-size:15px;color:#dceeff}.games-support p{margin:0;color:#bdc7d3;font-size:clamp(10px,1.6vw,12px);line-height:1.5;white-space:nowrap}.games-support-action{display:flex;flex-direction:column;align-items:center;gap:6px;flex:0 0 auto}.games-support button{padding:7px 10px;font-size:12px}.games-support button:disabled{cursor:default;opacity:1;background:#29313b;border-color:#46515d;color:#aebdcd}@media(max-width:600px){.games-support{flex-wrap:wrap;padding:10px 12px;gap:8px}.games-support-orbit{display:none}.games-support-action{width:100%;align-items:stretch;text-align:center}}
#games-home-back{position:absolute;top:5px;left:10px;padding:4px 7px;font-size:11px;background:transparent;border:0;z-index:2}#games-home-back[hidden]{display:none}#game-switch-hint{left:104px}
.games-home-active #game-audio-controls,.games-home-active #runner-brand,.games-home-active #runner-help,.games-home-active #game-switch-hint,.games-home-active #maze-help,.games-home-active #invaders-help,.games-home-active #asteroids-help,.games-home-active #breaker-help,.games-home-active #lander-help,.games-home-active #game-pause{display:none}
@media(min-width:1200px){.games-home-grid{grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(2,minmax(110px,1fr));min-height:240px}}
@media(max-width:480px){#games-home{padding:12px 10px}.games-home-grid{grid-template-columns:1fr;grid-template-rows:none;grid-auto-rows:minmax(145px,auto)}.games-home-head p{font-size:11px}}
`;document.head.append(style);
window.orbitzPreviewSize=target=>{const rect=target.getBoundingClientRect();target.width=rect.width&&rect.height?Math.max(740,Math.ceil(140*rect.width/rect.height)):740;target.height=rect.width?Math.max(140,Math.round(target.width*rect.height/rect.width)):360;return{width:target.width,height:target.height}};
const titles={runner:'Orbit Runner',maze:'Orbit Maze',invaders:'Orbit Invaders',asteroids:'Orbit Asteroids',breaker:'Orbit Breaker',lander:'Orbit Lander'};
home.innerHTML='<section class="keep-watching" aria-labelledby="keep-watching-title"><h2 id="keep-watching-title">Keep Watching</h2><div id="keep-watching-content"></div></section><div class="games-home-head"><h2 id="games-home-title"></h2><p id="games-home-hint"></p></div><div class="games-home-grid"></div><section class="games-support" aria-labelledby="games-support-title"><span class="games-support-orbit" aria-hidden="true">✦</span><div class="games-support-copy"><h2 id="games-support-title"></h2><p id="games-support-description"></p></div><div class="games-support-action"><button id="games-support-paypal" type="button" disabled></button></div></section>';
for(const game of Object.keys(titles)){
 const card=document.createElement('button');card.type='button';card.className='game-card';card.dataset.game=game;
 const miniature=document.createElement('canvas');miniature.setAttribute('aria-hidden','true');miniature.dataset.staticPreview=game;
 card.innerHTML='<span class="game-card-copy"><strong>'+titles[game]+'</strong></span>';
 card.prepend(miniature);
 card.onclick=()=>window.orbitzOpenGame(game);home.querySelector('.games-home-grid').append(card);window.orbitzGamePreviews[game](miniature);
 let size='';new ResizeObserver(()=>{if(home.hidden){size='';return}const r=miniature.getBoundingClientRect(),next=r.width+':'+r.height;if(!r.width||!r.height||size===next)return;size=next;window.orbitzGamePreviews[game](miniature)}).observe(miniature);
}
const back=document.createElement('button');back.id='games-home-back';back.type='button';back.hidden=true;panel.append(back);
function sync(){const resume=$('feature-resume');if(resume){if(resume.parentElement!==$('keep-watching-content'))$('keep-watching-content').append(resume)}panel.classList.toggle('games-home-active',Boolean(window.orbitzGamesHome));home.hidden=!window.orbitzGamesHome;back.hidden=Boolean(window.orbitzGamesHome);if(window.orbitzGamesHome)for(const canvas of home.querySelectorAll('canvas[data-static-preview]'))window.orbitzGamePreviews[canvas.dataset.staticPreview](canvas)}
window.orbitzHideGamesHome=()=>{window.orbitzGamesHome=false;sync()};
function openHome(){
 closeSettingsMenu();closeDiscovery();if(!$('config').hidden)closeSettings();if(window.orbitzFeaturesOpen?.())featureClose(false);
 stopPlaybackRetry();if(playerReady)youtubePlayer?.pauseVideo?.();$('screen').hidden=true;panel.hidden=false;window.orbitzGamesHome=true;sync();
 window.orbitzRunnerGameChanged?.();window.orbitzMazePauseChanged?.();window.orbitzInvadersActivate?.();window.orbitzAsteroidsActivate?.();window.orbitzBreakerActivate?.();window.orbitzLanderActivate?.();window.orbitzSyncGamePause?.();
 window.orbitzRefreshResume?.().catch(()=>{});notifyWindowState();syncControls();home.querySelector('.game-card').focus({preventScroll:true});
}
back.onclick=openHome;$('home-logo').onclick=openHome;
const menu=document.createElement('button');menu.type='button';menu.setAttribute('role','menuitem');menu.onclick=()=>{closeSettingsMenu();openHome()};$('settings-menu').append(menu);
const oldLanguage=window.orbitzRunnerLanguageChanged;window.orbitzRunnerLanguageChanged=()=>{oldLanguage?.();$('games-home-title').textContent=uiTr('youtube.games_home');$('games-home-hint').textContent=uiTr('youtube.games_home_hint');back.textContent=uiTr('youtube.games_back');for(const [id,key] of [['games-support-title','support_title'],['games-support-description','support_description'],['games-support-paypal','support_paypal']])$(id).textContent=uiTr('youtube.'+key);menu.textContent=uiTr('youtube.games_home')};
sync();window.orbitzRunnerLanguageChanged();
})();
