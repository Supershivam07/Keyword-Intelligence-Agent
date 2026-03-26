from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

import asyncio
import json
import time

from agent.keyword_agent import KeywordAgent

app = FastAPI()
agent = KeywordAgent()


# =========================================================
# HOME PAGE
# =========================================================
# ── Serves the main UI page — full HTML with CSS + JS for 3-step pipeline
@app.get("/", response_class=HTMLResponse)
def home():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Keyword Intelligence Agent</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:       #060910;
    --surface:  #0d1117;
    --border:   #1c2333;
    --accent:   #00d084;
    --accent2:  #0ea5e9;
    --accent3:  #f59e0b;
    --muted:    #4b5563;
    --text:     #e2e8f0;
    --text-dim: #94a3b8;
}

body {
    font-family: 'Space Grotesk', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 40px 20px 80px;
}

.container { max-width: 860px; margin: 0 auto; }

.header { text-align: center; margin-bottom: 48px; }

.header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
}

.header p { color: var(--text-dim); font-size: 1rem; }

.input-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
    margin-bottom: 28px;
}

.input-row {
    display: flex;
    gap: 12px;
    align-items: center;
}

#topicInput {
    flex: 1;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 13px 16px;
    font-size: 15px;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text);
    outline: none;
    transition: border-color 0.2s;
}

#topicInput:focus { border-color: var(--accent); }
#topicInput:disabled { opacity: 0.5; cursor: not-allowed; }

.steps-row {
    display: flex;
    gap: 8px;
    margin-top: 20px;
}

.step-pill {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--bg);
    font-size: 13px;
    color: var(--muted);
    transition: all 0.3s;
    white-space: nowrap;
    user-select: none;
}

.step-pill.active {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(0,208,132,0.06);
}

.step-pill.done {
    border-color: var(--accent2);
    color: var(--accent2);
    background: rgba(14,165,233,0.06);
}

.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: currentColor;
    flex-shrink: 0;
    display: inline-block;
}

#mainBtn {
    padding: 13px 28px;
    border-radius: 10px;
    border: none;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    background: var(--accent);
    color: #000;
    transition: background 0.2s, opacity 0.2s, transform 0.1s;
    white-space: nowrap;
    flex-shrink: 0;
}

#mainBtn:hover:not(:disabled) { background: #00b872; transform: translateY(-1px); }
#mainBtn.step2 { background: var(--accent2); color: #fff; }
#mainBtn.step2:hover:not(:disabled) { background: #0284c7; }
#mainBtn.step3 { background: var(--accent3); color: #000; }
#mainBtn.step3:hover:not(:disabled) { background: #d97706; }
#mainBtn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

#resetBtn {
    display: none;
    padding: 13px 20px;
    border-radius: 10px;
    border: 1px solid var(--border);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    background: transparent;
    color: var(--text-dim);
    transition: all 0.2s;
    flex-shrink: 0;
}

#resetBtn:hover {
    border-color: #ef4444;
    color: #ef4444;
    background: rgba(239,68,68,0.06);
}

.output-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
}

.output-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    font-size: 13px;
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    gap: 8px;
}

.output-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--muted);
    transition: background 0.3s;
    display: inline-block;
}

.output-dot.live {
    background: var(--accent);
    animation: pulse 1.2s infinite;
}

@keyframes pulse {
    0%,100% { opacity:1; }
    50%      { opacity:0.3; }
}

#output {
    padding: 24px;
    min-height: 280px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px;
    line-height: 1.85;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
}

a.result-link {
    color: var(--accent2);
    text-decoration: none;
    border-bottom: 1px solid rgba(14,165,233,0.3);
}

a.result-link:hover { border-color: var(--accent2); }

hr.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 14px 0;
}

/* ── SELECTION CARD ── */
#selectionCard {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px;
    margin-top: 24px;
    animation: slideIn 0.35s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.sel-section { margin-bottom: 28px; }

.sel-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 14px;
}

