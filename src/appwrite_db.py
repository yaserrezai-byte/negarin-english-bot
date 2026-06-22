import json
from datetime import datetime
from appwrite.query import Query
from appwrite.id import ID
from appwrite_client import get_databases
import config

db = get_databases()
DATABASE_ID = config.APPWRITE_DATABASE_ID

COL_USERS = "users"
COL_LESSONS = "lessons"
COL_HOMEWORK = "homework"
COL_PLACEMENT_Q = "placement_questions"
COL_PLACEMENT_A = "placement_answers"
COL_EXAMS = "exams"
COL_EXAM_RESULTS = "exam_results"


def _now():
    return datetime.utcnow().isoformat()


# ─── Users ───
def get_user_sync(telegram_id: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_USERS, queries=[
            Query.equal("telegram_id", telegram_id)
        ])
        docs = res.get("documents", [])
        return docs[0] if docs else None
    except Exception as e:
        print(f"get_user error: {e}")
        return None


def register_user_sync(telegram_id: int, full_name: str, username: str = None):
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
                "temp_state": "",
            }
        )
        return doc
    except Exception as e:
        print(f"register_user error: {e}")
        return None


def update_user_level_sync(telegram_id: int, level: str, status: str = "active"):
    user = get_user_sync(telegram_id)
    if not user:
        return
    db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
        "level": level,
        "status": status,
    })


def update_user_lesson_sync(telegram_id: int, lesson_number: int):
    user = get_user_sync(telegram_id)
    if not user:
        return
    db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
        "current_lesson": lesson_number,
        "last_lesson_at": _now(),
    })


# ─── Temp State (for stateless serverless) ───
def set_user_temp_state_sync(telegram_id: int, state_data: dict):
    user = get_user_sync(telegram_id)
    if not user:
        return
    try:
        db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
            "temp_state": json.dumps(state_data)
        })
    except Exception as e:
        print(f"set_temp_state error: {e}")


def get_user_temp_state_sync(telegram_id: int) -> dict:
    user = get_user_sync(telegram_id)
    if not user:
        return {}
    ts = user.get("temp_state", "")
    if not ts:
        return {}
    try:
        return json.loads(ts)
    except Exception:
        return {}


def clear_temp_state_sync(telegram_id: int):
    user = get_user_sync(telegram_id)
    if not user:
        return
    try:
        db.update_document(DATABASE_ID, COL_USERS, user["$id"], {
            "temp_state": ""
        })
    except Exception as e:
        print(f"clear_temp_state error: {e}")


# ─── Placement Questions ───
def get_placement_questions_sync(level_code: str = None):
    queries = [Query.limit(100)]
    if level_code:
        queries.append(Query.equal("level_code", level_code))
    try:
        res = db.list_documents(DATABASE_ID, COL_PLACEMENT_Q, queries=queries)
        return res.get("documents", [])
    except Exception as e:
        print(f"get_placement_questions error: {e}")
        return []


def clear_placement_answers_sync(user_id: int):
    try:
        res = db.list_documents(DATABASE_ID, COL_PLACEMENT_A, queries=[
            Query.equal("user_id", user_id)
        ])
        for doc in res.get("documents", []):
            db.delete_document(DATABASE_ID, COL_PLACEMENT_A, doc["$id"])
    except Exception as e:
        print(f"clear_placement_answers error: {e}")


def save_placement_answer_sync(user_id: int, question_id: str, answer: int, is_correct: bool):
    try:
        db.create_document(DATABASE_ID, COL_PLACEMENT_A, ID.unique(), {
            "user_id": user_id,
            "question_id": question_id,
            "answer": answer,
            "is_correct": is_correct,
        })
    except Exception as e:
        print(f"save_placement_answer error: {e}")


def get_user_placement_score_sync(user_id: int):
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
def get_lessons_by_level_sync(level_code: str):
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


def get_lesson_sync(level_code: str, lesson_number: int):
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


def set_lesson_video_sync(lesson_id: str, video_file_id: str):
    try:
        db.update_document(DATABASE_ID, COL_LESSONS, lesson_id, {
            "video_file_id": video_file_id,
        })
    except Exception as e:
        print(f"set_lesson_video error: {e}")


# ─── Homework ───
def submit_homework_sync(user_id: int, lesson_id: str, hw_type: str, file_id: str = None, file_type: str = None, text: str = None):
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


def get_pending_homework_sync():
    try:
        res = db.list_documents(DATABASE_ID, COL_HOMEWORK, queries=[
            Query.equal("status", "pending"),
            Query.limit(100),
        ])
        docs = res.get("documents", [])
        result = []
        for d in docs:
            try:
                ures = db.list_documents(DATABASE_ID, COL_USERS, queries=[
                    Query.equal("telegram_id", d.get("user_id")),
                    Query.limit(1),
                ])
                udocs = ures.get("documents", [])
                user = udocs[0] if udocs else {}
            except:
                user = {}
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


def review_homework_sync(homework_id: str, score: int, comment: str):
    try:
        db.update_document(DATABASE_ID, COL_HOMEWORK, homework_id, {
            "status": "reviewed",
            "score": score,
            "teacher_comment": comment,
        })
    except Exception as e:
        print(f"review_homework error: {e}")


# ─── Exams ───
def get_exam_sync(level_code: str, exam_type: str = "level_exit"):
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


def save_exam_result_sync(user_id: int, exam_id: str, score: int, passed: bool):
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
