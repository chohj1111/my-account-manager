"""
Glide Path 엔진: 목표 D-Day까지 잔여 기간에 따라 주식 비중을 비선형으로 조정.

공식: stock_weight = max_stock × (years_left / total_years) ^ EXPONENT
EXPONENT = 0.7 — 초반엔 주식 비중을 높게 유지하다가 D-Day가 다가올수록 급격히 감소.
"""

from dataclasses import dataclass
from datetime import date

EXPONENT = 0.7
MAX_STOCK_WEIGHT = 0.90  # 최대 주식 비중 90%
MIN_STOCK_WEIGHT = 0.05  # D-Day 직전 최소 주식 비중 5%


@dataclass(frozen=True)
class AllocationTarget:
    stock: float  # 0.0 ~ 1.0
    bond: float
    cash: float


def calc_glide_path(start_date: date, target_date: date, today: date | None = None) -> AllocationTarget:
    """
    잔여 기간 비율에 따른 목표 자산 배분 비율 계산.

    Args:
        start_date: 목표 시작일 (goal 생성일 또는 첫 투자일)
        target_date: D-Day
        today: 기준일 (기본값: 오늘)

    Returns:
        AllocationTarget(stock, bond, cash)
    """
    if today is None:
        today = date.today()

    total_days = (target_date - start_date).days
    remaining_days = (target_date - today).days

    if total_days <= 0 or remaining_days <= 0:
        # D-Day 도달 또는 초과 — 안전 자산 최대화
        return AllocationTarget(stock=MIN_STOCK_WEIGHT, bond=0.45, cash=0.50)

    ratio = min(remaining_days / total_days, 1.0)
    stock = round(MAX_STOCK_WEIGHT * (ratio**EXPONENT), 4)
    stock = max(MIN_STOCK_WEIGHT, min(MAX_STOCK_WEIGHT, stock))

    # bond : cash = 7 : 3 비율로 나머지 배분
    remaining = 1.0 - stock
    bond = round(remaining * 0.7, 4)
    cash = round(1.0 - stock - bond, 4)

    return AllocationTarget(stock=stock, bond=bond, cash=cash)
