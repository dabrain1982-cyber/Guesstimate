import test from 'node:test';
import assert from 'node:assert/strict';
import { createRemoteTurn } from './remote-turn.js';

function session(status = 'completed') {
  const saved = Object.fromEntries(['fetch', 'window', 'document', 'setTimeout', 'clearTimeout'].map(key => [key, globalThis[key]]));
  const timers = [];
  const destinations = [];
  const requests = [];
  const replies = [];
  globalThis.window = { location: { assign: url => destinations.push(url) }, addEventListener() {} };
  globalThis.document = { querySelector: () => ({ textContent: '' }) };
  globalThis.setTimeout = callback => { timers.push(callback); return timers.length; };
  globalThis.clearTimeout = () => {};
  globalThis.fetch = async (url, options) => {
    requests.push({ url, options });
    const result = replies.shift();
    assert.ok(result, 'An unexpected request was sent');
    return { ok: result.ok !== false, json: async () => result };
  };
  const game = {
    winner: status === 'completed' ? { name: 'Gewinner' } : null,
    lobby: { is_host: true, leave_url: '/leave', rematch_url: '/again' },
  };
  const turn = createRemoteTurn({ game, revision: 10, statusUrl: '/status', csrfToken: 'csrf', backUrl: '/room', overviewUrl: '/overview' }, { territories: [] });
  return { turn, timers, destinations, requests, replies, dispose() {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete globalThis[key]; else globalThis[key] = value;
    }
  } };
}

test('A completed table keeps watching and follows the host back into the same room', async () => {
  const f = session();
  try {
    assert.equal(f.timers.length, 1);
    f.replies.push({ status: 'waiting', revision: 11 });
    await f.timers.shift()();
    assert.deepEqual(f.destinations, ['/room']);
    assert.equal(f.timers.length, 0);
  } finally { f.dispose(); }
});

test('Closing the lobby redirects another playing viewer to the overview', async () => {
  const f = session('playing');
  try {
    f.replies.push({ status: 'closed', revision: 11 });
    await f.timers.shift()();
    assert.deepEqual(f.destinations, ['/overview']);
    assert.equal(f.timers.length, 0);
  } finally { f.dispose(); }
});

test('Rematch and leaving use the authenticated lifecycle routes with the current revision', async () => {
  const f = session();
  try {
    f.replies.push({ redirect: '/room' });
    await f.turn.rematch();
    const request = f.requests[0];
    assert.equal(request.url, '/again');
    assert.equal(request.options.method, 'POST');
    assert.equal(request.options.body.get('revision'), '10');
    assert.equal(request.options.body.get('csrf_token'), 'csrf');
    f.replies.push({ redirect: '/overview' });
    await f.turn.leaveLobby();
    assert.equal(f.requests[1].url, '/leave');
    assert.deepEqual(f.destinations, ['/room', '/overview']);
  } finally { f.dispose(); }
});

test('A changed profile updates the table at the same game revision without sending an action', async () => {
  const f = session('playing');
  try {
    let notifications = 0;
    f.turn.subscribe(() => notifications++);
    const armies = [{ id: '1', name: 'Aktueller Name', portrait: { url: '/static/avatars/stage/a05-waschbaer.webp' } }];
    f.replies.push({ status: 'playing', revision: 10, game: { armies } });
    await f.timers.shift()();
    assert.equal(notifications, 1);
    assert.deepEqual(f.turn.armies, armies);
    f.replies.push({ status: 'playing', revision: 10, game: { armies } });
    await f.timers.shift()();
    assert.equal(notifications, 1, 'Identical profiles should not redraw');
    f.replies.push({ status: 'playing', revision: 9, game: { armies: [] } });
    await f.timers.shift()();
    assert.deepEqual(f.turn.armies, armies, 'An older reply cannot replace the current portrait');
    assert.equal(notifications, 1);
    assert.ok(f.requests.every(request => request.options.method !== 'POST'));
  } finally { f.dispose(); }
});
