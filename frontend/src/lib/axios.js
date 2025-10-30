/* -----------------------------------------------------------------------------------
 * 파일 이름    : axios.js
 * 설명         : Axios 인스턴스 생성 - 기본 API 서버 URL 및 쿠키 송수신 설정
 * 주요 기능    :
 *   1) baseURL: http://localhost:5000 (백엔드 서버 주소) 설정
 *   2) withCredentials: 쿠키를 포함한 요청/응답 허용
 * ----------------------------------------------------------------------------------- */

// ────────────────────────────────────────────────────────────────────────────────────
// 1) axiosInstance 생성
//    - 역할: 기본 설정된 Axios 인스턴스를 만들어 API 요청에 재사용
//    - baseURL: API 서버 기본 경로
//    - withCredentials: cross-site Access-Control 요청에 쿠키 포함 허용
// ────────────────────────────────────────────────────────────────────────────────────
import axios from "axios";

export const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});
