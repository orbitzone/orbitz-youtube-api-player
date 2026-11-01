const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('app/index.html','utf8'),start=html.indexOf("let activeTab='videos'"),end=html.indexOf("$('videos-tab').onclick",start),recStart=html.indexOf('async function loadRecommendations'),recEnd=html.indexOf("$('query').addEventListener('input'",recStart);
const names=['videos','shorts','live','podcasts'],nodes=new Map();
for(const id of ['results','status','query','submit',...names.map(x=>x+'-tab')])nodes.set(id,{hidden:false,value:'',disabled:false,setAttribute(){},replaceChildren(){}});
const requests=[],rendered=[];
const context=vm.createContext({window:{},$:id=>nodes.get(id),AbortController,setTimeout:fn=>{fn();return 1},clearTimeout(){},api:(action,body,signal)=>new Promise(resolve=>requests.push({action,body,signal,resolve})),renderResults:items=>rendered.push(items),uiPrune(){},uiText(node,key){node.key=key},uiTr:key=>key,uiErrorText(){},play(){},videoId:()=>''});
vm.runInContext("let selected='',sequence=0;"+html.slice(start,end)+html.slice(recStart,recEnd),context);
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
(async()=>{
 context.setTab('videos');context.setTab('shorts');assert(requests[0].signal.aborted);
 requests[0].resolve({items:[{id:'old'}]});await flush();assert.equal(rendered.length,0);
 assert.equal(requests[1].body.mode,'shorts');requests[1].resolve({items:[{id:'short'}],basis:'personalized',terms:['music']});await flush();assert.equal(rendered.at(-1)[0].id,'short');
 context.setTab('live');context.setTab('podcasts');assert(requests[2].signal.aborted);
 requests[2].resolve({items:[{id:'late-live'}]});await flush();assert.equal(rendered.length,1);
 requests[3].resolve({items:[{id:'podcast'}]});await flush();assert.equal(rendered.at(-1)[0].id,'podcast');
 assert.deepEqual(requests.map(r=>r.body.mode),names);
 console.log('OK: recommendations load in all four categories; stale and aborted responses never overwrite the active tab.');
})().catch(error=>{console.error(error);process.exitCode=1});
