"""
سرور Flask برای ترکینگ باز شدن ایمیل و کلیک روی دکمه‌ها
"""

from flask import Flask, send_file, redirect, request, jsonify
import json
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# فایل ذخیره داده‌های ترکینگ
TRACKING_FILE = "tracking_data.json"


def load_tracking_data():
    """لود کردن داده‌های ترکینگ"""
    if Path(TRACKING_FILE).exists():
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'emails_sent': [],
        'opens': [],
        'clicks': []
    }


def save_tracking_data(data):
    """ذخیره داده‌های ترکینگ"""
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_transparent_pixel():
    """ساخت یک پیکسل شفاف 1x1"""
    img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


@app.route('/')
def home():
    """صفحه اصلی"""
    return """
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>سیستم ترکینگ ایمیل</title>
        <style>
            body {
                font-family: Tahoma, Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                text-align: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }
            h1 { color: #667eea; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
            }
            .stat-number {
                font-size: 36px;
                font-weight: bold;
            }
            .stat-label {
                font-size: 14px;
                margin-top: 5px;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 سیستم ترکینگ ایمیل مارکتینگ</h1>
            <p>سرور به درستی در حال اجرا است!</p>
            <div style="margin-top: 20px;">
                <a href="/stats" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 30px; display: inline-block;">
                    📊 مشاهده آمار
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@app.route('/track/open/<tracking_id>.png')
def track_open(tracking_id):
    """
    ترکینگ باز شدن ایمیل
    این endpoint یک پیکسل شفاف برمی‌گرداند و باز شدن ایمیل را ثبت می‌کند
    """
    # لود داده‌ها
    data = load_tracking_data()
    
    # بررسی تکراری نبودن
    already_opened = any(
        item['tracking_id'] == tracking_id 
        for item in data.get('opens', [])
    )
    
    if not already_opened:
        # ثبت باز شدن
        data.setdefault('opens', []).append({
            'tracking_id': tracking_id,
            'opened_at': datetime.now().isoformat(),
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        save_tracking_data(data)
        print(f"✅ ایمیل باز شد - Tracking ID: {tracking_id}")
    
    # ارسال پیکسل شفاف
    return send_file(
        create_transparent_pixel(),
        mimetype='image/png',
        as_attachment=False
    )


@app.route('/track/click/<tracking_id>/<action_name>')
def track_click(tracking_id, action_name):
    """
    ترکینگ کلیک روی دکمه‌ها
    """
    # لود داده‌ها
    data = load_tracking_data()
    
    # ثبت کلیک
    data.setdefault('clicks', []).append({
        'tracking_id': tracking_id,
        'action_name': action_name,
        'clicked_at': datetime.now().isoformat(),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    save_tracking_data(data)
    
    print(f"🖱️  کلیک ثبت شد - Tracking ID: {tracking_id}, Action: {action_name}")
    
    # ریدایرکت به URL اصلی
    redirect_url = request.args.get('redirect', 'https://google.com')
    return redirect(redirect_url)


@app.route('/unsubscribe/<tracking_id>')
def unsubscribe(tracking_id):
    """صفحه لغو اشتراک"""
    data = load_tracking_data()
    
    # ثبت لغو اشتراک
    data.setdefault('unsubscribes', []).append({
        'tracking_id': tracking_id,
        'unsubscribed_at': datetime.now().isoformat()
    })
    save_tracking_data(data)
    
    return """
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>لغو اشتراک</title>
        <style>
            body {
                font-family: Tahoma, Arial, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 40px;
                background: #f4f4f4;
                text-align: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            h1 { color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ اشتراک شما لغو شد</h1>
            <p>شما دیگر ایمیل‌های تبلیغاتی ما را دریافت نخواهید کرد.</p>
            <p>متشکریم از همراهی شما! 🙏</p>
        </div>
    </body>
    </html>
    """


@app.route('/stats')
def stats_page():
    """صفحه نمایش آمار"""
    data = load_tracking_data()
    
    total_sent = len(data.get('emails_sent', []))
    total_opens = len(data.get('opens', []))
    total_clicks = len(data.get('clicks', []))
    total_unsubscribes = len(data.get('unsubscribes', []))
    
    # محاسبه نرخ‌ها
    open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
    click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
    
    # تفکیک کلیک‌ها
    click_breakdown = {}
    for click in data.get('clicks', []):
        action = click.get('action_name', 'unknown')
        click_breakdown[action] = click_breakdown.get(action, 0) + 1
    
    # ساخت HTML آمار
    click_rows = ""
    for action, count in click_breakdown.items():
        action_labels = {
            'products': '🛍️ مشاهده محصولات',
            'catalog': '📥 دانلود کاتالوگ',
            'whatsapp': '💬 واتساپ'
        }
        label = action_labels.get(action, action)
        click_rows += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{label}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">{count}</td>
        </tr>
        """
    
    return f"""
    <html dir="rtl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>آمار کمپین</title>
        <style>
            body {{
                font-family: Tahoma, Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{
                color: #667eea;
                text-align: center;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }}
            .stat-number {{
                font-size: 48px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .stat-label {{
                font-size: 16px;
                opacity: 0.9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th {{
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: right;
            }}
            .refresh-btn {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border-radius: 30px;
                text-decoration: none;
                margin: 20px auto;
                display: block;
                width: fit-content;
            }}
            .refresh-btn:hover {{
                background: #764ba2;
            }}
        </style>
        <script>
            // رفرش خودکار هر 30 ثانیه
            setTimeout(function(){{ location.reload(); }}, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>📊 آمار کمپین ایمیل مارکتینگ</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_sent}</div>
                    <div class="stat-label">📧 ایمیل ارسالی</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{total_opens}</div>
                    <div class="stat-label">👁️ باز شده ({open_rate:.1f}%)</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{total_clicks}</div>
                    <div class="stat-label">🖱️ کلیک ({click_rate:.1f}%)</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number">{total_unsubscribes}</div>
                    <div class="stat-label">❌ لغو اشتراک</div>
                </div>
            </div>
            
            <h2 style="color: #667eea; margin-top: 40px;">📈 تفکیک کلیک‌ها</h2>
            <table>
                <thead>
                    <tr>
                        <th>دکمه</th>
                        <th>تعداد کلیک</th>
                    </tr>
                </thead>
                <tbody>
                    {click_rows if click_rows else '<tr><td colspan="2" style="padding: 20px; text-align: center; color: #999;">هنوز کلیکی ثبت نشده است</td></tr>'}
                </tbody>
            </table>
            
            <a href="/stats" class="refresh-btn">🔄 بروزرسانی</a>
            
            <p style="text-align: center; color: #999; margin-top: 20px; font-size: 14px;">
                صفحه به صورت خودکار هر 30 ثانیه بروزرسانی می‌شود
            </p>
        </div>
    </body>
    </html>
    """


@app.route('/api/stats')
def api_stats():
    """API برای دریافت آمار به صورت JSON"""
    data = load_tracking_data()
    
    total_sent = len(data.get('emails_sent', []))
    total_opens = len(data.get('opens', []))
    total_clicks = len(data.get('clicks', []))
    
    open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
    click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
    
    click_breakdown = {}
    for click in data.get('clicks', []):
        action = click.get('action_name', 'unknown')
        click_breakdown[action] = click_breakdown.get(action, 0) + 1
    
    return jsonify({
        'total_sent': total_sent,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'open_rate': round(open_rate, 2),
        'click_rate': round(click_rate, 2),
        'click_breakdown': click_breakdown
    })


if __name__ == '__main__':
    import os
    
    # تشخیص محیط (local یا production)
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if not is_production:
        print("🚀 سرور ترکینگ در حال اجرا...")
        print("📍 آدرس: http://localhost:5000")
        print("📊 آمار: http://localhost:5000/stats")
        print("\nبرای توقف سرور Ctrl+C را بزنید\n")
    
    # در production از debug=False استفاده می‌کنیم
    app.run(host='0.0.0.0', port=5000, debug=not is_production)

