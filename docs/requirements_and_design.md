# Phase 1 MVP 요구사항 명세 및 시스템 설계

> Target-Date 기반 절세형 자산 관리 및 리밸런싱 솔루션

---

## 목차

1. [기능 요구사항 명세](#1-기능-요구사항-명세)
2. [비기능 요구사항 명세](#2-비기능-요구사항-명세)
3. [DB 스키마 설계](#3-db-스키마-설계)
4. [API 엔드포인트 명세](#4-api-엔드포인트-명세)
5. [프론트엔드 화면 구성](#5-프론트엔드-화면-구성)
6. [핵심 알고리즘 로직](#6-핵심-알고리즘-로직)
7. [AI Advisor 모듈](#7-ai-advisor-모듈)
8. [개발 우선순위 및 태스크 분해](#8-개발-우선순위-및-태스크-분해)

---

## 1. 기능 요구사항 명세

### 1.1 사용자 인증 및 프로필

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-001 | 사용자로서 이메일/비밀번호로 회원가입하고 싶다 | 이메일 중복 검사, 비밀번호 8자 이상 |
| FR-002 | 사용자로서 로그인 후 내 데이터를 저장하고 싶다 | JWT 토큰 발급, 세션 유지 |
| FR-003 | 사용자로서 비로그인 상태에서도 계산기를 체험하고 싶다 | 게스트 모드 (로컬스토리지 저장) |

### 1.2 Goal 설정 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-010 | 사용자로서 목표 주택 가격을 입력하고 싶다 | 단위: 만원, 최소 1억 이상 |
| FR-011 | 사용자로서 목표 날짜(D-Day)를 설정하고 싶다 | 최소 1년 후, 최대 30년 후 |
| FR-012 | 사용자로서 허용 MDD를 설정하고 싶다 | 기본값 5%, 슬라이더 UI (1~30%) |
| FR-013 | 사용자로서 현재 보유 총 자산을 입력하고 싶다 | 금액 입력, 자동 LTV 갭 계산 트리거 |
| FR-014 | 사용자로서 D-Day까지 남은 기간이 대시보드에 표시되길 원한다 | D-Day 카운트다운, 월 단위 표시 |
| FR-015 | 사용자로서 부동산 가격 상승률을 설정하여 D-Day 시점의 실질 목표액을 시뮬레이션하고 싶다 | 기본값 연 3%, 0~10% 조절 가능. 목표 금액 미래가치 = 현재가격 × (1+r)^n 으로 재계산하여 표시 |

### 1.3 LTV 저축 가이드 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-020 | 사용자로서 목표 자기자본(주택가격 × 60%)을 자동으로 알고 싶다 | 목표액 = 주택가격 × LTV비율(기본 60%) |
| FR-021 | 사용자로서 목표 달성을 위한 월 최소 투자액을 알고 싶다 | 복리 계산 포함, 기대 수익률 입력 가능 |
| FR-022 | 사용자로서 현재 저축 속도 대비 달성 가능 여부를 알고 싶다 | 트래픽 라이트 (달성 가능 / 위험 / 불가) |

### 1.4 계좌/자산 수동 입력 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-030 | 사용자로서 계좌 유형을 추가하고 싶다 | ISA / 연금저축 / 일반계좌 선택 |
| FR-031 | 사용자로서 계좌별 연간 납입 한도와 현재까지 납입액을 입력하고 싶다 | ISA 2,000만원, 연금저축 900만원 한도 표시 |
| FR-031B | 사용자로서 ISA 계좌의 개설일을 입력하여 만기 예정일과 남은 기간을 알고 싶다 | 만기 = 개설일 + 3년. 만기 6개월 이내 시 AI Advisor가 연금저축 전환 알림 자동 생성 |
| FR-032 | 사용자로서 계좌 안에 ETF 종목을 추가하고 싶다 | 종목명 검색(KRX/네이버 금융 API 연동) 또는 직접 입력, 자산군 선택, 수량, 현재가 |
| FR-033 | 사용자로서 보유 자산의 현재 평가액을 자동 계산하여 보고 싶다 | 평가액 = 수량 × 현재가, 자동 합산 |
| FR-034 | 사용자로서 자산군(주식/채권/현금)별 현재 비중을 파이차트로 보고 싶다 | 실시간 비중 계산 및 시각화 |
| FR-035 | 사용자로서 복수의 계좌를 추가 관리하고 싶다 | 계좌 추가/삭제/편집 |
| FR-036 | 사용자로서 비상금 계좌(투자 제외)를 별도로 설정하고 싶다 | 비상금으로 지정된 계좌/금액은 리밸런싱 계산 대상에서 자동 제외. 대시보드에 '보호 자산'으로 별도 표시 |

### 1.5 Rebalancing Engine 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-040 | 사용자로서 자산군별 목표 비중(Target Weight)을 직접 설정하고 싶다 | 주식/채권/현금 합계 = 100% 검증 |
| FR-041 | 사용자로서 현재 비중과 목표 비중의 차이를 한눈에 보고 싶다 | 갭 테이블: 자산군별 Over/Under 금액 |
| FR-042 | 사용자로서 리밸런싱에 필요한 매수/매도 금액을 종목별로 알고 싶다 | 계좌별 매매 금액 산출 |
| FR-043 | 사용자로서 신규 투자금 입력 시 리밸런싱 우선 배분 금액을 알고 싶다 | 추가투자금 + 기존 포트폴리오 통합 계산 |

### 1.6 Tax-Order Engine 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-050 | 사용자로서 매수 시 세제 혜택이 큰 계좌 순서로 배분 안내를 받고 싶다 | ISA → 연금저축 → 일반 순서 |
| FR-051 | 사용자로서 매도 시 세금이 적게 나오는 계좌 순서로 안내를 받고 싶다 | 일반 → ISA → 연금저축 순서 |
| FR-052 | 사용자로서 각 계좌의 잔여 납입 한도를 확인하고 싶다 | ISA 잔여 한도 = 2,000만원 - 당해 납입액 |
| FR-053 | 사용자로서 세제 혜택 초과 시 자동으로 다음 계좌로 넘어가는 배분을 받고 싶다 | 한도 초과분 자동 이월 배분 |

### 1.7 AI Advisor 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-070 | 사용자로서 현재 포트폴리오 상태에 대한 자연어 진단을 받고 싶다 | 리밸런싱 계산 후 자동 생성, 2~4문장 이내 |
| FR-071 | 사용자로서 D-Day 및 MDD 기준에서 내 포트폴리오가 얼마나 벗어났는지 설명을 받고 싶다 | Glide Path 이탈 여부 + 이탈 폭 언급 |
| FR-072 | 사용자로서 이번 달 취해야 할 행동 1~3가지를 우선순위 순으로 받고 싶다 | 계좌별 납입 한도, 갭, 세제 혜택 기반 액션 아이템 |
| FR-073 | 사용자로서 조언 내용에 근거(왜 이 행동을 해야 하는지)가 포함되길 원한다 | 조언마다 근거 문장 1줄 이상 포함 |
| FR-074 | 사용자로서 조언이 투자 권유가 아닌 정보 제공임을 명확히 인지하고 싶다 | 모든 조언 하단 면책 고지 자동 삽입 |

### 1.8 Glide Path 시각화 모듈

| ID | 유저 스토리 | 인수 기준 |
|----|------------|----------|
| FR-060 | 사용자로서 D-Day까지 연도별 권장 주식/채권 비중 변화를 차트로 보고 싶다 | 선 그래프, X축: 연도, Y축: 비중(%) |
| FR-061 | 사용자로서 현재 내 포트폴리오 비중이 Glide Path와 얼마나 다른지 보고 싶다 | 현재 비중 포인트를 Glide Path 위에 오버레이 |
| FR-062 | 사용자로서 MDD 설정에 따라 Glide Path가 달라지는 것을 보고 싶다 | MDD 값 변경 시 차트 즉시 재계산 |
| FR-063 | 사용자로서 과거 내 실제 비중 궤적을 Glide Path 위에 함께 보고 싶다 | 리밸런싱 이력(rebalancing_history) 기반으로 실제 비중 변화를 점선으로 오버레이. "내가 권장 경로에서 얼마나 이탈했는지" 직관적으로 확인 가능 |

---

---

## 2. 비기능 요구사항 명세

### 2.1 성능

| ID | 항목 | 기준 |
|----|------|------|
| NFR-001 | API 응답 시간 | 리밸런싱 계산 API p95 < 500ms |
| NFR-002 | 페이지 초기 로딩 | FCP < 2초 (3G 기준) |
| NFR-003 | 동시 접속 | MVP 단계 50 동시 사용자 처리 |

### 2.2 보안

| ID | 항목 | 기준 |
|----|------|------|
| NFR-010 | 인증 | JWT (Access 15분, Refresh 7일) |
| NFR-010B | 2단계 인증(2FA) | 계좌 삭제, 비밀번호 변경 등 고위험 행동 시 TOTP(앱 인증) 또는 이메일 OTP 요구 |
| NFR-011 | 데이터 암호화 | HTTPS 필수, DB 비밀번호 bcrypt 해싱 |
| NFR-012 | 입력 검증 | 모든 API 입력 Pydantic 스키마 검증 |
| NFR-013 | 규제 준수 | 특정 종목 추천 문구 없음, 계산 결과는 참고용 면책 고지 필수 |

### 2.3 사용성

| ID | 항목 | 기준 |
|----|------|------|
| NFR-020 | 반응형 UI | 모바일/태블릿/데스크톱 지원 |
| NFR-021 | 접근성 | WCAG 2.1 AA 수준 |
| NFR-022 | 국제화 | 한국어 우선, 숫자 포맷 한국식 (만원 단위) |

### 2.4 운영/유지보수

| ID | 항목 | 기준 |
|----|------|------|
| NFR-030 | 가용성 | MVP 99% uptime 목표 |
| NFR-031 | 로깅 | API 요청/에러 로그 구조화 (JSON) |
| NFR-032 | 배포 | CI/CD 파이프라인 구성 (GitHub Actions) |

---

## 3. DB 스키마 설계

### 설계 원칙

- 세제 혜택 추적을 위해 납입 이력을 연도별로 독립 관리
- 계좌 유형별 한도 정책을 코드 레벨이 아닌 DB에서 관리 가능하도록 설계

### ERD

```
┌─────────────────┐         ┌──────────────────────┐
│     users       │         │       goals           │
├─────────────────┤         ├──────────────────────┤
│ id (PK, UUID)   │ 1     1 │ id (PK, UUID)         │
│ email (UNIQUE)  │─────────│ user_id (FK)          │
│ password_hash   │         │ target_price (BIGINT) │  ← 목표 주택 가격 (현재 기준, 원)
│ created_at      │         │ target_date (DATE)    │  ← D-Day
│ updated_at      │         │ max_drawdown (DECIMAL)│  ← 허용 MDD (%)
└─────────────────┘         │ ltv_ratio (DECIMAL)   │  ← 기본값 0.60
                            │ expected_return_rate  │  ← 기대 수익률 (%)
                            │ realestate_growth_rate│  ← 부동산 연 상승률 (기본값 0.03)
                            │ current_total_asset   │  ← 현재 보유 총 자산
                            │ created_at            │
                            │ updated_at            │
                            └──────────────────────┘
                                        │ 1
                                        │ N
                            ┌──────────────────────┐
                            │      accounts         │
                            ├──────────────────────┤
                            │ id (PK, UUID)         │
                            │ goal_id (FK)          │
                            │ account_type (ENUM)   │  ← 'ISA'|'PENSION'|'GENERAL'
                            │ account_name (VARCHAR)│  ← 사용자 정의 이름
                            │ is_emergency_fund     │  ← BOOL, 비상금 보호 여부 (리밸런싱 제외)
                            │ isa_opened_at (DATE)  │  ← ISA 전용: 개설일 (만기 계산용)
                            │ created_at            │
                            └──────────────────────┘
                                        │ 1
                    ┌───────────────────┼────────────────────┐
                    │ N                 │ N                  │ N
        ┌───────────────────┐  ┌───────────────────┐  ┌──────────────────────┐
        │   account_limits  │  │  annual_deposits  │  │      holdings        │
        ├───────────────────┤  ├───────────────────┤  ├──────────────────────┤
        │ id (PK)           │  │ id (PK)           │  │ id (PK, UUID)        │
        │ account_id (FK)   │  │ account_id (FK)   │  │ account_id (FK)      │
        │ tax_year (INT)    │  │ tax_year (INT)    │  │ ticker_name (VARCHAR)│  ← 자유 입력
        │ annual_limit      │  │ deposited_amount  │  │ asset_class (ENUM)   │  ← STOCK|BOND|CASH
        │  (BIGINT)         │  │  (BIGINT)         │  │ quantity (DECIMAL)   │
        │ benefit_type      │  │ created_at        │  │ current_price (BIGINT│
        │  (VARCHAR)        │  │ updated_at        │  │ updated_at           │
        └───────────────────┘  └───────────────────┘  └──────────────────────┘

┌──────────────────────────────┐     ┌──────────────────────────────┐
│      target_allocations      │     │      rebalancing_history      │
├──────────────────────────────┤     ├──────────────────────────────┤
│ id (PK, UUID)                │     │ id (PK, UUID)                │
│ goal_id (FK)                 │     │ goal_id (FK)                 │
│ asset_class (ENUM)           │     │ calculated_at                │
│ target_weight (DECIMAL)      │     │ new_investment (BIGINT)      │
│ updated_at                   │     │ result_snapshot (JSONB)      │  ← 전체 결과 스냅샷
└──────────────────────────────┘     └──────────────────────────────┘
```

### account_limits 초기 데이터 (세제 정책)

| account_type | annual_limit | tax_deduction_limit | benefit_type |
|-------------|-------------|--------------------:|--------------|
| ISA | 20,000,000 | - | TAX_FREE (비과세) |
| PENSION | 9,000,000 | 6,000,000 | TAX_DEDUCTION (세액공제) |
| GENERAL | 무제한 | - | NONE |

> **참고:** 연금저축 납입 한도(900만원)와 세액공제 혜택 한도(600만원)를 별도 컬럼으로 분리 관리합니다.

---

## 4. API 엔드포인트 명세

### 기술 스택

- **Backend:** Python 3.11 + FastAPI
- **DB:** PostgreSQL + SQLAlchemy (Alembic 마이그레이션)
- **인증:** JWT (python-jose)

### 4.1 인증 API

```
POST   /api/v1/auth/register      회원가입
POST   /api/v1/auth/login         로그인 (JWT 발급)
POST   /api/v1/auth/refresh       토큰 갱신
DELETE /api/v1/auth/logout        로그아웃
```

### 4.2 Goal API

```
POST   /api/v1/goals                        목표 생성
GET    /api/v1/goals/{goal_id}              목표 조회
PUT    /api/v1/goals/{goal_id}              목표 수정
DELETE /api/v1/goals/{goal_id}              목표 삭제
GET    /api/v1/goals/{goal_id}/summary      대시보드 요약 (D-Day, 달성률, 월 필요 투자액)
```

**Goal 생성 요청 바디**

```json
{
  "target_price": 500000000,
  "target_date": "2030-12-31",
  "max_drawdown": 5.0,
  "ltv_ratio": 60.0,
  "expected_return_rate": 5.0,
  "current_total_asset": 50000000
}
```

### 4.3 Account API

```
POST   /api/v1/goals/{goal_id}/accounts           계좌 추가
GET    /api/v1/goals/{goal_id}/accounts           계좌 목록 조회
PUT    /api/v1/accounts/{account_id}              계좌 수정
DELETE /api/v1/accounts/{account_id}              계좌 삭제
GET    /api/v1/accounts/{account_id}/limit-status 납입 한도 현황
```

**납입 한도 현황 응답**

```json
{
  "account_type": "ISA",
  "tax_year": 2026,
  "annual_limit": 20000000,
  "deposited_amount": 5000000,
  "remaining_limit": 15000000,
  "utilization_rate": 25.0
}
```

### 4.4 Holdings API

```
POST   /api/v1/accounts/{account_id}/holdings    보유 자산 추가
GET    /api/v1/accounts/{account_id}/holdings    보유 자산 목록 조회
PUT    /api/v1/holdings/{holding_id}             보유 자산 수정 (수량/현재가 갱신)
DELETE /api/v1/holdings/{holding_id}             보유 자산 삭제
```

**보유 자산 추가 요청 바디**

```json
{
  "ticker_name": "TIGER 미국S&P500",
  "asset_class": "STOCK",
  "quantity": 100,
  "current_price": 15000
}
```

### 4.5 Rebalancing API

```
POST   /api/v1/goals/{goal_id}/rebalance          리밸런싱 계산 실행
GET    /api/v1/goals/{goal_id}/rebalance/history  리밸런싱 이력 조회
```

**리밸런싱 계산 요청 바디**

```json
{
  "new_investment": 1000000,
  "target_allocations": [
    { "asset_class": "STOCK", "target_weight": 60.0 },
    { "asset_class": "BOND",  "target_weight": 30.0 },
    { "asset_class": "CASH",  "target_weight": 10.0 }
  ]
}
```

**리밸런싱 계산 응답**

```json
{
  "summary": {
    "total_portfolio_value": 55000000,
    "current_allocation": {
      "STOCK": { "amount": 38500000, "weight": 70.0 },
      "BOND":  { "amount": 13750000, "weight": 25.0 },
      "CASH":  { "amount": 2750000,  "weight": 5.0  }
    },
    "target_allocation": {
      "STOCK": { "target_weight": 60.0, "target_amount": 33000000, "gap": -5500000 },
      "BOND":  { "target_weight": 30.0, "target_amount": 16500000, "gap": 2750000  },
      "CASH":  { "target_weight": 10.0, "target_amount": 5500000,  "gap": 2750000  }
    }
  },
  "tax_ordered_actions": [
    {
      "action": "BUY",
      "asset_class": "BOND",
      "account_id": "uuid-isa",
      "account_type": "ISA",
      "amount": 2750000,
      "reason": "ISA 잔여 한도 내 매수 우선 배분"
    },
    {
      "action": "SELL",
      "asset_class": "STOCK",
      "account_id": "uuid-general",
      "account_type": "GENERAL",
      "amount": 5500000,
      "reason": "일반계좌 우선 매도 (연간 250만원 양도차익 공제 적용)"
    }
  ],
  "warnings": [
    {
      "level": "INFO",
      "message": "ISA 연간 납입 한도 90% 이상 소진. 잔여 한도: 1,500,000원"
    }
  ],
  "disclaimer": "이 계산 결과는 참고용이며 투자 권유가 아닙니다."
}
```

### 4.6 AI Advisor API

```
POST   /api/v1/goals/{goal_id}/advisor/diagnose    현재 상태 진단 및 조언 생성
GET    /api/v1/goals/{goal_id}/advisor/history     과거 조언 이력 조회
```

**진단 요청 바디** — 리밸런싱 계산 결과를 그대로 전달

```json
{
  "rebalance_result_id": "uuid-rebalance-snapshot"
}
```

**진단 응답**

```json
{
  "diagnosis": {
    "summary": "현재 주식 비중(70%)이 Glide Path 권장 비중(60%)보다 10% 높습니다. D-Day까지 4년이 남아 있어 지금이 비중을 낮추기 적절한 시점입니다.",
    "glide_path_status": {
      "status": "OVERWEIGHT_STOCK",
      "deviation_pct": 10.0,
      "message": "주식 비중 10% 초과 — 채권/현금 리밸런싱 권장"
    },
    "tax_limit_status": {
      "isa_utilization_pct": 25.0,
      "pension_tax_effective_remaining": 4500000,
      "message": "ISA 잔여 납입 한도 1,500만원 — 이달 추가 납입 여력 충분"
    },
    "ltv_status": {
      "achievability": "ACHIEVABLE",
      "monthly_gap": 200000,
      "message": "현재 저축 속도로 목표 달성 가능. 월 20만원 여유 있음"
    }
  },
  "action_items": [
    {
      "priority": 1,
      "action": "ISA 계좌에 이달 추가 납입 (권장: 100만원)",
      "reason": "ISA 비과세 한도(연 2,000만원) 잔여분이 1,500만원 남아 있어 세제 혜택 활용 여지가 큽니다.",
      "account_type": "ISA",
      "suggested_amount": 1000000
    },
    {
      "priority": 2,
      "action": "주식 비중을 60%로 낮추기 위해 채권 ETF 매수",
      "reason": "D-Day 4년 기준 Glide Path 권장 주식 비중은 60%입니다. 현재 70%로 10% 초과 상태입니다.",
      "account_type": "ISA",
      "suggested_amount": 5500000
    },
    {
      "priority": 3,
      "action": "연금저축 세액공제 잔여 구간(450만원) 납입 검토",
      "reason": "연금저축 세액공제 한도(연 600만원) 중 450만원이 남아 있습니다. 납입 시 최대 67.5만원 세금 환급 효과가 있습니다.",
      "account_type": "PENSION",
      "suggested_amount": 4500000
    }
  ],
  "disclaimer": "위 내용은 사용자가 입력한 데이터를 기반으로 한 정보 제공이며, 투자 권유가 아닙니다.",
  "generated_at": "2026-05-25T10:00:00Z"
}
```

### 4.7 Glide Path API

```
GET    /api/v1/goals/{goal_id}/glide-path    Glide Path 데이터 조회
```

**응답**

```json
{
  "data_points": [
    { "date": "2026-01-01", "years_to_goal": 4.0, "stock_weight": 60, "bond_weight": 30, "cash_weight": 10 },
    { "date": "2027-01-01", "years_to_goal": 3.0, "stock_weight": 50, "bond_weight": 38, "cash_weight": 12 },
    { "date": "2028-01-01", "years_to_goal": 2.0, "stock_weight": 35, "bond_weight": 48, "cash_weight": 17 },
    { "date": "2029-01-01", "years_to_goal": 1.0, "stock_weight": 20, "bond_weight": 55, "cash_weight": 25 },
    { "date": "2030-01-01", "years_to_goal": 0.0, "stock_weight": 10, "bond_weight": 45, "cash_weight": 45 }
  ],
  "current_position": {
    "date": "2026-05-25",
    "actual_stock_weight": 70.0,
    "recommended_stock_weight": 60.0,
    "deviation": 10.0
  }
}
```

---

## 5. 프론트엔드 화면 구성

### 기술 스택

- **Frontend:** React 18 + TypeScript (Vite)
- **차트:** Recharts
- **스타일:** Tailwind CSS

### 페이지/컴포넌트 트리

```
App (React Router)
├── /                               LandingPage
│   ├── HeroSection
│   ├── FeatureHighlights
│   └── GuestTrialCTA
│
├── /auth/register                  RegisterPage
├── /auth/login                     LoginPage
│
└── /app  (인증 필요, AppLayout)
    ├── /app/dashboard              DashboardPage          ← 메인 허브
    │   ├── GoalSummaryCard
    │   │   ├── DdayCountdown
    │   │   ├── AchievementProgressBar
    │   │   └── MonthlyInvestmentGuide
    │   ├── PortfolioSnapshotCard
    │   │   ├── AllocationPieChart
    │   │   └── GlidepathDeviationBadge
    │   └── QuickActionPanel
    │       ├── RebalanceNowButton
    │       └── UpdatePricesButton
    │
    ├── /app/goal/setup             GoalSetupPage          ← 목표 설정
    │   ├── TargetPriceInput
    │   ├── TargetDatePicker
    │   ├── MddSlider
    │   ├── LtvRatioSelector
    │   ├── ExpectedReturnInput
    │   └── GoalSummaryPreview
    │
    ├── /app/accounts               AccountsPage           ← 계좌/자산 관리
    │   ├── AccountList
    │   │   └── AccountCard (반복)
    │   │       ├── AccountHeader (유형 뱃지, 납입 한도 진행바)
    │   │       ├── HoldingsList
    │   │       │   └── HoldingRow (반복)
    │   │       │       ├── TickerName
    │   │       │       ├── AssetClassBadge
    │   │       │       ├── QuantityInput
    │   │       │       ├── PriceInput
    │   │       │       └── EvaluationAmount
    │   │       └── AddHoldingForm
    │   └── AddAccountModal
    │       ├── AccountTypeSelector
    │       └── AccountNameInput
    │
    ├── /app/rebalance              RebalancePage          ← 리밸런싱 계산
    │   ├── TargetAllocationEditor
    │   │   ├── AllocationSliderGroup (주식/채권/현금)
    │   │   └── AllocationSumValidator (합계 100% 검증)
    │   ├── NewInvestmentInput
    │   ├── RebalanceCalculateButton
    │   └── RebalanceResultPanel (계산 후 노출)
    │       ├── CurrentVsTargetTable
    │       │   └── GapIndicator (▲매수필요 / ▼매도필요)
    │       ├── TaxOrderActionList
    │       │   └── ActionCard (반복)
    │       │       ├── AccountTypeBadge
    │       │       ├── ActionType (BUY/SELL)
    │       │       ├── Amount
    │       │       └── TaxReasonTooltip
    │       └── DisclaimerNotice
    │
    ├── /app/glide-path             GlidepathPage          ← Glide Path 차트
    │   ├── GlidepathChart (Recharts LineChart)
    │   │   ├── StockWeightLine
    │   │   ├── BondWeightLine
    │   │   ├── CashWeightLine
    │   │   └── CurrentPositionMarker
    │   └── GlidepathTable
    │       └── YearlyAllocationRow (반복)
    │
    ├── /app/savings-guide          SavingsGuidePage       ← LTV 저축 가이드
    │   ├── LtvCalculatorPanel
    │   │   ├── TargetEquityDisplay (주택가격 × LTV)
    │   │   ├── CurrentAssetDisplay
    │   │   ├── GapDisplay
    │   │   └── MonthlyInvestmentCalculator
    │   └── AchievabilityIndicator (TrafficLight)
    │
    └── /app/advisor                AdvisorPage            ← AI 조언 (신규)
        ├── DiagnosisSummaryCard
        │   ├── GlidepathStatusBadge  (OVERWEIGHT / ON_TRACK / UNDERWEIGHT)
        │   ├── TaxLimitStatusBadge   (한도 여유 / 주의 / 소진)
        │   └── LtvStatusBadge        (달성 가능 / 위험 / 불가)
        ├── ActionItemList
        │   └── ActionItemCard (반복, priority 순 정렬)
        │       ├── PriorityBadge     (1 / 2 / 3)
        │       ├── ActionDescription
        │       ├── ReasonText        (왜 이 행동인지 근거)
        │       ├── AccountTypeBadge
        │       └── SuggestedAmount
        ├── RegenerateButton          (재진단 요청)
        ├── AdvisorHistoryPanel       (과거 조언 이력 접기/펼치기)
        └── DisclaimerNotice
```

---

## 6. 핵심 알고리즘 로직

### 6.1 Rebalancing Engine

```python
def calculate_rebalancing(goal_id, new_investment, target_allocations):
    """
    1단계: 현재 포트폴리오 집계
    """
    accounts = get_accounts_by_goal(goal_id)
    holdings = get_all_holdings(accounts)

    total_value = sum(h.quantity * h.current_price for h in holdings) + new_investment

    current_by_class = {}
    for asset_class in ['STOCK', 'BOND', 'CASH']:
        class_value = sum(
            h.quantity * h.current_price
            for h in holdings if h.asset_class == asset_class
        )
        current_by_class[asset_class] = {
            'amount': class_value,
            'weight': (class_value / (total_value - new_investment)) * 100
        }

    """
    2단계: 목표 대비 갭 계산
    """
    gaps = {}
    for alloc in target_allocations:
        target_amount = total_value * (alloc.target_weight / 100)
        current_amount = current_by_class[alloc.asset_class]['amount']
        gaps[alloc.asset_class] = {
            'target_amount': target_amount,
            'current_amount': current_amount,
            'gap': target_amount - current_amount  # 양수=매수필요, 음수=매도필요
        }

    """
    3단계: Tax-Order Engine 호출하여 계좌별 배분
    """
    actions = tax_order_engine(accounts, gaps, new_investment)

    return RebalanceResult(gaps=gaps, actions=actions)
```

### 6.2 Tax-Order Engine

#### 한국 세제 혜택 구조 (2026년 기준)

| 계좌 | 납입 한도 | 세제 혜택 | 매수 우선순위 | 매도 우선순위 |
|------|----------|----------|:------------:|:------------:|
| ISA (중개형) | 연 2,000만원 | 비과세 (일반형 200만원 / 서민형 400만원 초과 9.9% 분리과세) | 1순위 | 2순위 |
| 연금저축 | 연 900만원 (공제 효과: 600만원) | 세액공제 15% or 12% | 2순위 | 3순위 (최후) |
| 일반계좌 | 무제한 | 없음 (양도차익 연 250만원 공제) | 3순위 | 1순위 |

```python
BUY_PRIORITY  = ['ISA', 'PENSION', 'GENERAL']  # 매수: 세제 혜택 순
SELL_PRIORITY = ['GENERAL', 'ISA', 'PENSION']  # 매도: 세금 부담 낮은 순

def tax_order_engine(accounts, gaps, new_investment):
    actions = []
    current_year = get_current_tax_year()

    # 계좌별 잔여 납입 한도 계산
    account_limits = {}
    for account in accounts:
        if account.type == 'ISA':
            deposited = get_annual_deposited(account.id, current_year)
            account_limits[account.id] = {
                'remaining': max(0, 20_000_000 - deposited),
                'type': 'ISA'
            }
        elif account.type == 'PENSION':
            deposited = get_annual_deposited(account.id, current_year)
            account_limits[account.id] = {
                'remaining': max(0, 9_000_000 - deposited),
                'tax_effective_remaining': max(0, 6_000_000 - deposited),
                'type': 'PENSION'
            }
        else:
            account_limits[account.id] = {
                'remaining': float('inf'),
                'type': 'GENERAL'
            }

    # 매수 배분: ISA → 연금저축 → 일반 순으로 한도 내 배분
    buy_needs = {k: v['gap'] for k, v in gaps.items() if v['gap'] > 0}
    for asset_class, amount_needed in buy_needs.items():
        remaining = amount_needed
        for account_type in BUY_PRIORITY:
            if remaining <= 0:
                break
            for account in [a for a in accounts if a.type == account_type]:
                allocatable = min(remaining, account_limits[account.id]['remaining'])
                if allocatable > 0:
                    actions.append(Action(
                        action='BUY',
                        asset_class=asset_class,
                        account_id=account.id,
                        account_type=account_type,
                        amount=allocatable,
                        reason=generate_buy_reason(account_type, account_limits[account.id])
                    ))
                    account_limits[account.id]['remaining'] -= allocatable
                    remaining -= allocatable

    # 매도 배분: 일반 → ISA → 연금저축 순으로 배분
    sell_needs = {k: abs(v['gap']) for k, v in gaps.items() if v['gap'] < 0}
    for asset_class, amount_to_sell in sell_needs.items():
        remaining = amount_to_sell
        for account_type in SELL_PRIORITY:
            if remaining <= 0:
                break
            for account in [a for a in accounts if a.type == account_type]:
                available = get_holding_value(account.id, asset_class)
                sell_amount = min(remaining, available)
                if sell_amount > 0:
                    actions.append(Action(
                        action='SELL',
                        asset_class=asset_class,
                        account_id=account.id,
                        account_type=account_type,
                        amount=sell_amount,
                        reason=generate_sell_reason(account_type)
                    ))
                    remaining -= sell_amount

    return actions
```

#### 매수/매도 의사결정 플로우

```
[매수 의사결정]
신규 투자금 또는 매수 필요 금액 발생
        │
        ▼
ISA 잔여 납입 한도 > 0?
    YES → ISA에 min(필요금액, ISA잔여한도) 배분
    NO  ↓
        ▼
연금저축 세액공제 유효 구간(연 600만원) 내 잔여?
    YES → 연금저축에 배분 (실질 절세 효과 최대)
    NO  → 연금저축 600~900만원 구간 배분 (효과 감소)
        ↓
잔여분 → 일반계좌 배분

[매도 의사결정]
매도 필요 금액 발생
        │
        ▼
일반계좌에 해당 자산 보유 중?
    YES → 일반계좌 우선 매도 (연 250만원 양도차익 공제 활용)
    NO  ↓
        ▼
ISA 내 해당 자산 보유 중?
    YES → ISA 내 자산 교체 (손익 통산, 비과세 유지)
    NO  ↓
        ▼
연금저축 최후 매도 + 페널티 경고 표시
(중도 해지 시 기타소득세 16.5% + 세액공제 추징)
```

### 6.3 Glide Path 알고리즘

```python
"""
설계 원칙:
- MDD → 최대 주식 비중 결정: MDD 5% → 초기 주식 비중 60% 상한
- 비선형 감소: 초반 완만, 목표 1~2년 전 급격 보수화
- 잔여 비중(채권:현금) = 7:3 배분
"""

def calculate_glide_path(goal):
    today = date.today()
    max_stock_weight = min(95, goal.max_drawdown * 12)  # MDD → 주식 상한 (경험적 공식)
    min_stock_weight = 10                                # 목표 시점 최소 주식 비중

    data_points = []
    current = today.replace(month=1, day=1)

    while current <= goal.target_date:
        years_remaining = (goal.target_date - current).days / 365.25
        total_years = (goal.target_date - today).days / 365.25

        if years_remaining <= 0:
            stock_weight = min_stock_weight
        else:
            # 지수 0.7: 초반 완만, 후반 급격 감소
            ratio = (years_remaining / total_years) ** 0.7
            stock_weight = round(min_stock_weight + (max_stock_weight - min_stock_weight) * ratio)

        remaining = 100 - stock_weight
        bond_weight = round(remaining * 0.70)
        cash_weight = 100 - stock_weight - bond_weight

        data_points.append(GlidepathDataPoint(
            date=current,
            years_to_goal=round(years_remaining, 1),
            stock_weight=stock_weight,
            bond_weight=bond_weight,
            cash_weight=cash_weight
        ))
        current = current.replace(year=current.year + 1)

    return data_points
```

### 6.4 LTV 저축 가이드 계산

```python
def calculate_monthly_investment_needed(goal, current_asset):
    years = (goal.target_date - date.today()).days / 365.25
    months = years * 12

    # [보완] 부동산 가격 상승률 반영: 실질 목표액 = 현재가 × (1 + 상승률)^년수
    real_target_price = goal.target_price * ((1 + goal.realestate_growth_rate) ** years)
    target_equity = real_target_price * (goal.ltv_ratio / 100)

    # [보완] Glide Path 기반 보수적 기대 수익률 적용
    # 목표 시점에 가까울수록 채권/현금 비중이 높아져 실효 수익률이 낮아짐
    # 현재 주식비중 × 주식기대수익 + 채권비중 × 채권기대수익 + 현금비중 × 0 으로 가중 평균
    glide_stock_weight = calculate_current_glide_stock_weight(goal)  # 0.0 ~ 1.0
    effective_annual_rate = (
        glide_stock_weight * goal.expected_return_rate / 100 +
        (1 - glide_stock_weight) * 0.035  # 채권 기대 수익률 3.5% 고정
    )
    monthly_rate = effective_annual_rate / 12

    # PMT = (FV - PV × (1+r)^n) × r / ((1+r)^n - 1)
    # FV: 실질 목표 자기자본, PV: 현재 자산, r: 월 수익률, n: 남은 개월 수
    if monthly_rate == 0:
        monthly_investment = (target_equity - current_asset) / months
    else:
        future_value_current = current_asset * ((1 + monthly_rate) ** months)
        remaining_gap = target_equity - future_value_current
        if remaining_gap <= 0:
            monthly_investment = 0  # 현재 자산만으로 달성 가능
        else:
            monthly_investment = remaining_gap * monthly_rate / (((1 + monthly_rate) ** months) - 1)

    achievability = (
        'ACHIEVABLE'     if monthly_investment < 5_000_000  else
        'RISKY'          if monthly_investment < 10_000_000 else
        'NOT_ACHIEVABLE'
    )

    return SavingsGuide(
        nominal_target_price=goal.target_price,
        real_target_price=round(real_target_price),      # 물가 반영 실질 목표가
        target_equity=round(target_equity),
        current_asset=current_asset,
        gap=round(target_equity - current_asset),
        months_remaining=round(months),
        effective_annual_rate_pct=round(effective_annual_rate * 100, 2),
        monthly_investment_needed=round(monthly_investment),
        achievability=achievability
    )
```

---

## 7. AI Advisor 모듈

### 7.1 설계 원칙

- **규제 준수:** Claude API를 통해 자연어 조언을 생성하되, 프롬프트에 "특정 종목 추천 금지" 제약을 하드코딩
- **결정론적 입력:** AI에게 자유로운 판단을 맡기지 않고, 계산 엔진의 출력값(숫자)을 구조화하여 전달 → 조언의 일관성 확보
- **투명성:** 모든 조언에 근거 수치를 포함하여 사용자가 직접 검증 가능하게 함

### 7.2 아키텍처

```
[Rebalancing Engine 결과]
[Tax-Order Engine 결과]      →  [Context Builder]  →  [Claude API]  →  [조언 파싱]  →  [응답 반환]
[Glide Path 이탈 계산]
[LTV 달성 가능 여부]
```

- **Claude API 모델:** `claude-haiku-4-5-20251001` (빠른 응답, 저비용)
- **캐싱:** 동일 `rebalance_result_id`에 대한 중복 호출 방지 (DB 저장 후 재사용)

### 7.3 Advisor 알고리즘 의사코드

```python
import anthropic

SYSTEM_PROMPT = """
당신은 한국의 절세형 자산 관리 보조 도구입니다.
사용자의 포트폴리오 계산 결과를 바탕으로 이달 취해야 할 행동을 안내합니다.

반드시 지켜야 할 규칙:
1. 특정 종목(ETF 포함)을 직접 추천하지 않습니다.
2. 모든 조언은 사용자가 입력한 데이터 기반의 계산 결과임을 명시합니다.
3. 조언은 구체적인 금액과 계좌 유형을 포함하되, 최종 판단은 사용자에게 맡깁니다.
4. 응답은 반드시 JSON 형식으로만 반환합니다.
"""

def generate_advice(goal, rebalance_result, glide_path_deviation, ltv_status):
    """
    1단계: 컨텍스트 구성 (숫자 기반, AI의 자의적 해석 최소화)
    """
    context = {
        "goal": {
            "target_price_만원": goal.target_price // 10000,
            "d_day": str(goal.target_date),
            "years_remaining": round((goal.target_date - date.today()).days / 365.25, 1),
            "max_drawdown_pct": goal.max_drawdown
        },
        "portfolio_status": {
            "total_value_만원": rebalance_result.total_value // 10000,
            "current_stock_weight_pct": rebalance_result.current_allocation['STOCK']['weight'],
            "recommended_stock_weight_pct": glide_path_deviation['recommended_stock'],
            "stock_deviation_pct": glide_path_deviation['deviation'],
            "glide_path_status": glide_path_deviation['status']  # OVERWEIGHT/ON_TRACK/UNDERWEIGHT
        },
        "tax_account_status": {
            "isa_remaining_만원": rebalance_result.isa_remaining // 10000,
            "pension_tax_effective_remaining_만원": rebalance_result.pension_tax_remaining // 10000,
            "isa_utilization_pct": rebalance_result.isa_utilization_pct
        },
        "ltv_status": {
            "achievability": ltv_status.achievability,
            "monthly_investment_needed_만원": ltv_status.monthly_investment_needed // 10000,
            "months_remaining": ltv_status.months_remaining
        },
        "rebalancing_actions": [
            {
                "action": a.action,
                "asset_class": a.asset_class,
                "account_type": a.account_type,
                "amount_만원": a.amount // 10000
            }
            for a in rebalance_result.tax_ordered_actions
        ]
    }

    """
    2단계: Claude API 호출
    """
    client = anthropic.Anthropic()

    user_message = f"""
다음은 사용자의 현재 자산 관리 현황입니다. 이를 바탕으로 이달 취해야 할 행동 1~3가지를 우선순위 순으로 작성해주세요.

현황 데이터:
{json.dumps(context, ensure_ascii=False, indent=2)}

응답 형식 (JSON):
{{
  "summary": "2~3문장의 현재 상황 진단",
  "action_items": [
    {{
      "priority": 1,
      "action": "구체적 행동 내용",
      "reason": "이 행동을 해야 하는 이유 (수치 포함)",
      "account_type": "ISA|PENSION|GENERAL",
      "suggested_amount": 금액(원, 숫자)
    }}
  ]
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    """
    3단계: 응답 파싱 및 면책 고지 삽입
    """
    advice = json.loads(response.content[0].text)
    advice['disclaimer'] = "위 내용은 사용자가 입력한 데이터를 기반으로 한 정보 제공이며, 투자 권유가 아닙니다."
    advice['generated_at'] = datetime.utcnow().isoformat()

    return advice
```

### 7.4 대시보드 통합 (요약 카드)

대시보드(`/app/dashboard`)에 Advisor 결과의 핵심만 요약하여 표시합니다.

```
┌─────────────────────────────────────────┐
│  이달의 조언 (AI Advisor)                │
├─────────────────────────────────────────┤
│  [1] ISA 100만원 추가 납입               │
│      → ISA 비과세 한도 잔여 1,500만원    │
│  [2] 채권 ETF 매수로 주식 비중 10% 축소  │
│      → Glide Path 기준 초과 상태        │
│                                         │
│  [전체 조언 보기 →]                      │
│                                         │
│  ⚠ 이 내용은 정보 제공이며 투자 권유     │
│    가 아닙니다.                          │
└─────────────────────────────────────────┘
```

---

## 8. 개발 우선순위 및 태스크 분해

### Phase 1-A: 기반 구축 (Week 1~2)

| 태스크 | 우선순위 | 예상 공수 |
|-------|---------|----------|
| DB 스키마 생성 (Alembic 마이그레이션) | P0 | 0.5일 |
| FastAPI 프로젝트 구조 초기화 | P0 | 0.5일 |
| 인증 API (회원가입/로그인/JWT) | P0 | 1일 |
| React 프로젝트 구조 초기화 (Vite + TS) | P0 | 0.5일 |
| 공통 컴포넌트 (Layout, Button, Input) | P1 | 1일 |
| Goal CRUD API + 화면 | P0 | 1.5일 |

### Phase 1-B: 핵심 데이터 입력 (Week 3~4)

| 태스크 | 우선순위 | 예상 공수 |
|-------|---------|----------|
| Account CRUD API + 화면 | P0 | 1일 |
| Holdings CRUD API + 화면 | P0 | 1.5일 |
| 납입 한도 현황 계산 및 표시 | P0 | 0.5일 |
| 자산군별 현재 비중 계산 및 파이차트 | P1 | 1일 |

### Phase 1-C: 핵심 엔진 (Week 5~6)

| 태스크 | 우선순위 | 예상 공수 |
|-------|---------|----------|
| Rebalancing Engine 구현 + 단위 테스트 | P0 | 2일 |
| Tax-Order Engine 구현 + 단위 테스트 | P0 | 2일 |
| Rebalancing 결과 화면 | P0 | 1.5일 |
| 세제 경고 메시지 시스템 | P1 | 0.5일 |

### Phase 1-D: 시각화 및 가이드 (Week 7~8)

| 태스크 | 우선순위 | 예상 공수 |
|-------|---------|----------|
| Glide Path 알고리즘 구현 | P1 | 1일 |
| Glide Path 차트 (Recharts) | P1 | 1.5일 |
| LTV 저축 가이드 화면 | P1 | 1일 |
| AI Advisor Context Builder 구현 | P1 | 1일 |
| Claude API 연동 + 응답 파싱 | P1 | 1일 |
| Advisor 페이지 및 ActionItemCard 컴포넌트 | P1 | 1.5일 |
| 대시보드 Advisor 요약 카드 통합 | P1 | 0.5일 |

### Phase 1-E: 품질 및 배포 (Week 9~10)

| 태스크 | 우선순위 | 예상 공수 |
|-------|---------|----------|
| 면책 고지 및 규제 대응 문구 삽입 | P0 | 0.5일 |
| 반응형 CSS 작업 | P1 | 1일 |
| E2E 테스트 주요 시나리오 | P1 | 1일 |
| Docker Compose 구성 + GitHub Actions CI | P1 | 1일 |
| 서버 배포 (Railway 또는 Fly.io 권장) | P1 | 0.5일 |

---

> **면책 고지:** 이 서비스는 사용자가 직접 입력한 데이터를 기반으로 계산 결과를 제공하는 유틸리티 툴입니다. 특정 종목 투자를 권유하지 않으며, 모든 계산 결과는 참고용으로만 활용하시기 바랍니다.
