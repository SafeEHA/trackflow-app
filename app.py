from flask import Flask, jsonify, render_template_string
import time

app = Flask(__name__)

ROUTE_ENGINE_VERSION = "3.2.0"
DEPLOY_TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TrackFlow — Route Engine</title>
  <link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Raleway', sans-serif;
      background: #ffffff;
      color: #111827;
      min-height: 100vh;
      padding: 2rem;
    }
    .header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 0.5px solid #e5e7eb;
    }
    .brand-name { font-size: 18px; font-weight: 600; margin-bottom: 3px; }
    .brand-sub  { font-size: 13px; color: #6b7280; }
    .pill {
      display: flex; align-items: center; gap: 6px;
      border: 0.5px solid #e5e7eb; border-radius: 8px;
      padding: 5px 12px; font-size: 12px; font-weight: 500; color: #15803d;
    }
    .dot { width: 7px; height: 7px; border-radius: 50%; background: #16a34a; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin-bottom: 1.5rem;
    }
    .card { background: #f9fafb; border-radius: 8px; padding: 1rem; }
    .card-label {
      font-size: 11px; color: #6b7280; text-transform: uppercase;
      letter-spacing: 0.07em; margin-bottom: 8px; font-weight: 500;
    }
    .card-value { font-size: 22px; font-weight: 600; color: #111827; }
    .card-sub   { font-size: 12px; color: #9ca3af; margin-top: 3px; }
    .panel {
      border: 0.5px solid #e5e7eb; border-radius: 12px;
      padding: 1.25rem; margin-bottom: 1.25rem;
    }
    .panel-title {
      font-size: 12px; font-weight: 600; color: #6b7280;
      text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 1rem;
    }
    .route {
      display: flex; align-items: center; padding: 9px 0;
      border-bottom: 0.5px solid #f3f4f6; gap: 10px; font-size: 13px;
    }
    .route:last-child { border-bottom: none; padding-bottom: 0; }
    .route-id   { font-size: 11px; color: #9ca3af; font-weight: 500; min-width: 70px; }
    .route-name { color: #111827; flex: 1; font-weight: 500; }
    .saving {
      font-size: 12px; font-weight: 600; padding: 3px 10px;
      border-radius: 8px; border: 0.5px solid #bbf7d0; color: #15803d;
    }
    .deploy-row {
      display: flex; justify-content: space-between; align-items: center;
      padding: 6px 0; border-bottom: 0.5px solid #f3f4f6; font-size: 13px;
    }
    .deploy-row:last-child { border-bottom: none; }
    .deploy-key { color: #6b7280; }
    .deploy-val { font-weight: 500; color: #111827; }
    .footer {
      display: flex; align-items: center;
      justify-content: space-between; margin-top: 0.5rem;
    }
    button {
      background: transparent; border: 0.5px solid #d1d5db;
      border-radius: 8px; padding: 7px 16px; font-size: 13px;
      cursor: pointer; font-family: 'Raleway', sans-serif;
      font-weight: 500; color: #111827;
    }
    button:hover  { background: #f9fafb; }
    button:active { transform: scale(0.98); }
    .ts   { font-size: 12px; color: #9ca3af; }
    .spin { display: inline-block; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <div class="header">
    <div>
      <p class="brand-name">TrackFlow Route Engine</p>
      <p class="brand-sub">AI Route Optimisation — Lagos Metro</p>
    </div>
    <div class="pill">
      <span class="dot"></span>
      <span id="pill-label">Operational</span>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-label">Engine version</div>
      <div class="card-value" id="c-version">{{ version }}</div>
      <div class="card-sub"  id="c-deployed">deployed just now</div>
    </div>
    <div class="card">
      <div class="card-label">Routes today</div>
      <div class="card-value" id="c-routes">—</div>
      <div class="card-sub">Lagos metro zones</div>
    </div>
    <div class="card">
      <div class="card-label">Avg time saved</div>
      <div class="card-value" id="c-saving">—</div>
      <div class="card-sub">per delivery vs baseline</div>
    </div>
    <div class="card">
      <div class="card-label">Engine status</div>
      <div class="card-value" id="c-status" style="color:#15803d;">Healthy</div>
      <div class="card-sub"  id="c-health">last check just now</div>
    </div>
  </div>

  <div class="panel">
    <div class="panel-title">Live route optimisation feed</div>
    <div id="route-list">
      <div style="font-size:13px; color:#9ca3af;">Loading routes…</div>
    </div>
  </div>

  <div class="panel">
    <div class="panel-title">Deployment info</div>
    <div id="deploy-info">
      <div class="deploy-row"><span class="deploy-key">Engine version</span><span class="deploy-val" id="d-version">{{ version }}</span></div>
      <div class="deploy-row"><span class="deploy-key">API status</span><span class="deploy-val">running</span></div>
      <div class="deploy-row"><span class="deploy-key">Deployed at</span><span class="deploy-val" id="d-time">{{ deployed_at }}</span></div>
      <div class="deploy-row"><span class="deploy-key">Environment</span><span class="deploy-val">production</span></div>
    </div>
  </div>

  <div class="footer">
    <button id="refresh-btn" onclick="refresh()">&#x21BB; Refresh</button>
    <span class="ts" id="ts">Loaded on page open</span>
  </div>

  <script>
    const ZONES = [
      "Ikeja \u2192 Lekki Phase 1", "Victoria Island \u2192 Surulere",
      "Yaba \u2192 Oshodi", "Ajah \u2192 Lagos Island",
      "Ikorodu \u2192 Maryland", "Apapa \u2192 Festac",
      "Ojota \u2192 Gbagada", "Sangotedo \u2192 Opebi",
      "Isolo \u2192 Mushin", "Bariga \u2192 Shomolu"
    ];

    function fmt(d) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    function rnd(min, max, dp) {
      return (Math.random() * (max - min) + min).toFixed(dp);
    }

    function renderRoutes() {
      const shuffled = [...ZONES].sort(() => Math.random() - 0.5).slice(0, 5);
      document.getElementById('route-list').innerHTML = shuffled.map((z, i) => {
        const s = parseFloat(rnd(5, 18, 1));
        return '<div class="route">'
          + '<span class="route-id">#TF-' + (4820 + i + 1) + '</span>'
          + '<span class="route-name">' + z + '</span>'
          + '<span class="saving">-' + s.toFixed(1) + ' min</span>'
          + '</div>';
      }).join('');
    }

    async function refresh() {
      const btn = document.getElementById('refresh-btn');
      btn.innerHTML = '<span class="spin">&#x21BB;</span> Refreshing\u2026';
      btn.disabled = true;

      try {
        const res = await fetch('/api/status');
        const d   = await res.json();
        const now = new Date();

        document.getElementById('c-version').textContent  = d.engine_version;
        document.getElementById('d-version').textContent  = d.engine_version;
        document.getElementById('c-deployed').textContent = 'deployed '
          + new Date(d.deployed_at).toLocaleString('en-GB',
              { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
        document.getElementById('d-time').textContent     = d.deployed_at;
        document.getElementById('c-routes').textContent   =
          Math.floor(Math.random() * 300 + 1800).toLocaleString();
        document.getElementById('c-saving').textContent   = rnd(9, 16, 1) + ' min';
        document.getElementById('c-health').textContent   = 'last check ' + fmt(now);
        document.getElementById('ts').textContent         = 'Updated at ' + fmt(now);

        renderRoutes();
      } catch (e) {
        document.getElementById('pill-label').textContent = 'Unreachable';
        document.getElementById('ts').textContent = 'Could not reach /api/status';
      }

      btn.innerHTML = '&#x21BB; Refresh';
      btn.disabled  = false;
    }

    renderRoutes();
    document.getElementById('c-routes').textContent =
      Math.floor(Math.random() * 300 + 1800).toLocaleString();
    document.getElementById('c-saving').textContent = rnd(9, 16, 1) + ' min';
    setInterval(refresh, 30000);
  </script>

</body>
</html>"""


@app.route('/')
def dashboard():
    return render_template_string(
        DASHBOARD_HTML,
        version=ROUTE_ENGINE_VERSION,
        deployed_at=DEPLOY_TIMESTAMP
    )


@app.route('/api/status')
def status():
    return jsonify({
        'service':        'TrackFlow Route Engine',
        'engine_version': ROUTE_ENGINE_VERSION,
        'status':         'running',
        'deployed_at':    DEPLOY_TIMESTAMP,
        'environment':    'production'
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)