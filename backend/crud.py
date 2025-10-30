# -----------------------------------------------------------------------------------
# 파일 이름   : crud.py (기존 users.py 대체)
# 설명        : SQLAlchemy ORM을 사용하여 데이터베이스 CRUD(Create, Read, Update, Delete) 작업을 처리하는 함수 모음
# -----------------------------------------------------------------------------------

from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid
import datetime

# models.py에서 정의한 테이블 클래스들을 가져옵니다.
import models

# ────────────────────────────────────────────────
# User 관련 함수
# ────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str):
    """이메일로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, name: str, email: str, hashed_password: str):
    """새로운 사용자를 생성합니다."""
    db_user = models.User(name=name, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """ID를 기준으로 사용자를 삭제합니다."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # 참고: 이 작업이 성공하려면 User와 연결된 다른 데이터(채팅, 즐겨찾기 등)들이
        # 데이터베이스 모델(models.py)에서 'ondelete="CASCADE"' 옵션으로 설정되어 있어야 합니다.
        db.delete(db_user)
        db.commit()
    return True

# ────────────────────────────────────────────────
# Chat Session 관련 함수
# ────────────────────────────────────────────────
def create_session(db: Session, user_id: int, title: str):
    """새로운 채팅 세션을 생성합니다."""
    session_id = str(uuid.uuid4())
    db_session = models.ChatSession(id=session_id, user_id=user_id, title=title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_sessions(db: Session, user_id: int):
    # lazy='joined' 덕분에 더 이상 복잡한 서브쿼리가 필요 없습니다.
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user_id).order_by(desc(models.ChatSession.created_at)).all()

def get_session_logs(db: Session, session_id: str):
    return db.query(models.ChatLog).filter(models.ChatLog.session_id == session_id).order_by(models.ChatLog.created_at).all()

def delete_session(db: Session, session_id: str):
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False # 세션이 없어도 오류를 일으키지 않고 False 반환

def get_session_logs(db: Session, session_id: str):
    """특정 세션의 모든 채팅 로그를 조회합니다."""
    return db.query(models.ChatLog).filter(models.ChatLog.session_id == session_id).order_by(models.ChatLog.created_at).all()

def delete_session(db: Session, session_id: str):
    """특정 채팅 세션을 삭제합니다."""
    db_session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False

# ────────────────────────────────────────────────
# Chat Log 관련 함수
# ────────────────────────────────────────────────
def save_chat(db: Session, session_id: str, user_id: int, message: str, url: str, name: str, role: str):
    """채팅 메시지를 DB에 저장합니다."""
    db_log = models.ChatLog(
        session_id=session_id,
        user_id=user_id,
        message=message,
        url=url,
        name=name,
        role=role
    )
    db.add(db_log)
    db.commit()

# ────────────────────────────────────────────────
# Bookmark 관련 함수
# ────────────────────────────────────────────────
def add_bookmark(db: Session, user_id: int, name: str, url: str):
    """즐겨찾기를 추가합니다."""
    db_bookmark = models.Bookmark(user_id=user_id, name=name, url=url)
    db.add(db_bookmark)
    db.commit()

def get_bookmarks(db: Session, user_id: int):
    """사용자의 모든 즐겨찾기를 조회합니다."""
    return db.query(models.Bookmark).filter(models.Bookmark.user_id == user_id).order_by(models.Bookmark.created_at).all()

def update_bookmark(db: Session, bookmark_id: int, name: str, url: str):
    db_bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if db_bookmark: # 북마크가 존재할 때만 업데이트
        db_bookmark.name = name
        db_bookmark.url = url
        db.commit()
        return db_bookmark
    return None # 북마크가 없으면 None 반환

def delete_bookmark(db: Session, bookmark_id: int):
    db_bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if db_bookmark: # 북마크가 존재할 때만 삭제
        db.delete(db_bookmark)
        db.commit()
        return True
    return False # 북마크가 없어도 오류 없이 False 반환