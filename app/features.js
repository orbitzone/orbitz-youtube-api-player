/* Local desktop features. No provider/user text is interpreted as HTML. */
let featureState={preferences:{},favorites:[],later:[],queue:[],resume:null};
let featureLive=false,featureResumeDismissed=false;
let featureTransferPending=false,featureForceStopped=false,featureTrackStarted=false;
let featureMediaTimer=0,featurePauseOnStart=false;
let featureProgressPending=null,featureProgressLatest=null;
let featureChain=Promise.resolve(),featureView='favorites',featureTitle='',featureChannel='',featureProgressTimer=0,featureLastStatus=-1,featureResumeStart=null,featureAdvancePending=false,featureAlive=true;
const featureButton=(key,handler)=>{const b=document.createElement('button');b.type='button';uiText(b,'youtube.'+key);b.onclick=event=>{try{return Promise.resolve(handler(event)).catch(featureError)}catch{featureError()}};if(['move_up','move_down'].includes(key))uiAttr(b,'aria-label','youtube.'+key+'_label');return b};
function featureError(){uiText($('player-action-status'),'youtube.local_failed');if($('feature-local-status'))uiText($('feature-local-status'),'youtube.local_failed')}
function featureTask(task){const result=featureChain.then(task);featureChain=result.catch(featureError);return result}
function featureMutate(body){return featureTask(async()=>{const result=await api('local-state',body);if(result.preferences){featureState=result;featureRender();featurePublishMedia();}return result})}
window.orbitzResultActions=(button,item)=>{
 const row=document.createElement('div');row.className='feature-result-row';button.classList.add('feature-result-play');
 const add=document.createElement('button');add.type='button';add.className='feature-result-queue';add.textContent='+';uiAttr(add,'aria-label','youtube.add_queue');uiAttr(add,'title','youtube.add_queue');
 add.onclick=async()=>{add.disabled=true;try{await featureQueue({id:item.id,title:item.title});uiText($('player-action-status'),'youtube.added_queue')}catch{featureError()}finally{add.disabled=false}};
 row.append(button,add);$('results').append(row);
};
const featureStyle=document.createElement('style');featureStyle.textContent=`
#results .feature-result-row{display:flex;align-items:center;gap:0;margin-bottom:6px;border:1px solid #46515d;border-radius:8px;background:#252d36;overflow:hidden}#results .feature-result-play{flex:1;min-width:0;margin-bottom:0;border:0;border-radius:0;background:transparent}#results .feature-result-queue{flex:0 0 30px;width:30px;min-height:32px;height:32px;margin:0 5px 0 0;padding:0;justify-content:center;align-items:center;border:0;border-left:1px solid #46515d;border-radius:0;background:transparent}#results .feature-result-play:hover,#results .feature-result-queue:hover{background:#ffffff08}#results .feature-result-play:focus-visible,#results .feature-result-queue:focus-visible{outline-offset:-3px}
#feature-panel[hidden],#feature-resume[hidden],#feature-popmenu[hidden]{display:none}
#feature-panel{position:fixed;inset:0;z-index:25;display:flex;align-items:flex-start;justify-content:flex-end;padding:70px 12px 12px;background:transparent}
#feature-panel .modal-card{width:460px;max-width:100%;max-height:100%;min-height:0;border:1px solid #3b4653;border-radius:16px;background:#1c222a;box-shadow:0 18px 55px #0009;overflow:hidden;animation:feature-in .12s ease-out}
#feature-panel .modal-head{padding:13px 16px;border-color:#ffffff0c;gap:10px}#feature-panel .modal-head h2{font-size:15px;font-weight:650;letter-spacing:.1px}#feature-panel .modal-head button{width:28px;height:28px;padding:0;border:0;background:transparent;color:#9caabc;border-radius:8px}
#feature-panel .modal-body{display:flex;flex-direction:column;padding:0;min-height:0;overflow:hidden}
#feature-current{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid #ffffff0b;min-width:0}#feature-current[hidden]{display:none}.feature-thumb{width:64px;height:42px;border-radius:7px;background:#11161d;object-fit:cover;flex-shrink:0}.feature-current-copy{flex:1;min-width:0}.feature-eyebrow{font-size:10px;font-weight:650;letter-spacing:.9px;text-transform:uppercase;color:#8d9aac;margin-bottom:4px}#feature-current-title{font-size:12px;line-height:1.45;color:#e4ebf4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}#feature-current-actions{display:flex;gap:4px;flex-shrink:0}
#feature-nav[hidden],#feature-transfer[hidden]{display:none}#feature-nav{display:flex;padding:10px 12px 8px;gap:4px;flex-shrink:0}#feature-nav button{flex:1;display:flex;justify-content:center;align-items:center;gap:5px;padding:8px 5px;background:transparent;border:0;border-radius:9px;font-size:12px;color:#9caabc;white-space:nowrap}#feature-nav button[aria-pressed=true]{background:#303c4c;color:#c9e5ff}.feature-icon-button[aria-pressed=true] svg{fill:#f6cf75}.feature-count{font-size:10px;padding:1px 5px;border-radius:5px;background:#ffffff0b;color:inherit;font-variant-numeric:tabular-nums}
#feature-list{overflow-y:auto;min-height:0;padding:2px 8px 8px;max-height:300px;scrollbar-width:thin;scrollbar-color:#46515d transparent}.feature-row{display:flex;align-items:center;gap:3px;padding:3px;border:0;border-radius:10px}.feature-row:hover,.feature-row:focus-within{background:#ffffff06}.feature-row .feature-play{display:flex;align-items:center;gap:10px;flex:1;min-width:0;text-align:left;border:0;background:transparent;padding:5px;border-radius:8px}.feature-item-copy{flex:1;min-width:0}.feature-item-title{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:12px;line-height:1.45;font-weight:500;color:#e5ecf5}.feature-item-meta{display:block;color:#8290a3;font-size:10px;margin-top:4px}.feature-row .feature-thumb{width:64px;height:42px}
#feature-panel .feature-icon-button{display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;width:30px;height:30px;padding:6px;background:transparent;border:0;border-radius:8px;color:#92a1b5}#feature-panel .feature-icon-button:hover,#feature-panel .feature-icon-button:focus-visible{background:#ffffff0d;color:#d5e9ff}#feature-panel .feature-icon-button[aria-pressed=true]{color:#f6cf75;background:#f6cf7510}.feature-icon{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.feature-empty{padding:24px 16px 28px;text-align:center;color:#8b98aa}.feature-empty>.feature-icon{width:28px;height:28px;color:#6f849f;margin-bottom:9px}.feature-empty strong{display:block;font-size:13px;font-weight:550;color:#cfdae8;margin-bottom:6px}.feature-empty p{font-size:11px;line-height:1.5;margin:0}
#feature-transfer{display:flex;align-items:center;justify-content:space-between;border-top:1px solid #ffffff0b;padding:8px 14px;gap:8px;flex-shrink:0}#feature-transfer .feature-footer-note{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:10px;color:#7e8da0}#feature-transfer button{flex-shrink:0;display:flex;align-items:center;gap:6px;font-size:11px;background:transparent;border:0;padding:6px 8px;color:#a9bad0;border-radius:7px}#feature-transfer button:hover{background:#ffffff08}
#feature-popmenu{position:fixed;z-index:40;min-width:185px;max-height:calc(100vh - 20px);overflow:auto;padding:5px;border:1px solid #435064;border-radius:11px;background:#252e3a;box-shadow:0 9px 26px #0007}#feature-popmenu button{display:flex;align-items:center;gap:9px;min-height:34px;width:100%;padding:8px 10px;border:0;background:transparent;border-radius:7px;font-size:12px;text-align:left;color:#d7e1ee}#feature-popmenu button:hover,#feature-popmenu button:focus-visible{background:#ffffff0b}#feature-popmenu .feature-danger{color:#f7a3a9}
#feature-local-status{margin:0;padding:0 16px;color:#91cdb8;font-size:11px;flex-shrink:0}#feature-local-status:not(:empty){padding:7px 16px}#feature-diagnostics{white-space:pre-wrap;overflow:auto;overflow-wrap:anywhere;font-size:11px;padding:14px;margin:0;color:#becbdb}#feature-panel .feature-help{white-space:pre-line;padding:10px 16px;overflow:auto;font-size:12px;line-height:1.8;color:#b5c3d5}
#feature-resume{position:fixed;left:20px;right:20px;bottom:45px;z-index:3;display:flex;align-items:center;gap:8px;max-width:650px;padding:10px;background:#20252bf5;border:1px solid #46515d;border-radius:9px}#feature-resume .feature-resume-thumb{width:88px;height:50px;object-fit:cover;border-radius:6px;flex:0 0 88px;background:#11161d}#feature-resume strong{font-weight:700}#feature-resume small{font-size:inherit;font-weight:400}#feature-resume{flex-wrap:wrap}#feature-resume .feature-resume-copy{flex:1 1 220px;min-width:0;white-space:normal;overflow-wrap:normal;word-break:normal;line-height:1.4}#feature-resume .feature-resume-copy.compact{font-size:12px}#feature-resume .feature-resume-copy strong{white-space:normal}#feature-resume button{flex-shrink:0}#feature-recommendation-settings{border:1px solid #46515d;border-radius:8px;margin-top:14px}#feature-recommendation-settings .feature-check{display:flex;align-items:center;gap:8px;font-size:12px;margin:8px 0}#config #feature-use-recent{flex:0 0 auto;width:auto;margin:0}.feature-recommendation-actions{display:flex;gap:6px;flex-wrap:wrap}#feature-recommendation-status:empty{display:none}
@keyframes feature-in{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}@media(prefers-reduced-motion:reduce){#feature-panel .modal-card{animation:none}}@media(max-width:480px){#feature-panel{padding-left:8px;padding-right:8px}#feature-panel .modal-card{width:100%}#feature-current{padding:9px 12px}#feature-nav{padding:8px}#feature-nav button{font-size:11px}.feature-row .feature-thumb{width:54px;height:36px}}@media(max-height:430px){#feature-current .feature-thumb{width:46px;height:32px}#feature-current{padding-top:8px;padding-bottom:8px}.feature-empty{padding:12px}#feature-panel .modal-head{padding-top:9px;padding-bottom:9px}}
`;
document.head.append(featureStyle);
const featurePanel=document.createElement('div');featurePanel.id='feature-panel';featurePanel.hidden=true;featurePanel.setAttribute('role','dialog');featurePanel.setAttribute('aria-modal','true');featurePanel.setAttribute('aria-labelledby','feature-title');featurePanel.innerHTML='<section class="modal-card"><div class="modal-head"><h2 id="feature-title"></h2><button id="feature-close" type="button">×</button></div><div class="modal-body"><div id="feature-current" hidden><div id="feature-current-image"></div><div class="feature-current-copy"><div id="feature-now-label" class="feature-eyebrow"></div><div id="feature-current-title"></div></div><div id="feature-current-actions"></div></div><nav id="feature-nav"></nav><div id="feature-list"></div><pre id="feature-diagnostics" hidden></pre><p id="feature-local-status" role="status" aria-live="polite"></p><div id="feature-transfer"></div></div></section>';

