/* -----------------------------------------------------------------------------------
 * 파일 이름    : SettingsModal.jsx
 * 설명         : 회원탈퇴 기능이 들어있는 모달창
 * 주요 기능    :
 *   1) 회원 탈퇴 기능
 * ----------------------------------------------------------------------------------- */

import { X, Palette, ShieldAlert } from "lucide-react";
import { useThemeStore } from "../store/useThemeStore";
import { useAuthStore } from "../store/useAuthStore";

const themes = ["light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", "retro"];

const SettingsPage = ({ onClose }) => {
  const { theme, setTheme } = useThemeStore();
  const { deleteAccount, isDeletingAccount } = useAuthStore();

  const handleDeleteAccount = async () => {
    const isConfirmed = window.confirm(
      "정말로 회원에서 탈퇴하시겠습니까?\n모든 데이터가 영구적으로 삭제되며, 이 작업은 되돌릴 수 없습니다."
    );

    if (isConfirmed) {
      await deleteAccount();
      // 탈퇴 성공 시 authUser가 null이 되어 App.jsx에서 자동으로 로그인 페이지로 리디렉션합니다.
    }
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold">설정</h2>
        <button onClick={onClose} className="btn btn-sm btn-ghost btn-circle">
          <X className="size-5" />
        </button>
      </div>

      {/* 테마 설정 */}
      <div className="mb-8">
        <h3 className="flex items-center gap-2 text-lg font-semibold mb-4">
          <Palette className="size-5" />
          테마 변경
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {themes.map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={`btn btn-outline capitalize ${theme === t ? "btn-active" : ""}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* 회원탈퇴 위험 구역 (신규 추가) */}
      <div className="mt-auto pt-6 border-t border-error/30">
        <h3 className="flex items-center gap-2 text-lg font-bold text-error">
          <ShieldAlert className="size-5" />
          위험 구역
        </h3>
        <p className="text-sm text-base-content/70 mt-2">
          계정을 삭제하면 모든 채팅 기록과 즐겨찾기가 영구적으로 사라집니다. 이 결정에 신중해주세요.
        </p>
        <button
          onClick={handleDeleteAccount}
          className="btn btn-error btn-sm mt-4 w-full sm:w-auto"
          disabled={isDeletingAccount}
        >
          {isDeletingAccount ? (
            <span className="loading loading-spinner loading-xs" />
          ) : (
            "회원 탈퇴"
          )}
        </button>
      </div>
    </div>
  );
};

export default SettingsModal;