.title-option {
    display: block;
    width: 100%;
    text-align: left;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14px;
    color: var(--text);
    cursor: pointer;
    transition: all 0.2s;
    line-height: 1.5;
}

.title-option:hover {
    border-color: var(--accent2);
    background: rgba(14,165,233,0.04);
}

.title-option.selected {
    border-color: var(--accent2);
    background: rgba(14,165,233,0.08);
    color: var(--accent2);
}

.custom-title-row {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-top: 10px;
}

#customTitleInput {
    flex: 1;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 11px 14px;
    font-size: 14px;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text);
    outline: none;
    transition: border-color 0.2s;
}

#customTitleInput:focus { border-color: var(--accent); }
#customTitleInput::placeholder { color: var(--muted); }

.chips-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.kw-chip {
    padding: 7px 14px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: var(--bg);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    color: var(--text-dim);
    cursor: pointer;
    transition: all 0.2s;
    user-select: none;
}

.kw-chip:hover {
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(0,208,132,0.05);
}

.kw-chip.selected {
    border-color: var(--accent);
    background: rgba(0,208,132,0.12);
    color: var(--accent);
    font-weight: 600;
}

#selStatus {
    display: flex;
    gap: 16px;
    align-items: center;
    padding: 14px 18px;
    background: var(--bg);
    border-radius: 10px;
    border: 1px solid var(--border);
    font-size: 13px;
    margin-top: 4px;
}

.sel-status-item { display: flex; align-items: center; gap: 6px; }
.sel-status-item.done { color: var(--accent); }
.sel-status-item.pending { color: var(--muted); }
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>🔍 Keyword Intelligence Agent</h1>
    <p>AI-powered SEO analysis — keywords, titles, and blog outline in 3 focused steps.</p>
  </div>

  <div class="input-card">
    <div class="input-row">
      <input id="topicInput" placeholder="Enter topic (e.g., AI Agents)..." />
      <button id="mainBtn">🔍 Get Keywords &amp; URLs</button>
      <button id="resetBtn">↺ Reset</button>
    </div>
    <div class="steps-row">
      <div class="step-pill active" id="pill1"><span class="step-dot"></span> Step 1: Keywords &amp; URLs</div>
      <div class="step-pill" id="pill2"><span class="step-dot"></span> Step 2: Titles</div>
      <div class="step-pill" id="pill3"><span class="step-dot"></span> Step 3: Outline</div>
    </div>
  </div>

  <div class="output-card">
    <div class="output-header">
      <span class="output-dot" id="outputDot"></span>
      <span id="outputLabel">output</span>
    </div>
    <div id="output">Ready. Enter a topic and press Get Keywords &amp; URLs to begin.</div>
  </div>

  <div id="selectionCard">
    <div class="sel-section" id="kwSection" style="display:none;">
      <p class="sel-label">Select a Primary Keyword</p>
      <div class="chips-wrap" id="kwChips"></div>
    </div>
    <div class="sel-section" id="titleSection" style="display:none;">
      <p class="sel-label">Select a Title</p>
      <div id="titleOptions"></div>
      <div class="custom-title-row">
        <input id="customTitleInput" placeholder="Or type your own custom title here..." />
      </div>
    </div>
    <div id="selStatus">
      <span class="sel-status-item pending" id="titleStatus"></span>
      <span class="sel-status-item pending" id="kwStatus"></span>
    </div>
  </div>

</div>
<script>
// State
let currentStep        = 1;
let storedTopic        = "";
let storedUrls         = [];
let storedAnalysisUrls = [];
let storedTitles       = [];
let storedKeywords     = [];
let selectedTitle      = "";
let selectedKw         = "";

