# -----------------------------------------------------------------------------------
# 파일 이름   : app.py
# 설명        : FastAPI, SQLAlchemy 기반 AI 챗봇 및 음식 추천 API 서버 (최종 버전)
# 주요 기능   :
#   - SQLAlchemy를 이용한 안정적인 DB 세션 관리 (Supabase/PostgreSQL 연동)
#   - Depends를 사용한 인증 및 DB 의존성 주입
#   - Pydantic을 이용한 요청 데이터 검증
#   - 모든 API 엔드포인트 구현 (인증, 채팅, AI, 즐겨찾기)
# -----------------------------------------------------------------------------------

import os
import uuid
import datetime
import re
from typing import Optional, List
import random
from urllib.parse import unquote

from fastapi import FastAPI, Request, Response, Depends, Cookie, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import jwt
import bcrypt
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

# 새로 만든 모듈들을 import 합니다.
import crud, models
from database import engine, get_db

# AI 관련 모듈 import
from Ai.Logic import (
    classify_emotion_and_reply_with_gpt, is_emotion_related, 
    is_greeting, is_thanks, is_recommend
)
from Ai.SearchContent import find_restaurant_nearby

# ────────────────────────────────────────────────
# 1) 환경 변수 & DB 테이블 생성
# ────────────────────────────────────────────────
load_dotenv()
ENV = os.getenv("APP_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "capstone-secret")

# SQLAlchemy 모델을 기반으로 DB에 모든 테이블을 생성합니다.
# 서버가 시작될 때 한 번만 실행됩니다.
models.Base.metadata.create_all(bind=engine)

# ────────────────────────────────────────────────
# 2) FastAPI 앱 생성 & CORS
# ────────────────────────────────────────────────
app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://portfolio-1-frontend-coral.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────
# 3) 헬퍼 및 인증 의존성 함수
# ────────────────────────────────────────────────
def verify_token(token: Optional[str]) -> Optional[str]:
    if not token: return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("email")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def current_user_from_token(token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """요청 쿠키의 토큰을 검증하고 DB에서 사용자 정보를 찾아 반환하는 의존성 함수."""
    if not token: raise HTTPException(status_code=401, detail="Not authenticated")
    email = verify_token(token)
    if not email: raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = crud.get_user_by_email(db, email=email)
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user

# ────────────────────────────────────────────────
# 4) Pydantic 모델 정의 (API 입출력 데이터 형식)
# ────────────────────────────────────────────────
class UserCreate(BaseModel): name: str; email: str; password: str
class UserLogin(BaseModel): email: str; password: str
class SessionCreate(BaseModel): title: Optional[str] = ""
class SessionOut(BaseModel): 
    id: str
    title: Optional[str]
    created_at: datetime.datetime
    last_message: Optional[str] = None
    last_date: Optional[datetime.datetime] = None
    model_config = ConfigDict(from_attributes=True) # SQLAlchemy 모델을 Pydantic 모델로 변환 허용

class BookmarkCreate(BaseModel): name: str; url: str
class BookmarkUpdate(BaseModel): id: int; name: str; url: str
class BookmarkDelete(BaseModel): bookmark_id: int

# ────────────────────────────────────────────────
# 5) 인증 API
# ────────────────────────────────────────────────
@app.post("/api/signup")
async def api_signup(data: UserCreate, db: Session = Depends(get_db)):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data.email): raise HTTPException(status_code=400, detail="이메일 형식이 올바르지 않습니다.")
    db_user = crud.get_user_by_email(db, email=data.email)
    if db_user: raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")
    
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = crud.create_user(db=db, name=data.name, email=data.email, hashed_password=hashed_password)
    
    token = jwt.encode({"email": user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, SECRET_KEY, algorithm="HS256")
    resp = JSONResponse({"success": True, "message": "회원가입 성공", "data": {"id": user.id, "name": user.name, "email": user.email}})
    secure = ENV == "production"
    resp.set_cookie("token", token, httponly=True, path="/", secure=secure, samesite="none" if secure else "lax")
    return resp

@app.post("/api/login")
async def api_login(data: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=data.email)
    if not user or not bcrypt.checkpw(data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(401, "이메일 또는 비밀번호가 틀렸습니다.")
    
    token = jwt.encode({"email": user.email, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, SECRET_KEY, algorithm="HS256")
    resp = JSONResponse({"success": True, "message": "로그인 성공", "data": {"id": user.id, "name": user.name, "email": user.email}})
    secure = ENV == "production"
    resp.set_cookie("token", token, httponly=True, path="/", secure=secure, samesite="none" if secure else "lax")
    return resp

@app.get("/api/status")
async def api_status(user: models.User = Depends(current_user_from_token)):
    return {"logged_in": True, "id": user.id, "name": user.name, "email": user.email}

@app.post("/api/logout")
async def api_logout(response: Response):
    # 로그인과 동일한 로직으로 secure, samesite 값을 결정
    secure = os.getenv("APP_ENV") == "production"
    samesite = "none" if secure else "lax"
    
    # delete_cookie 호출 시 모든 속성을 명시
    response.delete_cookie(
        "token",
        path="/",
        httponly=True, # HttpOnly도 명시해주는 것이 더 안전합니다.
        secure=secure,
        samesite=samesite
    )
    return {"success": True, "message": "로그아웃 되었습니다."}

@app.delete("/api/delete-account")
async def api_delete_account(
    response: Response,
    user: models.User = Depends(current_user_from_token),
    db: Session = Depends(get_db)
):
    """현재 인증된 사용자의 계정을 삭제합니다."""
    
    # 1. crud 모듈의 사용자 삭제 함수를 호출합니다.
    crud.delete_user(db=db, user_id=user.id)
    
    # 2. 탈퇴 성공 시, 로그아웃과 동일하게 클라이언트의 인증 쿠키를 삭제합니다.
    secure = os.getenv("APP_ENV") == "production"
    samesite = "none" if secure else "lax"
    response.delete_cookie(
        "token",
        path="/",
        httponly=True,
        secure=secure,
        samesite=samesite
    )
    
    return {"success": True, "message": "회원 탈퇴가 정상적으로 처리되었습니다."}

# ────────────────────────────────────────────────
# 7) AI 챗 & 음식 추천
# ────────────────────────────────────────────────
@app.post("/get_response")
async def get_response(
    request: Request,
    message: str = Form(...),
    session_id: Optional[str] = Form(None),
    location: str = Form("서울"), 
    user: models.User = Depends(current_user_from_token), # SQLAlchemy 모델로 타입 변경
    db: Session = Depends(get_db) # 새로운 DB 세션 의존성으로 변경
):
    user_id = user.id
    if not session_id:
        # crud 모듈을 통해 함수 호출
        db_session = crud.create_session(db=db, user_id=user_id, title=(message[:30] or None))
        session_id = db_session.id

    text = message.strip()
    # crud 모듈을 통해 함수 호출 (db 세션 전달)
    crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=text, url=None, name=None, role="user")
    created_at = datetime.datetime.utcnow().isoformat() + "Z"

    # 인사 및 감사 메시지 우선 처리
    if is_greeting(text):
        reply = "안녕하세요! 무엇을 도와드릴까요?"
        crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=reply, url=None, name=None, role="assistant")
        return {"message": reply, "createdAt": created_at}

    if is_thanks(text):
        reply = "별말씀을요! 또 궁금하신 게 있으면 언제든 말씀해 주세요"
        crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=reply, url=None, name=None, role="assistant")
        return {"message": reply, "createdAt": created_at}

    # 감정 분석 또는 재추천 요청 처리
    if is_recommend(text) or is_emotion_related(text):
        food, reply_text = None, None
        
        if is_emotion_related(text):
            chat_history = crud.get_session_logs(db=db, session_id=session_id)
            emotion, food, reply_text = classify_emotion_and_reply_with_gpt(text, chat_history=chat_history)
        
        if not food:
            if not is_recommend(text):
                fallback_reply = (
                    "죄송해요, 제가 잘 이해하지 못했어요. "
                    "혹시 지금 느끼는 기분을 '행복', '우울', '스트레스', '화남'과 같이 "
                    "좀 더 명확한 감정 단어로 말씀해주실 수 있나요?"
                )
                crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=fallback_reply, url=None, name=None, role="assistant")
                return {"message": fallback_reply, "createdAt": created_at}
            
            foods = ["김밥", "떡볶이", "비빔밥", "갈비탕", "파스타", "치킨"]
            food = random.choice(foods)
            reply_text = f"그렇다면 {food}는 어떠세요?"

        restaurant = find_restaurant_nearby(food, location) # Form으로 받은 location 사용

        if restaurant:
            map_url = f"http://googleusercontent.com/maps/google.com/0:{restaurant.get('place_id')}"
            name = restaurant.get("name")
            formatted = (
                f"{reply_text}<br><br>"
                f"추천 식당: <strong>{name}</strong><br>"
                f"주소: {restaurant.get('address')}<br>"
                f"평점: {restaurant.get('rating','정보 없음')}점"
            )
            crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=formatted, url=map_url, name=name, role="assistant")
            return { "message": formatted, "restaurant": restaurant, "name": name, "url": map_url, "createdAt": created_at, "location": location}
        else:
            reply = f"{reply_text}<br><br>아쉽지만 근처 '{food}' 식당을 찾지 못했어요."
            crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=reply, url=None, name=None, role="assistant")
            return {"message": reply, "createdAt": created_at}

    # 모든 조건에 해당하지 않을 경우 (오프토픽)
    off_topic = "감정이나 기분에 대해 말씀해주시면 관련된 음식을 추천해 드릴게요."
    crud.save_chat(db=db, session_id=session_id, user_id=user_id, message=off_topic, url=None, name=None, role="assistant")
    return {"message": off_topic, "createdAt": created_at}

