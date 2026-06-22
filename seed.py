#!/usr/bin/env python3
"""
اسکریپت ورود داده‌های اولیه به Appwrite
اجرا: python seed.py
"""
import os
import json
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

load_dotenv()

client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1"))
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

db = Databases(client)
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "english_bot")


def ensure_collections():
    try:
        db.get(DATABASE_ID)
        print(f"✅ Database '{DATABASE_ID}' موجود است.")
    except Exception:
        print(f"🛠 ساخت دیتابیس '{DATABASE_ID}'...")
        db.create(DATABASE_ID, DATABASE_ID)

    schemas = {
        "users": {
            "attributes": [
                ("telegram_id", "integer", True, None),
                ("full_name", "string", False, 255),
                ("username", "string", False, 100),
                ("level", "string", False, 10),
                ("current_lesson", "integer", False, None),
                ("course_week", "integer", False, None),
                ("status", "string", False, 20),
                ("created_at", "string", False, 50),
                ("last_lesson_at", "string", False, 50),
                ("temp_state", "string", False, 5000),
            ]
        },
        "lessons": {
            "attributes": [
                ("level_code", "string", True, 10),
                ("lesson_number", "integer", True, None),
                ("title", "string", False, 255),
                ("content", "string", False, 5000),
                ("video_file_id", "string", False, 500),
                ("homework_type", "string", False, 20),
                ("homework_desc", "string", False, 2000),
            ]
        },
        "homework": {
            "attributes": [
                ("user_id", "integer", True, None),
                ("lesson_id", "string", True, 50),
                ("type", "string", False, 20),
                ("file_id", "string", False, 500),
                ("file_type", "string", False, 20),
                ("text_content", "string", False, 5000),
                ("submitted_at", "string", False, 50),
                ("status", "string", False, 20),
                ("score", "integer", False, None),
                ("teacher_comment", "string", False, 2000),
            ]
        },
        "placement_questions": {
            "attributes": [
                ("level_code", "string", False, 10),
                ("question_text", "string", True, 2000),
                ("options", "string", False, 4000),
                ("correct_answer", "integer", False, None),
            ]
        },
        "placement_answers": {
            "attributes": [
                ("user_id", "integer", True, None),
                ("question_id", "string", True, 50),
                ("answer", "integer", False, None),
                ("is_correct", "boolean", False, None),
            ]
        },
        "exams": {
            "attributes": [
                ("level_code", "string", True, 10),
                ("exam_type", "string", True, 50),
                ("title", "string", False, 255),
                ("questions_json", "string", False, 10000),
                ("passing_score", "integer", False, None),
            ]
        },
        "exam_results": {
            "attributes": [
                ("user_id", "integer", True, None),
                ("exam_id", "string", True, 50),
                ("score", "integer", False, None),
                ("passed", "boolean", False, None),
                ("taken_at", "string", False, 50),
            ]
        },
    }

    for col_id, schema in schemas.items():
        try:
            db.get_collection(DATABASE_ID, col_id)
            print(f"  ✅ Collection '{col_id}' موجود است.")
        except Exception:
            print(f"  🛠 ساخت Collection '{col_id}'...")
            db.create_collection(DATABASE_ID, col_id, col_id, permissions=["collection"])
            for attr in schema["attributes"]:
                name, type_, required, size = attr
                default = None
                if type_ == "integer":
                    default = 0 if not required else None
                if type_ == "string":
                    default = "" if not required else None
                if name == "status":
                    default = "pending"
                if name == "temp_state":
                    default = ""
                try:
                    if type_ == "string":
                        db.create_string_attribute(DATABASE_ID, col_id, name, size, required, default=default if not required else None)
                    elif type_ == "integer":
                        db.create_integer_attribute(DATABASE_ID, col_id, name, required, default=default if not required else None)
                    elif type_ == "boolean":
                        db.create_boolean_attribute(DATABASE_ID, col_id, name, required, default=default if not required else None)
                except Exception as e2:
                    print(f"    ⚠️ Attribute {name} error: {e2}")


