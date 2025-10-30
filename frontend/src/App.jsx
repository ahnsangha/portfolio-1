/* -----------------------------------------------------------------------------------
 * 파일 이름    : App.jsx
 * 설명         : 애플리케이션 루트 컴포넌트 - 인증 상태 확인, 테마 적용, 라우팅 처리
 * 주요 기능    :
 *   1) useAuthStore로 인증 상태 확인 및 로딩 처리
 *   2) useThemeStore로 다크/라이트 테마 적용
 *   3) react-router-dom을 이용한 페이지 라우팅
 *   4) 전역 토스트(Toaster) 컴포넌트 렌더링
 *   5) 지도 모달 상태 전역 관리
 * ----------------------------------------------------------------------------------- */

import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import MapModal from "./components/MapModal";
import { motion, AnimatePresence } from "framer-motion";


import HomePage from "./pages/HomePage";
import SignUpPage from "./pages/SignUpPage";
import LoginPage from "./pages/LoginPage";
import SettingsPage from "./pages/SettingsPage";
import ProfilePage from "./pages/ProfilePage";

import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/useAuthStore";
import { useThemeStore } from "./store/useThemeStore";

import { Loader } from "lucide-react";
import { Toaster } from "react-hot-toast";
import useBookmarkStore from "./store/useBookmarkStore";

// ────────────────────────────────────────────────────────────────────────────────────
// 1) App 컴포넌트 정의
//    - 인증 상태 확인 및 로딩 처리
//    - 테마 적용(data-theme 속성 설정)
//    - 라우팅 및 전역 UI 컴포넌트 렌더링
// ────────────────────────────────────────────────────────────────────────────────────
const App = () => {
  const [isModalOpen, setModalOpen] = useState(false);
  const [currentPlaceName, setCurrentPlaceName] = useState("");
  const { authUser, checkAuth, isCheckingAuth } = useAuthStore();
  const { readBookmarks } = useBookmarkStore();
  const { theme } = useThemeStore();
  const [isSettingsOpen, setSettingsOpen] = useState(false);

  const loadingMessages = [
    "오늘은 어떤 기분이신가요? 🌦️",
    "맛있는 음식으로 당신의 마음을 위로해드릴게요. 🍜",
    "최고의 맛집을 열심히 찾고 있어요... 🕵️",
    "서버와 안전하게 연결하고 있습니다. 🛡️",
  ];
  const [currentMessage, setCurrentMessage] = useState(loadingMessages[0]);


  // ──────────────────────────────────────────────────────────────────────────────────
  // 2) useEffect: 마운트 시 한 번만 인증 상태 확인
  // ──────────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // ──────────────────────────────────────────────────────────────────────────────────
  // 3) 로딩 스피너 표시
  //    - 인증 확인 중이고 인증된 사용자 정보가 없으면 전체 화면으로 스피너 렌더링
  // ──────────────────────────────────────────────────────────────────────────────────

  useEffect(() => {
    // 로딩 중에만 메시지가 바뀌도록 설정
    if (isCheckingAuth && !authUser) {
      const intervalId = setInterval(() => {
        const randomIndex = Math.floor(Math.random() * loadingMessages.length);
        setCurrentMessage(loadingMessages[randomIndex]);
      }, 2500); // 2.5초마다 메시지 변경

      return () => clearInterval(intervalId); // 컴포넌트 언마운트 시 인터벌 정리
    }
  }, [isCheckingAuth, authUser]);

  if (isCheckingAuth && !authUser)
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-base-100 gap-4">
        <img src="/newlogo2.png" alt="마음맛집 로고" className="w-16 h-16 mb-2" />
        <Loader className="size-10 animate-spin text-primary" />
        <p className="text-base-content/70 mt-2 transition-opacity duration-500">{currentMessage}</p>
      </div>
    );

  // ──────────────────────────────────────────────────────────────────────────────────
  // 4) 메인 렌더링
  //    - data-theme으로 테마 적용
  //    - 네비게이션 바
  //    - 페이지 라우팅
  //    - 전역 Toaster 컴포넌트
  // ──────────────────────────────────────────────────────────────────────────────────
  return (
    <div data-theme={theme}>
      <Navbar
      onPlaceClick={(name) => {
        setCurrentPlaceName(name);
        setModalOpen(true);
      }}
      onSettingsClick={() => {
        setSettingsOpen(true);
      }}
    />

      <Routes>
        <Route
          path="/"
          element={authUser ? <HomePage shiftLeft={isSettingsOpen} /> : <Navigate to="/login" />}
        />
        <Route path="/signup" element={!authUser ? <SignUpPage /> : <Navigate to="/" />} />
        <Route path="/login" element={!authUser ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/profile" element={authUser ? <ProfilePage /> : <Navigate to="/login" />} />
      </Routes>

      <Toaster />
      <MapModal
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
        placeName={currentPlaceName}
      />

      <AnimatePresence>
        {isSettingsOpen && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "tween", duration: 0.3 }}
            className="fixed top-0 right-0 w-[450px] max-w-full h-full bg-base-100 shadow-[-8px_0_12px_-4px_rgba(0,0,0,0.1)] z-50"
          >
            <SettingsPage onClose={() => setSettingsOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
