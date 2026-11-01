const assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync('app/index.html','utf8');
const nav=html.match(/<nav id="view-tabs"[\s\S]*?<\/nav>/)?.[0];assert(nav);
assert.deepEqual([...nav.matchAll(/<button id="([a-z]+)-tab"/g)].map(match=>match[1]),['videos','shorts','live','podcasts']);
for(const mode of ['videos','shorts','live','podcasts']){
 const button=nav.match(new RegExp('<button id="'+mode+'-tab"[\\s\\S]*?<\\/button>'))[0];
 assert(button.includes('data-i18n-aria-label="youtube.'+mode+'"'));assert(button.includes('data-i18n-title="youtube.'+mode+'"'));
 assert.match(button,/<svg class="filter-icon" aria-hidden="true" focusable="false" viewBox="[^"]+"><path d="[^"]+"\/>/);
 assert(button.includes('class="filter-label" data-i18n="youtube.'+mode+'"'));
 for(const locale of ['pt-BR','en-US'])assert(JSON.parse(fs.readFileSync('i18n/'+locale+'.json','utf8'))['youtube.'+mode]);
}
assert.match(html,/@media\(max-width:640px\)\{#view-tabs\{width:44px;gap:4px\}[\s\S]*?\.filter-label\{display:none\}/);
assert.match(html,/#view-tabs\{min-height:0;overflow-y:auto;padding:2px\}/);
assert(!html.includes('comments'),'comments UI, handlers and requests are completely absent');
for(const file of ['material-icons-LICENSE.txt','simple-icons-LICENSE.txt'])assert(fs.statSync('data/licenses/'+file).size>1000);
assert(fs.readFileSync('Makefile','utf8').includes('data/licenses/*.txt'));
assert(fs.readFileSync('THIRD_PARTY_NOTICES.md','utf8').includes('Simple Icons'));
console.log('OK: four inline SVG filters, compact breakpoint, localized accessible names/tooltips, removed comments and packaged icon licenses.');
