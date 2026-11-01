const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('app/index.html','utf8');
assert(!html.includes('youtubeAPI().catch(()=>{})'),'opening the app must not eagerly load third-party player code');
const nodes=new Map();for(const id of ['runner','screen','copy-video-link','external','status'])nodes.set(id,{hidden:true,replaceChildren(){},append(){}});
let requests=0;
const context=vm.createContext({$:id=>nodes.get(id),window:{},document:{createElement:()=>({})},location:{origin:'http://127.0.0.1:1234'},encodeURIComponent,notifyWindowState(){},syncControls(){},stopPlaybackRetry(){},startSelectedVideo(){},syncExternalVideoLink(){},uiRaw(){},uiText(){},uiAttr(){},uiErrorText(){},selected:'',youtubePlayer:null,playerReady:false,playbackRequest:0,youtubeAPI:async()=>{requests++;return{Player:function(){}}}});
vm.runInContext(html.slice(html.indexOf('async function play('),html.indexOf('\nlet activeTab=')),context);
(async()=>{
 assert.equal(requests,0);await context.play('abcdefghijk','Synthetic');assert.equal(requests,1,'first selection still loads the official iframe player');
 assert.equal(nodes.get('screen').hidden,false);assert.equal(nodes.get('runner').hidden,true);
 console.log('OK: official player API is loaded on first video selection, avoiding work during idle startup.');
})().catch(error=>{console.error(error);process.exitCode=1});