def seed_data():
    print("\n📥 در حال ورود داده‌های نمونه...")

    questions = [
        ("A1", "What ______ your name?", json.dumps(["is", "are", "am", "be"]), 0),
        ("A1", "I ______ from Iran.", json.dumps(["is", "am", "are", "be"]), 1),
        ("A2", "She ______ to the gym every day.", json.dumps(["go", "goes", "going", "gone"]), 1),
        ("B1", "If I ______ rich, I would buy a house.", json.dumps(["am", "was", "were", "be"]), 2),
        ("B2", "By the time we arrived, the movie ______.", json.dumps(["started", "has started", "had started", "starts"]), 2),
        ("C1", "The politician's speech was full of ______.", json.dumps(["rhetoric", "fallacies", "hyperbole", "euphemisms"]), 1),
    ]
    for q in questions:
        try:
            db.create_document(DATABASE_ID, "placement_questions", ID.unique(), {
                "level_code": q[0], "question_text": q[1], "options": q[2], "correct_answer": q[3]
            })
            print(f"  ✅ Question added: {q[1][:30]}...")
        except Exception as e:
            print(f"  ⚠️ Question error: {e}")

    lessons = [
        ("A1", 1, "درس ۱: معرفی خود", "در این درس با نحوه معرفی خود آشنا می‌شوید.", "both", "یک متن ۵۰ کلمه‌ای درباره خودتان بنویسید و صوتی بفرستید."),
        ("A1", 2, "درس ۲: خانواده", "در این درس واژگان خانواده را یاد می‌گیرید.", "writing", "درباره خانواده‌تان ۶۰ کلمه بنویسید."),
        ("A1", 3, "درس ۳: غذاها", "در این درس با نام غذاها آشنا می‌شوید.", "listening", "نام ۵ غذای مورد علاقه‌تان را صوتی بفرستید."),
        ("A1", 4, "درس ۴: رنگ‌ها", "در این درس رنگ‌ها را تمرین می‌کنید.", "writing", "۵ جمله درباره رنگ‌های مورد علاقه بنویسید."),
        ("A1", 5, "درس ۵: حیوانات", "واژگان حیوانات.", "listening", "صوتی: ۵ حیوان را توصیف کنید."),
        ("A1", 6, "درس ۶: سفر", "نحوه صحبت درباره سفر.", "both", "یک متن ۸۰ کلمه‌ای درباره آخرین سفر و صوتی از آن."),
    ]
    for l in lessons:
        try:
            db.create_document(DATABASE_ID, "lessons", ID.unique(), {
                "level_code": l[0], "lesson_number": l[1], "title": l[2], "content": l[3],
                "homework_type": l[4], "homework_desc": l[5]
            })
            print(f"  ✅ Lesson added: {l[2]}")
        except Exception as e:
            print(f"  ⚠️ Lesson error: {e}")

    exam_questions = json.dumps([
        {"q": "Choose the correct sentence:", "options": ["He don't like apples", "He doesn't likes apples", "He doesn't like apples", "He not like apples"], "correct": 2},
        {"q": "______ you live in Tehran?", "options": ["Do", "Does", "Are", "Is"], "correct": 0},
        {"q": "She is ______ than her brother.", "options": ["tall", "taller", "tallest", "more tall"], "correct": 1},
        {"q": "I ______ a movie last night.", "options": ["watch", "watched", "have watched", "watching"], "correct": 1},
    ])
    try:
        db.create_document(DATABASE_ID, "exams", ID.unique(), {
            "level_code": "A1", "exam_type": "level_exit", "title": "امتحان پایان سطح A1",
            "questions_json": exam_questions, "passing_score": 70
        })
        print("  ✅ Exam A1 added")
    except Exception as e:
        print(f"  ⚠️ Exam error: {e}")

    print("\n🎉 داده‌های اولیه با موفقیت وارد شدند!")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Appwrite Database Setup & Seed")
    print("=" * 50)
    ensure_collections()
    seed_data()
