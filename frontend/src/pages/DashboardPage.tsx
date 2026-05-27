import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { type GoalSummary, getGoalSummary, listGoals } from "../api/goals";
import GoalSummaryCard from "../components/GoalSummaryCard";
import NewGoalForm from "../components/NewGoalForm";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [summaries, setSummaries] = useState<GoalSummary[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    const goals = await listGoals();
    const results = await Promise.all(goals.map((g) => getGoalSummary(g.id)));
    setSummaries(results);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  function logout() {
    localStorage.removeItem("access_token");
    navigate("/login");
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>My Account Manager</h1>
        <div>
          <button onClick={() => setShowForm(true)}>+ 목표 추가</button>
          <button className="logout" onClick={logout}>
            로그아웃
          </button>
        </div>
      </header>

      {loading ? (
        <p>불러오는 중...</p>
      ) : summaries.length === 0 ? (
        <div className="empty-state">
          <p>등록된 목표가 없습니다.</p>
          <button onClick={() => setShowForm(true)}>첫 목표 만들기</button>
        </div>
      ) : (
        <div className="goal-grid">
          {summaries.map((s) => (
            <GoalSummaryCard key={s.goal.id} summary={s} />
          ))}
        </div>
      )}

      {showForm && (
        <NewGoalForm
          onClose={() => setShowForm(false)}
          onCreated={() => {
            setShowForm(false);
            load();
          }}
        />
      )}
    </div>
  );
}
