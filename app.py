from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# واجهة الموقع وشريط التحميل
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>أداة التخطي السريعة</title>
    <style>
        * { box-sizing: border-box; font-family: system-ui, sans-serif; }
        body { background-color: #0d1117; color: #c9d1d9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 30px; width: 100%; max-width: 450px; text-align: center; }
        h2 { color: #58a6ff; margin-top: 0; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: #fff; outline: none; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #238636; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background: #2ea043; }
        button:disabled { background: #21262d; color: #8b949e; cursor: not-allowed; }
        
        .progress-wrapper { display: none; margin-top: 20px; }
        .progress-bar-bg { background: #21262d; border-radius: 10px; height: 10px; width: 100%; overflow: hidden; }
        .progress-bar-fill { background: linear-gradient(90deg, #238636, #58a6ff); height: 100%; width: 0%; transition: width 0.3s; }
        .status-text { font-size: 13px; color: #8b949e; margin-top: 8px; }
        
        .result-box { display: none; margin-top: 20px; background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 15px; word-break: break-all; }
        .copy-btn { margin-top: 10px; background: #1f6beb; }
        .copy-btn:hover { background: #388bfd; }
    </style>
</head>
<body>

<div class="card">
    <h2>تخطي الروابط</h2>
    <input type="text" id="linkInput" placeholder="ضع الرابط هنا...">
    <button id="submitBtn" onclick="startBypass()">تخطي الآن</button>

    <div class="progress-wrapper" id="progressWrapper">
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="progressBar"></div>
        </div>
        <div class="status-text" id="statusText">جاري الاتصال...</div>
    </div>

    <div class="result-box" id="resultBox">
        <div id="resultUrl" style="color: #3fb950; font-size: 14px;"></div>
        <button class="copy-btn" id="copyBtn" onclick="copyResult()">نسخ الرابط</button>
    </div>
</div>

<script>
let finalResultUrl = "";

async function startBypass() {
    const input = document.getElementById('linkInput').value.trim();
    const submitBtn = document.getElementById('submitBtn');
    const progressWrapper = document.getElementById('progressWrapper');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const resultBox = document.getElementById('resultBox');

    if (!input) return alert('يرجى وضع رابط أولاً!');

    submitBtn.disabled = true;
    resultBox.style.display = 'none';
    progressWrapper.style.display = 'block';
    progressBar.style.width = '15%';
    statusText.innerText = 'جاري البحث وتجربة الخوادم...';

    let progress = 15;
    const interval = setInterval(() => {
        if (progress < 85) {
            progress += 10;
            progressBar.style.width = progress + '%';
        }
    }, 300);

    try {
        const response = await fetch(`/api/bypass?url=${encodeURIComponent(input)}`);
        const data = await response.json();

        clearInterval(interval);

        if (data.success) {
            progressBar.style.width = '100%';
            statusText.innerText = 'تم التخطي بنجاح! 🎉';
            finalResultUrl = data.result;

            setTimeout(() => {
                progressWrapper.style.display = 'none';
                resultBox.style.display = 'block';
                document.getElementById('resultUrl').innerText = finalResultUrl;
                submitBtn.disabled = false;
            }, 400);
        } else {
            progressWrapper.style.display = 'none';
            alert(data.error || 'فشل التخطي عبر جميع الخوادم المتاحة');
            submitBtn.disabled = false;
        }
    } catch (e) {
        clearInterval(interval);
        progressWrapper.style.display = 'none';
        alert('حدث خطأ بالاتصال');
        submitBtn.disabled = false;
    }
}

function copyResult() {
    navigator.clipboard.writeText(finalResultUrl).then(() => {
        const copyBtn = document.getElementById('copyBtn');
        copyBtn.innerText = 'تم النسخ! ✓';
        setTimeout(() => copyBtn.innerText = 'نسخ الرابط', 2000);
    });
}
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/bypass', methods=['GET'])
def bypass():
    url = request.args.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'الرابط مفقود'}), 400

    # مصفوفة الخوادم لتجربتها بالترتيب عند الفشل
    apis = [
        f"https://api.bypass.city/bypass?url={requests.utils.quote(url)}",
        f"https://api.bypass.vip/bypass?url={requests.utils.quote(url)}",
        f"https://adbypass.org/api/bypass?url={requests.utils.quote(url)}"
    ]

    for endpoint in apis:
        try:
            res = requests.get(endpoint, timeout=6)
            if res.status_code == 200:
                data = res.json()
                result = data.get('destination') or data.get('result') or data.get('url')
                if result:
                    return jsonify({'success': True, 'result': result}), 200
        except Exception:
            continue  # التنقل تلقائياً للـ API التالي عند الخطأ

    return jsonify({'success': False, 'error': 'تعذر التخطي عبر الخوادم، حاول مجدداً'}), 500

if __name__ == '__main__':
    app.run(debug=True)
