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

## تست

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

تست‌ها بدون تماس با تلگرام و با توکن آزمایشی اجرا می‌شوند.
