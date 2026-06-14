import json
from datetime import datetime
from appwrite.query import Query
from appwrite.id import ID
from appwrite_client import get_databases
import config

db = get_databases()
DATABASE_ID = config.APPWRITE_DATABASE_ID

# Collection IDs (must match Appwrite Console)
COL_USERS = "users"
COL_LESSONS = "lessons"
COL_HOMEWORK = "homework"
COL_PLACEMENT_Q = "placement_questions"
COL_PLACEMENT_A = "placement_answers"
COL_EXAMS = "exams"
COL_EXAM_RESULTS = "exam_results"


# ─── Helpers ───
def _now():
    return datetime.utcnow().isoformat()


# ─── Users ───
async def get_user(telegram_id: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_USERS, queries=[
            Query.equal("telegram_id", telegram_id)
        ])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception as e:
        print(f"get_user error: {e}")
        return None


async def register_user(telegram_id: int, full_name: str, username: str = None):
    try:
        doc = db.create_document(
            DATABASE_ID, COL_USERS, ID.unique(),
            {
                "telegram_id": telegram_id,
                "full_name": full_name,
                "username": username or "",
                "level": "",
                "current_lesson": 0,
                "course_week": 0,
                "status": "placement",
                "created_at": _now(),
                "last_lesson_at": "",
            }
        )
        return doc
    except Exception as e:
        print(f"register_user error: {e}")
        return None


async def update_user_level(telegram_id: int, level: str, status: str = "active"):
    user = await get_user(telegram_id)
    if not user:
        return
    db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
        "level": level,
        "status": status,
    })


async def update_user_lesson(telegram_id: int, lesson_number: int):
    user = await get_user(telegram_id)
    if not user:
        return
    db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
        "current_lesson": lesson_number,
        "last_lesson_at": _now(),
    })


# ─── Placement Questions ───
async def get_placement_questions(level_code: str = None):
    queries = [Query.limit(100)]
    if level_code:
        queries.append(Query.equal("level_code", level_code))
    try:
        res = db.list_documents(DATABASE_ID, COL_PLACEMENT_Q, queries=queries)
        return res.get("documents", [])
    except Exception as e:
        print(f"get_placement_questions error: {e}")
        return []


async def clear_placement_answers(user_id: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_PLACEMENT_A, queries=[
            Query.equal("user_id", user_id)
        ])
        for doc in res.get("documents", []):
            db.delete_document(DATABASE_ID, COL_PLACEMENT_A, doc["$id"])
    except Exception as e:
        print(f"clear_placement_answers error: {e}")


async def save_placement_answer(user_id: int, question_id: str, answer: int, is_correct: bool):
    try:
        db.create_document(DATABASE_ID, COL_PLACEMENT_A, ID.unique(), {
            "user_id": user_id,
            "question_id": question_id,
            "answer": answer,
            "is_correct": is_correct,
        })
    except Exception as e:
        print(f"save_placement_answer error: {e}")


async def get_user_placement_score(user_id: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_PLACEMENT_A, queries=[
            Query.equal("user_id", user_id)
        ])
        docs = res.get("documents", [])
        total = len(docs)
        correct = sum(1 for d in docs if d.get("is_correct"))
        return {"total": total, "correct": correct}
    except Exception as e:
        print(f"get_user_placement_score error: {e}")
        return {"total": 0, "correct": 0}


# ─── Lessons ───
async def get_lessons_by_level(level_code: str):
    try:
        res = db.list_documents(DATABASE_ID, COL_LESSONS, queries=[
            Query.equal("level_code", level_code),
            Query.order_asc("lesson_number"),
            Query.limit(100),
        ])
        return res.get("documents", [])
    except Exception as e:
        print(f"get_lessons_by_level error: {e}")
        return []


async def get_lesson(level_code: str, lesson_number: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_LESSONS, queries=[
            Query.equal("level_code", level_code),
            Query.equal("lesson_number", lesson_number),
            Query.limit(1),
        ])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception as e:
        print(f"get_lesson error: {e}")
        return None


async def set_lesson_video(lesson_id: str, video_file_id: str):
    try:
        db.update_document(DATABASE_ID, COL_LESSONS, lesson_id, {
            "video_file_id": video_file_id,
        })
    except Exception as e:
        print(f"set_lesson_video error: {e}")


# ─── Homework ───
async def submit_homework(user_id: int, lesson_id: str, hw_type: str, file_id: str = None, file_type: str = None, text: str = None):
    try:
        db.create_document(DATABASE_ID, COL_HOMEWORK, ID.unique(), {
            "user_id": user_id,
            "lesson_id": lesson_id,
            "type": hw_type,
            "file_id": file_id or "",
            "file_type": file_type or "",
            "text_content": text or "",
            "submitted_at": _now(),
            "status": "pending",
            "score": 0,
            "teacher_comment": "",
        })
    except Exception as e:
        print(f"submit_homework error: {e}")


async def get_pending_homework():
    try:
        res = db.list_documents(DATABASE_ID, COL_HOMEWORK, queries=[
            Query.equal("status", "pending"),
            Query.limit(100),
        ])
        docs = res.get("documents", [])
        # Enrich with user and lesson info
        result = []
        for d in docs:
            # get user
            try:
                ures = db.list_documents(DATABASE_ID, COL_USERS, queries=[
                    Query.equal("telegram_id", d.get("user_id")),
                    Query.limit(1),
                ])
                udocs = ures.get("documents", [])
                user = udocs[0] if udocs else {}
            except:
                user = {}
            # get lesson
            try:
                ldoc = db.get_document(DATABASE_ID, COL_LESSONS, d.get("lesson_id"))
            except:
                ldoc = {}
            result.append({
                **d,
                "user": user,
                "lesson": ldoc,
            })
        return result
    except Exception as e:
        print(f"get_pending_homework error: {e}")
        return []


async def review_homework(homework_id: str, score: int, comment: str):
    try:
        db.update_document(DATABASE_ID, COL_HOMEWORK, homework_id, {
            "status": "reviewed",
            "score": score,
            "teacher_comment": comment,
        })
    except Exception as e:
        print(f"review_homework error: {e}")


# ─── Exams ───
async def get_exam(level_code: str, exam_type: str = "level_exit"):
    try:
        res = db.list_documents(DATABASE_ID, COL_EXAMS, queries=[
            Query.equal("level_code", level_code),
            Query.equal("exam_type", exam_type),
            Query.limit(1),
        ])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception as e:
        print(f"get_exam error: {e}")
        return None


async def save_exam_result(user_id: int, exam_id: str, score: int, passed: bool):
    try:
        db.create_document(DATABASE_ID, COL_EXAM_RESULTS, ID.unique(), {
            "user_id": user_id,
            "exam_id": exam_id,
            "score": score,
            "passed": passed,
            "taken_at": _now(),
        })
    except Exception as e:
        print(f"save_exam_result error: {e}")
