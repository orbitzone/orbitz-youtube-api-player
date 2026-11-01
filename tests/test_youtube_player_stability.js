const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('app/index.html','utf8'),nodes=new Map();
for(const id of ['runner','screen','copy-video-link','external','status'])nodes.set(id,{hidden:true,replaceChildren(){},append(){}});
let events;
const context=vm.createContext({$:id=>nodes.get(id),window:{YT:{Player:function(frame,options){events=options.events;}}},document:{createElement:()=>({})},location:{origin:'http://127.0.0.1:1234'},encodeURIComponent,notifyWindowState(){},syncControls(){},stopPlaybackRetry(){},startSelectedVideo(){},syncExternalVideoLink(){},uiRaw(){},uiText(){},uiAttr(){},uiErrorText(){},selected:'',youtubePlayer:null,playerReady:false,playbackRequest:0});
vm.runInContext(html.slice(html.indexOf('async function play('),html.indexOf("\nlet activeTab=")),context);
(async()=>{
 await context.play('abcdefghijk','Synthetic');
 assert.equal(nodes.get('copy-video-link').hidden,false);assert.equal(nodes.get('external').hidden,false);
 for(const data of [-1,3,1,3,2,1,0,5]){events.onStateChange({data});assert.equal(nodes.get('copy-video-link').hidden,false,`stable copy button in player state ${data}`);assert.equal(nodes.get('external').hidden,false,`stable external link in player state ${data}`);}
 events.onAutoplayBlocked();assert.equal(nodes.get('copy-video-link').hidden,false);assert.equal(nodes.get('external').hidden,false);
 events.onError();assert.equal(nodes.get('copy-video-link').hidden,false);assert.equal(nodes.get('external').hidden,false);
 assert.match(html,/header>#copy-video-link\[hidden\]\{display:inline-flex;visibility:hidden;pointer-events:none\}/,'copy button always reserves header space');
 console.log('OK: copy-link stays stable across playback, buffering, pause, end and error events; header reserves its space.');
})().catch(error=>{console.error(error);process.exitCode=1});