document.body.append(featurePanel);
const featurePaths={similar:'M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14m5 12 6 6M7 10h6m-3-3v6',star:'m12 3 2.7 5.6 6.2.9-4.5 4.4 1.1 6.2-5.5-2.9-5.5 2.9 1.1-6.2L3.6 9.5l6.1-.9L12 3Z',clock:'M12 8v4l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',queue:'M4 5h12M4 10h12M4 15h7m6-1v8m-4-4h8',more:'M12 5h.01M12 12h.01M12 19h.01',trash:'M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7',up:'m6 14 6-6 6 6',down:'m6 10 6 6 6-6',import:'M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5',export:'M12 15V3m-4 4 4-4 4 4M4 16v5h16v-5',library:'M4 4h5v16H4zM12 5l5-1 3 15-5 1z',check:'m5 12 4 4L19 6'};
function featureIcon(name){const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.classList.add('feature-icon');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d',featurePaths[name]||featurePaths.library);if(name==='more'){svg.style.strokeWidth='3.7'}svg.append(path);return svg}
function featureIconButton(key,icon,handler){const button=featureButton(key,handler);uiRaw(button,'');button.className='feature-icon-button';button.append(featureIcon(icon));uiAttr(button,'aria-label','youtube.'+key);uiAttr(button,'title','youtube.'+key);return button}
function featureThumb(item){const image=document.createElement('img');image.className='feature-thumb';image.src='https://i.ytimg.com/vi/'+encodeURIComponent(item.id)+'/default.jpg';image.alt='';image.loading='lazy';image.decoding='async';image.referrerPolicy='no-referrer';return image}
const featurePopup=document.createElement('div');featurePopup.id='feature-popmenu';featurePopup.hidden=true;featurePopup.setAttribute('role','menu');featurePanel.append(featurePopup);
let featurePopupAnchor=null;
function featureCloseMenu(restore=false){if(featurePopupAnchor){featurePopupAnchor.setAttribute('aria-expanded','false');if(restore&&featurePopupAnchor.isConnected)featurePopupAnchor.focus()}featurePopup.hidden=true;featurePopupAnchor=null}
function featureShowMenu(anchor,actions){
 if(featurePopupAnchor===anchor&&!featurePopup.hidden){featureCloseMenu(true);return}
 featureCloseMenu();featurePopupAnchor=anchor;anchor.setAttribute('aria-haspopup','menu');anchor.setAttribute('aria-expanded','true');featurePopup.replaceChildren();
 for(const action of actions){const button=featureButton(action.key,async()=>{featureCloseMenu();await action.run();if(!featurePanel.hidden&&!featurePanel.contains(document.activeElement))$('feature-close').focus()});button.setAttribute('role','menuitem');if(action.danger)button.className='feature-danger';button.prepend(featureIcon(action.icon));featurePopup.append(button)}
 featurePopup.hidden=false;const rect=anchor.getBoundingClientRect(),menu=featurePopup.getBoundingClientRect();
 featurePopup.style.left=Math.max(8,Math.min(innerWidth-menu.width-8,rect.right-menu.width))+'px';
 featurePopup.style.top=Math.max(8,Math.min(innerHeight-menu.height-8,rect.bottom+5))+'px';featurePopup.querySelector('button')?.focus();
}
featurePopup.addEventListener('keydown',event=>{if(['ArrowDown','ArrowUp','Home','End'].includes(event.key)){event.preventDefault();event.stopPropagation();const items=[...featurePopup.querySelectorAll('button')],i=items.indexOf(document.activeElement);items[event.key==='Home'?0:event.key==='End'?items.length-1:(i+(event.key==='ArrowUp'?-1:1)+items.length)%items.length]?.focus()}else if(event.key==='Tab'){event.preventDefault();event.stopPropagation();const anchor=featurePopupAnchor;featureCloseMenu();const buttons=[...featurePanel.querySelectorAll('button')].filter(button=>!button.disabled&&button.offsetParent!==null),index=buttons.indexOf(anchor);buttons[(index+(event.shiftKey?-1:1)+buttons.length)%buttons.length]?.focus()}});
document.addEventListener('pointerdown',event=>{if(!featurePopup.contains(event.target)&&!featurePopupAnchor?.contains(event.target))featureCloseMenu()});
$('feature-list').addEventListener('scroll',()=>featureCloseMenu(),{passive:true});
function featureRestoreFocus(index){if(index<0||featurePanel.hidden)return;const buttons=[...featurePanel.querySelectorAll('button')].filter(button=>!button.disabled&&button.offsetParent!==null);buttons[Math.min(index,buttons.length-1)]?.focus()}
function featurePosition(){if(featurePanel.hidden)return;const rect=$('feature-library-button')?.getBoundingClientRect();featurePanel.style.paddingTop=Math.min(Math.max(8,(rect?.bottom||54)+8),Math.max(8,innerHeight-170))+'px'}
window.addEventListener('resize',()=>{featureCloseMenu();featurePosition()});
function featureCurrentOptions(item){return [
 {key:featureState.favorites.some(v=>v.id===item.id)?'remove_favorite':'favorite',icon:'star',run:()=>featureMutate({op:featureState.favorites.some(v=>v.id===item.id)?'remove':'save',kind:'favorites',video:item})},
 {key:featureState.later.some(v=>v.id===item.id)?'remove_later':'watch_later',icon:'clock',run:()=>featureMutate({op:featureState.later.some(v=>v.id===item.id)?'remove':'save',kind:'later',video:item})},
 {key:'add_queue',icon:'queue',run:()=>featureQueue(item)},
 {key:'similar_videos',icon:'similar',run:()=>featureSimilar(item)}
]}

let featureReturnFocus=null;
window.orbitzFeaturesOpen=()=>!featurePanel.hidden;
function featureOpen(view='favorites'){
 featureReturnFocus=document.activeElement;featureView=view;featurePanel.hidden=false;closeSettingsMenu();if(!$('discovery').hidden)closeDiscovery();
 featurePosition();featureRender();$('feature-close').focus();syncChrome();
}
function featureClose(restoreFocus=true){if(featurePanel.hidden)return;featurePanel.hidden=true;featureCloseMenu();if(typeof featureHeader!=='undefined')featureHeader.setAttribute('aria-expanded','false');if(restoreFocus)(featureReturnFocus?.isConnected?featureReturnFocus:$('settings')).focus();syncChrome()}
$('feature-close').onclick=featureClose;
featurePanel.onclick=e=>{if(e.target===featurePanel)featureClose()};
featurePanel.addEventListener('keydown',e=>{
 if(e.key==='Escape'){e.preventDefault();e.stopPropagation();if(!featurePopup.hidden){featureCloseMenu(true);return}featureClose()}
 if(e.key==='Tab'){
  const buttons=[...featurePanel.querySelectorAll('button,input,a[href]')].filter(n=>!n.disabled&&n.offsetParent!==null);
  const first=buttons[0],last=buttons.at(-1);
  if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}
  else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}
 }
});
const featureMenu=featureButton('library',()=>featureOpen());featureMenu.setAttribute('role','menuitem');$('settings-menu').insertBefore(featureMenu,$('fit-player'));
const featureDiagMenu=featureButton('diagnostics',()=>featureOpen('diagnostics'));featureDiagMenu.setAttribute('role','menuitem');$('settings-menu').insertBefore(featureDiagMenu,$('fit-player'));
const featureShortcutMenu=featureButton('shortcuts',()=>featureOpen('shortcuts'));featureShortcutMenu.setAttribute('role','menuitem');$('settings-menu').insertBefore(featureShortcutMenu,$('fit-player'));
const featureHeader=featureButton('library',()=>featurePanel.hidden?featureOpen():featureClose());featureHeader.id='feature-library-button';featureHeader.setAttribute('aria-haspopup','dialog');featureHeader.setAttribute('aria-controls','feature-panel');featureHeader.setAttribute('aria-expanded','false');uiRaw(featureHeader,'');featureHeader.append(featureIcon('library'));uiAttr(featureHeader,'aria-label','youtube.library');uiAttr(featureHeader,'title','youtube.library');$('settings').parentElement.before(featureHeader);
const featureResume=document.createElement('aside');featureResume.id='feature-resume';featureResume.hidden=true;featureResume.setAttribute('aria-label',uiTr('youtube.continue_watching'));document.body.append(featureResume);
const featureRecommendationSettings=document.createElement('fieldset');featureRecommendationSettings.id='feature-recommendation-settings';
featureRecommendationSettings.innerHTML='<legend data-i18n="youtube.recommendation_settings"></legend><label for="feature-interests" data-i18n="youtube.your_interests"></label><input id="feature-interests" type="text" maxlength="809" data-i18n-placeholder="youtube.interests_placeholder"><label class="feature-check"><input id="feature-use-recent" type="checkbox"><span data-i18n="youtube.use_recent_searches"></span></label><p data-i18n="youtube.recommendation_privacy"></p><div class="feature-recommendation-actions"></div><p id="feature-recommendation-status" role="status" aria-live="polite"></p>';
$('config').querySelector('.modal-body').append(featureRecommendationSettings);
const featureSaveRecommendations=featureButton('save_interests',async()=>{
 const interests=$('feature-interests').value.split(',').map(term=>term.trim()).filter(Boolean);
 if(interests.length>10||interests.some(term=>term.length>80||/[\u0000-\u001f]/.test(term))){uiText($('feature-recommendation-status'),'youtube.invalid_interests');return}
 featureSaveRecommendations.disabled=true;
 try{await featureMutate({op:'recommendation-settings',values:{interests,use_recent:$('feature-use-recent').checked}});uiText($('feature-recommendation-status'),'youtube.interests_saved');if(!$('discovery').hidden)window.orbitzRefreshRecommendations?.();}
 catch{uiText($('feature-recommendation-status'),'youtube.local_failed')}finally{featureSaveRecommendations.disabled=false}
});
const featureClearSearches=featureButton('clear_recent_searches',async()=>{
 featureClearSearches.disabled=true;
 try{await featureMutate({op:'clear-searches'});uiText($('feature-recommendation-status'),'youtube.recent_searches_cleared');if(!$('discovery').hidden)window.orbitzRefreshRecommendations?.();}
 catch{uiText($('feature-recommendation-status'),'youtube.local_failed')}finally{featureClearSearches.disabled=false}
});
featureRecommendationSettings.querySelector('.feature-recommendation-actions').append(featureSaveRecommendations,featureClearSearches);

