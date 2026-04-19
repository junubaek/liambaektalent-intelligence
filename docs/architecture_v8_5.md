# ANTIGRAVITY Talent Intelligence OS
## 기술 아키텍처 및 과학적 설계 원리

**V8.5 | 2026년 4월 | 내부 기술 문서**

*이 문서의 목적*
이 페이퍼는 Antigravity Talent Intelligence OS의 단순한 기능 설명서가 아니다. "왜 이 기술을 선택했는가", "어떤 수학적 원리로 작동하는가", "어떤 문제를 해결하기 위해 이 설계를 택했는가"를 설명하는 기술 철학 문서다.

*현재 완료 상태*
- 2,886명 SQLite 복구 / 2,366명 Neo4j 재파싱
- 동명이인 완전 분리 (복합 식별자 MERGE)
- L1/L2 Ontology Vector Fallback 완성
- UNIFIED_GRAVITY_FIELD + 노이즈 페널티 적용
- 딥 리페어 13개 노드 완료
- system_auditor.py 자동화 + 슬랙 알림

---

## 1장. 왜 이 아키텍처인가?
대부분의 이력서 검색 시스템은 키워드 매칭(Keyword Matching)에 머문다. "자금관리"라는 단어가 있으면 나오고, 없으면 안 나온다. 이는 두 가지 치명적인 실패를 낳는다.

| 문제 | 키워드 매칭의 한계 | V8.5의 해결 |
|---|---|---|
| False Negative | 이력서에 "Treasury"라고 영문 표기 → 자금관리 검색에 안 나옴 | 그래프 엣지 + 벡터 의미망으로 뉘앙스 포착 |
| False Positive | "기획"이라는 단어가 있는 모든 사람 → 서비스기획/전략기획/인사기획 혼재 | CANONICAL_MAP 498개 노드로 직무 정밀 구분 |
| 랭킹 왜곡 | 이것저것 다 해본 20년차가 항상 1위 | 노이즈 페널티로 스페셜리스트 보호 |
| 동명이인 오염 | 김민수(마케터)와 김민수(개발자)가 하나로 병합 | document_hash + 복합 식별자로 완전 분리 |

**설계 철학 3원칙**
1. PostgreSQL/SQLite = 뼈대 (Source of Truth, 모든 상태 중앙 통제)
2. Graph + Vector = 두뇌 (좌뇌: 사실/엣지 정확도, 우뇌: 의미/문맥 이해)
3. 수학적 점수 융합 = 판단 (이산적 그래프 점수와 연속적 벡터 확률을 하나의 공식으로)

---

## 2장. 데이터 저장 구조 — 3개 이기종 DB의 수학적 역할
V8.5 시스템은 단일 DB가 아닌 3개의 이기종 데이터베이스를 목적에 따라 분리 운용한다. 각각은 서로 다른 수학적 이론에 기반한다.

| 저장소 | 수학적 기반 | 역할 | 현재 규모 |
|---|---|---|---|
| SQLite | 관계 대수 (집합론) | Source of Truth 상태 중앙 통제 | 2,886명 |
| Neo4j | 그래프 이론 (G=V,E) | 구조적 인덱스 행위 엣지 저장 | 2,366명 / 18,423개 엣지 |
| Pinecone | 고차원 벡터 공간 (R^n) | 의미론적 인덱스 문맥 유사도 | 진행 중 |

### 2.1 SQLite — 관계 대수와 집합론
[이론] 관계 대수 (Relational Algebra) — 데이터를 튜플의 집합 R = (A₁, A₂, ..., Aₙ)으로 표현. 집합 연산(합집합, 교집합, 차집합)으로 데이터 무결성을 보장한다.

왜 SQLite인가: 2,886명 규모에서 PostgreSQL은 오버엔지니어링이다. SQLAlchemy ORM을 사용하므로 나중에 연결 문자열 1줄만 변경하면 PostgreSQL로 전환 가능하다.

`candidates` 테이블 핵심 컬럼:
- `document_hash VARCHAR(64) UNIQUE`  -- SHA256 해시 (중복 방지의 수학적 기준)
- `is_parsed BOOLEAN`             -- 상태 머신 플래그
- `is_neo4j_synced / is_pinecone_synced`  -- 분산 트랜잭션 복구용
- `last_error TEXT`                -- DLQ 로그

`parsing_cache` — logic_hash 기반 캐시 무효화
logic_hash = SHA256(raw_text + prompt_version). 이력서 내용과 프롬프트 버전이 동일하면 0.01초 즉시 반환. 하나라도 바뀌면 자동 재파싱. 이는 암호학적 해시 함수의 충돌 저항성(Collision Resistance)을 활용한 결정론적 캐시 설계다.

