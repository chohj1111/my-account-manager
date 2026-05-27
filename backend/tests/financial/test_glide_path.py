"""Glide Path 엔진 단위 테스트."""

from datetime import date

import pytest

from app.services.glide_path import MIN_STOCK_WEIGHT, calc_glide_path


@pytest.mark.financial
class TestGlidePath:
    def test_early_phase_high_stock(self):
        """투자 초기(잔여 기간 100%)에 주식 비중이 최대에 가까워야 함."""
        start = date(2025, 1, 1)
        target = date(2030, 1, 1)
        today = date(2025, 1, 2)  # 시작 직후
        result = calc_glide_path(start, target, today)
        assert result.stock > 0.85

    def test_midpoint_moderate_stock(self):
        """중반(잔여 50%)에 주식 비중이 초기보다 낮아야 함."""
        start = date(2020, 1, 1)
        target = date(2030, 1, 1)
        today = date(2025, 1, 1)  # 중간
        result = calc_glide_path(start, target, today)
        assert 0.50 < result.stock < 0.85

    def test_dday_reached_min_stock(self):
        """D-Day 도달 시 주식 비중이 최솟값이어야 함."""
        start = date(2020, 1, 1)
        target = date(2025, 1, 1)
        today = date(2025, 1, 1)  # D-Day
        result = calc_glide_path(start, target, today)
        assert result.stock == MIN_STOCK_WEIGHT

    def test_allocation_sums_to_one(self):
        """stock + bond + cash = 1.0 (부동소수점 허용 오차 내)."""
        start = date(2023, 1, 1)
        target = date(2028, 1, 1)
        today = date(2025, 6, 1)
        result = calc_glide_path(start, target, today)
        total = result.stock + result.bond + result.cash
        assert abs(total - 1.0) < 0.001

    def test_stock_decreases_over_time(self):
        """시간이 지날수록 주식 비중이 단조 감소해야 함."""
        start = date(2020, 1, 1)
        target = date(2030, 1, 1)
        weights = []
        for year in range(2020, 2030):
            today = date(year, 6, 1)
            weights.append(calc_glide_path(start, target, today).stock)
        assert weights == sorted(weights, reverse=True)
