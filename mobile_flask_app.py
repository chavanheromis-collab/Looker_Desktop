"""
Flask demo to serve a mobile-friendly, attractive page that embeds a Looker Studio (Google Data Studio) report.

How to use:
1. Install dependencies: pip install flask
2. Replace REPORT_URL with your Looker Studio *shareable* URL (the URL used for embedding).
   - Make sure the report is shared appropriately (Anyone with link can view) or the embed will show a sign-in wall.
3. Run: python looker_mobile_flask_app.py
4. Expose to mobile: use ngrok/localtunnel or host on a server and open the URL on your phone.

Notes:
- This is a minimal, mobile-first layout using Tailwind via CDN. The page includes zoom controls, a fullscreen toggle, a compact header, and a bottom nav for quick actions.
- The iframe is responsive and will keep the report usable on narrow screens.
- If you want to embed multiple pages or add authentication, extend the app accordingly.
"""

from flask import Flask, render_template_string, request

app = Flask(__name__)

# ----- CONFIGURE THIS -----
REPORT_URL = "https://lookerstudio.google.com/embed/reporting/103aa740-f3fa-458e-b496-a6861c15c88c/page/p_qpwrvqb8ud"  # <-- replace
PORT = 5000
# -------------------------

TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>   
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Looker Studio - Mobile Viewer</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Make iframe behave like a touch-friendly embedded app */
    html,body,#app{height:100%;}
    .report-frame { border: none; width:100%; height:100%; transform-origin: top center; }
    /* Container height accounts for header and bottom nav */
    .view-area { height: calc(100vh - 4.5rem); }
    /* Small visual polish */
    .glass { background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)); backdrop-filter: blur(4px); }
  </style>
</head>
<body class="bg-gray-900 text-white">
  <div id="app" class="flex flex-col h-full">
    <!-- Header -->
    <header class="flex items-center justify-between px-4 py-3 glass">
      <div class="flex items-center gap-3">
        <button id="menuBtn" class="p-2 rounded-lg hover:bg-white/5">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div>
          <div class="text-sm font-semibold">Looker Studio</div>
          <div class="text-xs text-gray-300">Mobile-friendly view</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button id="shareBtn" class="p-2 rounded-lg hover:bg-white/5" title="Share">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M15 8a3 3 0 10-2.83-4H9a3 3 0 100 6h3.17A3 3 0 1015 8z"/></svg>
        </button>
        <button id="fullscreenBtn" class="p-2 rounded-lg hover:bg-white/5" title="Fullscreen">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 4a1 1 0 011-1h3a1 1 0 110 2H5v2a1 1 0 11-2 0V4zm14-1a1 1 0 00-1 1v3a1 1 0 102 0V5h-2V4zM4 16a1 1 0 011 1v-3a1 1 0 112 0v3H5a1 1 0 01-1-1zm12 0a1 1 0 00-1 1h-3a1 1 0 100 2h3a1 1 0 001-1v-3z" clip-rule="evenodd"/></svg>
        </button>
      </div>
    </header>

    <!-- View area -->
    <main class="flex-1 view-area bg-black/60 flex items-start justify-center p-2">
      <div id="frameWrap" class="w-full max-w-[1100px] h-full rounded-xl overflow-hidden shadow-2xl border border-white/5 bg-black">
        <!-- iframe wrapper to allow scaling -->
        <iframe id="reportFrame" class="report-frame" src="{{ report_url }}" allow="fullscreen"></iframe>
      </div>
    </main>

    <!-- Bottom controls -->
    <nav class="h-14 flex items-center justify-between px-4 glass">
      <div class="flex items-center gap-2">
        <button id="zoomOut" class="px-3 py-1 rounded-md bg-white/5">-</button>
        <div id="zoomLevel" class="min-w-[48px] text-center">100%</div>
        <button id="zoomIn" class="px-3 py-1 rounded-md bg-white/5">+</button>
      </div>
      <div class="flex gap-2">
        <a id="openInNew" target="_blank" rel="noopener" class="px-4 py-2 rounded-md bg-gradient-to-r from-sky-500 to-indigo-600 text-sm font-semibold">Open</a>
        <button id="fitWidth" class="px-4 py-2 rounded-md border border-white/10 text-sm">Fit</button>
      </div>
    </nav>

    <script>
      const reportUrl = `{{ report_url }}`;
      document.getElementById('openInNew').href = reportUrl;

      // Zoom controls (applies CSS scale to the iframe)
      const frameWrap = document.getElementById('frameWrap');
      const frame = document.getElementById('reportFrame');
      const zoomLevelEl = document.getElementById('zoomLevel');
      let zoom = 1;
      function applyZoom() {
        frame.style.transform = `scale(${zoom})`;
        frame.style.height = `calc(100% / ${zoom})`;
        zoomLevelEl.textContent = Math.round(zoom * 100) + '%';
      }
      document.getElementById('zoomIn').addEventListener('click', ()=>{ zoom = Math.min(2, +(zoom + 0.1).toFixed(2)); applyZoom(); });
      document.getElementById('zoomOut').addEventListener('click', ()=>{ zoom = Math.max(0.5, +(zoom - 0.1).toFixed(2)); applyZoom(); });
      document.getElementById('fitWidth').addEventListener('click', ()=>{ zoom = Math.min(1, window.innerWidth / frame.offsetWidth); applyZoom(); });
      applyZoom();

      // Fullscreen
      document.getElementById('fullscreenBtn').addEventListener('click', async ()=>{
        try{
          if (!document.fullscreenElement) await frameWrap.requestFullscreen(); else await document.exitFullscreen();
        }catch(e){console.warn(e)}
      });

      // Share
      document.getElementById('shareBtn').addEventListener('click', async ()=>{
        if(navigator.share){
          try{ await navigator.share({ title: 'Looker Report', text: 'Open this report', url: reportUrl }); }
          catch(err){ console.warn('share cancelled', err); }
        } else {
          // fallback: copy link
          await navigator.clipboard.writeText(reportUrl);
          alert('Link copied to clipboard');
        }
      });

      // Improve touch scrolling inside iframe area on mobile
      frame.addEventListener('load', ()=>{
        // nothing required here; many Looker Studio reports are responsive by design
      });

      // Optional: detect if iframe blocked by X-Frame-Options
      frame.addEventListener('error', ()=>{
        console.warn('Iframe error — report may not allow embedding.');
      });
    </script>
  </div>
</body>
</html>
'''

@app.route('/')
def index():
    # If user passes a ?report= URL param we allow quick preview of any URL (useful during testing)
    report_param = request.args.get('report')
    url = report_param if report_param else REPORT_URL
    return render_template_string(TEMPLATE, report_url=url)

if __name__ == '__main__':
    print(f"Serving mobile-friendly Looker Studio viewer on http://0.0.0.0:{PORT}/")
    app.run(host='0.0.0.0', port=PORT, debug=True)