# ────────────────────────────────────────────────
# 8) 채팅 세션 API
# ────────────────────────────────────────────────
@app.post("/api/sessions", response_model=SessionOut)
async def api_create_session(body: SessionCreate, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # crud 모듈의 함수를 사용하여 새 세션 생성
    db_session = crud.create_session(db=db, user_id=user.id, title=body.title or None)
    return db_session

@app.get("/api/sessions", response_model=List[SessionOut])
async def api_read_sessions(user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # crud 모듈의 함수를 사용하여 세션 목록 조회
    return crud.get_sessions(db=db, user_id=user.id)

@app.get("/api/sessions/{session_id}/logs")
async def api_read_session_logs(session_id: str, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # 소유권 확인
    sessions = crud.get_sessions(db=db, user_id=user.id)
    if session_id not in [s.id for s in sessions]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    # crud 모듈의 함수를 사용하여 로그 조회
    return crud.get_session_logs(db=db, session_id=session_id)

@app.delete("/api/sessions/{session_id}")
async def api_delete_session(session_id: str, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # 소유권 확인
    sessions = crud.get_sessions(db=db, user_id=user.id)
    if session_id not in [s.id for s in sessions]:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    if not crud.delete_session(db=db, session_id=session_id):
        raise HTTPException(status_code=500, detail="삭제에 실패했습니다.")
    return {"success": True}

# ────────────────────────────────────────────────
# 9) 즐겨찾기 API
# ────────────────────────────────────────────────
@app.post("/api/add_bookmark")
async def api_add_bookmark(data: BookmarkCreate, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    crud.add_bookmark(db=db, user_id=user.id, name=data.name, url=data.url)
    return {"success": True, "message": "즐겨찾기 추가 성공"}

@app.get("/api/bookmarks")
async def api_bookmarks(user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    return crud.get_bookmarks(db=db, user_id=user.id)

@app.post("/api/delete_bookmark")
async def api_delete_bookmark(data: BookmarkDelete, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # 참고: 실제 서비스에서는 이 북마크가 정말 해당 유저의 것인지 확인하는 로직이 추가되어야 합니다.
    crud.delete_bookmark(db=db, bookmark_id=data.bookmark_id)
    return {"success": True, "message": "즐겨찾기 삭제 성공"}

@app.post("/api/update_bookmark")
async def api_update_bookmark(data: BookmarkUpdate, user: models.User = Depends(current_user_from_token), db: Session = Depends(get_db)):
    # 참고: 실제 서비스에서는 이 북마크가 정말 해당 유저의 것인지 확인하는 로직이 추가되어야 합니다.
    crud.update_bookmark(db=db, bookmark_id=data.id, name=data.name, url=data.url)
    return {"success": True, "message": "즐겨찾기 수정 성공"}

# ────────────────────────────────────────────────
# 10) 서버 실행
# ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)


