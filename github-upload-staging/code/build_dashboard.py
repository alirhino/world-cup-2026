"""Build the Iran WC 2026 Fan Dashboard HTML from the latest computed data.

Single-source-of-truth pipeline:
  data/teams_fifa_ranking_april2026.json   ──┐
  data/iran_group_stage_schedule.json      ──┤
  data/knockout_bracket_structure.json     ──┼─► compute_paths.py
  ── Annex C embedded in compute_paths.py  ──┘        │
                                                      ▼
                                            data/iran_r16_paths.json
                                                      │
                                                      ▼
                                        build_dashboard.py  (this script)
                                                      │
                                                      ▼
                              Iran_WC2026_Fan_Dashboard.html
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / "data" / "iran_r16_paths.json"))
TEAMS = json.load(open(ROOT / "data" / "teams_fifa_ranking_april2026.json"))["teams"]

# Inline both data blobs into the page (file:// blocks fetch CORS)
JS_DATA_BLOB = "const FULL_DATA = " + json.dumps(DATA, separators=(',', ':')) + ";\n"
JS_TEAMS_BLOB = "const TEAMS = " + json.dumps(TEAMS, separators=(',', ':')) + ";\n"

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iran — FIFA World Cup 2026 Fan Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --iran-green:#239F40; --iran-red:#DA0000;
    --bg:#0c0d10; --panel:#15171c; --panel-2:#1c1f26;
    --border:#262a33; --text:#e7e9ee; --muted:#8a8f9c;
    --good:#4ade80; --warn:#facc15; --bad:#f87171; --accent:#60a5fa;
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
    font:14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, system-ui, sans-serif; }
  .wrap { max-width:1240px; margin:0 auto; padding:32px 24px 80px; }

  .hero {
    background: linear-gradient(180deg, rgba(35,159,64,.08), rgba(218,0,0,.08) 100%),
                radial-gradient(1200px 200px at 70% 0, rgba(35,159,64,.25), transparent), var(--panel);
    border:1px solid var(--border); border-radius:14px; padding:28px 30px;
    margin-bottom:24px; position:relative; overflow:hidden;
  }
  .hero-flag { position:absolute; right:30px; top:30px; width:84px; height:56px;
    border-radius:6px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,.4);
    display:flex; flex-direction:column; }
  .hero-flag > div { flex:1; }
  .hero-flag > div:nth-child(1) { background:var(--iran-green); }
  .hero-flag > div:nth-child(2) { background:#fff; }
  .hero-flag > div:nth-child(3) { background:var(--iran-red); }
  .hero h1 { margin:0 0 4px; font-size:26px; font-weight:700; letter-spacing:-.4px; }
  .hero .sub { color:var(--muted); font-size:14px; }
  .hero .stats { display:flex; gap:24px; margin-top:18px; flex-wrap:wrap; }
  .stat { background:rgba(255,255,255,.03); border:1px solid var(--border);
    border-radius:10px; padding:14px 18px; min-width:180px; }
  .stat .lbl { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.6px; }
  .stat .val { font-size:24px; font-weight:700; margin-top:4px; }
  .stat .val.green { color:var(--good); }
  .stat .val.yellow { color:var(--warn); }
  .stat .sub2 { color:var(--muted); font-size:12px; margin-top:2px; }

  h2 { font-size:13px; text-transform:uppercase; letter-spacing:1.2px; color:var(--muted);
    margin:36px 0 14px; font-weight:600; }
  .panel { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:20px; }
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  .grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
  @media (max-width:900px) { .grid-2, .grid-3 { grid-template-columns:1fr; } }

  .match-card { background:var(--panel-2); border:1px solid var(--border); border-radius:10px;
    padding:16px; display:flex; flex-direction:column; gap:8px; }
  .match-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
  .team-code { background:rgba(255,255,255,.06); padding:4px 8px; border-radius:5px;
    font-family:ui-monospace, SFMono-Regular, monospace; font-size:12px; border:1px solid var(--border); }
  .team-code.iran { background:rgba(35,159,64,.18); border-color:rgba(35,159,64,.5); color:#a7f3d0; }
  .vs { color:var(--muted); font-size:12px; }
  .venue-line { color:var(--muted); font-size:13px; display:flex; gap:10px; align-items:center; }
  .pill { display:inline-flex; align-items:center; gap:6px; padding:2px 8px; border-radius:999px;
    font-size:11px; background:rgba(255,255,255,.05); border:1px solid var(--border); color:var(--muted); }
  .pill.iran { background:rgba(35,159,64,.12); border-color:rgba(35,159,64,.35); color:#a7f3d0; }

  table { width:100%; border-collapse:collapse; }
  th, td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--border); }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.6px; }
  tbody tr:hover { background:rgba(255,255,255,.02); }
  td.num { font-variant-numeric:tabular-nums; text-align:right; }
  .badge { display:inline-block; padding:2px 8px; border-radius:5px; font-size:11px; font-weight:600; }
  .badge.tier-1 { background:rgba(74,222,128,.15); color:#86efac; }
  .badge.tier-2 { background:rgba(250,204,21,.15); color:#fde047; }
  .badge.tier-3 { background:rgba(248,113,113,.15); color:#fca5a5; }

  /* Paths */
  .paths-wrap { display:flex; flex-direction:column; gap:10px; }
  .path-card { background:var(--panel); border:1px solid var(--border); border-radius:10px; overflow:hidden; transition:border-color .2s; }
  .path-card:hover { border-color:rgba(96,165,250,.35); }
  .path-card.expanded { border-color:rgba(96,165,250,.5); }
  .path-header { display:grid;
    grid-template-columns:46px 1fr 200px 200px 110px 24px;
    gap:14px; align-items:center; padding:14px 16px; cursor:pointer; user-select:none; }
  @media (max-width:1100px) { .path-header { grid-template-columns:46px 1fr 60px; row-gap:8px; }
    .path-header > *:nth-child(3), .path-header > *:nth-child(4), .path-header > *:nth-child(5) { grid-column:span 2; } }
  .path-rank { color:var(--muted); font-family:ui-monospace,monospace; font-weight:700; font-size:13px; text-align:center; }
  .path-main .opp { font-size:15px; font-weight:600; }
  .path-main .opp-meta { color:var(--muted); font-weight:normal; font-size:12px; }
  .path-main .finish { color:var(--muted); font-size:12px; margin-top:2px; }
  .path-r32 { background:rgba(255,255,255,.03); border:1px solid var(--border); padding:6px 10px; border-radius:6px; font-size:11.5px; }
  .path-r16 { background:rgba(35,159,64,.08); border:1px solid rgba(35,159,64,.25); padding:6px 10px; border-radius:6px; font-size:11.5px; color:#bbf7d0; }
  .path-prob { text-align:right; }
  .path-prob .pct { font-size:18px; font-weight:700; }
  .path-prob .pct.high { color:var(--good); }
  .path-prob .pct.mid { color:var(--warn); }
  .path-prob .pct.low { color:var(--muted); }
  .path-prob .detail { font-size:10px; color:var(--muted); margin-top:2px; }
  .path-chevron { color:var(--muted); font-size:18px; transition:transform .25s; text-align:center; }
  .path-card.expanded .path-chevron { transform:rotate(180deg); color:var(--accent); }
  .path-body { padding:0 16px 18px; display:none; }
  .path-card.expanded .path-body { display:block; animation:reveal .25s ease; }
  @keyframes reveal { from { opacity:0; transform:translateY(-4px);} to { opacity:1; transform:none;} }

  .chain { background:rgba(0,0,0,.18); border:1px solid var(--border); border-radius:8px; padding:14px 16px; }
  .chain h4 { margin:0 0 12px; font-size:11.5px; text-transform:uppercase; letter-spacing:.8px; color:var(--muted); }
  .chain-step { display:grid; grid-template-columns:30px 1fr 80px 220px; gap:12px; align-items:center; padding:6px 0; font-size:13.5px; }
  .chain-step .op { color:var(--muted); font-family:ui-monospace,monospace; text-align:center; font-size:16px; }
  .chain-step .label { color:var(--text); }
  .chain-step .label .why { color:var(--muted); font-size:11.5px; margin-top:2px; }
  .chain-step .pct { font-variant-numeric:tabular-nums; text-align:right; font-weight:600; color:#cbd5e1; }
  .chain-bar { background:rgba(255,255,255,.06); border-radius:4px; height:8px; overflow:hidden; }
  .chain-bar > div { height:100%; background:linear-gradient(90deg, #60a5fa, #4ade80); border-radius:4px; }
  .chain-total { display:grid; grid-template-columns:30px 1fr 80px 220px; gap:12px;
    margin-top:8px; padding-top:10px; border-top:1px dashed var(--border);
    font-size:14.5px; align-items:center; }
  .chain-total .op { text-align:center; color:#60a5fa; font-weight:600; }
  .chain-total .pct { color:#a7f3d0; font-weight:700; }

  .group-mini { margin-top:14px; }
  .group-mini h4 { margin:0 0 8px; font-size:11.5px; text-transform:uppercase; letter-spacing:.8px; color:var(--muted); }
  .group-mini h4 .role { color:#a7f3d0; }
  .gm-row { display:grid; grid-template-columns:140px 1fr; gap:10px; align-items:center; padding:5px 0; font-size:12.5px; }
  .gm-row .gm-name { color:var(--text); font-size:13px; }
  .gm-row .gm-name.opp { color:#a7f3d0; font-weight:600; }
  .gm-row .gm-name .gm-rank { color:var(--muted); font-weight:normal; font-size:11px; margin-left:6px; }
  .gm-stack { display:flex; height:14px; border-radius:3px; overflow:hidden; background:rgba(255,255,255,.04); border:1px solid var(--border); }
  .gm-stack > div { height:100%; display:flex; align-items:center; justify-content:center;
    font-size:10px; color:rgba(255,255,255,.85); font-variant-numeric:tabular-nums; }
  .gm-stack > .p1 { background:#239F40; }     /* 1st */
  .gm-stack > .p2 { background:#4ade80; }     /* 2nd */
  .gm-stack > .p3 { background:#facc15; color:#111;}     /* 3rd — qualifying role highlighted */
  .gm-stack > .p4 { background:#7f1d1d; }     /* 4th */
  .gm-stack > .p3.role { box-shadow:inset 0 0 0 2px #fff; }
  .gm-legend { font-size:11px; color:var(--muted); display:flex; gap:14px; margin-top:6px; }
  .gm-legend .sw { display:inline-block; width:10px; height:10px; border-radius:2px; vertical-align:middle; margin-right:4px; }

  .filter-bar { display:flex; gap:10px; margin-bottom:12px; align-items:center; flex-wrap:wrap; }
  .filter-bar button { background:var(--panel-2); color:var(--text); border:1px solid var(--border);
    padding:6px 12px; border-radius:6px; cursor:pointer; font-size:13px; }
  .filter-bar button.active { border-color:var(--accent); color:var(--accent); }
  .filter-bar input { background:var(--panel-2); color:var(--text); border:1px solid var(--border);
    padding:6px 12px; border-radius:6px; font-size:13px; width:200px; }
  .filter-bar .right { margin-left:auto; color:var(--muted); font-size:12px; }

  .callout { background: linear-gradient(135deg, rgba(35,159,64,.10), rgba(218,0,0,.10));
    border:1px solid var(--border); border-radius:12px; padding:18px 20px; margin-bottom:16px; }
  .callout h3 { margin:0 0 8px; font-size:14px; color:var(--text); }
  .callout p { margin:4px 0; color:var(--muted); font-size:13px; }
  .callout .key { color:var(--text); font-weight:600; }
  .callout .seattle { color:#7dd3fc; }
  .callout .atlanta { color:#fca5a5; }

  .chart-box { background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:16px; }
  details { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:14px 18px; margin-top:14px; }
  details summary { cursor:pointer; color:var(--text); font-size:13px; user-select:none; }
  details p, details li { color:var(--muted); font-size:13px; line-height:1.6; }
  details code { background:rgba(255,255,255,.06); padding:1px 5px; border-radius:3px; font-size:12px; }
  details .math { background:rgba(96,165,250,.05); border-left:2px solid var(--accent);
    padding:8px 12px; margin:8px 0; font-family:ui-monospace,monospace; font-size:12.5px; color:#cbd5e1; }
  footer { color:var(--muted); font-size:12px; margin-top:30px; text-align:center; }

  .nav { display:flex; gap:8px; margin-bottom:16px; border-bottom:1px solid var(--border); padding-bottom:0; }
  .nav button { background:transparent; color:var(--muted); border:0; padding:10px 16px; cursor:pointer;
    font-size:14px; border-bottom:2px solid transparent; margin-bottom:-1px; }
  .nav button.active { color:var(--text); border-bottom-color:var(--iran-green); }
  .nav button:hover { color:var(--text); }
  .tab-pane { display:none; }
  .tab-pane.active { display:block; animation:fade .2s ease; }
  @keyframes fade { from { opacity:0; transform:translateY(2px);} to { opacity:1; transform:none;} }
</style>
</head>
<body>
<div class="wrap">

  <!-- HERO -->
  <div class="hero">
    <div class="hero-flag" title="Flag of Iran"><div></div><div></div><div></div></div>
    <h1>Team Melli at the 2026 FIFA World Cup</h1>
    <div class="sub">Group G &middot; Iran with Belgium, Egypt, New Zealand &middot; FIFA rank #20 (1,615 pts)</div>
    <div class="stats">
      <div class="stat"><div class="lbl">Reaches R16</div>
        <div class="val green" id="stat-total">—</div>
        <div class="sub2">Via 1st OR 2nd place</div></div>
      <div class="stat"><div class="lbl">Via winning Group G</div>
        <div class="val yellow" id="stat-via-1st">—</div>
        <div class="sub2">→ Seattle R32 + Seattle R16</div></div>
      <div class="stat"><div class="lbl">Via runner-up</div>
        <div class="val" id="stat-via-2nd">—</div>
        <div class="sub2">→ Dallas R32 + Atlanta R16</div></div>
      <div class="stat"><div class="lbl">Most likely path</div>
        <div class="val" id="stat-top-opp">—</div>
        <div class="sub2" id="stat-top-detail">—</div></div>
    </div>
  </div>

  <!-- NAV -->
  <div class="nav">
    <button class="active" data-tab="schedule">Schedule</button>
    <button data-tab="group">Group G</button>
    <button data-tab="paths">Paths to R16</button>
    <button data-tab="tickets">Ticket Decision</button>
    <button data-tab="method">Methodology</button>
  </div>

  <!-- TAB: SCHEDULE -->
  <div class="tab-pane active" id="tab-schedule">
    <h2>Iran &mdash; Group Stage Matches</h2>
    <div class="grid-3" id="iran-matches"></div>
    <h2>Other Group G Matches (Worth Watching for Tiebreakers)</h2>
    <div class="grid-3" id="other-matches"></div>
  </div>

  <!-- TAB: GROUP G -->
  <div class="tab-pane" id="tab-group">
    <h2>Group G Profile (April 2026 FIFA Ranking)</h2>
    <div class="panel">
      <table id="group-table">
        <thead><tr>
          <th>Team</th><th class="num">FIFA Rank</th><th class="num">Points</th>
          <th>Confederation</th><th>Strength Tier</th>
          <th>Win prob vs Iran (90 min, no draws)</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <h2>Iran's Group Finish Distribution (80,000 simulations)</h2>
    <div class="chart-box" style="height:280px;"><canvas id="finish-chart"></canvas></div>
  </div>

  <!-- TAB: PATHS -->
  <div class="tab-pane" id="tab-paths">
    <h2>Every Path Iran Can Take to the Round of 16</h2>
    <div class="callout">
      <p>Each row is one specific way Iran can reach the R16. <span class="key">Click any row</span> to expand the opponent's qualification chain &mdash; what had to happen for that opponent to end up facing Iran, and how probable each step is.</p>
      <p>Sorted <span class="key">least likely &rarr; most likely</span>. Path probability = P(Iran finishes that group position) &times; P(opponent reaches Iran's R32 slot) &times; P(Iran wins R32).</p>
    </div>
    <div class="filter-bar">
      <button data-filter="all" class="active">All 24 paths</button>
      <button data-filter="1st">Iran 1st only (20)</button>
      <button data-filter="2nd">Iran 2nd only (4)</button>
      <input id="search-input" type="text" placeholder="Filter by opponent name…">
      <span class="right" id="path-count"></span>
    </div>
    <div class="paths-wrap" id="paths-list"></div>
  </div>

  <!-- TAB: TICKETS -->
  <div class="tab-pane" id="tab-tickets">
    <h2>Ticket Decision Tree</h2>
    <div class="callout">
      <h3>Your conditional R16 tickets need to be in one of two cities</h3>
      <p>If Iran <span class="key seattle">wins Group G</span> &rarr; R16 match is <span class="key seattle">Lumen Field, Seattle</span>, Jul 6, 8:00 PM ET (5:00 PM PT).</p>
      <p>If Iran <span class="key atlanta">finishes 2nd</span> &rarr; R16 match is <span class="key atlanta">Mercedes-Benz Stadium, Atlanta</span>, Jul 7, 12:00 PM ET.</p>
      <p style="margin-top:10px;">Bracket locks <span class="key">June 27</span>. Iran's group finish is decided after their final group match on <span class="key">June 26 (Egypt vs Iran, Seattle)</span>. You have ~<span class="key">8&ndash;10 days</span> to confirm tickets.</p>
    </div>
    <div class="grid-2">
      <div class="panel" style="border-color:rgba(125,211,252,.3);">
        <h3 style="margin:0 0 14px; color:#7dd3fc;">Scenario A — Iran wins Group G</h3>
        <p style="color:var(--muted); margin:6px 0;">Probability: <span class="key" id="ticket-1st-prob">—</span></p>
        <table style="margin-top:8px;">
          <tr><th>R32</th><td>M82 — Lumen Field, Seattle<br><span style="color:var(--muted)">Jul 1, 16:00 ET (13:00 PT)</span></td></tr>
          <tr><th>Opponent</th><td>Best 3rd-place from Group A/E/H/I/J<br><span style="color:var(--muted)">Most likely: Czechia, South Africa, Korea Republic</span></td></tr>
          <tr><th>R16 (if win)</th><td>M94 — Lumen Field, Seattle<br><span style="color:var(--muted)">Jul 6, 20:00 ET (17:00 PT)</span></td></tr>
          <tr><th>R16 opponent</th><td>Winner of (Group D winner vs best 3rd B/E/F/I/J)<br><span style="color:var(--muted)">Likely USA, Türkiye, or Germany</span></td></tr>
        </table>
        <p style="color:var(--muted); margin-top:14px; font-size:13px;">
          <strong>Travel note:</strong> Same stadium R32 &rarr; R16, 5 days apart. Single lodging. DC&rarr;SEA is ~6 hr direct.
        </p>
      </div>
      <div class="panel" style="border-color:rgba(252,165,165,.3);">
        <h3 style="margin:0 0 14px; color:#fca5a5;">Scenario B — Iran 2nd in Group G</h3>
        <p style="color:var(--muted); margin:6px 0;">Probability: <span class="key" id="ticket-2nd-prob">—</span></p>
        <table style="margin-top:8px;">
          <tr><th>R32</th><td>AT&amp;T Stadium, Arlington/Dallas<br><span style="color:var(--muted)">Jul 3, 14:00 ET</span></td></tr>
          <tr><th>Opponent</th><td>Runner-up of Group D<br><span style="color:var(--muted)">Most likely Türkiye, Australia, or USA</span></td></tr>
          <tr><th>R16 (if win)</th><td>Mercedes-Benz Stadium, Atlanta<br><span style="color:var(--muted)">Jul 7, 12:00 ET</span></td></tr>
          <tr><th>R16 opponent</th><td>Winner of (Group J winner vs Group H runner-up)<br><span style="color:var(--muted)">Likely Argentina or Spain/Uruguay</span></td></tr>
        </table>
        <p style="color:var(--muted); margin-top:14px; font-size:13px;">
          <strong>Travel note:</strong> Dallas then Atlanta — ~2 hr direct flight. Two hotel bookings.
        </p>
      </div>
    </div>
  </div>

  <!-- TAB: METHODOLOGY -->
  <div class="tab-pane" id="tab-method">
    <h2>How These Numbers Are Computed</h2>
    <div class="panel">
      <p style="color:var(--text); line-height:1.7; margin:0 0 6px;">
        <strong style="color:var(--text)">Monte Carlo simulation, 80,000 runs.</strong> Every run plays out the entire group stage for all 12 groups, then resolves Iran's specific R32 matchup using FIFA's published bracket rules. The simulation is deterministic given the seed (<code>random.seed(20260614)</code>).
      </p>
      <details open>
        <summary><strong>Step 1 — Per-match win/draw/loss probabilities</strong></summary>
        <p>FIFA's SUM ranking system updates points after matches using an Elo-style formula with divisor <code>600</code>. We invert it to get pre-match win probabilities:</p>
        <div class="math">P(A beats B, no draw) = 1 / (1 + 10<sup>−(pts<sub>A</sub> − pts<sub>B</sub>)/600</sup>)</div>
        <p>Worked example for <strong>Iran vs Belgium</strong>: pts<sub>IRN</sub>=1615.3, pts<sub>BEL</sub>=1734.7, gap = −119.4.<br>
        P(Iran beats Belgium) = 1 / (1 + 10<sup>119.4/600</sup>) = 1 / (1 + 10<sup>0.199</sup>) = 1 / (1 + 1.58) = <strong>38.7%</strong>.</p>
        <p>For group-stage matches we add a draw probability that decays with the rating gap:</p>
        <div class="math">P(draw) ≈ 0.28 × exp(−gap² / 300²)</div>
        <p>So evenly-matched sides draw ~28% of the time, falling toward 0 for blowouts. Iran vs Belgium has P(draw) ≈ 0.24, and the W/L probabilities scale to fill the remaining 76%.</p>
      </details>
      <details>
        <summary><strong>Step 2 — Simulate every group's 6 matches, rank by FIFA tiebreakers</strong></summary>
        <p>Each group has 4 teams and 6 round-robin matches. After all 6 are played, teams are ranked by:</p>
        <ol>
          <li>Total points (3-1-0)</li>
          <li>Goal difference</li>
          <li>Goals for</li>
          <li>Deterministic tiebreak by FIFA rating (proxy for fair-play / drawn lots — rare edge cases only)</li>
        </ol>
        <p>For Group G, Iran's typical outcomes look like:</p>
        <ul>
          <li>Beat NZL (78.3% per match), beat EGY (55.0%), at-least-draw BEL (~57% any non-loss) → <strong>Iran wins the group</strong></li>
          <li>Lose or draw BEL but beat both other → <strong>Iran 2nd</strong></li>
          <li>Lose to BEL AND drop points to either EGY or NZL → <strong>Iran 3rd or 4th</strong></li>
        </ul>
        <p>Counting Iran's finish position across 80,000 simulations gives: <strong>1st 23.9%, 2nd 40.4%, 3rd 25.7%, 4th 10.0%</strong>.</p>
      </details>
      <details>
        <summary><strong>Step 3 — Resolve Iran's R32 opponent</strong></summary>
        <p>Per FIFA's published bracket:</p>
        <ul>
          <li>If Iran wins Group G → plays Match 82 vs the best-3rd-place team from Group A/E/H/I/J (specific team determined by Annex C's 495-row mapping)</li>
          <li>If Iran 2nd → plays Match 88 vs Group D runner-up</li>
        </ul>
        <p>For each simulation we (a) collect all 12 third-placed teams' tiebreaker records, (b) pick the best 8 to qualify, and (c) look up which group's 3rd-place team is assigned to face Iran via the Annex C combo for those 8 qualifying groups.</p>
      </details>
      <details>
        <summary><strong>Step 4 — Knockout match resolution</strong></summary>
        <p>R32 matches are sampled as binary win/lose using the same Elo formula (no draw — extra time + penalties collapse into a single Bernoulli outcome with equal variance contribution from both sides). Iran's R32 win probability is computed per opponent.</p>
      </details>
      <details>
        <summary><strong>Step 5 — Path probability decomposition</strong></summary>
        <p>For each path (e.g. <em>Iran 1st → Czechia → R16 in Seattle</em>):</p>
        <div class="math">P(path) = P(Iran 1st) × P(opp 3rd in their group) × P(group selected & assigned to 1G | opp 3rd) × P(Iran wins R32)</div>
        <p>For <strong>Czechia (the most-likely 1st-place path)</strong>: 0.239 × 0.340 × 0.595 × 0.602 = <strong>2.91%</strong>.</p>
        <p>For <strong>Türkiye (the most-likely 2nd-place path)</strong>: 0.404 × 0.302 × 1.0 × 0.520 = <strong>6.32%</strong>.</p>
        <p>Summing across all 24 paths gives Iran's total chance of reaching the R16 via 1st or 2nd place = <strong>34.2%</strong>.</p>
      </details>
      <details>
        <summary><strong>Limitations</strong></summary>
        <ul>
          <li>FIFA rankings are a lagging proxy for current form. Squad changes / injuries Apr→Jun aren't modeled.</li>
          <li>Home-region advantage is partially baked into ratings but not explicitly modeled (USA could outperform; Iran on US soil with massive LA diaspora — unclear net effect).</li>
          <li>Iran's path via 3rd place (best-of-8) is excluded by design per your request. Including it adds roughly 10–15 percentage points to Iran's total R16 probability.</li>
          <li>The draw probability shape is heuristic. A beta-binomial fit to historical group-stage data would tighten the model but the relative path ordering would barely change.</li>
        </ul>
      </details>
      <details>
        <summary><strong>Data lineage</strong></summary>
        <ul>
          <li>FIFA Apr-2026 rankings — <code>data/teams_fifa_ranking_april2026.json</code> (via football-ranking.com mirror of inside.fifa.com)</li>
          <li>Iran group schedule — <code>data/iran_group_stage_schedule.json</code> (FIFA + Yahoo Sports + Al Jazeera cross-check)</li>
          <li>Knockout bracket + venues — <code>data/knockout_bracket_structure.json</code></li>
          <li>Annex C 495-row table — embedded in <code>code/compute_paths.py</code></li>
          <li>Computed paths — <code>data/iran_r16_paths.json</code></li>
          <li>This page — built by <code>code/build_dashboard.py</code></li>
        </ul>
      </details>
    </div>
  </div>

  <footer>
    Built from FIFA April 2026 rankings + official 2026 World Cup schedule &middot; Monte Carlo (n=80,000) &middot; Re-run <code>python3 code/compute_paths.py &amp;&amp; python3 code/build_dashboard.py</code> to refresh
  </footer>
</div>

<script>
__DATA_BLOB__
__TEAMS_BLOB__

// --------------------------------------------------------------
// Page boot
// --------------------------------------------------------------
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);
const fmt1 = p => (p*100).toFixed(1) + "%";
const fmt2 = p => (p*100).toFixed(2) + "%";

// Static group G info (small enough to keep inline)
const groupG = ["BEL","EGY","IRN","NZL"].map(c => Object.assign({code:c, conf:({BEL:"UEFA",EGY:"CAF",IRN:"AFC",NZL:"OFC"})[c]}, TEAMS[c]));
const iranMatches = [
  { date:"Mon Jun 15, 2026", localTime:"6:00 PM PT", easternTime:"9:00 PM ET",
    home:"IRN", away:"NZL", venue:"SoFi Stadium (LA Stadium)", city:"Inglewood, CA",
    note:"Tournament opener for Iran" },
  { date:"Sun Jun 21, 2026", localTime:"12:00 PM PT", easternTime:"3:00 PM ET",
    home:"BEL", away:"IRN", venue:"SoFi Stadium (LA Stadium)", city:"Inglewood, CA",
    note:"Decisive match for top spot" },
  { date:"Fri Jun 26, 2026", localTime:"8:00 PM PT", easternTime:"11:00 PM ET",
    home:"EGY", away:"IRN", venue:"Lumen Field (Seattle Stadium)", city:"Seattle, WA",
    note:"Seattle Pride Match (designation contested by Iran + Egypt FA)" }
];
const otherG = [
  { date:"Mon Jun 15", time:"3:00 PM ET", match:"BEL vs EGY", venue:"Lumen Field, Seattle" },
  { date:"Sun Jun 21", time:"9:00 PM ET", match:"NZL vs EGY", venue:"BC Place, Vancouver" },
  { date:"Fri Jun 26", time:"11:00 PM ET", match:"NZL vs BEL", venue:"BC Place, Vancouver" }
];

// --------------------------------------------------------------
// Hero stats
// --------------------------------------------------------------
const headline = FULL_DATA.headline;
$("#stat-total").textContent = (headline.total_p_iran_reaches_r16*100).toFixed(1) + "%";
$("#stat-via-1st").textContent = (headline.via_winning_group*100).toFixed(1) + "%";
$("#stat-via-2nd").textContent = (headline.via_runner_up*100).toFixed(1) + "%";
const topPath = FULL_DATA.paths.reduce((a,b)=> b.p_path_to_r16 > a.p_path_to_r16 ? b : a);
$("#stat-top-opp").textContent = topPath.r32_opponent;
$("#stat-top-detail").textContent = `${topPath.iran_group_finish.split(" ")[0]} place → ${topPath.r32_opponent} (${fmt2(topPath.p_path_to_r16)})`;
$("#ticket-1st-prob").textContent = (headline.via_winning_group*100).toFixed(1) + "%";
$("#ticket-2nd-prob").textContent = (headline.via_runner_up*100).toFixed(1) + "%";

// --------------------------------------------------------------
// Schedule
// --------------------------------------------------------------
const iranBox = $("#iran-matches");
iranMatches.forEach(m => {
  iranBox.innerHTML += `
    <div class="match-card">
      <div class="match-row">
        <span class="team-code ${m.home==='IRN'?'iran':''}">${m.home}</span>
        <span class="vs">vs</span>
        <span class="team-code ${m.away==='IRN'?'iran':''}">${m.away}</span>
      </div>
      <div class="venue-line"><span class="pill iran">${m.date}</span></div>
      <div class="venue-line">${m.localTime} <span style="color:var(--muted)">·</span> ${m.easternTime} <span style="color:var(--muted)">(yours)</span></div>
      <div class="venue-line">📍 ${m.venue}, ${m.city}</div>
      ${m.note ? `<div class="venue-line" style="color:var(--muted); font-style:italic;">${m.note}</div>`: ''}
    </div>`;
});
const otherBox = $("#other-matches");
otherG.forEach(m => {
  otherBox.innerHTML += `
    <div class="match-card">
      <div class="match-row"><div style="font-weight:600;">${m.match}</div></div>
      <div class="venue-line"><span class="pill">${m.date}</span> ${m.time}</div>
      <div class="venue-line">📍 ${m.venue}</div>
    </div>`;
});

// --------------------------------------------------------------
// Group G table + finish chart
// --------------------------------------------------------------
const iranPts = TEAMS.IRN.pts;
const gBody = $("#group-table tbody");
groupG.slice().sort((a,b)=> a.rank - b.rank).forEach(t => {
  const isIran = t.code === "IRN";
  let winP = "—", tier = "";
  if (!isIran) {
    const p = 1 / (1 + Math.pow(10, -(iranPts - t.pts)/600));
    winP = (p*100).toFixed(1) + "%";
    if (p > 0.6) tier = '<span class="badge tier-1">Iran favored</span>';
    else if (p > 0.4) tier = '<span class="badge tier-2">Toss-up</span>';
    else tier = '<span class="badge tier-3">Iran underdog</span>';
  }
  gBody.innerHTML += `
    <tr ${isIran ? 'style="background:rgba(35,159,64,.06);"' : ''}>
      <td><strong>${t.name}</strong> ${isIran ? '<span class="pill iran" style="margin-left:6px;">🇮🇷 you</span>': ''}</td>
      <td class="num">#${t.rank}</td>
      <td class="num">${t.pts.toFixed(1)}</td>
      <td>${t.conf}</td>
      <td>${isIran ? '<span class="pill iran">—</span>' : tier}</td>
      <td class="num">${winP}</td>
    </tr>`;
});

const iranFinish = FULL_DATA.iran_group_finish;
new Chart($("#finish-chart"), {
  type:"bar",
  data:{ labels:["1st (advances)","2nd (advances)","3rd (best-of-8 only)","4th (out)"],
         datasets:[{ data:[iranFinish["1st_pct"], iranFinish["2nd_pct"], iranFinish["3rd_pct"], iranFinish["4th_pct"]],
                     backgroundColor:["#239F40","#4ade80","#facc15","#f87171"], borderRadius:6 }] },
  options:{ plugins:{ legend:{display:false},
                      tooltip:{callbacks:{label:c=>` ${c.parsed.y.toFixed(2)}%`}} },
            scales:{ y:{beginAtZero:true, ticks:{color:"#8a8f9c", callback:v=>v+"%"}, grid:{color:"#262a33"}},
                     x:{ticks:{color:"#e7e9ee"}, grid:{display:false}} },
            maintainAspectRatio:false }
});

// --------------------------------------------------------------
// Paths — expandable rows with qualification chain + group mini chart
// --------------------------------------------------------------
function tier(pct) { return pct > 4 ? "high" : pct > 1 ? "mid" : "low"; }

function chainStepRow(step, isLast) {
  const op = isLast ? "" : "×";
  const pct = step.prob * 100;
  return `
    <div class="chain-step">
      <div class="op">${op}</div>
      <div class="label">${step.step}<div class="why">${step.explain}</div></div>
      <div class="pct">${pct.toFixed(2)}%</div>
      <div class="chain-bar"><div style="width:${Math.max(2, Math.min(100, pct))}%;"></div></div>
    </div>`;
}

function groupMiniViz(path) {
  // For Iran-1st paths: show source group, highlight 3rd-place
  // For Iran-2nd paths: show Group D, highlight 2nd-place
  const isFirst = path.iran_group_finish.startsWith("1st");
  const sourceGroup = path.opp_group; // for Iran 1st: A/E/H/I/J; for Iran 2nd: D
  const requiredPos = isFirst ? "p_3rd" : "p_2nd";
  const requiredPosLabel = isFirst ? "3rd" : "2nd";
  const teams = FULL_DATA.group_finish_distribution[sourceGroup].slice()
                  .sort((a,b)=> TEAMS[a.code].rank - TEAMS[b.code].rank);
  const rows = teams.map(t => {
    const isOpp = t.code === path.r32_opponent_code;
    const p1 = t.p_1st*100, p2 = t.p_2nd*100, p3 = t.p_3rd*100, p4 = t.p_4th*100;
    const seg = (cls, v, role) => v < 2 ? "" : `<div class="${cls}${role?' role':''}" style="flex:${v};">${v>=8?v.toFixed(0)+'%':''}</div>`;
    return `
      <div class="gm-row">
        <div class="gm-name ${isOpp?'opp':''}">${t.name}${isOpp?' ← needs '+requiredPosLabel:''}<span class="gm-rank">#${t.rank}</span></div>
        <div class="gm-stack">
          ${seg('p1', p1, isOpp && requiredPos==='p_1st')}
          ${seg('p2', p2, isOpp && requiredPos==='p_2nd')}
          ${seg('p3', p3, isOpp && requiredPos==='p_3rd')}
          ${seg('p4', p4, isOpp && requiredPos==='p_4th')}
        </div>
      </div>`;
  }).join("");
  return `
    <div class="group-mini">
      <h4>Group ${sourceGroup} simulated finish probabilities &middot; <span class="role">opponent needs ${requiredPosLabel} place</span></h4>
      ${rows}
      <div class="gm-legend">
        <span><span class="sw" style="background:#239F40"></span>1st</span>
        <span><span class="sw" style="background:#4ade80"></span>2nd</span>
        <span><span class="sw" style="background:#facc15"></span>3rd</span>
        <span><span class="sw" style="background:#7f1d1d"></span>4th</span>
        <span style="margin-left:auto;">White outline = the slot the opponent needs to fill</span>
      </div>
    </div>`;
}

function pathCard(p, rank) {
  const pct = p.p_path_to_r16 * 100;
  const chain = p.qualification_chain;
  const chainHTML = chain.map((s, i)=> chainStepRow(s, false)).join("");
  return `
    <div class="path-card" data-finish="${p.iran_group_finish.startsWith('1st') ? '1st' : '2nd'}" data-opp="${p.r32_opponent.toLowerCase()}">
      <div class="path-header">
        <div class="path-rank">#${rank}</div>
        <div class="path-main">
          <div class="opp">vs <strong>${p.r32_opponent}</strong>
            <span class="opp-meta">(#${p.opp_fifa_rank} · ${p.opp_fifa_pts.toFixed(0)} pts · ${p.opp_qualification_route})</span>
          </div>
          <div class="finish">${p.iran_group_finish} · P(R32 win) = ${(p.p_iran_wins_r32_vs_this_opp*100).toFixed(1)}%</div>
        </div>
        <div class="path-r32"><strong>R32:</strong> ${p.r32_match}</div>
        <div class="path-r16"><strong>R16:</strong> ${p.r16_match_if_advance}</div>
        <div class="path-prob">
          <div class="pct ${tier(pct)}">${pct.toFixed(2)}%</div>
          <div class="detail">P(finish) ${(p.p_iran_finishes_this_position*100).toFixed(0)}% · P(opp) ${(p.p_this_opponent_given_finish*100).toFixed(1)}%</div>
        </div>
        <div class="path-chevron">▾</div>
      </div>
      <div class="path-body">
        <div class="chain">
          <h4>Qualification chain</h4>
          ${chainHTML}
          <div class="chain-total">
            <div class="op">=</div>
            <div class="label">Joint probability of this exact path</div>
            <div class="pct">${pct.toFixed(2)}%</div>
            <div class="chain-bar"><div style="width:${Math.max(2, Math.min(100, pct*5))}%; background:linear-gradient(90deg,#239F40,#4ade80);"></div></div>
          </div>
        </div>
        ${groupMiniViz(p)}
      </div>
    </div>`;
}

function renderPaths(filter, search) {
  const list = $("#paths-list");
  list.innerHTML = "";
  let shown = 0;
  FULL_DATA.paths.forEach((p, i) => {
    const isFirst = p.iran_group_finish.startsWith("1st");
    if (filter === "1st" && !isFirst) return;
    if (filter === "2nd" && isFirst) return;
    if (search && !p.r32_opponent.toLowerCase().includes(search.toLowerCase())) return;
    list.innerHTML += pathCard(p, i+1);
    shown++;
  });
  $("#path-count").textContent = `Showing ${shown} of ${FULL_DATA.paths.length} paths`;
  // wire up clicks
  $$(".path-card .path-header").forEach(h => {
    h.addEventListener("click", () => h.parentElement.classList.toggle("expanded"));
  });
}
renderPaths("all", "");

// Filters
$$(".filter-bar button").forEach(b => {
  b.addEventListener("click", () => {
    $$(".filter-bar button").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    renderPaths(b.dataset.filter, $("#search-input").value);
  });
});
$("#search-input").addEventListener("input", e => {
  const f = document.querySelector(".filter-bar button.active").dataset.filter;
  renderPaths(f, e.target.value);
});

// Tab navigation
$$(".nav button").forEach(b => {
  b.addEventListener("click", () => {
    $$(".nav button").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    $$(".tab-pane").forEach(x => x.classList.remove("active"));
    $(`#tab-${b.dataset.tab}`).classList.add("active");
  });
});
</script>
</body>
</html>
"""

html = HTML.replace("__DATA_BLOB__", JS_DATA_BLOB).replace("__TEAMS_BLOB__", JS_TEAMS_BLOB)
out = ROOT / "Iran_WC2026_Fan_Dashboard.html"
out.write_text(html)
print(f"Wrote {out} ({len(html):,} bytes)")
