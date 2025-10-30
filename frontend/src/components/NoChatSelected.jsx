/* -----------------------------------------------------------------------------------
 * 파일 이름    : NoChatSelected.jsx
 * 설명         : 채팅방이 선택되지 않았을 때 표시할 웰컴 안내 UI 컴포넌트
 * 주요 기능    :
 *   1) 채팅방 미선택 시 안내 아이콘 및 텍스트 렌더링
 *   2) 메시지 입력 전 사이드바 클릭을 유도하는 가이드 제공
 * ----------------------------------------------------------------------------------- */
import React from "react";
import { Info } from "lucide-react";

// ────────────────────────────────────────────────────────────────────────────────────
// 1) NoChatSelected 컴포넌트 정의
//    - 역할: 채팅방을 선택하기 전 사용자에게 웰컴 메시지와 가이드를 제공
// ────────────────────────────────────────────────────────────────────────────────────
const NoChatSelected = () => {
  return (
    <div className="w-full flex flex-1 flex-col items-center justify-center p-16 bg-base-100/50">
      <div className="max-w-md text-center space-y-6">
        {/* 아이콘 화면 */}
        <div className="flex justify-center gap-4 mb-4">
          <div className="relative">
            <div
              className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center
						justify-center animate-bounce"
            >
              <img src="/logo2.png" alt="description" className="w-16 h-16 object-contain" />
            </div>
          </div>
        </div>

        {/* 환영인사말 */}
        <h2 className="text-2xl font-bold">마음 맛집에 오신것을 환영합니다!</h2>
        <p className="text-base-content/60 inline-flex items-center gap-1 justify-center">
          상단 도움말을 클릭하면 마음맛집의 사용법을 안내해드립니다.
        </p>
      </div>
    </div>
  );
};

export default NoChatSelected;
