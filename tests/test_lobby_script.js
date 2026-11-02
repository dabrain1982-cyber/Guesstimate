const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');
const source = readFileSync(require('node:path').join(__dirname, '../static/lobby.js'), 'utf8');

function roomFixture({host = true, fail = false, gone = false} = {}) {
  const listeners = {};
  const timers = new Map();
  const requests = [];
  const server = {status: 'waiting', revision: 1, host_user_id: 1, members: [{id: 1}], name: 'Runde'};
  const hint = {textContent: ''};
  const title = {textContent: 'Runde'};
  const submitted = [];
  const form = {value: 'alt', dataset: {settingsUrl: '/settings'},
    querySelector: () => hint, addEventListener: (name, callback) => {listeners[name] = callback;},
    requestSubmit: button => {submitted.push(button);}};
  const room = {dataset: {statusUrl: '/status', overviewUrl: '/overview', lobbyState: 'waiting',
    lobbyHost: '1', memberCount: '1', memberSignature: '1', revision: '1', lobbyName: 'Runde'},
    querySelector: selector => selector === '[data-lobby-settings]' ? (host ? form : null) : selector === '[data-lobby-title]' ? title : {textContent: 'conquest'}};
  const navigation = [];
  let sequence = 0;
  vm.runInNewContext(source, {document: {querySelector: () => room},
    FormData: class {constructor(current) {this.value = current.value;}},
    window: {location: {assign: url => navigation.push(url), reload: () => navigation.push('reload')}},
    setTimeout: callback => {timers.set(++sequence, callback); return sequence;}, clearTimeout: id => timers.delete(id),
    fetch: async (url, options) => {
      if (url === '/settings') {
        requests.push(options.body.value);
        if (fail) return {ok: false};
        server.revision++;
      }
      return {ok: !gone, status: gone ? 410 : 200, json: async () => ({...server})};
    }});
  return {form, listeners, timers, requests, submitted, navigation, hint,
    allowSave: () => {fail = false;}};
}

test('rapid edits and start drain snapshots in order and retain the developer submitter', async () => {
  const fixture = roomFixture();
  fixture.form.value = 'erste Einstellung';
  fixture.listeners.change();
  fixture.form.value = 'zweite Einstellung';
  fixture.listeners.change();
  fixture.form.value = 'letzte Eingabe vor Start';
  const button = {name: 'developer_test', value: '1'};
  const start = fixture.listeners.submit({preventDefault() {}, submitter: button});
  assert.equal(fixture.submitted.length, 0);
  await start;
  assert.deepEqual(fixture.requests, ['erste Einstellung', 'zweite Einstellung', 'letzte Eingabe vor Start']);
  assert.deepEqual(fixture.submitted, [button]);
  assert.equal(fixture.hint.textContent, 'Gespeichert.');
});

test('a failed save preserves the form, blocks start and can be retried', async () => {
  const fixture = roomFixture({fail: true});
  const event = {preventDefault() {}, submitter: {name: 'start'}};
  fixture.form.value = 'bleibt erhalten';
  await fixture.listeners.submit(event);
  assert.equal(fixture.submitted.length, 0);
  assert.match(fixture.hint.textContent, /fehlgeschlagen/);
  assert.equal(fixture.form.value, 'bleibt erhalten');
  fixture.allowSave();
  await fixture.listeners.submit(event);
  assert.equal(fixture.submitted.length, 1);
});

test('a guest leaves an unavailable lobby for the overview without a reload loop', async () => {
  const fixture = roomFixture({host: false, gone: true});
  await [...fixture.timers.values()][0]();
  assert.deepEqual(fixture.navigation, ['/overview']);
});