function featureCurrent(){return selected?{id:selected,title:featureTitle||youtubePlayer?.getVideoData?.().title||selected,...(featureChannel?{channel:featureChannel}:{})}:null}
function featureSave(kind){const item=featureCurrent();if(item)return featureMutate({op:'save',kind,video:item})}
function featureQueue(item){return featureMutate({op:'queue-add',video:item})}
function featureSimilar(item){
 const query=(item.title||'').replace(/[\u0000-\u001f|]/g,' ').trim().slice(0,300);
 if(!query||query===item.id)return;
 featureClose(false);$('query').value=query;setTab('videos');openDiscovery();return searchCurrentTab(item.id);
}
function featurePlay(item,position=0){featureResumeStart={id:item.id,position};featureClose(false);closeDiscovery();play(item.id,item.title,Boolean(item.live),item.channel)}
window.orbitzPeekPaused=()=>featurePauseOnStart;
window.orbitzVideoPaused=()=>{const paused=featurePauseOnStart;featurePauseOnStart=false;return paused};
window.orbitzVideoStart=id=>{if(featureResumeStart?.id!==id)return 0;const position=featureResumeStart.position;featureResumeStart=null;return position};
window.orbitzBeforeVideo=()=>{featureSaveProgress();clearTimeout(featureProgressTimer);featureProgressTimer=0};
window.orbitzOnVideo=(id,title,live=false,channel='')=>{featureChannel=channel||'';featureLive=Boolean(live);featureResumeDismissed=false;featureTrackStarted=false;featureForceStopped=false;featureTitle=title||id;featureLastStatus=-1;
 const start=featureResumeStart?.id===id?featureResumeStart.position:0;
 const duration=featureState.resume?.id===id?featureState.resume.duration:0;
 const remembered={op:'remember',video:{id,title:title||id,...(featureChannel?{channel:featureChannel}:{})},position:start,duration,live:featureLive};
 featureTask(()=>api('local-state',remembered)).catch(()=>{});
 featureResume.hidden=true;featureRender();
 if(!featureChannel)featureMetadata({id}).then(details=>{
  if(!featureAlive||selected!==id||!details?.channel)return;
  featureChannel=details.channel;featureMutate({op:'resume-metadata',video:{id,title:featureTitle,channel:featureChannel}}).catch(()=>{});
 });};
