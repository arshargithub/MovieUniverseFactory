// Offline interaction test for the small native-render comparison.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const text = fs.readFileSync('scripts/entrance200_review.template.html', 'utf8');
const sources = {before:{close:'bc',side:'bs',grip:'bg'},after:{close:'ac',side:'as',grip:'ag'}};
function button(data){return {dataset:data,attributes:{},listeners:{},textContent:'',setAttribute(k,v){this.attributes[k]=v},addEventListener(k,v){this.listeners[k]=v}}}
const versions=['before','after'].map(version=>button({version}));
const views=['close','side','grip'].map(view=>button({view}));
const size=button({}), img={}, caption={}, classes=new Set();
const root={querySelector(s){return {'img':img,'figcaption':caption,'[data-size]':size}[s]},querySelectorAll(s){return s==='[data-version]'?versions:views},classList:{toggle(n,v){v?classes.add(n):classes.delete(n)}}};
let state=null;const events={};
const window={openai:{widgetState:null,setWidgetState(s){state=s;return Promise.resolve()}},addEventListener(n,f){events[n]=f}};
const js=text.match(/<script>([\s\S]*?)<\/script>/)[1].replace('__IMAGES__',JSON.stringify(sources));
vm.runInNewContext(js,{document:{getElementById(id){assert.equal(id,'rider-treatment-200');return root}},window});
assert.equal(img.src,'ac');assert.equal(state,null);
versions[0].listeners.click();assert.equal(img.src,'bc');assert.equal(state.modelContent.version,'before');
views[2].listeners.click();assert.equal(img.src,'bg');assert.equal(state.modelContent.view,'grip');
size.listeners.click();assert(classes.has('expanded'));assert.equal(size.textContent,'Fit view');
events['openai:set_globals']({detail:{globals:{widgetState:{modelContent:{review:'rider-treatment-200',version:'after',view:'side'},privateContent:{expanded:false}}}}});
assert.equal(img.src,'as');assert(!classes.has('expanded'));
assert.equal(versions[1].attributes['aria-pressed'],'true');
console.log('Comparison controls, restoration and enlargement PASS; browser layout not tested here.');
