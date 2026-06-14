# 🚀 راهنمای گام‌به‌گام استفاده از Appwrite برای ربات

این راهنما خیلی ساده و مرحله‌به‌مرحله توضیح می‌دهد که چطور دیتابیس و فایل‌های ربات را در **Appwrite Cloud** (رایگان) بگذاریم و ربات را به آن متصل کنیم.

---

## 🎯 خلاصه: Appwrite چی کار می‌کند؟

- **Appwrite** = یک دیتابیس آنلاین و رایگان
- ربات شما در هر جا (PythonAnywhere، کامپیوتر، یا سرور) اجرا می‌شود
- ولی اطلاعات کاربران، درس‌ها، تکالیف و نمرات در **Appwrite Cloud** ذخیره می‌شوند
- دیگر نیازی به SQLite روی کامپیوتر نیست!

---

## ۱️⃣ ساخت اکانت Appwrite (رایگان)

1. برو به https://cloud.appwrite.io
2. روی **"Get Started"** یا **"Sign Up"** بزن
3. یک ایمیل و رمز بده و ثبت‌نام کن
4. وارد ایمیل شو و روی لینک تایید کلیک کن

✅ الان یک پنل Appwrite داری.

---

## ۲️⃣ ساخت پروژه (Project)

1. داخل پنل Appwrite، روی **"Create Project"** بزن
2. **Name** بده: `english-bot`
3. **Project ID** خودکار ساخته می‌شود (مثلاً `65abc123def`) — این را یادداشت کن
4. روی **Create** بزن

> ✅ پروژه ساخته شد.

---

## ۳️⃣ ساخت دیتابیس (Database)

1. از منوی سمت چپ، روی **Databases** بزن
2. روی **Create Database** بزن
3. **Database ID** را بنویس: `english_bot`
4. **Name** را بنویس: `English Bot Database`
5. روی **Create** بزن

> ✅ دیتابیس ساخته شد. ID آن را یادداشت کن (`english_bot`).

---

## ۴️⃣ ساخت جداول (Collections)

حالا باید ۷ تا Collection (جدول) بسازیم. یکی‌یکی:

### ۴-۱: Collection اول — users

1. در صفحه Database، روی **Create Collection** بزن
2. **Collection ID** = `users`
3. **Name** = `Users`
4. روی **Create** بزن
5. حالا باید **Attributes** (ستون‌ها) را بسازی. روی تب **Attributes** بزن و این‌ها را اضافه کن:

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `telegram_id` | Integer | ✅ Yes | — |
| `full_name` | String | No | 255 |
| `username` | String | No | 100 |
| `level` | String | No | 10 |
| `current_lesson` | Integer | No | Default: 0 |
| `course_week` | Integer | No | Default: 0 |
| `status` | String | No | Default: `placement` |
| `created_at` | String | No | 50 |
| `last_lesson_at` | String | No | 50 |

روی **Create Attribute** برای هر کدام بزن و پر کن.

### ۴-۲: Collection دوم — lessons

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `level_code` | String | ✅ Yes | 10 |
| `lesson_number` | Integer | ✅ Yes | — |
| `title` | String | No | 255 |
| `content` | String | No | 5000 |
| `video_file_id` | String | No | 500 |
| `homework_type` | String | No | 20 |
| `homework_desc` | String | No | 2000 |

### ۴-۳: Collection سوم — homework

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `user_id` | Integer | ✅ Yes | — |
| `lesson_id` | String | ✅ Yes | 50 |
| `type` | String | No | 20 |
| `file_id` | String | No | 500 |
| `file_type` | String | No | 20 |
| `text_content` | String | No | 5000 |
| `submitted_at` | String | No | 50 |
| `status` | String | No | Default: `pending` |
| `score` | Integer | No | Default: 0 |
| `teacher_comment` | String | No | 2000 |

### ۴-۴: Collection چهارم — placement_questions

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `level_code` | String | No | 10 |
| `question_text` | String | ✅ Yes | 2000 |
| `options` | String | No | 4000 |
| `correct_answer` | Integer | No | Default: 0 |

### ۴-۵: Collection پنجم — placement_answers

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `user_id` | Integer | ✅ Yes | — |
| `question_id` | String | ✅ Yes | 50 |
| `answer` | Integer | No | — |
| `is_correct` | Boolean | No | — |

### ۴-۶: Collection ششم — exams

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `level_code` | String | ✅ Yes | 10 |
| `exam_type` | String | ✅ Yes | 50 |
| `title` | String | No | 255 |
| `questions_json` | String | No | 10000 |
| `passing_score` | Integer | No | Default: 70 |

### ۴-۷: Collection هفتم — exam_results

| Attribute Key | Type | Required | Size/Default |
|-------------|------|----------|-------------|
| `user_id` | Integer | ✅ Yes | — |
| `exam_id` | String | ✅ Yes | 50 |
| `score` | Integer | No | — |
| `passed` | Boolean | No | — |
| `taken_at` | String | No | 50 |

> ✅ حالا همه ۷ جدول را ساختی!

---

## ۵️⃣ ساخت API Key (کلید دسترسی)

