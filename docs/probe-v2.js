// SP-01b probe: v1 asserts re-run (subset) + the 14 delta asserts, against the public/ pages and the artifact wrapper.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const PUB = '/home/claude/paddock1/public';
function rgb(c){ if(c.startsWith('color(srgb')){ const m=c.match(/[\d.]+/g).map(Number); return [m[0]*255,m[1]*255,m[2]*255] } const m=c.match(/[\d.]+/g).map(Number); return [m[0],m[1],m[2]] }
function lum(c){ const [r,g,b]=rgb(c).map(v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}); return .2126*r+.7152*g+.0722*b }
function ratio(a,b){ const l1=lum(a),l2=lum(b); return ((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05)).toFixed(2) }
function chroma(c){ const [r,g,b]=rgb(c); return Math.max(r,g,b)-Math.min(r,g,b) }
(async () => {
  const b = await chromium.launch(); const out = [];
  const V = (ok, surface, prop, claimed, measured, per) => out.push(`${ok===true?'VERIFIED':ok==='un'?'UNMEASURABLE':'FAILED'} :: SP-01b :: ${surface} :: ${prop} :: claimed=${claimed} measured=${measured} :: PER=${per}`);
  // determinism + weight (filesystem)
  const tile = fs.readFileSync(path.join(PUB,'topo-tile.svg'),'utf8');
  const idx = fs.statSync(path.join(PUB,'index.html')).size;
  const alphas = [...tile.matchAll(/stroke-opacity="([\d.]+)"/g)].map(m=>+m[1]);
  V(alphas.length===2 && Math.max(...alphas)<=0.12 && /stroke="#432a27"/.test(tile), 'all', 'contour strokes: bark ink, ≤ .12 alpha', '#432a27, .075 / .12', `${tile.match(/stroke="(#[0-9a-f]+)"/)[1]}, ${alphas.join(' / ')}`, 'D2410 · D3006');
  V(idx<=120*1024 && tile.length<=75*1024, 'all', 'page weight', 'index ≤ 120 KB, tile ≤ 75 KB', `index ${(idx/1024).toFixed(0)} KB, tile ${(tile.length/1024).toFixed(0)} KB`, 'D4987 · LENS-06');
  const h = ['/tmp/t1.svg','/tmp/t2.svg',path.join(PUB,'topo-tile.svg')].map(f=>crypto.createHash('sha1').update(fs.readFileSync(f)).digest('hex').slice(0,8));
  V(new Set(h).size===1, 'all', 'seeded field: three builds hash identically', 'one hash', h.join(' '), 'D1851 · D3077 · LAW-10 · PAIR-06');

  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } }); const p = await ctx.newPage();
  const errors=[]; p.on('pageerror',e=>errors.push(String(e))); p.on('console',m=>{ if(m.type()==='error' && !/fonts.g|net::/.test(m.text())) errors.push(m.text()) });
  await p.goto('file://'+path.join(PUB,'index.html')); await p.waitForTimeout(700);
  const layer = await p.evaluate(()=>{ const cs=getComputedStyle(document.body,'::after'); return {pos:cs.position, z:cs.zIndex, pe:cs.pointerEvents, bg:cs.backgroundImage.slice(0,60), size:cs.backgroundSize, anim:cs.animationName, tr:cs.transitionProperty, body:getComputedStyle(document.body).backgroundColor, fs:getComputedStyle(document.body).fontSize} });
  V(layer.pos==='fixed' && layer.z==='-1' && layer.pe==='none' && /topo-tile|svg\+xml/.test(layer.bg) && layer.anim==='none', 'all', 'contour layer = body::after fixed, z −1, no animation', 'fixed / -1 / none / svg', `${layer.pos} / ${layer.z} / ${layer.anim} / ${layer.bg}`, 'D2410 · LAW-44 · D3453');
  V(/150px 150px/.test(layer.size), 'all', 'grid cell 150px = 1 km', '150px', layer.size, 'D0041 · D6468');
  const sb = await p.evaluate(()=>document.querySelector('.scalebar .bar').getBoundingClientRect().width);
  V(Math.abs(sb-150)<0.6, 'all', 'scale bar width', '150px', `${sb.toFixed(1)}px`, 'D0041 · D6468');
  const census = await p.evaluate(()=>{ const set={}; for(const el of document.querySelectorAll('body *')){ const cs=getComputedStyle(el); for(const q of ['backgroundColor','color','borderTopColor','outlineColor','fill','stroke']){ const v=cs[q]; if(v && v!=='none' && !v.startsWith('rgba(0, 0, 0, 0')) set[v]=(set[v]||0)+1 } } return set });
  const sat = Object.keys(census).filter(c=>/^(rgb|color)/.test(c) && chroma(c)>50 && !/\/ 0?\.\d|, 0?\.\d\)/.test(c));
  const allowed = c=> c==='rgb(46, 110, 78)' || /rgb\(44, 132, 219\)|rgb\(155, 44, 32\)/.test(c);
  V(sat.filter(c=>!allowed(c)).length===0, 'all', 'saturated-hue census unchanged', 'accent + focus + error only', sat.join(' | ')||'(none beyond accent)', 'D3004 · PALRULE-02');
  const pairs = await p.evaluate(()=>{ const g=(s,q)=>getComputedStyle(document.querySelector(s))[q]; return {body:[g('body','color'),g('body','backgroundColor')], ink2:[g('.eyebrow','color'),g('body','backgroundColor')], btn:[g('.hero .btn-primary','color'),g('.hero .btn-primary','backgroundColor')]} });
  const cr = Object.fromEntries(Object.entries(pairs).map(([k,[a,b]])=>[k,ratio(a,b)]));
  V(cr.body>=12 && cr.ink2>=7 && cr.btn>=5.9, 'all', 'token contrast unchanged', 'body ≥12, ink-2 ≥7, button ≥5.9', JSON.stringify(cr), 'D0192 · LENS-15');
  // hover census
  let tC=0,sC=0,n=0;
  for (let i=0;i<40;i++){ const r=await p.evaluate((i)=>{ const sel=['.nav a','.btn','.tile','.creds li','.copy','.chips li','.legend dd','.map circle']; const c=[]; sel.forEach(s=>document.querySelectorAll(s).forEach(e=>{ if(e.offsetParent!==null||e.ownerSVGElement) c.push(e) })); const e=c[i]; if(!e) return null; e.scrollIntoView({block:'center',behavior:'instant'}); const cs=getComputedStyle(e); const rc=e.getBoundingClientRect(); return {x:rc.x+rc.width/2,y:rc.y+rc.height/2,t:cs.transform,s:cs.boxShadow,tr:cs.translate} }, i); if(!r) break; await p.mouse.move(r.x,r.y); await p.waitForTimeout(240); const a=await p.evaluate((i)=>{ const sel=['.nav a','.btn','.tile','.creds li','.copy','.chips li','.legend dd','.map circle']; const c=[]; sel.forEach(s=>document.querySelectorAll(s).forEach(e=>{ if(e.offsetParent!==null||e.ownerSVGElement) c.push(e) })); const e=c[i]; const cs=getComputedStyle(e); return {t:cs.transform,s:cs.boxShadow,tr:cs.translate} }, i); n++; if(r.t!==a.t||r.tr!==a.tr) tC++; if(r.s!==a.s && !/inset 0px -2px/.test(a.s)) sC++; await p.mouse.move(0,0); await p.waitForTimeout(200); }
  V(tC===0&&sC===0, 'all', `hover census (${n} candidates)`, 'transformChanged=0 shadowChanged=0', `transformChanged=${tC} shadowChanged=${sC}`, 'D3171 · LAW-03');
  // map + chips + key
  const map = await p.evaluate(()=>{ const m=document.querySelector('.map'); return {towns:m.querySelectorAll('circle.town').length, base:m.querySelectorAll('rect.base').length, label:m.getAttribute('aria-label').slice(0,40), key:document.querySelectorAll('.legend dt').length, keyText:[...document.querySelectorAll('.legend dd')].every(d=>d.textContent.trim().length>3), chips:[...document.querySelectorAll('.chips li .gr')].map(e=>e.textContent), warragul:(document.querySelector('.chips li')||{}).textContent} });
  V(map.towns===10 && map.base===1 && map.label.startsWith('Schematic map'), 'home', 'locality map: 10 rings + 1 base square, labelled', '10 / 1 / aria-label', `${map.towns} / ${map.base} / "${map.label}"`, 'D0436 · D0191 · LAW-23 · LENS-14');
  V(map.chips.length===11 && /GR 063 758/.test(map.warragul), 'home', 'grid references on chips', '11 chips, Warragul GR 063 758', `${map.chips.length} chips, "${map.warragul.trim()}"`, 'D0142 · PAIR-794 · LENS-02');
  V(map.key===8 && map.keyText, 'home', 'map key: 8 shape+text entries', '8, all with text', `${map.key}, text=${map.keyText}`, 'D3780 · PAIR-125 · LAW-23');
  const frames = await p.evaluate(()=>[...document.querySelectorAll('.slot')].every(s=>s.querySelectorAll('.corner').length===4 && s.querySelector('.plate')));
  V(frames, 'all', 'photo frames: 4 ticks + privacy plate', 'every slot', `${frames}`, 'D0041 · D3813 · LENS-07');
  await p.goto('file://'+path.join(PUB,'services.html')); await p.waitForTimeout(500);
  const notes = await p.evaluate(()=>{ const a=document.querySelector('.margin-notes'); const marks=[...document.querySelectorAll('.fn')].map(f=>+f.textContent); const n=a.querySelectorAll('p').length; return {col:getComputedStyle(a.parentElement).gridTemplateColumns.split(' ').length, n, ok:marks.every(m=>m>=1&&m<=n), sticky:getComputedStyle(a).position} });
  V(notes.col===2 && notes.ok && notes.sticky==='sticky', 'services', 'marginalia column + resolving footnotes', '2 columns, all markers resolve, sticky', `${notes.col} cols, resolve=${notes.ok}, ${notes.sticky}`, 'D0098 · D0433');
  await ctx.close();
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }); const q = await m.newPage();
  await q.goto('file://'+path.join(PUB,'index.html')); await q.waitForTimeout(600);
  const mob = await q.evaluate(()=>{ const cs=getComputedStyle(document.body,'::after'); const a=document.querySelector('.margin-notes'); return {layers:cs.backgroundImage.split('url(').length-1, op:cs.opacity, fs:getComputedStyle(document.body).fontSize, sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth, ms:getComputedStyle(document.querySelector('.map-scroll')).overflowX} });
  V(mob.layers===1 && mob.op==='0.8' && mob.fs==='17px' && mob.sw<=mob.cw && mob.ms==='auto', 'all (<700px)', 'grid dropped, field .8, body 17px, no overflow, map scrolls', '1 layer / .8 / 17px / no overflow / auto', `${mob.layers} / ${mob.op} / ${mob.fs} / ${mob.sw}≤${mob.cw} / ${mob.ms}`, 'D3193 · LENS-15');
  await m.close();
  // reduced motion
  const r = await b.newContext({ viewport:{width:1280,height:900}, reducedMotion:'reduce' }); const rp = await r.newPage(); await rp.goto('file://'+path.join(PUB,'index.html')); await rp.waitForTimeout(400);
  const rm = await rp.evaluate(()=>({anims:document.getAnimations().filter(a=>!(window.ScrollTimeline && a.timeline instanceof ScrollTimeline)).length, sensors:document.getAnimations().filter(a=>window.ScrollTimeline && a.timeline instanceof ScrollTimeline).map(a=>a.animationName).join(','), reveal:getComputedStyle(document.querySelector('.reveal')).animationName}));
  V(rm.anims===0 && rm.reveal==='none', 'all', 'reduced motion: no time-driven animation constructed (scroll-state sensors allowed)', '0 clock animations', `${rm.anims} clock, sensors=[${rm.sensors}], reveal=${rm.reveal}`, 'D3453 · LAW-12 · LAW-67');
  await r.close();
  V(errors.length===0, 'all', 'console/page errors', '0', `${errors.length} ${errors.join(' | ')}`, 'contract');
  await b.close();
  fs.writeFileSync('/home/claude/paddock1/docs/verdicts-v2.txt', out.join('\n')+'\n');
  console.log(out.join('\n')); const f=out.filter(l=>l.startsWith('FAILED')).length; console.log(`\n${out.length} verdicts · ${f} FAILED · STAMP D700 · 4 Oct 2026`); process.exit(f);
})();
