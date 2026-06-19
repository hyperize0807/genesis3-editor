# -*- coding: utf-8 -*-
"""
창세기전3 통합 세이브 에디터 빌드.
파트1/파트2 각 에디터(단일 HTML)를 base64로 내장하고, 로고 선택 랜딩 셸을 얹어
단일 index.html 로 출력한다. 두 에디터는 iframe srcdoc 로 격리 실행(ID/전역 충돌 없음).

- 파트1 = genesis3part1_editor/dist/index.html  (적갈색으로 재테마: 임베드 복사본만)
- 파트2 = genesis3part2_editor/dist/index.html  (이미 연푸른 테마)
"""
import os, re, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # genesis3_save_editor
PROJ   = os.path.dirname(ROOT)                                  # Projects
P1_HTML= os.path.join(PROJ, "genesis3part1_editor", "dist", "index.html")
P2_HTML= os.path.join(PROJ, "genesis3part2_editor", "dist", "index.html")
LOGO1  = os.path.join(ROOT, "assets", "g3p1_logo_crop.png")
LOGO2  = os.path.join(ROOT, "assets", "g3p2_logo_crop.png")
OUT    = os.path.join(ROOT, "index.html")
VERSION= "v1.5.0"

# ── 파트1 적갈색 재테마(임베드 복사본 한정) ──
P1_ROOT_RED = (":root{--bg:#1a1011;--panel:#241618;--panel2:#30191c;--line:#4a2d30;"
               "--fg:#f0e6e6;--mut:#b59a9c;--acc:#d9656b;--ok:#5ed18b;--warn:#e6b65c}")
P1_COLOR_SWAPS = {  # 파트1이 쓰던 푸른 계열 하드코딩 → 붉은 계열
    "#33405e":"#5e3340", "#3a4a6b":"#6b3a4a", "#1b2233":"#2a1518", "#6ea8fe":"#d9656b",
}
def theme_part1(html):
    html = re.sub(r":root\{[^}]*\}", P1_ROOT_RED, html, count=1)
    for a,b in P1_COLOR_SWAPS.items(): html = html.replace(a,b)
    return html

def b64_utf8(s):  return base64.b64encode(s.encode("utf-8")).decode("ascii")
def b64_file(p):  return base64.b64encode(open(p,"rb").read()).decode("ascii")

def main():
    p1 = theme_part1(open(P1_HTML, encoding="utf-8").read())
    p2 = open(P2_HTML, encoding="utf-8").read()
    ED1, ED2 = b64_utf8(p1), b64_utf8(p2)
    LG1 = "data:image/png;base64," + b64_file(LOGO1)
    LG2 = "data:image/png;base64," + b64_file(LOGO2)

    html = SHELL.replace("__VER__", VERSION).replace("__LOGO1__", LG1).replace("__LOGO2__", LG2)
    html = html.replace("__ED1__", ED1).replace("__ED2__", ED2)
    open(OUT, "w", encoding="utf-8").write(html)
    kb = len(html.encode("utf-8"))//1024
    print(f"-> {OUT}  ({kb} KB)")
    print(f"   파트1 임베드 {len(ED1)//1024}KB(b64, 적갈색 재테마) · 파트2 {len(ED2)//1024}KB(b64)")

