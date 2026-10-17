# Telegram currency charts

ربات تلگرام برای نمایش نمودار قیمت دلار و یورو در سه ماه اخیر.
بعد از `/start`، کاربر یکی از دو دکمهٔ دلار یا یورو را انتخاب می‌کند و تصویر نمودار را دریافت می‌کند.

## اجرا

به Python 3.11 یا جدیدتر نیاز دارید.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item token_api.example.py token_api.py
```

توکن دریافتی از BotFather را در `token_api.py` قرار دهید و سپس اجرا کنید:

```powershell
python main.py
```

فایل `token_api.py` در گیت نادیده گرفته می‌شود؛ توکن واقعی را منتشر نکنید.

## داده‌ها

تاریخچهٔ روزانه از [Iran Market](https://github.com/iran-market/iran-market.github.io) در زمان درخواست دریافت می‌شود.
قیمت‌ها به تومان هستند و مقدار هر روز میانگین سقف و کف همان روز است.
بازهٔ نمودار سه ماه تقویمی میلادی تا تاریخ روز با منطقهٔ زمانی تهران است؛ تاریخ‌ها در نمودار به جلالی نمایش داده می‌شوند.

## استقرار روی Vercel

ورودی وب `main:app` در `pyproject.toml` تعریف شده است. Vercel پیام‌ها را از مسیر
`/webhook` دریافت می‌کند؛ `python main.py` فقط برای اجرای محلی با polling است.

1. در تنظیمات Environment Variables پروژهٔ Vercel این مقادیر را برای محیط Production اضافه کنید:
   - `TELEGRAM_BOT_TOKEN`: توکن BotFather.
   - `TELEGRAM_WEBHOOK_SECRET`: یک رشتهٔ تصادفی محرمانه، شامل حروف، عدد، خط تیره یا زیرخط.
2. برای ساخت secret می‌توانید `python -c "import secrets; print(secrets.token_urlsafe(32))"` را اجرا کنید.
3. تغییرات را پوش کنید و استقرار جدید انجام دهید. Build Command و Output Directory را روی پیش‌فرض نگه دارید.
4. آدرس اصلی استقرار باید از اینترنت قابل دسترسی باشد و صفحهٔ ورود Vercel نداشته باشد.
   در صورت فعال‌بودن Deployment Protection، دسترسی webhook عمومی تلگرام را فراهم کنید.
5. اجرای محلی ربات با polling را متوقف کنید. دو متغیر بالا را با همان مقادیر در ترمینال محلی قرار دهید و اجرا کنید:

```powershell
python -m pip install -r requirements.txt
$env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
$env:TELEGRAM_WEBHOOK_SECRET = "SAME_SECRET_AS_VERCEL"
python setup_webhook.py https://YOUR-PROJECT.vercel.app
```

توکن و secret را فقط در تنظیمات محرمانهٔ سرویس یا ترمینال خود وارد کنید؛ آن‌ها را کامیت نکنید.
ثبت webhook فقط یک‌بار و پس از تغییر آدرس یا secret لازم است؛ هنگام build یا import انجام نمی‌شود.

برای بررسی، آدرس `/` باید `{"status":"ok"}` برگرداند؛ سپس `/start` و هر دو دکمه را در تلگرام امتحان کنید.
تست‌های محلی، build واقعی Vercel و ارسال واقعی تلگرام را شبیه‌سازی نمی‌کنند.

برای بازگشت به نسخهٔ قبلی، در Vercel استقرار قبلیِ سازگار با webhook را Promote کنید و سلامت `/` را بررسی کنید.
برای بازگشت به polling، ابتدا webhook را با `bot.delete_webhook()` حذف کنید و سپس `python main.py` را اجرا کنید.

## تست

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

تست‌ها بدون تماس با تلگرام و با توکن آزمایشی اجرا می‌شوند.
