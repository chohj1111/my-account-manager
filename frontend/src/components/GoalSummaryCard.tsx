import type { GoalSummary } from "../api/goals";
import { formatDDay, formatKRWShort, formatPercent } from "../utils/format";

const ACHIEVABILITY_LABEL = {
  ACHIEVABLE: { text: "달성 가능", color: "#22c55e" },
  RISKY: { text: "주의 필요", color: "#f59e0b" },
  NOT_ACHIEVABLE: { text: "달성 어려움", color: "#ef4444" },
};

interface Props {
  summary: GoalSummary;
}

export default function GoalSummaryCard({ summary }: Props) {
  const { goal, d_day_months, target_equity, gap, monthly_investment_needed, achievability } =
    summary;
  const badge = ACHIEVABILITY_LABEL[achievability];

  return (
    <div className="goal-card">
      <div className="goal-card-header">
        <span className="d-day">D-{formatDDay(d_day_months)}</span>
        <span className="badge" style={{ color: badge.color }}>
          {badge.text}
        </span>
      </div>

      <div className="goal-card-body">
        <div className="stat">
          <span className="label">목표 주택가격</span>
          <span className="value">{formatKRWShort(goal.target_price)}</span>
        </div>
        <div className="stat">
          <span className="label">필요 자기자본 (LTV {goal.ltv_ratio}%)</span>
          <span className="value">{formatKRWShort(target_equity)}</span>
        </div>
        <div className="stat">
          <span className="label">현재 자산</span>
          <span className="value">{formatKRWShort(goal.current_total_asset)}</span>
        </div>
        <div className="stat highlight">
          <span className="label">부족액</span>
          <span className="value">{formatKRWShort(gap)}</span>
        </div>
        <div className="stat">
          <span className="label">월 필요 투자액</span>
          <span className="value">{formatKRWShort(monthly_investment_needed)}</span>
        </div>
        <div className="stat">
          <span className="label">기대수익률</span>
          <span className="value">{formatPercent(goal.expected_return_rate / 100)}</span>
        </div>
      </div>
    </div>
  );
}
