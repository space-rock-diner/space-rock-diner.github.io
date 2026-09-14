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

async function passesTurnstile(env, token) {
  if (!env.TURNSTILE_SECRET) return true; // 秘密鍵を置くまでは検査しない
  if (!token) return false;
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token }),
  });
  const out = await res.json().catch(() => ({}));
  return out.success === true;
}

export async function onRequestPost({ request, env }) {
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
  if (!(await passesTurnstile(env, form.get("cf-turnstile-response")))) {
    return reply(request, 400, { ok: false, error: "turnstile" });
  }
  await env.DB.prepare("INSERT INTO letters (created_at, radio_name, body) VALUES (?, ?, ?)")
    .bind(new Date().toISOString(), name, body)
    .run();
  return reply(request, 200, { ok: true });
}

export const onRequest = ({ request }) => reply(request, 405, { ok: false, error: "method" });