function featureSaveProgress(){
 if(!selected||!playerReady||!youtubePlayer)return Promise.resolve();
 const actual=youtubePlayer.getVideoData?.().video_id;if(actual!==selected)return Promise.resolve();
 const position=youtubePlayer.getCurrentTime?.()||0,duration=youtubePlayer.getDuration?.()||0,item=featureCurrent();
 featureProgressLatest={op:'progress',video:item,position,duration,live:featureLive,restart:featureForceStopped||featureLastStatus===0};
 if(featureProgressPending)return featureProgressPending;
 featureProgressPending=featureTask(()=>api('local-state',featureProgressLatest)).finally(()=>{featureProgressPending=null});
 return featureProgressPending;
}
function featurePublishMedia(seeked=false){
 const item=featureCurrent();if(!item||!playerReady)return;
 const actual=youtubePlayer.getVideoData?.().video_id;if(actual!==selected)return;
 const status=featureForceStopped?'Stopped':featureLastStatus===1?'Playing':[2,3,5].includes(featureLastStatus)?'Paused':'Stopped';
 return api('media-state',{...item,status,seeked,live:featureLive,restart:featureForceStopped||featureLastStatus===0,rate:youtubePlayer.getPlaybackRate?.()||1,position:youtubePlayer.getCurrentTime?.()||0,duration:youtubePlayer.getDuration?.()||0,volume:youtubePlayer.isMuted?.()?0:(youtubePlayer.getVolume?.()??100)/100,next:featureState.queue.length>0}).catch(()=>{});
}
function featureScheduleProgress(){
 clearTimeout(featureProgressTimer);featureProgressTimer=0;
 if(featureLastStatus!==1||!featureAlive)return;
 featureProgressTimer=setTimeout(()=>{featureProgressTimer=0;featureSaveProgress().catch(()=>{});featurePublishMedia();featureScheduleProgress()},15000);
}
window.orbitzOnPlayerState=state=>{
 if(youtubePlayer?.getVideoData?.().video_id!==selected)return;
 if(youtubePlayer.getPlayerState&&youtubePlayer.getPlayerState()!==state)return;
 if(state===1&&featurePauseOnStart){featurePauseOnStart=false;youtubePlayer.pauseVideo();return;}
 if(state===1){featureForceStopped=false;featureTrackStarted=true;}
 featureLastStatus=state;if(state===1){const title=youtubePlayer?.getVideoData?.().title;if(title)featureTitle=title.slice(0,300);const author=youtubePlayer?.getVideoData?.().author;if(author)featureChannel=author.slice(0,200)}
 featureScheduleProgress();featurePublishMedia();
 if([0,2].includes(state))featureSaveProgress().catch(()=>{});
 if(state===0&&featureTrackStarted){featureTrackStarted=false;featureNext();}
};
async function featureNext(options=null){
 if(featureAdvancePending)return;
 featureAdvancePending=true;
 try{const result=await featureMutate({op:'queue-next'});if(result.next){featurePauseOnStart=options?.keepPaused===true;featurePlay(result.next);}}catch{featureError()}finally{featureAdvancePending=false}
}
window.orbitzMediaCommand=(command,value)=>{
 if(command==='next'){featureNext(value);return}
 if(!selected||!playerReady||!youtubePlayer)return;
 if(command==='playpause'){youtubePlayer.getPlayerState()===1?youtubePlayer.pauseVideo():youtubePlayer.playVideo()}
 else if(command==='play')youtubePlayer.playVideo();else if(command==='pause')youtubePlayer.pauseVideo();else if(command==='stop'){featureForceStopped=true;youtubePlayer.stopVideo();featureSaveProgress().catch(()=>{});featurePublishMedia();}
 else if(command==='seek'||command==='previous')youtubePlayer.seekTo(Math.max(0,(youtubePlayer.getCurrentTime()||0)+(command==='previous'?-10:Number(value)||0)),true);
 else if(command==='position')youtubePlayer.seekTo(Math.max(0,Number(value)||0),true);
 else if(command==='mute'){youtubePlayer.isMuted()?youtubePlayer.unMute():youtubePlayer.mute()}
 else if(command==='volume'){youtubePlayer.setVolume(Math.max(0,Math.min(1,Number(value)||0))*100);if(Number(value)>0)youtubePlayer.unMute?.();}
 else if(command==='rate'&&youtubePlayer.getAvailablePlaybackRates?.().includes(Number(value)))youtubePlayer.setPlaybackRate(Number(value));
 clearTimeout(featureMediaTimer);featureMediaTimer=setTimeout(()=>featurePublishMedia(['seek','position','previous'].includes(command)),250);
};
window.orbitzOnRateChange=()=>featurePublishMedia();
async function featureTransfer(mode){
 if(featureTransferPending)return;featureTransferPending=true;
 $('feature-local-status').textContent='';
 try{const result=await featureTask(()=>api('library-transfer',{mode}));if(result.preferences){featureState=result;featureRender()}if(!result.cancelled)uiText($('feature-local-status'),mode==='import'?'youtube.imported':'youtube.exported')}catch{uiText($('feature-local-status'),'youtube.local_failed')}finally{featureTransferPending=false}
}
const featureMetadataRequests=new Map();
function featureMetadata(item){
 if(!item||item.channel)return Promise.resolve(item);
 if(!featureMetadataRequests.has(item.id))featureMetadataRequests.set(item.id,api('video-details',{id:item.id}).catch(()=>null));
 return featureMetadataRequests.get(item.id);
}
async function featureEnrichResume(){
 const original=featureState.resume;if(!original||original.channel)return;
 const details=await featureMetadata(original);
 if(!details?.channel||!featureAlive)return;
 await featureMutate({op:'resume-metadata',video:details});
}
window.orbitzResumeOffered=()=>Boolean(window.orbitzGamesHome&&featureState.resume);
window.orbitzRefreshResume=async()=>{await featureSaveProgress();const current=await api('local-state',{});if(window.orbitzGamesHome){featureState=current;featureRender()}};
function featureDismissResume(){featureResumeDismissed=true;featureRender()}
function featureRender(){
 const wasHidden=featureResume.hidden;
 featureResume.replaceChildren();featureResume.hidden=false;
 if(wasHidden!==featureResume.hidden)syncChrome();
 if(featureState.resume){const item=featureState.resume,label=document.createElement('span');const title=document.createElement('strong');title.textContent=item.title||item.id;label.append(title);if(item.channel){const channel=document.createElement('small');channel.textContent=' ('+item.channel+')';label.append(channel)}label.className='feature-resume-copy'+(Array.from(label.textContent).length>40?' compact':'');const thumbnail=featureThumb(item);thumbnail.classList.add('feature-resume-thumb');thumbnail.onerror=()=>{thumbnail.hidden=true};featureResume.append(thumbnail,label,featureButton('continue_watching',()=>featurePlay(item,item.position)))}
 if(!featureState.resume){const empty=document.createElement('span');uiText(empty,'youtube.keep_watching_empty');featureResume.append(empty)}
 if(featurePanel.hidden)return;
 const focusIndex=[...featurePanel.querySelectorAll('button')].filter(button=>!button.disabled&&button.offsetParent!==null).indexOf(document.activeElement);
 featureCloseMenu();
 const libraryView=['favorites','later','queue'].includes(featureView);
 uiText($('feature-title'),'youtube.'+(featureView==='diagnostics'?'diagnostics':featureView==='shortcuts'?'shortcuts':'library'));
 uiAttr($('feature-close'),'aria-label','youtube.close_settings');
 featureHeader.setAttribute('aria-expanded','true');
 const item=featureCurrent();$('feature-current').hidden=!item||!libraryView;
 $('feature-current-title').textContent=item?item.title:'';if(item)$('feature-current-title').title=item.title;
 $('feature-current-image').replaceChildren();$('feature-current-actions').replaceChildren();
 if(item&&libraryView){
  $('feature-current-image').append(featureThumb(item));uiText($('feature-now-label'),'youtube.current_video');
  const saved=featureState.favorites.some(v=>v.id===item.id);
  const star=featureIconButton(saved?'saved_favorite':'favorite','star',()=>featureMutate({op:saved?'remove':'save',kind:'favorites',video:item}));
  star.setAttribute('aria-pressed',String(saved));$('feature-current-actions').append(star,featureIconButton('more_actions','more',event=>featureShowMenu(event.currentTarget,featureCurrentOptions(item))));
 }
 $('feature-nav').hidden=!libraryView;$('feature-nav').replaceChildren();
 for(const kind of ['favorites','later','queue']){
  const b=featureButton(kind,()=>{featureView=kind;featureRender()});
  b.setAttribute('aria-pressed',String(featureView===kind));
  const count=document.createElement('span');count.className='feature-count';count.textContent=featureState[kind].length;count.setAttribute('aria-hidden','true');b.append(count);$('feature-nav').append(b);
 }
 const list=$('feature-list');list.replaceChildren();$('feature-diagnostics').hidden=true;$('feature-transfer').replaceChildren();$('feature-transfer').hidden=!libraryView;
 if(featureView==='diagnostics'){
  $('feature-diagnostics').hidden=false;uiText($('feature-diagnostics'),'youtube.loading_diagnostics');
  api('diagnostics',{}).then(result=>{if(featureView==='diagnostics'&&!featurePanel.hidden)$('feature-diagnostics').textContent=JSON.stringify(result,null,2)}).catch(()=>uiText($('feature-diagnostics'),'youtube.local_failed'));featureRestoreFocus(focusIndex);return;
 }
 if(featureView==='shortcuts'){const help=document.createElement('p');help.className='feature-help';uiText(help,'youtube.shortcuts_help');list.append(help);featureRestoreFocus(focusIndex);return}
 const rows=featureState[featureView]||[];
 if(!rows.length){const empty=document.createElement('div');empty.className='feature-empty';const title=document.createElement('strong'),hint=document.createElement('p');uiText(title,'youtube.empty_'+featureView);uiText(hint,'youtube.empty_'+featureView+'_hint');empty.append(featureIcon(featureView==='favorites'?'star':featureView==='queue'?'queue':'clock'),title,hint);list.append(empty)}
 rows.forEach((row,index)=>{
  const element=document.createElement('div');element.className='feature-row';
  const playButton=document.createElement('button');playButton.type='button';playButton.className='feature-play';playButton.title=row.title||row.id;
  const copy=document.createElement('span');copy.className='feature-item-copy';const title=document.createElement('span');title.className='feature-item-title';title.textContent=row.title||row.id;
  const meta=document.createElement('small');meta.className='feature-item-meta';meta.textContent=featureView==='queue'?String(index+1).padStart(2,'0')+' · YouTube':'YouTube';copy.append(title,meta);playButton.append(featureThumb(row),copy);playButton.onclick=()=>featurePlay(row);element.append(playButton);
  if(featureView!=='queue')element.append(featureIconButton('add_queue','queue',async()=>{await featureQueue(row);uiText($('feature-local-status'),'youtube.added_queue')}));
  const kind=featureView;
  const actions=[];
  if(kind==='queue'){
   if(index>0)actions.push({key:'move_up_label',icon:'up',run:()=>featureMutate({op:'queue-up',qid:row.qid})});
   if(index<rows.length-1)actions.push({key:'move_down_label',icon:'down',run:()=>featureMutate({op:'queue-down',qid:row.qid})});
  }else actions.push({key:'add_queue',icon:'queue',run:()=>featureQueue(row)});
  actions.push({key:'similar_videos',icon:'similar',run:()=>featureSimilar(row)});
  actions.push({key:'remove',icon:'trash',danger:true,run:()=>featureMutate(kind==='queue'?{op:'queue-remove',qid:row.qid}:{op:'remove',kind,video:row})});
  element.append(featureIconButton('more_actions','more',event=>featureShowMenu(event.currentTarget,actions)));list.append(element);
 });
 const note=document.createElement('span');note.className='feature-footer-note';uiText(note,'youtube.library_local');$('feature-transfer').append(note);
 if(featureView==='queue'){$('feature-transfer').append(featureButton('next_video',featureNext));}
 const manage=featureButton('manage_library',event=>featureShowMenu(event.currentTarget,[{key:'import_library',icon:'import',run:()=>featureTransfer('import')},{key:'export_library',icon:'export',run:()=>featureTransfer('export')}]));manage.append(featureIcon('down'));$('feature-transfer').append(manage);
 uiPrune();featureRestoreFocus(focusIndex);
}