// DOM refs
const btn          = document.getElementById("mainBtn");
const resetBtn     = document.getElementById("resetBtn");
const topicInput   = document.getElementById("topicInput");
const output       = document.getElementById("output");
const dot          = document.getElementById("outputDot");
const lbl          = document.getElementById("outputLabel");
const pill1        = document.getElementById("pill1");
const pill2        = document.getElementById("pill2");
const pill3        = document.getElementById("pill3");
const selCard      = document.getElementById("selectionCard");
const titleOptions = document.getElementById("titleOptions");
const kwChips      = document.getElementById("kwChips");
const customInput  = document.getElementById("customTitleInput");
const titleStatus  = document.getElementById("titleStatus");
const kwStatus     = document.getElementById("kwStatus");

// Helpers
function linkify(text){
    return text.replace(/(https?:\\/\\/[^\\s<"]+)/g,
        url => `<a href="${url}" target="_blank" class="result-link">${url}</a>`);
}

function setLive(on){
    dot.className = "output-dot" + (on ? " live" : "");
    lbl.textContent = on ? "streaming..." : "output";
}

function setPill(n, state){
    [pill1,pill2,pill3][n-1].className = "step-pill " + state;
}

function updateButton(){
    if(currentStep === 1){
        btn.textContent = "🔍 Get Keywords & URLs";
        btn.className = "";
    } else if(currentStep === 2){
        btn.textContent = "💡 Generate Titles";
        btn.className = "step2";
    } else if(currentStep === 3){
        btn.textContent = "📑 Generate Outline";
        btn.className = "step3";
    } else {
        btn.textContent = "✅ All Done";
        btn.disabled = true;
    }
}

// Selection status checkers
function checkKwReady(){
    const kwOk = selectedKw.trim().length > 0;
    kwStatus.textContent = kwOk ? "✅ Keyword selected" : "⏳ Select a keyword to continue";
    kwStatus.className   = "sel-status-item " + (kwOk ? "done" : "pending");
    btn.disabled = !kwOk;
}

function checkTitleReady(){
    const titleOk = selectedTitle.trim().length > 0;
    titleStatus.textContent = titleOk ? "✅ Title selected" : "⏳ Select a title to continue";
    titleStatus.className   = "sel-status-item " + (titleOk ? "done" : "pending");
    btn.disabled = !titleOk;
}

// Build keyword selection card (shown after Step 1)
function buildKwSelectionCard(keywords){
    document.getElementById("titleSection").style.display = "none";
    document.getElementById("kwSection").style.display    = "block";

    selectedKw = "";
    kwChips.innerHTML = "";

    keywords.forEach(function(kw){
        const chip = document.createElement("span");
        chip.className   = "kw-chip";
        chip.textContent = kw;
        chip.addEventListener("click", function(){
            if(chip.classList.contains("selected")){
                chip.classList.remove("selected");
                selectedKw = "";
            } else {
                document.querySelectorAll(".kw-chip").forEach(c => c.classList.remove("selected"));
                chip.classList.add("selected");
                selectedKw = kw;
            }
            checkKwReady();
        });
        kwChips.appendChild(chip);
    });

    kwStatus.textContent = "⏳ Select a keyword to continue";
    kwStatus.className   = "sel-status-item pending";
    titleStatus.textContent = "";

    selCard.style.display = "block";
    btn.disabled = true;
}

// Build title selection card (shown after Step 2)
function buildTitleSelectionCard(titles){
    document.getElementById("titleSection").style.display = "block";
    document.getElementById("kwSection").style.display    = "none";

    selectedTitle = "";
    titleOptions.innerHTML = "";
    customInput.value = "";

    titles.forEach(function(t, i){
        const btn_t = document.createElement("button");
        btn_t.className    = "title-option";
        btn_t.textContent  = (i+1) + ". " + t;
        btn_t.dataset.title = t;
        btn_t.addEventListener("click", function(){
            document.querySelectorAll(".title-option").forEach(b => b.classList.remove("selected"));
            btn_t.classList.add("selected");
            customInput.value = "";
            selectedTitle = t;
            checkTitleReady();
        });
        titleOptions.appendChild(btn_t);
    });

    customInput.value = "";
    customInput.oninput = function(){
        const val = customInput.value.trim();
        if(val.length > 0){
            document.querySelectorAll(".title-option").forEach(b => b.classList.remove("selected"));
            selectedTitle = val;
        } else {
            selectedTitle = "";
        }
        checkTitleReady();
    };

    titleStatus.textContent = "⏳ Select a title to continue";
    titleStatus.className   = "sel-status-item pending";
    kwStatus.textContent    = "";

    selCard.style.display = "block";
    btn.disabled = true;
}

// Loading messages
// Step 1: 5 msgs over 45s → every 9000ms
// Step 2: 2 msgs over 13s → every 6500ms
// Step 3: 3 msgs over 22s → every 7300ms
const stepMessages = {
    1: ["🧠 Understanding topic...", "🔎 Searching top ranking pages...",
        "🌐 Fetching authoritative websites...", "📊 Extracting SEO signals...",
        "🔥 Identifying high-ranking keywords..."],
    2: ["💡 Analyzing ranking pages...", "✍️ Crafting SEO-optimized titles..."],
    3: ["📑 Structuring blog architecture...", "🏗️ Building H2 sections...",
        "🔩 Adding H3 subsections..."]
};

const stepIntervals = { 1: 9000, 2: 6500, 3: 7300 };

async function animateMessages(msgs, control, step){
    const interval = stepIntervals[step] || 5000;
    let i = 0;
    while(!control.done && i < msgs.length){
        output.innerHTML += msgs[i] + "\\n";
        i++;
        await new Promise(r => setTimeout(r, interval));
    }
}

// Reset
function doReset(){
    currentStep        = 1;
    storedTopic        = "";
    storedUrls         = [];
    storedAnalysisUrls = [];
    storedTitles       = [];
    storedKeywords     = [];
    selectedTitle      = "";
    selectedKw         = "";

    topicInput.disabled    = false;
    topicInput.value       = "";
    btn.disabled           = false;
    resetBtn.style.display = "none";
    selCard.style.display  = "none";
    titleOptions.innerHTML = "";
    kwChips.innerHTML      = "";
    customInput.value      = "";

    setPill(1,"active"); setPill(2,""); setPill(3,"");
    updateButton(); setLive(false);
    output.innerHTML = "Ready. Enter a topic and press Get Keywords &amp; URLs to begin.";
}

resetBtn.addEventListener("click", doReset);

// Main button click handler
btn.addEventListener("click", async function(){

    // STEP 1
    if(currentStep === 1){
        const topic = topicInput.value.trim();
        if(!topic){ output.innerHTML = "❌ Please enter a topic first."; return; }

        storedTopic            = topic;
        topicInput.disabled    = true;
        btn.disabled           = true;
        resetBtn.style.display = "block";
        setPill(1,"active"); setLive(true);
        output.innerHTML = "🤖 Starting Step 1 — Keywords & URLs...\\n\\n";

        const ctrl = {done:false};
        animateMessages(stepMessages[1], ctrl, 1);

        try {
            const res    = await fetch("/stream/step1?topic=" + encodeURIComponent(topic));
            const reader = res.body.getReader();
            const dec    = new TextDecoder();
            let buf = "", rawAll = "", first = true;

            while(true){
                const {done,value} = await reader.read();
                if(done) break;
                const chunk = dec.decode(value);
                rawAll += chunk;
                if(first){ ctrl.done=true; await new Promise(r=>setTimeout(r,300)); first=false; }
                buf += chunk;
                const display = buf
                    .replace(/<!--URLS:.*?-->/g,"")
                    .replace(/<!--ANALYSIS_URLS:.*?-->/g,"")
                    .replace(/<!--KWS:.*?-->/g,"");
                output.innerHTML = linkify(display.replace(/\\\\n/g,"\\n").replace(/\\n/g,"<br>"));
            }

            const mUrls = rawAll.match(/<!--URLS:(.*?)-->/);
            if(mUrls){ try{ storedUrls = JSON.parse(decodeURIComponent(mUrls[1])); }catch(e){} }

            const mAnalysis = rawAll.match(/<!--ANALYSIS_URLS:(.*?)-->/);
            if(mAnalysis){ try{ storedAnalysisUrls = JSON.parse(decodeURIComponent(mAnalysis[1])); }catch(e){} }
            if(!storedAnalysisUrls.length) storedAnalysisUrls = storedUrls;

            const mKws = rawAll.match(/<!--KWS:(.*?)-->/);
            if(mKws){ try{ storedKeywords = JSON.parse(decodeURIComponent(mKws[1])); }catch(e){} }

            setLive(false); setPill(1,"done"); setPill(2,"active");
            currentStep = 2;
            updateButton();
            buildKwSelectionCard(storedKeywords);

        } catch(err){
            ctrl.done=true; setLive(false);
            output.innerHTML += "\\n❌ Error: "+err;
            btn.disabled=false;
        }

    // STEP 2
    } else if(currentStep === 2){
        btn.disabled=true;
        selCard.style.display = "none";
        setPill(2,"active"); setLive(true);

        const prev = output.innerHTML;
        output.innerHTML = prev + "<br><hr class='divider'>🤖 Starting Step 2 — Titles...\\n\\n";

        const ctrl = {done:false};
        animateMessages(stepMessages[2], ctrl, 2);

        try {
            const urlsParam = encodeURIComponent(JSON.stringify(storedAnalysisUrls));
            const kwParam   = encodeURIComponent(selectedKw);
            const res    = await fetch(
                "/stream/step2?topic="+encodeURIComponent(storedTopic)+
                "&urls="+urlsParam+
                "&selected_kw="+kwParam
            );
            const reader = res.body.getReader();
            const dec    = new TextDecoder();
            let newBuf="", rawAll2="", first=true;

            while(true){
                const {done,value} = await reader.read();
                if(done) break;
                const chunk = dec.decode(value);
                rawAll2 += chunk;
                if(first){ ctrl.done=true; await new Promise(r=>setTimeout(r,300));
                    output.innerHTML = prev+"<br><hr class='divider'>"; first=false; }
                newBuf += chunk;
                const display2 = newBuf.replace(/<!--TITLES:.*?-->/g,"");
                output.innerHTML = prev+"<br><hr class='divider'>" +
                    linkify(display2.replace(/\\\\n/g,"\\n").replace(/\\n/g,"<br>"));
            }

            const mTitles = rawAll2.match(/<!--TITLES:(.*?)-->/);
            if(mTitles){ try{ storedTitles = JSON.parse(decodeURIComponent(mTitles[1])); }catch(e){} }

            setLive(false); setPill(2,"done"); setPill(3,"active");
            currentStep = 3;
            updateButton();
            buildTitleSelectionCard(storedTitles);

        } catch(err){
            ctrl.done=true; setLive(false);
            output.innerHTML += "\\n❌ Error: "+err;
            btn.disabled=false;
        }

    // STEP 3
    } else if(currentStep === 3){
        btn.disabled=true;
        selCard.style.display = "none";
        setPill(3,"active"); setLive(true);

        const prev = output.innerHTML;
        output.innerHTML = prev + "<br><hr class='divider'>🤖 Starting Step 3 — Outline...\\n\\n";

        const ctrl = {done:false};
        animateMessages(stepMessages[3], ctrl, 3);

        try {
            const urlsParam  = encodeURIComponent(JSON.stringify(storedAnalysisUrls));
            const titleParam = encodeURIComponent(selectedTitle);
            const kwParam    = encodeURIComponent(selectedKw);
            const res    = await fetch(
                "/stream/step3?topic="+encodeURIComponent(storedTopic)+
                "&urls="+urlsParam+
                "&selected_title="+titleParam+
                "&selected_kw="+kwParam
            );
            const reader = res.body.getReader();
            const dec    = new TextDecoder();
            let newBuf="", first=true;

            while(true){
                const {done,value} = await reader.read();
                if(done) break;
                const chunk = dec.decode(value);
                if(first){ ctrl.done=true; await new Promise(r=>setTimeout(r,300));
                    output.innerHTML = prev+"<br><hr class='divider'>"; first=false; }
                newBuf += chunk;
                output.innerHTML = prev+"<br><hr class='divider'>" +
                    linkify(newBuf.replace(/\\\\n/g,"\\n").replace(/\\n/g,"<br>"));
            }

            setLive(false); setPill(3,"done");
            currentStep=4; btn.disabled=true;
            btn.textContent="✅ All Done"; btn.className="";

        } catch(err){
            ctrl.done=true; setLive(false);
            output.innerHTML += "\\n❌ Error: "+err;
            btn.disabled=false;
        }
    }
});
</script>
</body>
</html>"""



# ── Step 1 endpoint — called when user clicks "Get Keywords & URLs"
# ── Runs agent.run_step1() in a thread, streams results to browser as plain text
# ── Passes display URLs, analysis URLs, and keywords to frontend via hidden HTML comments
# ── Frontend extracts these hidden comments to use in step2 and step3 fetch calls
@app.get("/stream/step1")
async def stream_step1(topic: str):

    start_time = time.time()

    async def event_generator():
        try:
            result = await asyncio.to_thread(agent.run_step1, topic)

            if not result or "error" in result:
                yield f"❌ Error: {result.get('error', 'Unknown error')}\\n"
                return

            urls          = result.get("top_urls", [])        # display URLs (clean 5)
            analysis_urls = result.get("analysis_urls", urls)  # raw URLs for analysis
            keywords      = result.get("high_ranking_keywords", [])

            yield "🧠 Topic\\n"
            yield f"{result.get('topic', topic)}\\n\\n"

            yield "🔗 Top Ranking URLs\\n"
            for url in urls:
                yield f"• {url}\\n"
                await asyncio.sleep(0.2)

            yield "\\n🔥 High-Ranking Keywords\\n"
            for kw in keywords:
                yield f"• {kw}\\n"
                await asyncio.sleep(0.15)

            total_time = time.time() - start_time
            yield f"\\n⏱ Step 1 Time: {total_time:.2f}s\\n"

            # Pass display URLs, analysis URLs + keywords to frontend
            import urllib.parse
            urls_encoded     = urllib.parse.quote(json.dumps(urls))
            analysis_encoded = urllib.parse.quote(json.dumps(analysis_urls))
            kws_encoded      = urllib.parse.quote(json.dumps(keywords))
            yield f"<!--URLS:{urls_encoded}-->"
            yield f"<!--ANALYSIS_URLS:{analysis_encoded}-->"
            yield f"<!--KWS:{kws_encoded}-->"

        except Exception as e:
            yield f"\\n❌ Streaming error: {str(e)}\\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# ── Step 2 endpoint — called when user clicks "Generate Titles" after selecting a keyword
# ── Receives topic, analysis URLs (raw 10), and user-selected keyword as query params
# ── Passes generated titles back to frontend via hidden HTML comment for title selection card
@app.get("/stream/step2")
async def stream_step2(topic: str, urls: str = "[]", selected_kw: str = ""):

    start_time = time.time()

    async def event_generator():
        try:
            urls_list = json.loads(urls)
            result    = await asyncio.to_thread(agent.run_step2, topic, urls_list, selected_kw)

            if not result or "error" in result:
                yield f"❌ Error: {result.get('error', 'Unknown error')}\\n"
                return

            titles = result.get("title_suggestions", [])

            yield "💡 Title Suggestions\\n"
            if selected_kw:
                yield f"🔑 Reference Keyword: {selected_kw}\\n\\n"
            for i, title in enumerate(titles, 1):
                yield f"{i}. {title}\\n"
                await asyncio.sleep(0.25)

            total_time = time.time() - start_time
            yield f"\\n⏱ Step 2 Time: {total_time:.2f}s\\n"

            # Pass titles to frontend via hidden comment
            import urllib.parse
            titles_encoded = urllib.parse.quote(json.dumps(titles))
            yield f"<!--TITLES:{titles_encoded}-->"

        except Exception as e:
            yield f"\\n❌ Streaming error: {str(e)}\\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# ── Step 3 endpoint — called when user clicks "Generate Outline" after selecting a title
# ── Receives topic, analysis URLs, user-selected title and keyword as query params
# ── Gemini uses selected title + keyword as primary reference to keep outline on-topic
@app.get("/stream/step3")
async def stream_step3(
    topic: str,
    urls: str = "[]",
    selected_title: str = "",
    selected_kw: str = "",
):

    start_time = time.time()

    async def event_generator():
        try:
            urls_list = json.loads(urls)
            result    = await asyncio.to_thread(
                agent.run_step3,
                topic,
                urls_list,
                selected_title,
                selected_kw,
            )

            if not result or "error" in result:
                yield f"❌ Error: {result.get('error', 'Unknown error')}\\n"
                return

            outline = result.get("outline", [])

            yield "📑 SEO Blog Outline\\n"
            if selected_title:
                yield f"📌 Title: {selected_title}\\n"
            if selected_kw:
                yield f"🔑 Primary Keyword: {selected_kw}\\n"
            yield "\\n"

            for section in outline:
                yield "\\n---------------------------\\n"
                yield f"H2: {section.get('h2', '')}\\n"
                await asyncio.sleep(0.2)
                for sub in section.get("h3", []):
                    yield f"  H3: {sub}\\n"
                    await asyncio.sleep(0.15)

            total_time = time.time() - start_time
            yield f"\\n⏱ Step 3 Time: {total_time:.2f}s\\n"
            yield "\\n✅ All steps complete.\\n"

        except Exception as e:
            yield f"\\n❌ Streaming error: {str(e)}\\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# ── Original /stream endpoint — kept for backward compatibility with api.py
# ── Runs the full pipeline in one shot: URLs + keywords + titles + outline
# ── Not used by the UI — UI uses /stream/step1, /stream/step2, /stream/step3 instead
@app.get("/stream")
async def stream(topic: str):

    start_time = time.time()

    async def event_generator():
        try:
            result = await asyncio.to_thread(agent.run, topic)

            if not result or "error" in result:
                yield f"❌ Error: {result.get('error','Unknown error')}\\n"
                return

            yield "🧠 Topic\\n"
            yield f"{result.get('topic','N/A')}\\n\\n"

            yield "🔗 Top Ranking URLs\\n"
            for url in result.get("top_urls", []):
                yield f"• {url}\\n"
                await asyncio.sleep(0.25)

            yield "\\n🔥 High-Ranking Keywords\\n"
            for kw in result.get("high_ranking_keywords", []):
                yield f"• {kw}\\n"
                await asyncio.sleep(0.25)

            titles = result.get("title_suggestions", [])
            if titles:
                yield "\\n💡 Title Suggestions\\n"
                for title in titles:
                    yield f"• {title}\\n"
                    await asyncio.sleep(0.25)

            outline = result.get("outline", [])
            if outline:
                yield "\\n📑 SEO Outline\\n"
                for section in outline:
                    yield "\\n---------------------------\\n"
                    yield f"H2: {section.get('h2')}\\n"
                    await asyncio.sleep(0.25)
                    for sub in section.get("h3", []):
                        yield f"  H3: {sub}\\n"
                        await asyncio.sleep(0.25)

            yield "\\n✅ Analysis complete.\\n"
            total_time = time.time() - start_time
            yield f"\\n⏱ Total Time: {total_time:.2f} seconds\\n"

        except Exception as e:
            yield f"\\n❌ Streaming error: {str(e)}\\n"

    return StreamingResponse(event_generator(), media_type="text/plain")