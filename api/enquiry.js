// Enquiry endpoint for the Fitz Feral Hunters site (Vercel Node function).
// Accepts the contact form two ways:
//   - JSON (fetch from the enhanced form)      → responds JSON {ok:true}
//   - application/x-www-form-urlencoded (no-JS) → responds with an HTML confirmation page
// If RESEND_API_KEY is set, the enquiry is emailed with Resend (https://resend.com) to ENQUIRY_TO;
// otherwise it is logged to the function logs so the flow can be tested before mail is configured.

const TO = process.env.ENQUIRY_TO || 'fitzferalhunters1@gmail.com';
const FROM = process.env.ENQUIRY_FROM || 'Fitz Feral Hunters site <onboarding@resend.dev>';
const PHONE = '0499 866 580';

function clean(v, max) { return String(v == null ? '' : v).replace(/[\u0000-\u001f]+/g, ' ').trim().slice(0, max); }

function parseBody(req) {
  const ct = String(req.headers['content-type'] || '');
  const raw = req.body;
  if (ct.includes('application/json')) return typeof raw === 'string' ? JSON.parse(raw || '{}') : (raw || {});
  if (ct.includes('application/x-www-form-urlencoded')) {
    const params = new URLSearchParams(typeof raw === 'string' ? raw : '');
    const o = {};
    for (const [k, v] of params) { if (k === 'help') (o.help = o.help || []).push(v); else o[k] = v; }
    if (typeof raw === 'object' && raw && !Array.isArray(raw)) Object.assign(o, raw);
    return o;
  }
  return typeof raw === 'object' && raw ? raw : {};
}

function validate(b) {
  const e = {
    name: clean(b.name, 120), phone: clean(b.phone, 40), email: clean(b.email, 200),
    location: clean(b.location, 120), message: clean(b.message, 2000),
    help: Array.isArray(b.help) ? b.help.map(x => clean(x, 40)).filter(Boolean).slice(0, 8) : (b.help ? [clean(b.help, 40)] : []),
    company: clean(b.company, 200),
  };
  const errors = [];
  if (!e.name) errors.push('Enter your name.');
  if (e.phone.replace(/\D/g, '').length < 8) errors.push('Enter a phone number with at least eight digits.');
  if (e.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.email)) errors.push('That email address does not look right.');
  if (!e.location) errors.push('Tell me the town or locality.');
  if (!e.help.length) errors.push('Tick at least one thing you need help with.');
  return { e, errors };
}

async function send(e) {
  const lines = [
    `Name: ${e.name}`, `Phone: ${e.phone}`, `Email: ${e.email || '(not given)'}`, `Property location: ${e.location}`,
    `Help with: ${e.help.join(', ')}`, '', e.message || '(no message)', '', `Sent from the website enquiry form.`,
  ];
  if (!process.env.RESEND_API_KEY) {
    console.log('[enquiry] (no RESEND_API_KEY set, logging only)\n' + lines.join('\n'));
    return { delivered: false };
  }
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: FROM, to: [TO], reply_to: e.email || undefined, subject: `Enquiry: ${e.help.join(', ')} near ${e.location} (${e.name})`, text: lines.join('\n') }),
  });
  if (!r.ok) throw new Error(`Resend ${r.status}: ${await r.text()}`);
  return { delivered: true };
}

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function htmlPage(title, body) {
  return `<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><meta name="robots" content="noindex"><style>body{margin:0;background:#f8f6f2;color:#432a27;font:17px/1.5 Barlow,system-ui,sans-serif;padding:max(16px,env(safe-area-inset-left))}main{max-width:40rem;margin:48px auto;border:2px solid #2E6E4E;border-radius:4px;padding:24px;background:#f1eee8}h1{font:700 1.6rem/1.05 "Barlow Condensed","Arial Narrow",sans-serif;text-transform:uppercase;margin:0 0 12px}a{color:inherit}ul{padding-left:18px}</style></head><body><main>${body}</main></body></html>`;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false, error: 'POST only' }); }
  const wantsJson = String(req.headers['accept'] || '').includes('application/json') || String(req.headers['content-type'] || '').includes('application/json');
  let body;
  try { body = parseBody(req); } catch { return res.status(400).json({ ok: false, error: 'Could not read the enquiry.' }); }
  const { e, errors } = validate(body);
  if (e.company) { // honeypot filled: pretend success, send nothing
    return wantsJson ? res.status(200).json({ ok: true }) : res.status(200).send(htmlPage('Enquiry received', '<h1>Enquiry received</h1><p>Thanks.</p>'));
  }
  if (errors.length) {
    if (wantsJson) return res.status(400).json({ ok: false, error: errors.join(' ') });
    return res.status(400).send(htmlPage('Fix the enquiry', `<h1>Fix the following</h1><ul>${errors.map(x => `<li>${esc(x)}</li>`).join('')}</ul><p><a href="/contact#enquiry">Back to the form</a> · or call ${PHONE}</p>`));
  }
  try {
    const out = await send(e);
    if (wantsJson) return res.status(200).json({ ok: true, delivered: out.delivered });
    return res.status(200).send(htmlPage('Enquiry received', `<h1>Enquiry received</h1><p>Thanks, ${esc(e.name.split(' ')[0])}. Fitz will ring the number you gave, usually within two business days.</p><p><strong>What happens next:</strong> a quick phone chat about the property and the animals, then a site visit if it's a fit. If it's urgent, call ${PHONE}.</p><p><a href="/">Back to the site</a></p>`));
  } catch (err) {
    console.error('[enquiry] send failed', err);
    if (wantsJson) return res.status(502).json({ ok: false, error: `The enquiry could not be sent. Ring ${PHONE} instead.` });
    return res.status(502).send(htmlPage('Not sent', `<h1>Not sent</h1><p>The enquiry could not be sent. Ring ${PHONE} instead.</p><p><a href="/contact#enquiry">Back to the form</a></p>`));
  }
}
