import { describe, it, expect } from "vitest";
import { formatKRW, formatKRWShort, formatPercent, formatDDay } from "../utils/format";

describe("formatKRW", () => {
  it("천 단위 쉼표 + 원 표시", () => {
    expect(formatKRW(1_234_567)).toBe("1,234,567원");
  });

  it("0원 처리", () => {
    expect(formatKRW(0)).toBe("0원");
  });

  it("음수 금액", () => {
    expect(formatKRW(-500_000)).toBe("-500,000원");
  });
});

describe("formatKRWShort", () => {
  it("5억 정확히", () => {
    expect(formatKRWShort(500_000_000)).toBe("5억");
  });

  it("5.5억 소수점", () => {
    expect(formatKRWShort(550_000_000)).toBe("5.5억");
  });

  it("3000만", () => {
    expect(formatKRWShort(30_000_000)).toBe("3,000만");
  });

  it("1만 미만은 원 단위", () => {
    expect(formatKRWShort(9_999)).toBe("9,999원");
  });
});

describe("formatPercent", () => {
  it("5% 표시", () => {
    expect(formatPercent(0.05)).toBe("5.00%");
  });

  it("소수점 자릿수 지정", () => {
    expect(formatPercent(0.1234, 1)).toBe("12.3%");
  });

  it("0% 처리", () => {
    expect(formatPercent(0)).toBe("0.00%");
  });
});

describe("formatDDay", () => {
  it("2년 3개월", () => {
    expect(formatDDay(27)).toBe("2년 3개월");
  });

  it("정확히 1년", () => {
    expect(formatDDay(12)).toBe("1년");
  });

  it("12개월 미만", () => {
    expect(formatDDay(11)).toBe("11개월");
  });

  it("만료 (음수)", () => {
    expect(formatDDay(-1)).toBe("만료");
  });

  it("0개월", () => {
    expect(formatDDay(0)).toBe("0개월");
  });
});
