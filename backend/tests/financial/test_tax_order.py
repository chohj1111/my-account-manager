"""세금 순서 엔진 단위 테스트."""

from decimal import Decimal

import pytest

from app.models.account import AccountType
from app.services.tax_order import AccountSnapshot, calc_rebalance_orders


def _make_account(
    account_id: str,
    account_type: AccountType,
    stock: int,
    bond: int,
    cash: int,
    is_emergency_fund: bool = False,
) -> AccountSnapshot:
    total = Decimal(stock + bond + cash)
    return AccountSnapshot(
        account_id=account_id,
        account_type=account_type,
        is_emergency_fund=is_emergency_fund,
        total_value=total,
        stock_value=Decimal(stock),
        bond_value=Decimal(bond),
        cash_value=Decimal(cash),
    )


@pytest.mark.financial
class TestTaxOrderEngine:
    def test_buy_order_isa_first(self):
        """매수 시 ISA 계좌가 먼저 선택되어야 함."""
        accounts = [
            _make_account("isa", AccountType.ISA, stock=0, bond=0, cash=10_000_000),
            _make_account("general", AccountType.GENERAL, stock=0, bond=0, cash=10_000_000),
        ]
        # 현재 주식 0%, 목표 50% → 주식 매수 필요
        orders = calc_rebalance_orders(accounts, target_stock=0.5, target_bond=0.35, target_cash=0.15)
        buy_orders = [o for o in orders if o.action == "BUY" and o.asset_class == "STOCK"]
        assert len(buy_orders) > 0
        assert buy_orders[0].account_type == AccountType.ISA

    def test_sell_order_general_first(self):
        """매도 시 GENERAL 계좌가 먼저 선택되어야 함."""
        accounts = [
            _make_account("isa", AccountType.ISA, stock=5_000_000, bond=0, cash=0),
            _make_account("general", AccountType.GENERAL, stock=5_000_000, bond=0, cash=0),
        ]
        # 현재 주식 100%, 목표 10% → 주식 매도 필요
        orders = calc_rebalance_orders(accounts, target_stock=0.1, target_bond=0.63, target_cash=0.27)
        sell_orders = [o for o in orders if o.action == "SELL" and o.asset_class == "STOCK"]
        assert len(sell_orders) > 0
        assert sell_orders[0].account_type == AccountType.GENERAL

    def test_emergency_fund_excluded(self):
        """비상금 계좌는 리밸런싱 대상에서 제외."""
        accounts = [
            _make_account("emergency", AccountType.GENERAL, stock=0, bond=0, cash=5_000_000, is_emergency_fund=True),
            _make_account("normal", AccountType.ISA, stock=0, bond=0, cash=5_000_000),
        ]
        orders = calc_rebalance_orders(accounts, target_stock=0.5, target_bond=0.35, target_cash=0.15)
        order_account_ids = {o.account_id for o in orders}
        assert "emergency" not in order_account_ids

    def test_no_orders_when_balanced(self):
        """이미 목표 배분과 일치하면 주문 없음 (1% 임계값 이내)."""
        accounts = [
            _make_account("isa", AccountType.ISA, stock=5_000_000, bond=3_500_000, cash=1_500_000),
        ]
        orders = calc_rebalance_orders(accounts, target_stock=0.5, target_bond=0.35, target_cash=0.15)
        assert orders == []

    def test_empty_portfolio_returns_no_orders(self):
        """총 자산 0원이면 주문 없음."""
        accounts = [_make_account("isa", AccountType.ISA, stock=0, bond=0, cash=0)]
        orders = calc_rebalance_orders(accounts, target_stock=0.5, target_bond=0.35, target_cash=0.15)
        assert orders == []
