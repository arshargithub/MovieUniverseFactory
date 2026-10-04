// Interaction contract only. Actual browser layout is not checked here.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(process.argv[2], 'utf8');
const script = html.match(/<script>([\s\S]+?)<\/script>/)[1];
class Element {
  constructor() { this.attributes = {}; this.style = {}; this.listeners = {}; this.children = []; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  appendChild(child) { this.children.push(child); }
  setAttribute(name, value) { this.attributes[name] = value; }
  click() { this.listeners.click(); }
}
const selectors = ['[data-image]', '[data-caption]', '[data-count]', '[data-views]', '[data-prev]', '[data-next]', '[data-enlarge]'];
const elements = Object.fromEntries(selectors.map(s => [s, new Element()]));
const root = {querySelector: s => { assert.ok(elements[s], s); return elements[s]; }};
const events = {}, saved = [];
const window = {openai: {widgetState: null, setWidgetState: state => {saved.push(state); return Promise.resolve();}},
  addEventListener: (name, fn) => { events[name] = fn; }};
vm.runInNewContext(script, {document: {getElementById: id => {assert.equal(id, 'pashtun-outer175'); return root;}, createElement: () => new Element()}, window});
const buttons = elements['[data-views]'].children;
assert.equal(buttons.length, 10);
const picture = elements['[data-image]'];
assert.ok(picture.src.startsWith('data:image/jpeg;base64,'));
const first = picture.src;
elements['[data-prev]'].click(); assert.equal(elements['[data-count]'].textContent, '2 / 10');
elements['[data-next]'].click(); assert.equal(picture.src, first);
buttons[5].click(); assert.equal(elements['[data-count]'].textContent, '6 / 10');
assert.equal(buttons[5].attributes['aria-pressed'], 'true');
elements['[data-enlarge]'].click(); assert.equal(picture.style.maxHeight, '680px');
events['openai:set_globals']({detail: {globals: {widgetState: {privateContent: {selected: 3, enlarged: false}}}}});
assert.equal(elements['[data-count]'].textContent, '4 / 10');
assert.equal(picture.style.maxHeight, '420px');
buttons[9].click(); elements['[data-next]'].click();
assert.equal(elements['[data-count]'].textContent, '1 / 10');
assert.equal(saved.length, 6);
assert.ok(saved.every(state => state.modelContent.candidate === 'outer175-diagnostic32' && state.modelContent.approval === 'failed_internal_review'));
console.log(JSON.stringify({views: 10, internal_visual_status: 'FAIL', navigation: true, direct_selection: true, enlargement: true, restored_state: true, browser_layout: 'NOT_RUN'}));
