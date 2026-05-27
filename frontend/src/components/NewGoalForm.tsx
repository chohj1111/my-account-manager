import { useState } from "react";
import { createGoal } from "../api/goals";

interface Props {
  onClose: () => void;
  onCreated: () => void;
}

export default function NewGoalForm({ onClose, onCreated }: Props) {
  const [targetPrice, setTargetPrice] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [ltvRatio, setLtvRatio] = useState("60");
  const [currentAsset, setCurrentAsset] = useState("0");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await createGoal({
        target_price: Number(targetPrice),
        target_date: targetDate,
        ltv_ratio: Number(ltvRatio),
        current_total_asset: Number(currentAsset),
      });
      onCreated();
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "오류가 발생했습니다";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>새 목표 설정</h2>
        <form onSubmit={handleSubmit}>
          <label>
            목표 주택가격 (원)
            <input
              type="number"
              value={targetPrice}
              onChange={(e) => setTargetPrice(e.target.value)}
              placeholder="500000000"
              required
              min={1}
            />
          </label>

          <label>
            목표 날짜
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              required
              min={new Date().toISOString().split("T")[0]}
            />
          </label>

          <label>
            LTV 비율 (%)
            <input
              type="number"
              value={ltvRatio}
              onChange={(e) => setLtvRatio(e.target.value)}
              min={10}
              max={90}
            />
          </label>

          <label>
            현재 보유 자산 (원)
            <input
              type="number"
              value={currentAsset}
              onChange={(e) => setCurrentAsset(e.target.value)}
              min={0}
            />
          </label>

          {error && <p className="error">{error}</p>}

          <div className="form-actions">
            <button type="button" onClick={onClose}>
              취소
            </button>
            <button type="submit" disabled={loading}>
              {loading ? "저장 중..." : "목표 저장"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
