#  마음맛집

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green.svg)](https://fastapi.tiangolo.com/) [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-orange.svg)](https://www.sqlalchemy.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/) [![Vite](https://img.shields.io/badge/Vite-5.2-purple.svg)](https://vitejs.dev/) [![Zustand](https://img.shields.io/badge/Zustand-4.5-yellow.svg)](https://github.com/pmndrs/zustand) [![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-cyan.svg)](https://tailwindcss.com/)  
FastAPI와 다양한 AI 모델을 기반으로 사용자의 감정에 맞는 음식을 추천하고, 근처 맛집 정보를 제공하는 AI 챗봇 API 서버입니다.

## Backend

## ✨ 주요 기능

* **AI 기반 음식 추천**: 사용자의 대화 내용을 분석하여 감정을 파악하고, 그에 맞는 음식을 추천합니다.
* **실시간 맛집 검색**: Google Maps API와 연동하여 추천된 음식에 대한 주변 맛집 정보를 제공합니다.
* **사용자 인증**: JWT 토큰 기반의 안전한 회원가입, 로그인, 로그아웃 기능을 제공합니다.
* **채팅 및 즐겨찾기 관리**: 사용자의 대화 기록과 즐겨찾기 목록을 생성하고 관리하는 API를 제공합니다.
* **안정적인 DB 관리**: SQLAlchemy ORM을 사용하여 PostgreSQL 데이터베이스(Supabase)와 안정적으로 통신합니다.

## 🛠️ 기술 스택

* **Framework**: FastAPI
* **Database**: PostgreSQL (via Supabase), SQLAlchemy
* **AI Models**:
    * OpenAI GPT-4o (감정 분석 및 음식 추천)
    * Groq (일반 대화 및 실시간 검색)
    * Cohere (사용자 의도 분류)
* **APIs**: Google Maps Places API
* **Authentication**: JWT (JSON Web Tokens), bcrypt
* **Deployment**: Render

## ⚙️ 시작하기

### 1. Repository 클론

```bash
git clone [https://github.com/](https://github.com/)[your-username]/[your-repo-name].git
cd [your-repo-name]/backend
```

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
# .env

### 서버 환경 (로컬 테스트 시 'development')
APP_ENV="development"

### JWT 토큰 암호화를 위한 비밀키 (아무 문자열이나 가능)
SECRET_KEY="your-super-secret-key"

### Supabase에서 발급받은 데이터베이스 연결 URL
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@..."

### 각 AI 및 API 서비스에서 발급받은 키
OPENAI_API_KEY="sk-..."
CO_API_KEY="..."
GROQ_API_KEY="..."
GOOGLE_MAPS_API_KEY="AIza..."

### AI 프롬프트에 사용될 이름 (선택사항)
Assistantname="마음이"
Username="손님"

### 5. 서버 실행
```bash
python app.py
```

### 🚀 API 엔드포인트
* 인증

* POST /api/signup: 회원가입

* POST /api/login: 로그인

* GET /api/status: 로그인 상태 확인

* POST /api/logout: 로그아웃

### 채팅 세션

* POST /api/sessions: 새 채팅 생성

* GET /api/sessions: 모든 채팅 목록 조회

* GET /api/sessions/{id}/logs: 특정 채팅의 대화 기록 조회

### AI 챗

* POST /get_response: AI 응답 생성

## Frontend

## ✨ 주요 기능

* **인터랙티브 채팅 UI**: 실시간으로 AI와 대화하고 응답을 받을 수 있는 사용자 친화적인 채팅 인터페이스를 제공합니다.
* **사용자 인증**: 회원가입 및 로그인 페이지를 통해 안전하게 계정을 관리할 수 있습니다.
* **위치 설정 및 지도 연동**: 사용자가 직접 위치를 설정할 수 있으며, 추천된 맛집은 Google Maps 모달을 통해 시각적으로 확인할 수 있습니다.
* **전역 상태 관리**: Zustand를 사용하여 인증, 채팅, 테마 등 앱의 상태를 효율적으로 관리합니다.
* **다이나믹 테마**: 사용자가 원하는 테마를 선택하여 앱의 전체적인 디자인을 변경할 수 있습니다.

## 🛠️ 기술 스택

* **Framework**: React (with Vite)
* **State Management**: Zustand
* **HTTP Client**: Axios
* **Styling**: Tailwind CSS, daisyUI
* **Routing**: React Router
* **Deployment**: Vercel

## ⚙️ 시작하기

### 1. Repository 클론

```bash
git clone [https://github.com/](https://github.com/)[your-username]/[your-repo-name].git
cd [your-repo-name]/frontend
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 환경 변수 설정
* 프로젝트 루트의 frontend 폴더에 .env 파일을 생성하고 아래 내용을 채워주세요.
```bash
# .env

# 로컬에서 테스트할 백엔드 서버 주소
VITE_API_BASE_URL="http://localhost:5000"

# Google Maps API 키 (지도 표시용)
VITE_GOOGLE_MAP_KEY="AIza..."
```
### 4. 개발 서버 실행
```bash
npm run dev
```
* 애플리케이션이 http://localhost:5173에서 실행됩니다.

### 📦 프로덕션 빌드
```bash
npm run build
```

* 프로젝트를 배포용으로 빌드하려면 아래 명령어를 실행하세요. dist 폴더에 최적화된 파일들이 생성됩니다.
