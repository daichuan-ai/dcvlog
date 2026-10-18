"use strict";

// Separate opt-in content collector. No public read endpoint; inspect via SQL.
// Public beta accepts anonymous submissions only when explicitly enabled in
// server-side config. Consent is enforced by the client UI and request check;
// the HTTP caller's consent claim cannot independently prove human consent.
const { randomUUID } = require("node:crypto");
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const CONSENT_VERSION = "2026-10-18-v1";

function respond(statusCode, message, fields = {}) {
  return { statusCode, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
    body: JSON.stringify({ ...fields, message }) };
}

function maskContacts(text) {
  return text
    .replace(/(?<!\d)1[3-9]\d{9}(?!\d)/g, "[手机号已隐去]")
    .replace(/\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b/g, "[邮箱已隐去]")
    .replace(/(?<!\d)\d{17}[\dXx](?!\w)/g, "[身份证号已隐去]")
    .replace(/(?:微信号|微信|vx|v信|wechat)\s*[:：=]?\s*([a-z][\w-]{5,19})/gi, "[微信号已隐去]");
}

function validate(event, env) {
  if ((event?.httpMethod || "").toUpperCase() !== "POST") return { error: respond(405, "method_not_allowed") };
  let raw = event.body;
  if (typeof raw !== "string") return { error: respond(400, "invalid_json") };
  if (event.isBase64Encoded) raw = Buffer.from(raw, "base64").toString("utf8");
  if (Buffer.byteLength(raw, "utf8") > 65536) return { error: respond(413, "payload_too_large") };
  let data;
  try { data = JSON.parse(raw); } catch { return { error: respond(400, "invalid_json") }; }
  if (!data || typeof data !== "object" || Array.isArray(data)) return { error: respond(400, "invalid_data") };
  const allowed = new Set((env.PILOT_DEVICE_IDS || "").split(",").map(x => x.trim().toLowerCase()).filter(Boolean));
  const publicBetaEnabled = env.REVIEW_PUBLIC_BETA === "true";
  if (!publicBetaEnabled && !allowed.size) return { error: respond(503, "collector_not_enabled") };
  if (!UUID.test(data.anonymous_id || "") ||
      (!publicBetaEnabled && !allowed.has(data.anonymous_id.toLowerCase()))) {
    return { error: respond(403, "device_not_in_pilot") };
  }
  if (data.consent !== true || data.consent_version !== CONSENT_VERSION) {
    return { error: respond(403, "consent_required") };
  }
  if (!UUID.test(data.submission_id || "") || !/^\d+\.\d+\.\d+$/.test(data.skill_version || "") ||
      data.skill_version !== "1.8.7" || !Number.isInteger(data.client_count) ||
      data.client_count < 1 || data.client_count > 20 || !["ready", "limited"].includes(data.draft_status) ||
      typeof data.final_text !== "string" || typeof data.facts_summary !== "string") {
    return { error: respond(400, "invalid_fields") };
  }
  const finalText = maskContacts(data.final_text.trim());
  const facts = maskContacts(data.facts_summary.trim());
  if (finalText.length < 20 || finalText.length > 12000 || facts.length > 1600) {
    return { error: respond(400, "invalid_length") };
  }
  return { row: { submission_id: data.submission_id, anonymous_id: data.anonymous_id,
    skill_version: data.skill_version, client_count: data.client_count,
    draft_status: data.draft_status, final_text: finalText, facts_summary: facts,
    consent_version: data.consent_version } };
}

async function persistToCloudbase(row, env) {
  if (!env.TCB_ENV || !env.CLOUDBASE_APIKEY) throw new Error("database_not_configured");
  if (!/^[a-zA-Z0-9-]+$/.test(env.TCB_ENV)) throw new Error("invalid_environment");
  const url = `https://${env.TCB_ENV}.api.tcloudbasegateway.com/v1/rdb/rest/dcvlog_draft_reviews?on_conflict=submission_id`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.CLOUDBASE_APIKEY}`,
      "Content-Type": "application/json",
      "Prefer": "return=minimal,resolution=ignore-duplicates",
    },
    body: JSON.stringify(row),
    // Keep the outbound DB request inside the 3-second Personal-plan function limit.
    signal: AbortSignal.timeout(1800),
  });
  if (!response.ok) throw new Error("database_write_failed");
}

async function handleEvent(event, env = process.env, persist = persistToCloudbase) {
  const result = validate(event, env);
  if (result.error) return result.error;
  try {
    await persist(result.row, env);
    return respond(200, "accepted", { accepted: true, submission_id: result.row.submission_id });
  } catch {
    // Do not log the request, generated prose, client details or credentials.
    return respond(503, "temporarily_unavailable", { accepted: false, request_id: randomUUID() });
  }
}

exports.main = async (event) => handleEvent(event);
exports.handleEvent = handleEvent;
exports.maskContacts = maskContacts;
exports.persistToCloudbase = persistToCloudbase;
