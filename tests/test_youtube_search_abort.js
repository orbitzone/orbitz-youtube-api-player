const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('app/index.html', 'utf8');
const start = html.indexOf("let activeTab='videos'");
const end = html.indexOf("$('videos-tab').onclick", start);
const names = ['videos', 'shorts', 'live', 'podcasts'];
const makeNode = () => ({
  hidden: false, value: '', disabled: false, tabIndex: -1, attributes: {},
  setAttribute(key, value) { this.attributes[key] = value; }, replaceChildren() {},
});
const nodes = new Map(['results', 'status', 'query', 'submit', 'view-tabs', ...names.map(name => `${name}-tab`)].map(id => [id, makeNode()]));
nodes.get('query').value = 'query in progress';
const controllers = [];
const context = vm.createContext({
  $: id => nodes.get(id), api: () => new Promise(() => {}),
  AbortController: class { signal = {}; aborted = false; constructor() { controllers.push(this); } abort() { this.aborted = true; } },
  setTimeout: callback => { callback(); return 1; }, clearTimeout() {},
  videoId: () => '', renderResults() {}, uiPrune() {}, uiText() {}, uiErrorText() {},
  loadRecommendations() {}, play() {},
});
vm.runInContext("let selected='',sequence=0;" + html.slice(start, end), context);
vm.runInContext("setTab('videos')", context);
assert.equal(nodes.get('submit').disabled, true, 'active search disables its submit button');
nodes.get('query').value='';
vm.runInContext("setTab('shorts')", context);
assert.equal(controllers[0].aborted, true, 'switching tabs aborts the previous frontend request');
assert.equal(nodes.get('submit').disabled, false, 'switching to an empty Shorts query restores the search button');
console.log('OK: leaving a pending search for an empty Shorts tab cancels the request and restores the Search button.');
