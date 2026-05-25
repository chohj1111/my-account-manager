/**
 * 한국 원화 포맷 유틸리티.
 */

/** 원화 표시: 1234567 → "1,234,567원" */
export function formatKRW(amount: number): string {
  return `${amount.toLocaleString("ko-KR")}원`;
}

/** 억/만 단위 축약: 500000000 → "5억", 30000000 → "3,000만" */
export function formatKRWShort(amount: number): string {
  if (amount >= 100_000_000) {
    const eok = amount / 100_000_000;
    return Number.isInteger(eok) ? `${eok}억` : `${eok.toFixed(1)}억`;
  }
  if (amount >= 10_000) {
    const man = Math.round(amount / 10_000);
    return `${man.toLocaleString("ko-KR")}만`;
  }
  return formatKRW(amount);
}

/** 퍼센트 포맷: 0.05 → "5.00%", 소수점 자릿수 지정 가능 */
export function formatPercent(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/** D-Day 포맷: months → "2년 3개월", 12 미만 → "11개월" */
export function formatDDay(months: number): string {
  if (months < 0) return "만료";
  const years = Math.floor(months / 12);
  const remainMonths = months % 12;
  if (years === 0) return `${remainMonths}개월`;
  if (remainMonths === 0) return `${years}년`;
  return `${years}년 ${remainMonths}개월`;
}
