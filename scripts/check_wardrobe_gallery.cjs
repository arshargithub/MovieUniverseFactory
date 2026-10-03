// Interaction check only; this does not claim browser layout verification.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const script = html.match(/<script>([\s\S]+?)<\/script>/)[1];
class Element {
  constructor() { this.dataset = {}; this.attributes = {}; this.listeners = {}; this.children = []; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  appendChild(child) { this.children.push(child); }
  setAttribute(name, value) { this.attributes[name] = value; }
  click() { this.listeners.click(); }
}
const elements = Object.fromEntries(['img', 'figcaption', '[data-count]', '.viz-controls', '[data-size]'].map(name => [name, new Element()]));
const arrows = [-1, 1].map(step => { const e = new Element(); e.dataset.step = String(step); return e; });
const root = new Element();
root.querySelector = name => { assert.ok(elements[name], name); return elements[name]; };
root.querySelectorAll = name => { assert.equal(name, '[data-step]'); return arrows; };
const events = {}; const saved = [];
const window = {openai: {widgetState: null, setWidgetState: state => {saved.push(state); return Promise.resolve();}}, addEventListener: (name, fn) => {events[name] = fn;}};
vm.runInNewContext(script, {document: {getElementById: id => {assert.equal(id, 'pashtun-wardrobe-fit-review'); return root;}, createElement: () => new Element()}, window});
const buttons = elements['.viz-controls'].children;
assert.equal(buttons.length, 12);
assert.ok(elements.img.src.startsWith('data:image/jpeg;base64,'));
const first = elements.img.src;
arrows[1].click(); assert.notEqual(elements.img.src, first);
arrows[0].click(); assert.equal(elements.img.src, first);
buttons[7].click(); assert.equal(elements['[data-count]'].textContent, '8 / 12');
elements['[data-size]'].click(); assert.equal(root.dataset.large, 'true');
events['openai:set_globals']({detail: {globals: {widgetState: {privateContent: {version: 'wardrobe169', index: 11, large: false}}}}});
assert.equal(elements['[data-count]'].textContent, '12 / 12');
assert.equal(root.dataset.large, 'false');
assert.equal(saved.length, 4);
console.log(JSON.stringify({views: 12, navigation: true, direct_selection: true, enlargement: true, restored_state: true, browser_layout: 'NOT_RUN'}));
