// Drive the huashu-motion studio over CDP: press C, click the frame, type, send.
// No dependencies — Node 22 has a global WebSocket.
//
//   node tools/drive_studio.mjs <studio-url> <out-dir> [x] [y]
//
// The point is to exercise the real comment loop the way a person does it: a keyboard event on the
// document, a mouse click on the stage at composition coordinates, text typed into the composer, and
// the send button clicked. Screenshots are taken around each step so the evidence is the UI itself,
// not a log line.
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const [url, outDir, px, py] = process.argv.slice(2);
const PORT = Number(process.env.CDP_PORT || 9222);
mkdirSync(outDir, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function targets() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await r.json();
      const page = list.find((t) => t.type === 'page' && /^https?:/.test(t.url));
      if (page) return page;
    } catch { /* chrome not up yet */ }
    await sleep(500);
  }
  throw new Error('no CDP page target');
}

const page = await targets();
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let id = 0;
const waiters = new Map();
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && waiters.has(m.id)) { waiters.get(m.id)(m); waiters.delete(m.id); }
};
const send = (method, params = {}) => new Promise((res) => {
  const n = ++id;
  waiters.set(n, res);
  ws.send(JSON.stringify({ id: n, method, params }));
});
const evaluate = async (expr) => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  return r.result?.result?.value;
};
const shot = async (name) => {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(join(outDir, name), Buffer.from(r.result.data, 'base64'));
  console.log('shot', name);
};

await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url });
await sleep(2500);
for (let i = 0; i < 30; i++) {
  if (await evaluate("!!document.querySelector('#stage') && !!window.__filmTimeline || document.querySelectorAll('#stage').length > 0")) break;
  await sleep(500);
}
await sleep(1200);
console.log('ready:', await evaluate('document.title'));

const stage = await evaluate(`(() => {
  const r = document.querySelector('#stage').getBoundingClientRect();
  const img = document.querySelector('#stage');
  return { x: r.x, y: r.y, w: r.width, h: r.height, title: document.title };
})()`);
console.log('stage', JSON.stringify(stage));
await shot('studio-01-editor.png');

// press C — the comment tool
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'c', code: 'KeyC', windowsVirtualKeyCode: 67, text: 'c' });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'c', code: 'KeyC', windowsVirtualKeyCode: 67 });
await sleep(500);
console.log('tool:', await evaluate("document.body.dataset.tool || (document.querySelector('.tool.active') || {}).textContent || 'unknown'"));
await shot('studio-02-comment-tool.png');

// click the composition at (px, py) in 1920x1080 space, mapped onto the stage
const cx = Number(px || 620), cy = Number(py || 500);
const x = Math.round(stage.x + (cx / 1920) * stage.w);
const y = Math.round(stage.y + (cy / 1080) * stage.h);
console.log('click at', x, y);
for (const type of ['mousePressed', 'mouseReleased']) {
  await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 });
  await sleep(60);
}
await sleep(700);
await shot('studio-03-composer.png');
console.log('composer open:', await evaluate("!!document.querySelector('#composer') && !document.querySelector('#composer').hidden"));
console.log('ctx:', await evaluate("(document.querySelector('#composer-ctx')||{}).textContent || ''"));

// type the comment and send it
const text = '这一段比标题弱太多了，我想要更强的开场：让终端面板从下方冲进来，同时把数字 4 放大到能一眼看清';
await evaluate("const t=document.querySelector('#composer-text'); if(t){t.focus();}");
await send('Input.insertText', { text });
await sleep(300);
await shot('studio-04-typed.png');
await evaluate("document.querySelector('#composer-send').click()");
await sleep(1200);
await shot('studio-05-sent.png');
console.log('composer closed:', await evaluate("(document.querySelector('#composer')||{}).hidden === true"));
console.log('pending in UI:', await evaluate("document.querySelectorAll('.comment.pending').length"));

ws.close();
