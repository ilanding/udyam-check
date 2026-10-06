"""Udyam Checker web app — mobile number/email daalo, registered hai ya nahi jaano."""
from flask import Flask, request, render_template_string

from checker import check

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Udyam Check</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, 'Segoe UI', Arial, sans-serif; background: #fff; color: #111;
         min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
  .box { width: 100%; max-width: 420px; border: 2px solid #111; border-radius: 12px; padding: 28px 24px; }
  h1 { font-size: 22px; margin-bottom: 6px; }
  p.sub { font-size: 13px; color: #555; margin-bottom: 20px; }
  input { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #111; border-radius: 8px; margin-bottom: 12px; }
  button { width: 100%; padding: 14px; font-size: 16px; font-weight: bold; background: #111; color: #fff;
           border: none; border-radius: 8px; cursor: pointer; }
  button:disabled { opacity: .5; }
  .result { margin-top: 18px; padding: 14px; border-radius: 8px; font-size: 15px; display: none; }
  .result.ok { display: block; background: #111; color: #fff; }
  .result.no { display: block; background: #fff; color: #111; border: 2px solid #111; }
  .result.warn { display: block; background: #f5f5f5; color: #111; border: 1px dashed #111; }
  .note { margin-top: 16px; font-size: 11px; color: #777; }
</style>
</head>
<body>
<div class="box">
  <h1>Udyam Check</h1>
  <p class="sub">Mobile number ya email daalo — pata chalega Udyam registered hai ya nahi.</p>
  <form id="f">
    <input id="ident" name="ident" placeholder="9876543210 ya email" autocomplete="off" required>
    <button id="btn" type="submit">Check karo</button>
  </form>
  <div id="res" class="result"></div>
  <p class="note">Note: agar number registered hai to uspe asli OTP SMS jayega. Sirf customer ke apne number pe, uski permission se check karo.</p>
</div>
<script>
document.getElementById('f').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('btn'), res = document.getElementById('res');
  btn.disabled = true; btn.textContent = 'Checking...';
  res.className = 'result'; res.textContent = '';
  try {
    const r = await fetch('/api/check', { method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ ident: document.getElementById('ident').value }) });
    const j = await r.json();
    if (j.status === 'REGISTERED') { res.className = 'result ok'; res.textContent = '✅ REGISTERED hai — OTP bhej diya gaya hai is number pe.'; }
    else if (j.status === 'NOT_REGISTERED') { res.className = 'result no'; res.textContent = '❌ NOT REGISTERED — is pe koi Udyam nahi hai.'; }
    else { res.className = 'result warn'; res.textContent = '❓ ' + j.message; }
  } catch (err) { res.className = 'result warn'; res.textContent = '❓ Network error — dobara try karo.'; }
  btn.disabled = false; btn.textContent = 'Check karo';
});
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/api/check")
def api_check():
    ident = (request.json or {}).get("ident", "")
    try:
        status, message = check(ident)
    except Exception as e:  # noqa: BLE001 - portal/network failure
        return {"status": "ERROR", "message": f"Portal se baat nahi ho payi: {e}"}, 502
    code = 200 if status in ("REGISTERED", "NOT_REGISTERED") else 400
    return {"status": status, "message": message}, code


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
