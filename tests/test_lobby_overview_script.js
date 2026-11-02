const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const source = require('node:fs').readFileSync(require('node:path').join(__dirname,'../static/lobby-overview.js'),'utf8');

function fixture() {
  const handlers = {};
  const timers = [];
  const error = {hidden:true};
  const retry = {addEventListener: (event, fn) => {handlers.retry = fn;}};
  const state = {signature:'same',fail:false,hidden:false};
  let reloads = 0;
  let requests = 0;
  const page = {dataset:{statusUrl:'/overview',signature:'same'},
    querySelector: selector => selector === '[data-overview-error]' ? error : retry,
    addEventListener: (event,fn) => {handlers[event] = fn;}};
  vm.runInNewContext(source, {
    document:{querySelector:()=>page,get hidden(){return state.hidden;},addEventListener:(event,fn)=>{handlers[event]=fn;}},
    location:{reload:()=>{reloads++;}},addEventListener:(event,fn)=>{handlers[event]=fn;},
    setTimeout: fn=>{timers.push(fn);return timers.length;},clearTimeout:()=>{},
    fetch:async ()=>{requests++;if(state.fail) throw new Error('offline');return {ok:true,status:200,redirected:false,json:async()=>({signature:state.signature})};}
  });
  return {state,handlers,error,poll:timers[0],reloads:()=>reloads,requests:()=>requests};
}

test('room changes reload once; unchanged state keeps the overview stable',async()=>{
  const f=fixture();await f.poll();assert.equal(f.reloads(),0);
  f.state.signature='new membership';await f.poll();assert.equal(f.reloads(),1);
});
test('an interruption preserves the overview and retry clears its common error',async()=>{
  const f=fixture();f.state.fail=true;await f.poll();assert.equal(f.error.hidden,false);assert.equal(f.reloads(),0);
  f.state.fail=false;await f.handlers.retry();assert.equal(f.error.hidden,true);
});
test('hidden tabs pause requests and a submitted join never triggers a stale reload',async()=>{
  const f=fixture();f.state.hidden=true;await f.poll();assert.equal(f.requests(),0);
  f.state.hidden=false;f.state.signature='another room';f.handlers.submit();await f.poll();
  assert.equal(f.requests(),0);assert.equal(f.reloads(),0);
});
test('returning through browser history resumes overview updates',async()=>{
  const f=fixture();f.handlers.submit();await f.poll();assert.equal(f.requests(),0);
  await f.handlers.pageshow({persisted:true});assert.equal(f.requests(),1);
});
