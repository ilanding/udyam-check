"""Udyam Checker web app — mobile number/email daalo, registered hai ya nahi jaano."""
from flask import Flask, request, render_template_string

from checker import check

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Udyam Check</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, 'Segoe UI', Arial, sans-serif; background: #fff; color: #111;
         min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
  .box { width: 100%; max-width: 420px; border: 2px solid #111; border-radius: 12px; padding: 28px 24px; text-align: center; }
  h1 { font-size: 22px; margin-bottom: 20px; }
  input { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #111; border-radius: 8px; margin-bottom: 12px; text-align: center; }
  button { width: 100%; padding: 14px; font-size: 16px; font-weight: bold; background: #111; color: #fff;
           border: none; border-radius: 8px; cursor: pointer; }
  button:disabled { opacity: .5; }
  .result { margin-top: 18px; padding: 16px; border-radius: 8px; font-size: 18px; font-weight: bold;
            letter-spacing: 1px; display: none; }
  .result.ok { display: block; background: #111; color: #fff; }
  .result.no { display: block; background: #fff; color: #111; border: 2px solid #111; }
  .result.warn { display: block; background: #f5f5f5; color: #111; border: 1px dashed #111;
                 font-size: 14px; font-weight: normal; letter-spacing: 0; }
</style>
</head>
<body>
<div class="box">
  <h1>Udyam Check</h1>
  <form id="f">
    <input id="ident" name="ident" placeholder="Enter mobile number" inputmode="numeric" autocomplete="off" required>
    <button id="btn" type="submit">Check</button>
  </form>
  <div id="res" class="result"></div>
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
    if (j.status === 'REGISTERED') { res.className = 'result ok'; res.textContent = 'REGISTERED'; }
    else if (j.status === 'NOT_REGISTERED') { res.className = 'result no'; res.textContent = 'NOT REGISTERED'; }
    else { res.className = 'result warn'; res.textContent = j.message || 'Something went wrong. Try again.'; }
  } catch (err) { res.className = 'result warn'; res.textContent = 'Something went wrong. Try again.'; }
  btn.disabled = false; btn.textContent = 'Check';
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
