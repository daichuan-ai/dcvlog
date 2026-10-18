const { test } = require('node:test');
const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const { handleEvent, persistToCloudbase } = require('../cloudbase/review-collector/index');

const id = randomUUID();
const env = { PILOT_DEVICE_IDS: id };
const valid = () => ({
  httpMethod: 'POST',
  body: JSON.stringify({ submission_id: randomUUID(), anonymous_id: id,
    consent: true, consent_version: '2026-10-18-v1', skill_version: '1.8.7',
    client_count: 3, draft_status: 'ready',
    final_text: '今天来的这位姑娘去过生日，她想配合自己的裙子，但不想画得太浓，所以我给她保留原本的轻盈感。',
    facts_summary: '生日；希望自然；减轻眼妆；看到了照片里的轻盈感。',
  }),
});

test('a consented pilot device can submit and the teacher sees the full text', async () => {
  let written;
  const out = await handleEvent(valid(), env, async row => { written = row; });
  assert.equal(out.statusCode, 200);
  assert.equal(JSON.parse(out.body).accepted, true);
  assert.match(written.final_text, /生日/);
  assert.equal(written.skill_version, '1.8.7');
});

test('no consent, no record', async () => {
  const event = valid();
  const body = JSON.parse(event.body);
  body.consent = false;
  event.body = JSON.stringify(body);
  let calls = 0;
  const out = await handleEvent(event, env, async () => { calls++; });
  assert.equal(out.statusCode, 403);
  assert.equal(calls, 0);
});

test('rejects other devices and missing pilot whitelist', async () => {
  assert.equal((await handleEvent(valid(), {}, async () => {})).statusCode, 503);
  const event = valid();
  const body = JSON.parse(event.body);
  body.anonymous_id = randomUUID();
  event.body = JSON.stringify(body);
  assert.equal((await handleEvent(event, env, async () => {})).statusCode, 403);
});

test('public beta accepts other valid anonymous devices only when enabled', async () => {
  const event = valid();
  const body = JSON.parse(event.body);
  body.anonymous_id = randomUUID();
  event.body = JSON.stringify(body);
  let calls = 0;
  const out = await handleEvent(event, { REVIEW_PUBLIC_BETA: 'true' }, async () => { calls++; });
  assert.equal(out.statusCode, 200);
  assert.equal(calls, 1);
});

test('public beta still rejects requests without explicit consent', async () => {
  const event = valid();
  const body = JSON.parse(event.body);
  body.consent = false;
  event.body = JSON.stringify(body);
  let calls = 0;
  const out = await handleEvent(event, { REVIEW_PUBLIC_BETA: 'true' }, async () => { calls++; });
  assert.equal(out.statusCode, 403);
  assert.equal(calls, 0);
});

test('rejects too-large payload before reaching the database', async () => {
  const event = valid();
  event.body = 'x'.repeat(65537);
  assert.equal((await handleEvent(event, env, async () => {})).statusCode, 413);
});

test('returns neutral error when database is unavailable', async () => {
  const out = await handleEvent(valid(), env, async () => { throw Error('sensitive secret'); });
  assert.equal(out.statusCode, 503);
  assert.doesNotMatch(out.body, /sensitive secret/);
});

test('database adapter uses private token and ignores repeated submission IDs', async () => {
  const originalFetch = global.fetch;
  let call;
  global.fetch = async (url, init) => {
    call = { url, init };
    return { ok: true };
  };
  try {
    await persistToCloudbase({ submission_id: randomUUID(), final_text: '虚构内测内容' },
      { TCB_ENV: 'example-env', CLOUDBASE_APIKEY: 'server-only-placeholder' });
    assert.match(call.url, /on_conflict=submission_id/);
    assert.equal(call.init.headers.Authorization, 'Bearer server-only-placeholder');
    assert.match(call.init.headers.Prefer, /ignore-duplicates/);
  } finally {
    global.fetch = originalFetch;
  }
});
