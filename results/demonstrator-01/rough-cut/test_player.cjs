const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('runs/demonstrator-01/cut-review/review.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements={};for(const id of ['film','exact','scrub','label','play','prev','next'])elements[id]={style:{},value:'0',textContent:''};
let callback;Object.assign(elements.film,{pause(){},play(){return Promise.resolve()},requestVideoFrameCallback(fn){callback=fn},currentTime:0,ended:false});
const pending=[];class Image{decode(){return new Promise((resolve,reject)=>pending.push({image:this,resolve,reject}))}}
const context={document:{getElementById:id=>elements[id]},window:{addEventListener(){}},Image,Math,Number,String};vm.createContext(context);vm.runInContext(script,context);
(async()=>{
 const first=context.exact(21);const second=context.exact(22);
 assert.strictEqual(elements.label.textContent,'');
 pending[1].resolve();await second;assert.match(elements.label.textContent,/Source frame 22 /);assert.match(elements.exact.src,/0022\.png$/);
 pending[0].resolve();await first;assert.match(elements.label.textContent,/Source frame 22 /);assert.match(elements.exact.src,/0022\.png$/);
 callback(0,{mediaTime:21/24});assert.match(elements.label.textContent,/Source frame 22 /);
 elements.play.onclick();assert.strictEqual(elements.film.currentTime,22/24);
 callback(0,{mediaTime:21/24});assert.match(elements.label.textContent,/Presented frame 21 /);
 const last=context.exact(900);pending[2].resolve();await last;assert.match(elements.label.textContent,/Source frame 575 /);
 console.log(JSON.stringify({passed:true,checks:['label waits for loaded PNG','out-of-order load cannot overwrite newer frame','hidden video callback cannot overwrite source label','video label follows presented timestamp','source index clamps to final frame']}));
})().catch(e=>{console.error(e);process.exitCode=1});