### 2.2 Neo4j — 그래프 이론과 네트워크 중심성
[이론] 그래프 이론 (Graph Theory) — 데이터를 노드와 엣지의 집합으로 모델링.

8개 행위 동사 — 단순한 스킬 보유가 아닌 "행위"를 저장한다.
| 동사 | 의미 | 예시 |
|---|---|---|
| BUILT | 직접 코드 작성 또는 시스템 구축 | 결제 시스템을 직접 개발 |
| DESIGNED | 아키텍처/정책/BM 기획 및 설계 | 자금 운용 정책 수립 |
| MANAGED | 기존 시스템/조직/프로세스 운영 | Treasury 팀 운영 총괄 |
| ANALYZED | 데이터 추출/분석으로 인사이트 도출 | 현금흐름 모델 분석 |
| LAUNCHED | 프로덕트/서비스를 시장에 출시 | IPO 추진 및 상장 완료 |
| NEGOTIATED | 외부와 협상/계약 체결 | 은행 크레딧 라인 협상 |
| GREW | 지표를 수치적으로 성장시킴 | AUM 3,000억 달성 |
| SUPPORTED | 협업/일부 지원 (비주도적) | 자금팀 보조 업무 |

### 2.3 Pinecone — 고차원 벡터 공간 모델
[이론] 벡터 공간 모델 (Vector Space Model) — 자연어를 차원에 투영하여 코사인 유사도를 구한다.
- Chunk 임베딩: 1,000자 단위 분할
- 네임스페이스 분리: resume_vectors / jd_vectors

---

## 3장. 데이터 입수 파이프라인
1. Smart Chunking (노이즈 제거)
2. 중복 감지 2단계 (해시 + 연락처)
3. 복합 식별자 MERGE (동명이인 처리)
4. Gemini 파싱 (8개 동사 엣지 추출)
5. Neo4j + SQLite + Pinecone 동시 적재

[이론] 멱등성 (Idempotency)에 따라 Merge 연산 우선순위 지정: phone -> email -> name+company -> document_hash 신규.

---

## 4장. 검색 질문 분석
### 4.1 L1 텍스트 매핑 (0원, 0초)
CANONICAL_MAP 498개 매핑. 배경/핵심 맥락 구분(is_mandatory: false/true).

### 4.2 L2 Vector Fallback (0.05초)
OpenAI 임베딩 → 코사인 유사도 연산으로 생소한 단어를 대체.

---

## 5장. 하이브리드 검색 엔진
Step 1: TF-IDF 프리필터 (300명 + Union)
Step 2: Neo4j Graph Score
Step 3: Pinecone Vector Score
Step 4: UNIFIED_GRAVITY_FIELD Score Fusion

**V8.5 최종 Score Fusion 수식**
```
Final_Score = max(0.0,
  log(Graph_Score + Core_Bonus + Synergy_Bonus×1.5 + 1) × 0.6
  + Vector_Score × 0.4
  - min(Repulsion, 0.3)
  - min(Noise_Penalty, 0.10)
)
```

---

## 6장. 통합 중력장 (UNIFIED_GRAVITY_FIELD)
| 물리 개념 | 천체물리학적 의미 | Talent OS 구현 |
|---|---|---|
| Core Attracts | 중력장 | 필수 스킬군 |
| Synergy Attracts | 공명 | 1.5배 증폭 하이퍼 퍼포머 지표 |
| Repels | 전자기 척력 | 다른 직군 노이즈 페널티 |
| Noise Penalty | 엔트로피 | 잡다항목 과잉 시 감점 |
| Gravity Inversion | 중력 반전 | 임원(EXECUTIVE)의 경우 척력을 오히려 가산점으로 반전 (+0.5) |

---

## 7장. 데이터 무결성 면역 체계
1. 1차: 격리 병동 (DLQ)
2. 2차: 자동 순찰 (system_auditor.py)
3. 3차: Recovery Worker (is_synced=False 재시도)
4. 4차: Logic Hash 롤백

---

## 8장. 현재 상태 및 로드맵
완료: 복합 식별자 MERGE, Vector Fallback, 중력장 페널티, 척력 반전, 딥 리페어 등
진행: Pinecone 부분 적재, profile_summary 배치 생성
예정: DLQ 격리병동 적용, COO 온톨로지 추가, 리커버리 워커, PostgreSQL 전환 등