SHELL = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>창세기전3 세이브 에디터</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%}
  body{font:14px/1.5 "Segoe UI",Malgun Gothic,sans-serif;background:#0c0e12;color:#e6e8ee}
  /* 랜딩 */
  #landing{min-height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;
    gap:28px;padding:40px 20px;background:radial-gradient(1200px 600px at 50% -10%,#16181f,#0a0b0e)}
  #landing h1{margin:0;font-size:24px;font-weight:700;letter-spacing:.5px}
  #landing .sub{color:#9aa0ad;font-size:13px;margin-top:-14px}
  .cards{display:flex;gap:26px;flex-wrap:wrap;justify-content:center;width:100%;max-width:980px}
  .card{flex:1 1 360px;max-width:460px;cursor:pointer;border-radius:14px;overflow:hidden;
    border:2px solid #2a2d36;background:#15171d;transition:transform .12s,border-color .12s,box-shadow .12s}
  .card:hover{transform:translateY(-4px)}
  .card img{display:block;width:100%;height:184px;object-fit:cover;object-position:center;background:#0a0b0e}
  .card .cap{padding:12px 16px;font-weight:700;display:flex;justify-content:space-between;align-items:center}
  .card .cap small{font-weight:400;color:#9aa0ad}
  .card.p1{border-color:#5a2f31}
  .card.p1:hover{border-color:#d9656b;box-shadow:0 8px 30px rgba(160,37,10,.35)}
  .card.p1 .cap{background:linear-gradient(#241618,#1a1011);color:#e7a6a8}
  .card.p2{border-color:#33415a}
  .card.p2:hover{border-color:#8cb8ff;box-shadow:0 8px 30px rgba(80,120,200,.35)}
  .card.p2 .cap{background:linear-gradient(#19212e,#10151d);color:#aacbff}
  /* 세이브 업로드(자동 판별) */
  #uploadbox{width:100%;max-width:980px;border:2px dashed #2f333d;border-radius:12px;padding:18px 20px;
    text-align:center;color:#9aa0ad;background:#101218;transition:border-color .12s,background .12s}
  #uploadbox.hl{border-color:#8cb8ff;background:#12161f;color:#cfd6e2}
  #uploadbox b{color:#cdd3dd}
  #uploadbox .pick{margin-top:10px}
  #uploadbox button{background:#23262e;color:#e6e8ee;border:1px solid #3a3f4b;border-radius:6px;padding:6px 14px;cursor:pointer}
  #uploadbox button:hover{border-color:#8cb8ff}
  #uperr{margin-top:8px;font-size:12px;min-height:16px}
  #uperr.err{color:#e6736b}#uperr.ok{color:#5ed18b}
  #landing .foot{color:#5b606b;font-size:11px;margin-top:6px;text-align:center}
  /* 에디터 뷰 */
  #app{display:none;height:100%;flex-direction:column}
  #appbar{flex:none;display:flex;align-items:center;gap:14px;padding:7px 14px;background:#15171d;border-bottom:1px solid #2a2d36}
  #appbar button{background:#23262e;color:#e6e8ee;border:1px solid #3a3f4b;border-radius:6px;padding:5px 12px;cursor:pointer}
  #appbar button:hover{border-color:#888}
  #appbar .who{font-weight:700}
  #appbar .who.p1{color:#e7a6a8}#appbar .who.p2{color:#aacbff}
  #frame{flex:1 1 auto;width:100%;border:0;background:#0c0e12}
</style>
</head>
<body>
<div id="landing">
  <h1>창세기전3 세이브 에디터</h1>
  <div class="sub">편집할 작품을 선택하세요</div>
  <div class="cards">
    <div class="card p1" data-game="1">
      <img src="__LOGO1__" alt="창세기전3 파트1">
      <div class="cap"><span>파트1</span><small>The War of Genesis III</small></div>
    </div>
    <div class="card p2" data-game="2">
      <img src="__LOGO2__" alt="창세기전3 파트2">
      <div class="cap"><span>파트2</span><small>The War of Genesis III · Part 2</small></div>
    </div>
  </div>
  <div id="uploadbox">
    <div>📁 <b>세이브 파일</b>을 여기에 끌어다 놓거나 선택하면 <b>작품을 자동 판별</b>해 바로 엽니다</div>
    <div class="pick"><button id="savepick">세이브 파일 선택</button>
      <input type="file" id="savefile" accept=".sav" style="display:none"></div>
    <div id="uperr"></div>
  </div>
  <div class="foot">통합본 __VER__ · 팬메이드 비공식 도구 · 편집 전 세이브 백업 권장 · 파일은 브라우저 안에서만 처리(업로드 없음)</div>
</div>

<div id="app">
  <div id="appbar">
    <button id="back">← 작품 선택</button>
    <span class="who" id="who"></span>
  </div>
  <iframe id="frame" title="save editor"></iframe>
</div>

<script>
const b64dec = b64 => new TextDecoder().decode(Uint8Array.from(atob(b64), c=>c.charCodeAt(0)));
const ED = { 1: "__ED1__", 2: "__ED2__" };
const WHO = { 1: ["파트1","p1"], 2: ["파트2","p2"] };
const landing=document.getElementById("landing"), app=document.getElementById("app");
const frame=document.getElementById("frame"), who=document.getElementById("who");
function openGame(game, file){
  who.textContent = "창세기전3 "+WHO[game][0];
  who.className = "who "+WHO[game][1];
  // 파일이 있으면 iframe 로드 완료 후 에디터의 #file 입력에 주입(파트1/2 공통)
  frame.onload = file ? ()=>{ try{
      const w=frame.contentWindow, inp=frame.contentDocument.getElementById("file");
      const dt=new w.DataTransfer(); dt.items.add(file);   // iframe realm 기준 구성
      inp.files=dt.files; inp.dispatchEvent(new w.Event("change",{bubbles:true}));
    }catch(e){} frame.onload=null; } : null;
  frame.srcdoc = b64dec(ED[game]);          // 격리 실행(srcdoc, same-origin) — 스크립트/다운로드 동작
  landing.style.display="none"; app.style.display="flex";
}
function back(){ app.style.display="none"; frame.onload=null; frame.srcdoc=""; landing.style.display="flex"; setErr(""); }
document.querySelectorAll(".card").forEach(c=>c.onclick=()=>openGame(c.dataset.game));
document.getElementById("back").onclick=back;

// ── 세이브 자동 판별 ── (XOR 0xFF 디코드 → 파트1 레코드 마커 30 3A 10 10 다수면 파트1, 아니면 파트2)
function checksum(raw,base){ let acc=0; for(let i=0;i<raw.length-2;i++) acc=(acc+raw[i]*(2*(i&3)+base))%32000; return acc; }
function detectGame(bytes){
  if(bytes.length<0x100) return null;
  const stored=bytes[bytes.length-2]|(bytes[bytes.length-1]<<8);
  if(checksum(bytes,1)!==stored && checksum(bytes,3)!==stored) return null;  // 창세기전3 세이브 아님
  let mark=0;
  for(let i=0;i+4<=bytes.length;i++){              // 디코드값 30 3A 10 10 = raw CF C5 EF EF
    if(bytes[i]===0xCF&&bytes[i+1]===0xC5&&bytes[i+2]===0xEF&&bytes[i+3]===0xEF){ mark++; if(mark>=10) break; }
  }
  return mark>=10 ? 1 : 2;     // 파트1=마커 다수, 파트2=마커 없음
}
function setErr(t,ok){ const e=document.getElementById("uperr"); e.textContent=t||""; e.className=ok?"ok":(t?"err":""); }
function handleUpload(file){
  if(!file) return;
  setErr("판별 중… "+file.name);
  file.arrayBuffer().then(ab=>{
    const g=detectGame(new Uint8Array(ab));
    if(!g){ setErr("창세기전3 파트1/2 세이브로 인식되지 않습니다: "+file.name); return; }
    setErr("→ 창세기전3 "+WHO[g][0]+" 에디터로 엽니다 ("+file.name+")", true);
    openGame(g, file);
  });
}
const ub=document.getElementById("uploadbox"), sf=document.getElementById("savefile");
document.getElementById("savepick").onclick=()=>sf.click();
sf.onchange=e=>handleUpload(e.target.files[0]);
["dragover","dragenter"].forEach(ev=>ub.addEventListener(ev,e=>{e.preventDefault();ub.classList.add("hl");}));
["dragleave"].forEach(ev=>ub.addEventListener(ev,e=>{e.preventDefault();ub.classList.remove("hl");}));
ub.addEventListener("drop",e=>{e.preventDefault();ub.classList.remove("hl");handleUpload(e.dataTransfer.files[0]);});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