window.orbitzFeaturesLanguage=()=>{uiAttr(featureResume,'aria-label','youtube.continue_watching');featureRender();for(const scope of [featureRecommendationSettings])for(const n of scope.querySelectorAll('[data-i18n]'))uiText(n,n.dataset.i18n);$('feature-interests').placeholder=uiTr('youtube.interests_placeholder');uiText(featureSaveRecommendations,'youtube.save_interests');uiText(featureClearSearches,'youtube.clear_recent_searches');uiRaw(featureHeader,'');featureHeader.append(featureIcon('library'));uiAttr(featureHeader,'aria-label','youtube.library');uiAttr(featureHeader,'title','youtube.library');uiText(featureMenu,'youtube.library');uiText(featureDiagMenu,'youtube.diagnostics');uiText(featureShortcutMenu,'youtube.shortcuts')};
window.addEventListener('pagehide',()=>{featureAlive=false;clearTimeout(featureProgressTimer);clearTimeout(featureMediaTimer)});
(async()=>{
 $('always-above').disabled=true;
 try{
  featureState=await api('local-state',{});
  const recommendationPrefs=featureState.recommendation_preferences||{interests:[],use_recent:true};$('feature-interests').value=recommendationPrefs.interests.join(', ');$('feature-use-recent').checked=recommendationPrefs.use_recent;
  if(featureState.preferences.always_above&&!alwaysAbove)await $('always-above').onclick();
  window.orbitzFeaturesLanguage();featureEnrichResume().catch(()=>{});
 }catch{featureError()}finally{$('always-above').disabled=false}
})();
