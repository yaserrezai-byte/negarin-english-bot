# 🚀 راهنمای فوق ساده: ربات در Appwrite Function (Webhook)

این راهنما برای اجرای ربات در **Appwrite Function** با روش **Webhook** است.

**تفاوت Webhook با Polling:**
- **Polling**: ربات همیشه در حال چک کردن تلگرام است → نیاز به سرور همیشه روشن
- **Webhook**: تلگرام خودش وقتی پیامی می‌رسد، یک درخواست به Appwrite می‌فرستد → Appwrite Function فقط چند ثانیه اجرا می‌شود و **هیچ خطای 408 نمی‌دهد!**

---

## ✅ مراحل کلی (فقط ۵ قدم)

1. **کد را در Appwrite Function آپلود کنید**
2. **دیتابیس و داده‌ها را در Appwrite بسازید**
3. **URL Function را بگیرید و Webhook را تنظیم کنید**
4. **ربات را در تلگرام تست کنید**

---

## ۱️⃣ ساخت Appwrite Function

1. برو به https://cloud.appwrite.io
2. پروژه `english learning` را انتخاب کن
3. از منوی سمت چپ، روی **Functions** بزن
4. روی **Create Function** (یا +) بزن
5. تنظیمات:
   - **Name**: `telegram-bot`
   - **Runtime**: `Python 3.10` (یا Python 3.9)
   - **Entrypoint**: `main` (تابع اصلی)
   - **Execute Access**: `Any` ⬅️ خیلی مهم!
6. روی **Create** بزن

### آپلود کد (روش Manual - ZIP)

1. فایل `telegram-appwrite-webhook.zip` را از همین پنل دانلود کن
2. در Appwrite Function → تب **Build** یا **Deploy**
3. روی **Upload** بزن و ZIP را انتخاب کن
4. مطمئن شو **Root Directory** روی `src` تنظیم شده (یا اگر ZIP را Extract کرده‌ای، روی جایی که `main.py` هست)
5. روی **Deploy** بزن

### یا از GitHub (اگر پوشه src را در گیت‌هاب گذاشته‌ای)

1. در Appwrite Function → Settings → Git
2. GitHub را وصل کن
3. مخزن `negarin-english-bot` را انتخاب کن
4. **Root Directory** را بده: `telegram-appwrite-webhook/src` (یا جایی که main.py هست)
5. روی **Deploy** بزن

---

## ۲️⃣ تنظیم متغیرهای محیطی (Environment Variables)

در Appwrite Function → Settings → Variables، این موارد را اضافه کن:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | توکن ربات (از BotFather) |
| `ADMIN_IDS` | آیدی عددی شما (مثلاً 971177625) |
| `APPWRITE_ENDPOINT` | `https://cloud.appwrite.io/v1` |
| `APPWRITE_PROJECT_ID` | Project ID شما (مثلاً fra-6a279bb700127e8c7ae8) |
| `APPWRITE_API_KEY` | API Key جدید (مثلاً standard_...) |
| `APPWRITE_DATABASE_ID` | Database ID شما (مثلاً 6a27a04200b32bef5b6) |

> ⚠️ توکن و API Key قدیمی را عوض کن! چون در گیت‌هاب لو رفتند.

---

## ۳️⃣ ساخت دیتابیس و داده‌ها (Seed)

این کار را در کامپیوتر خودت انجام بده (یا هر جا که Python داری):

1. فایل `.env` را درست کن (مقادیر جدید)
2. در Command Prompt یا Terminal:
```bash
pip install appwrite python-dotenv
python seed.py
```

این اسکریپت:
- ۷ تا Collection (جدول) می‌سازد
- سوالات تعیین سطح را اضافه می‌کند
- ۶ درس نمونه A1 اضافه می‌کند
- ۱ امتحان نمونه A1 اضافه می‌کند

---

## ۴️⃣ گرفتن URL Function و تنظیم Webhook

### ۴-۱: URL Function را بگیر

1. در Appwrite Console → Functions → `telegram-bot`
2. در صفحه Overview، بخش **Domains** یا **URL** را ببین
3. URL شبیه این است:
   ```
   https://65abc...appwrite.host/
   ```
   یا
   ```
   https://cloud.appwrite.io/v1/functions/telegram-bot/... (نسخه‌های جدیدتر)
   ```

> **اگر URL ندیدید** (Appwrite Cloud رایگان ممکن است Domain ندهد)، باید از **Proxy** یا **Appwrite Site** استفاده کنید. در این صورت بگو تا راهنمایی کنم.

### ۴-۲: تنظیم Webhook

روش ۱: در کامپیوتر خودت

1. فایل `.env` را باز کن و این خط را اضافه کن:
   ```env
   FUNCTION_URL=https://your-appwrite-function-url.com
   ```
2. این دستور را اجرا کن:
   ```bash
   pip install requests python-dotenv
   python set_webhook.py
   ```

روش ۲: مستقیم در مرورگر

این آدرس را در مرورگر باز کن:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=<YOUR_FUNCTION_URL>&drop_pending_updates=true
```

> جای `<YOUR_BOT_TOKEN>` توکن ربات و جای `<YOUR_FUNCTION_URL>` URL Appwrite Function را بگذار.

اگر پاسخ این شکل بود، یعنی موفق:
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

---

## ۵️⃣ تست ربات! 🎉

1. در تلگرام برو به `@NegarinEnglishAcademyBot`
2. روی **Start** بزن
3. اگر ربات خوش‌آمد گویی کرد و دکمه **«🎯 شروع تعیین سطح»** آمد → **تبریک!** 🎉

---

## ❌ اگر خطا داد

| خطا | راه‌حل |
|-----|--------|
| **Error 408** | دیگر نباید بدهد! چون Webhook است. اگر داد، یعنی هنوز Polling است. |
| **403 Forbidden** | Execute Access در Appwrite Function را بذار `Any` |
| **404 Not Found** | URL Function اشتباه است |
| **Database not found** | `seed.py` را اجرا نکرده‌ای یا Database ID اشتباه است |
| **Webhook not set** | URL را در تلگرام setWebhook نکرده‌ای |
| **Appwrite Function URL ندارد** | Appwrite Cloud رایگان ممکن است Domain ندهد. بگو تا راه‌حل بدهم. |

---

## ⚠️ نکات مهم

1. **فایل `.env` را در گیت‌هاب نگذار!**
2. **توکن و API Key قدیمی را عوض کن** (چون در گیت‌هاب لو رفت)
3. **Appwrite Function فقط یکبار اجرا می‌شود** (Serverless) → پس هیچ پنجره‌ای برای نگه داشتن نیست!
4. **داده‌ها در Appwrite Database** ذخیره می‌شوند → همیشه امن هستند

---

## ❓ سوالات متداول

**س: آیا ربات همیشه روشن است؟**
ج: بله! ولی نه مثل سرور. هر بار که پیام می‌آید، Appwrite Function فعال می‌شود. اگر کسی پیام ندهد، هیچ هزینه‌ای ندارد.

**س: آیا می‌توانم چند پیام همزمان بدهم؟**
ج: بله! Appwrite Function برای هر پیام یکبار جداگانه اجرا می‌شود.

**س: اگر Appwrite Function Domain نداشت چه کنم؟**
ج: بگو تا راهنمایی کنم. یک راه: Appwrite Site بسازی و درخواست‌ها را Proxy کنی.

---

**موفق باشید!** 🚀
