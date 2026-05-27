import { api } from "./client";

export interface Goal {
  id: string;
  target_price: number;
  target_date: string;
  max_drawdown: number;
  ltv_ratio: number;
  expected_return_rate: number;
  realestate_growth_rate: number;
  current_total_asset: number;
  created_at: string;
  updated_at: string;
}

export interface GoalSummary {
  goal: Goal;
  d_day_months: number;
  target_equity: number;
  gap: number;
  monthly_investment_needed: number;
  achievability: "ACHIEVABLE" | "RISKY" | "NOT_ACHIEVABLE";
}

export interface GoalCreate {
  target_price: number;
  target_date: string;
  ltv_ratio?: number;
  max_drawdown?: number;
  expected_return_rate?: number;
  realestate_growth_rate?: number;
  current_total_asset?: number;
}

export async function listGoals(): Promise<Goal[]> {
  const res = await api.get<Goal[]>("/goals");
  return res.data;
}

export async function createGoal(body: GoalCreate): Promise<Goal> {
  const res = await api.post<Goal>("/goals", body);
  return res.data;
}

export async function getGoalSummary(goalId: string): Promise<GoalSummary> {
  const res = await api.get<GoalSummary>(`/goals/${goalId}/summary`);
  return res.data;
}
