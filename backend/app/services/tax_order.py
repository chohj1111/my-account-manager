"""
세금 순서 엔진 (Tax-Order Engine).

매수 순서: ISA → PENSION → GENERAL  (절세 계좌 우선 채우기)
매도 순서: GENERAL → ISA → PENSION  (과세 계좌 먼저 비우기)

비상금 계좌(is_emergency_fund=True)는 리밸런싱 대상에서 제외.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.models.account import AccountType


@dataclass
class AccountSnapshot:
    account_id: str
    account_type: AccountType
    is_emergency_fund: bool
    total_value: Decimal  # 현재 평가액 (원)
    stock_value: Decimal
    bond_value: Decimal
    cash_value: Decimal


@dataclass
class RebalanceOrder:
    account_id: str
    account_type: AccountType
    action: str  # "BUY" | "SELL"
    asset_class: str  # "STOCK" | "BOND" | "CASH"
    amount: Decimal  # 원


_BUY_ORDER = [AccountType.ISA, AccountType.PENSION, AccountType.GENERAL]
_SELL_ORDER = [AccountType.GENERAL, AccountType.ISA, AccountType.PENSION]


def calc_rebalance_orders(
    accounts: list[AccountSnapshot],
    target_stock: float,
    target_bond: float,
    target_cash: float,
) -> list[RebalanceOrder]:
    """
    현재 포트폴리오와 목표 배분 비율을 비교하여 리밸런싱 주문 목록 생성.

    Args:
        accounts: 전체 계좌 스냅샷 목록
        target_stock/bond/cash: Glide Path 목표 비율 (합계 = 1.0)

    Returns:
        RebalanceOrder 목록 (세금 순서 적용)
    """
    # 비상금 계좌 제외
    active = [a for a in accounts if not a.is_emergency_fund]

    total = sum(a.total_value for a in active)
    if total == 0:
        return []

    current_stock = sum(a.stock_value for a in active)
    current_bond = sum(a.bond_value for a in active)
    current_cash = sum(a.cash_value for a in active)

    target_stock_val = total * Decimal(str(target_stock))
    target_bond_val = total * Decimal(str(target_bond))
    target_cash_val = total * Decimal(str(target_cash))

    delta_stock = target_stock_val - current_stock
    delta_bond = target_bond_val - current_bond
    delta_cash = target_cash_val - current_cash

    orders: list[RebalanceOrder] = []

    def _allocate(delta: Decimal, asset_class: str, account_order: list[AccountType]) -> None:
        remaining = abs(delta)
        action = "BUY" if delta > 0 else "SELL"
        for acc_type in account_order:
            for acc in sorted(active, key=lambda a: a.account_type != acc_type):
                if acc.account_type != acc_type or remaining <= 0:
                    continue
                alloc = min(remaining, acc.total_value)
                if alloc > 0:
                    orders.append(
                        RebalanceOrder(
                            account_id=acc.account_id,
                            account_type=acc.account_type,
                            action=action,
                            asset_class=asset_class,
                            amount=alloc,
                        )
                    )
                    remaining -= alloc

    threshold = total * Decimal("0.01")  # 1% 미만 차이는 무시

    if abs(delta_stock) > threshold:
        _allocate(delta_stock, "STOCK", _BUY_ORDER if delta_stock > 0 else _SELL_ORDER)
    if abs(delta_bond) > threshold:
        _allocate(delta_bond, "BOND", _BUY_ORDER if delta_bond > 0 else _SELL_ORDER)
    if abs(delta_cash) > threshold:
        _allocate(delta_cash, "CASH", _BUY_ORDER if delta_cash > 0 else _SELL_ORDER)

    return orders
