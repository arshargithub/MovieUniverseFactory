// Local DOM-contract check only; no browser or production-media qualification.
const fs = require('fs');
const vm = require('vm');
const manifest = JSON.parse(fs.readFileSync('results/sikh391/GALLERY_MANIFEST.json', 'utf8'));
const html = fs.readFileSync(manifest.viewer_path, 'utf8');
if (Buffer.byteLength(html) >= 1024 * 1024) throw Error('Oversized gallery');
const source = html.match(/<script>([\s\S]*)<\/script>/)[1];
let checked = 0;
for (const saved of [null, {privateContent: {selected: 'inverse'}}, {privateContent: {selected: 'unknown-old-state'}}]) {
  const nodes = {};
  const buttons = [];
  const persisted = [];
  function element() {
    return {dataset: {}, children: [], attrs: {},
      addEventListener(k, fn) {this[k] = fn;},
      setAttribute(k, v) {this.attrs[k] = v;},
      appendChild(x) {this.children.push(x);}};
  }
  for (const id of ['#r391-image', '#r391-caption', '#r391-experiments', '#r391-context']) nodes[id] = element();
  const root = {querySelector(id) {if (!nodes[id]) throw Error('Unknown selector ' + id); return nodes[id];}};
  const context = {document: {
    getElementById(id) {if (id !== 'rearing391') throw Error('Unknown root'); return root;},
    createElement() {const x = element(); buttons.push(x); return x;}
  }, window: {addEventListener() {}, openai: {
    widgetState: saved,
    setWidgetState(state) {persisted.push(state); return Promise.resolve();}
  }}};
  vm.runInNewContext(source, context);
  if (!nodes['#r391-image'].src) throw Error('Initial image missing');
  if (persisted.length) throw Error('State saved on load');
  if (buttons.length !== manifest.items.length) throw Error('Wrong choice count');
  for (const button of buttons) {
    button.click();
    if (button.attrs['aria-pressed'] !== 'true') throw Error('Selection failed');
    if (!nodes['#r391-image'].src.startsWith('data:image/jpeg;base64,')) throw Error('Image missing');
    if (!nodes['#r391-caption'].textContent) throw Error('Caption missing');
    checked += 1;
  }
  if (persisted.length !== buttons.length) throw Error('State persistence failed');
}
const result = {image_choices: manifest.items.length, selection_checks: checked,
  initial_states: 3, status: 'PASS', bytes: Buffer.byteLength(html),
  limits: 'DOM-contract harness, not a real-browser screenshot or mobile-playback qualification.'};
fs.writeFileSync('results/sikh391/GALLERY_VALIDATION.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
