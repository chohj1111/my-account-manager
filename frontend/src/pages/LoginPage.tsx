import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        const tokens = await login(email, password);
        localStorage.setItem("access_token", tokens.access_token);
        navigate("/");
      } else {
        await register(email, password);
        const tokens = await login(email, password);
        localStorage.setItem("access_token", tokens.access_token);
        navigate("/");
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "오류가 발생했습니다";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <h1>My Account Manager</h1>
      <p className="subtitle">Target-Date 기반 절세 자산 관리</p>

      <form onSubmit={handleSubmit} className="auth-form">
        <h2>{mode === "login" ? "로그인" : "회원가입"}</h2>

        <label>
          이메일
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "처리 중..." : mode === "login" ? "로그인" : "가입하기"}
        </button>
      </form>

      <button
        className="mode-toggle"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
      >
        {mode === "login" ? "계정이 없으신가요? 회원가입" : "이미 계정이 있으신가요? 로그인"}
      </button>
    </div>
  );
}
