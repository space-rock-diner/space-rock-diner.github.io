// お便りの受け口 (Cloudflare Pages Functions)。POST /api/otayori
// 本文とラジオネームを D1 の letters 表 (schema.sql) に 1 行入れる。送り主を特定する情報は保存しない。
// fetch から来たら JSON を、JavaScript の無いブラウザの普通の送信ならトップへの転送を返す。
const MAX_NAME = 40;
const MAX_BODY = 20000; // 400 字詰め原稿用紙 50 枚 (2026-09-14 所有者判断)。D1 の 1 行の上限 2 MB に対し、日本語で約 60 KB

const reply = (request, status, data) => {
  const wantsJson = (request.headers.get("accept") || "").includes("application/json");
  if (!wantsJson) {
    const to = new URL(data.ok ? "/#otayori-sent" : "/#otayori-failed", request.url);
    return Response.redirect(to.toString(), 303);
  }
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
};

// Turnstile の確認 (Cloudflare 公式の手順どおり)。成功・動作名・送信元のホスト名がすべて合うときだけ通す。
// 秘密鍵が無い・通信に失敗した・形が変、はすべて拒否する (= 確認できないものは受け付けない)
const TURNSTILE_ACTION = "otayori";

async function passesTurnstile(env, request, token) {
  const hostnames = new Set((env.TURNSTILE_HOSTNAMES || "").split(",").map((h) => h.trim()).filter(Boolean));
  if (!env.TURNSTILE_SECRET || hostnames.size === 0) return false;
  if (typeof token !== "string" || token.length === 0 || token.length > 2048) return false;
  let result;
  try {
    const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      signal: AbortSignal.timeout(10_000),
      body: new URLSearchParams({
        secret: env.TURNSTILE_SECRET,
        response: token,
        remoteip: request.headers.get("CF-Connecting-IP") || "",
      }),
    });
    if (!res.ok) return false;
    result = await res.json();
  } catch {
    return false;
  }
  return result.success === true && result.action === TURNSTILE_ACTION && hostnames.has(result.hostname);
}

export async function onRequestPost({ request, env, waitUntil }) {
  const origin = request.headers.get("origin");
  if (origin && new URL(origin).host !== new URL(request.url).host) {
    return reply(request, 403, { ok: false, error: "origin" });
  }
  if (!env.DB) return reply(request, 503, { ok: false, error: "not_ready" });
  let form;
  try {
    form = await request.formData();
  } catch {
    return reply(request, 400, { ok: false, error: "form" });
  }
  if ((form.get("website") || "").toString() !== "") {
    return reply(request, 200, { ok: true }); // 人には見えない欄が埋まっている = 機械。保存せずに捨てる
  }
  const name = (form.get("radio_name") || "").toString().trim();
  const body = (form.get("body") || "").toString().trim();
  if (!body) return reply(request, 400, { ok: false, error: "empty" });
  if (name.length > MAX_NAME || body.length > MAX_BODY) return reply(request, 400, { ok: false, error: "too_long" });
  if (!(await passesTurnstile(env, request, form.get("cf-turnstile-response")))) {
    return reply(request, 400, { ok: false, error: "turnstile" });
  }
  const episode = parseEpisode(form.get("episode"));
  await saveLetter(env.DB, name, body, episode);
  // 知らせは保存の後、返事を待たせずに送る (失敗しても手紙はもう保存されている)
  if (env.DISCORD_WEBHOOK_URL) waitUntil(notifyDiscord(env.DISCORD_WEBHOOK_URL, name, body, episode));
  return reply(request, 200, { ok: true });
}

// 届いたお便りを Discord のチャンネルに書く (ふたりが同時に気づけるように)。URL は Pages の Secret DISCORD_WEBHOOK_URL。
// 本文に @everyone などが書かれていても誰も呼び出さない (allowed_mentions を空に)。Discord の 1 通は 2000 字までなので長い手紙は途中まで
const DISCORD_LIMIT = 2000;
async function notifyDiscord(url, name, body, episode) {
  const head = `📮 お便りが届きました（${episode === null ? "番組へ" : `第${episode}回について`}）\n` +
    `ラジオネーム: ${name || "(なし)"}\n\n`;
  const room = DISCORD_LIMIT - head.length;
  const text = body.length <= room ? body : `${body.slice(0, room - 40)}\n\n（長いので途中まで。全文 ${body.length.toLocaleString("ja-JP")} 字）`;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      signal: AbortSignal.timeout(10_000),
      body: JSON.stringify({ content: head + text, allowed_mentions: { parse: [] } }),
    });
    if (!res.ok) console.error("otayori: Discord への知らせが失敗", res.status);
  } catch (e) {
    console.error("otayori: Discord への知らせが失敗", String(e && e.message));
  }
}

// 回のページから「第N回について」のチェックを入れたまま送ると N が来る。無い・形が変なら回を決めない (拒否はしない)
function parseEpisode(value) {
  const s = (value || "").toString().trim();
  return /^[1-9][0-9]{0,3}$/.test(s) ? Number(s) : null;
}

async function saveLetter(db, name, body, episode) {
  const at = new Date().toISOString();
  const insertPlain = (text) => db.prepare("INSERT INTO letters (created_at, radio_name, body) VALUES (?, ?, ?)")
    .bind(at, name, text).run();
  if (episode === null) {
    await insertPlain(body);
    return;
  }
  const insert = () => db.prepare("INSERT INTO letters (created_at, radio_name, body, episode) VALUES (?, ?, ?, ?)")
    .bind(at, name, body, episode).run();
  try {
    await insert();
  } catch (err) {
    try {
      // episode 欄は 2026-09-24 に足した。それより前に作った D1 には欄が無いので、最初の回つきのお便りでここが足す
      // (= 欄を足す作業を wrangler のあるマシンに頼らない。2 通が同時に来て片方が先に足しても、もう片方は重複で落ちるだけ)
      if (!/no column named episode|no such column: episode/i.test(String(err && err.message))) throw err;
      try {
        await db.prepare("ALTER TABLE letters ADD COLUMN episode INTEGER").run();
      } catch (e) {
        if (!/duplicate column/i.test(String(e && e.message))) throw e;
      }
      await insert();
    } catch (e2) {
      // 回の欄に入れられなくても手紙は失わない: 回の番号を本文の頭に書いて、回を決めない形で入れる
      // (ここまで来るのは想定外 = Cloudflare の log に残す。お便りを読む側は本文の頭で回が分かる)
      console.error("otayori: episode の欄に入れられなかった", String(e2 && e2.message));
      await insertPlain(`［第${episode}回について］\n${body}`);
    }
  }
}

export const onRequest = ({ request }) => reply(request, 405, { ok: false, error: "method" });
