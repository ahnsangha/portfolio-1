/* -----------------------------------------------------------------------------------
 * 파일 이름    : useAuthStore.js
 * 설명         : Zustand 기반 인증(Store) 관리 모듈 - 사용자 인증 상태 및 관련 액션 제공
 * 주요 기능    :
 *   1) authUser, isSigningUp, isLoggingIn, isUpdatingProfile, isCheckingAuth, onlineUsers 상태 관리
 *   2) checkAuth: 서버로 인증 상태 확인 및 로컬스토리지 동기화
 *   3) signup: 회원가입 API 호출 및 authUser 설정
 *   4) login: 로그인 API 호출 및 authUser 설정
 *   5) logout: 로그아웃 처리 및 로컬스토리지 정리
 *   6) updateProfile: 프로필 업데이트 API 호출 및 상태 갱신
 *   7) deleteAccount: 회원탈퇴 호출 및 authUser 설정
 * ----------------------------------------------------------------------------------- */

import { create } from "zustand";
import { axiosInstance } from "../lib/axios";
import toast from "react-hot-toast";
import { useChatStore } from "./useChatStore";

const localAuth = localStorage.getItem("authUser");

// ────────────────────────────────────────────────────────────────────────────────────
// 1) Store 초기화 및 상태 정의
//    - authUser: 로컬스토리지에서 복원된 사용자 정보
//    - 로딩 및 인증 관련 플래그(isSigningUp, isLoggingIn, isUpdatingProfile, isCheckingAuth)
//    - onlineUsers: 현재 온라인 사용자 ID 목록
// ────────────────────────────────────────────────────────────────────────────────────
export const useAuthStore = create((set) => ({
  authUser: localAuth ? JSON.parse(localAuth) : null,
  isSigningUp: false,
  isLoggingIn: false,
  isUpdatingProfile: false,
  isCheckingAuth: true,
  isDeletingAccount: false,
  onlineUsers: [],

  // ────────────────────────────────────────────────────────────────────────────────
  // 2) checkAuth 액션
  //    - 서버로 현재 인증 상태 확인(GET /api/status)
  //    - authUser 상태 및 로컬스토리지 동기화
  //    - 완료 후 isCheckingAuth 플래그 해제
  // ────────────────────────────────────────────────────────────────────────────────
  checkAuth: async () => {
    try {
      const res = await axiosInstance.get("/api/status");
      set({ authUser: res.data });
      localStorage.setItem("authUser", JSON.stringify(res.data));
    } catch (error) {
      console.log("checkAuth error:", error);
      set({ authUser: null });
      localStorage.removeItem("authUser");
    } finally {
      set({ isCheckingAuth: false });
    }
  },

  // ────────────────────────────────────────────────────────────────────────────────
  // 3) signup 액션
  //    - 회원가입 요청(POST /signup)
  //    - 성공 시 authUser 상태 설정 및 로컬스토리지 저장
  //    - toast로 성공/실패 메시지 표시
  // ────────────────────────────────────────────────────────────────────────────────
  signup: async (data) => {
    set({ isSigningUp: true });
    try {
      const res = await axiosInstance.post("/signup", data);
      if (res.data?.data) {
        set({ authUser: res.data.data });
        localStorage.setItem("authUser", JSON.stringify(res.data.data));
      }
      toast.success(res.data.message || "계정 생성이 완료되었습니다!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "회원가입 실패");
      console.log("signup:" + error.response?.data?.message);
    } finally {
      set({ isSigningUp: false });
    }
  },

  // ────────────────────────────────────────────────────────────────────────────────
  // 4) login 액션
  //    - 로그인 요청(POST /login)
  //    - 성공 시 authUser 상태 설정 및 로컬스토리지 저장
  //    - toast로 성공/실패 메시지 표시
  // ────────────────────────────────────────────────────────────────────────────────
  login: async (data) => {
    set({ isLoggingIn: true });
    try {
      const res = await axiosInstance.post("/login", data);
      if (res.data?.data) {
        set({ authUser: res.data.data });
        localStorage.setItem("authUser", JSON.stringify(res.data.data));
      }
      console.log("loginSuccess");
      toast.success(res.data.message || "로그인 성공!");
    } catch (error) {
      toast.error(error.response?.data?.message || "로그인 실패");
    } finally {
      set({ isLoggingIn: false });
    }
  },

  loginSuccess: (user) => {
    set({ authUser: user });
    const chat = useChatStore.getState();
    chat.$reset(); // 메모리 클리어
    chat.setSession(null);
  },

  // ────────────────────────────────────────────────────────────────────────────────
  // 5) logout 액션
  //    - 로그아웃 요청(POST /logout)
  //    - authUser 상태 초기화 및 로컬스토리지 제거
  //    - toast로 성공/실패 메시지 표시
  // ────────────────────────────────────────────────────────────────────────────────

  logout: async () => {
    try {
        // 1. 서버에 로그아웃을 요청하여 서버 세션을 정리하고 쿠키 삭제 응답
        await axiosInstance.post("/logout");
        
    } catch (error) {
        // 서버 요청에 실패하더라도 클라이언트 측에서는 로그아웃을 진행
        console.error("Logout API call failed:", error);
        toast.error(error.response?.data?.message || "로그아웃 실패");
    } finally {
        // 2. 클라이언트의 모든 인증 정보를 확실하게 제거.
        set({ authUser: null });
        localStorage.removeItem("authUser");
        useChatStore.getState().$reset(); // 채팅 상태 초기화
        
        // 3. 쿠키를 직접 만료시키는 코드를 추가
        document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

        toast.success("로그아웃 되었습니다!");
    }
},

  // ────────────────────────────────────────────────────────────────────────────────
  // 6) updateProfile 액션
  //    - 프로필 업데이트 요청(PUT /update-profile)
  //    - 성공 시 authUser 상태 갱신
  //    - toast로 성공/실패 메시지 표시
  // ────────────────────────────────────────────────────────────────────────────────
  updateProfile: async (data) => {
    set({ isUpdatingProfile: true });
    try {
      const res = await axiosInstance.put("/update-profile", data);
      if (res.data?.data) {
        set({ authUser: res.data.data });
        toast.success("프로필이 성공적으로 변경되었습니다!");
      }
    } catch (error) {
      console.error("프로필 수정 실패:", error);
      toast.error(error.response?.data?.message || "프로필 수정 실패");
      console.log("profile:" + error.response?.data?.message);
    } finally {
      set({ isUpdatingProfile: false });
    }
  },

  // ────────────────────────────────────────────────────────────────────────────────
  // 7) deleteAccount 액션
  //    - 회원 탈퇴 요청(DELETE /delete-account)
  //    - 성공 시 authUser 상태 초기화 및 로컬스토리지/쿠키 정리
  // ────────────────────────────────────────────────────────────────────────────────
  deleteAccount: async () => {
    set({ isDeletingAccount: true }); // 👈 로딩 시작
    try {
      await axiosInstance.delete("/delete-account");

      // 성공 시, 클라이언트에서도 로그아웃과 동일한 정리 작업을 수행합니다.
      set({ authUser: null });
      localStorage.removeItem("authUser");
      useChatStore.getState().$reset(); // 채팅 상태 초기화
      document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      toast.success("회원 탈퇴가 완료되었습니다.");

    } catch (error) {
      console.error("회원 탈퇴 실패:", error);
      toast.error(error.response?.data?.message || "회원 탈퇴 중 오류가 발생했습니다.");
    } finally {
      set({ isDeletingAccount: false }); // 👈 로딩 종료
    }
  },

}));