1. از منوی سمت چپ Appwrite، روی **API Keys** بزن
2. روی **Create API Key** بزن
3. **Name** = `Bot API Key`
4. **Expiration** = `Never` (یا تاریخ طولانی)
5. پایین صفحه، **Scopes** را باز کن و این موارد را تیک بزن:
   - ✅ `databases.read`
   - ✅ `databases.write`
   - ✅ `documents.read`
   - ✅ `documents.write`
   - ✅ `collections.read`
   - ✅ `collections.write`
6. روی **Create** بزن

7. یک کد طولانی بهت می‌ده. **کپی کن و در جایی امن نگه دار!**
   - مثلاً: `standard_123456789abcdef...`
   - این همان `APPWRITE_API_KEY` است.

> ⚠️ این کد را کسی نبیند! مثل رمز عبور است.

---

## ۶️⃣ تنظیم فایل `.env`

فایل `.env` در پوشه ربات را باز کن. این خطوط را مطابق Appwrite خود پر کن:

```env
BOT_TOKEN=8882257549:AAEHfFlSHQxkHWon_EdBrn4c9hTzNybOy60
ADMIN_IDS=971177625

APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id_here
APPWRITE_API_KEY=your_api_key_here
APPWRITE_DATABASE_ID=english_bot
```

| متغیر | از کجا بیاوری | مثال |
|-------|--------------|------|
| `APPWRITE_PROJECT_ID` | از صفحه Overview پروژه Appwrite | `65abc123def` |
| `APPWRITE_API_KEY` | از بخش API Keys | `standard_123...` |
| `APPWRITE_DATABASE_ID` | همان `english_bot` که ساختی | `english_bot` |

> 💡 توکن و آیدی ادمین را قبلاً داشتی.

---

## ۷️⃣ ورود داده‌های اولیه (Seed)

باید سوالات تعیین سطح، درس‌ها و امتحان اولیه را در Appwrite بگذاری.

### روش A: اسکریپت خودکار (ساده‌تر)

1. فایل `seed.py` را در کنار `main.py` بگذار
2. از ترمینال (Bash/Command Prompt) اجرا کن:
   ```bash
   pip install appwrite python-dotenv
   python seed.py
   ```
3. اسکریپت خودکار Collectionها را می‌سازد و داده‌های نمونه را وارد می‌کند.

### روش B: دستی در کنسول Appwrite

1. در Appwrite، برو به **Databases** → `english_bot`
2. روی Collection `placement_questions` بزن
3. تب **Documents** را باز کن
4. روی **Create Document** بزن و یکی‌یکی سوالات را وارد کن

---

## ۸️⃣ اجرای ربات

حالا که Appwrite آماده است، ربات را در هر جا که دوست داری اجرا کن:

### PythonAnywhere (راحت‌ترین)
1. فایل‌ها را در PythonAnywhere آپلود کن
2. فایل `.env` را درست کن (مطابق بالا)
3. در Console بزن:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

### کامپیوتر خودت
1. فایل ZIP را Extract کن
2. فایل `.env` را درست کن
3. ترمینال را باز کن (Command Prompt یا Terminal)
4. برو داخل پوشه ربات:
   ```bash
   cd telegram-appwrite-bot
   ```
5. نصب کن:
   ```bash
   pip install -r requirements.txt
   ```
6. اجرا کن:
   ```bash
   python main.py
   ```

### Render.com (۲۴ ساعته رایگان)
مثل راهنمای قبلی، فقط فایل `requirements.txt` را آپلود کن و `.env` را در Environment Variables وارد کن.

---

## ۹️⃣ بررسی اتصال

اگر ربات اجرا شد و در تلگرام `/start` زدی و پاسخ داد، یعنی همه چی درست است!

اگر خطا دیدی، احتمالاً یکی از این‌هاست:
- Project ID اشتباه است
- API Key اشتباه است یا دسترسی ندارد
- Database ID اشتباه است (`english_bot` نباشد)
- Collection هنوز ساخته نشده

---

## 🔟 مدیریت بعدی (اضافه کردن درس/سوال جدید)

برای اضافه کردن درس یا سوال جدید، کافی است در کنسول Appwrite:
1. برو به Databases → english_bot
2. روی Collection مربوطه (مثلاً `lessons`) بزن
3. تب **Documents** را باز کن
4. روی **Create Document** بزن و اطلاعات را پر کن

نیازی به ری‌استارت ربات نیست! Appwrite همیشه به‌روز است.

---

## ✅ مزایای Appwrite نسبت به SQLite

| ویژگی | SQLite | Appwrite |
|-------|--------|----------|
| محل دیتابیس | روی یک کامپیوتر | در اینترنت (Cloud) |
| اگر کامپیوتر خاموش شود | داده‌ها از دست می‌روند | داده‌ها امن هستند |
| کاربران همزمان | مشکل دارد | راحت |
| بک‌آپ | دستی | خودکار |
| دیدن داده‌ها | باید نرم‌افزار نصب کنی | از هر جا با مرورگر |
| هزینه | رایگان | رایگان (تا حدی) |

---

اگر در هر مرحله سوال یا مشکل داشتی، بپرس! 🚀
