<!-- Synthetic resume for algorithm evaluation. Not a real person. -->
# 정민서 (Minseo Jung) — Backend / Platform Engineer

> Synthetic resume for algorithm evaluation. Not a real person.

## Summary
백엔드/플랫폼 중심으로 2.5년간 결제·정산 도메인의 API와 비동기 처리 시스템을 운영한 서버 엔지니어입니다.
Java/Kotlin + Spring Boot 기반의 REST/gRPC API 설계, RDB 데이터 모델링, 트랜잭션 정합성, 메시지 큐 기반
비동기 처리에 강점이 있습니다. 프론트엔드(React) 화면을 일부 직접 수정한 경험이 있으나 프론트엔드 전문가는
아니며, 머신러닝/데이터 사이언스 경험은 거의 없습니다.

## Skills
- Languages: Java, Kotlin, SQL, Python (보조)
- Frameworks: Spring Boot, Spring MVC, Spring Data JPA, Hibernate
- Datastores: PostgreSQL, MySQL, Redis
- Messaging/Async: Apache Kafka, AWS SQS, Spring @Async, 스케줄러 배치
- API: REST, gRPC, OpenAPI/Swagger, gRPC protobuf 스키마 설계
- Cloud/Infra: AWS (EC2, RDS, ElastiCache, S3), Docker, 기본 수준의 Kubernetes
- Observability: Prometheus, Grafana, CloudWatch, 분산 트레이싱(OpenTelemetry 입문)
- Etc: Git, GitHub Actions, JUnit5, 약간의 React/TypeScript (사내 어드민 화면 수정)

## Experience
### 핀테크 스타트업 — Backend Engineer (2023.03 ~ 현재, 1년 3개월)
- 결제 정산 도메인의 핵심 정산 API를 Spring Boot + JPA로 재설계, 정산 배치 처리 시간을 42분 → 9분으로 단축.
- Kafka 기반 이벤트 파이프라인을 도입해 정산-알림-원장 기록을 비동기 분리, 피크 시간대 API p99 지연을 380ms → 120ms로 개선.
- PostgreSQL 인덱스/쿼리 튜닝과 트랜잭션 경계 재설계로 정산 중복 기록 장애(idempotency 미흡)를 제거.
- 사내 어드민의 일부 React 화면을 직접 수정(목록 필터, 상태 뱃지)했으나 컴포넌트 설계는 프론트 팀이 담당.

### 커머스 SI 회사 — Junior Server Developer (2021.09 ~ 2023.02, 1년 5개월)
- MySQL 기반 주문/재고 도메인 REST API 개발 및 유지보수, 재고 차감 동시성 이슈를 비관적 락 → 분산 락(Redis)으로 전환해 해결.
- 일 200만 건 주문 로그를 SQS로 비동기 적재하는 배치를 구축, 야간 정산 실패율을 3.1% → 0.2%로 감소.
- 모니터링이 없던 서비스에 Prometheus/Grafana 대시보드와 알람을 도입.

## Projects
### 사내 gRPC 사양 통합 (2023)
- 서비스 간 통신을 REST에서 gRPC로 부분 이관, protobuf 스키마와 버전 정책을 설계.
- 결과: 내부 호출 평균 응답 시간 35% 감소. 다만 외부 공개 API는 여전히 REST 유지(전면 전환은 아님).

### 토이: 분산 락 라이브러리 학습용 클론 (2022)
- Redisson을 참고해 간단한 분산 락 인터페이스를 직접 구현하며 동작 원리 학습. 프로덕션 사용 아님.

## Education
- OO대학교 컴퓨터공학 학사 (2017.03 ~ 2021.08)
- 학부 캡스톤: 학내 중고거래 웹 서비스(백엔드 담당, Spring + MySQL)

## Preferences
- 희망 직무: 백엔드 / 서버 / 플랫폼 백엔드 엔지니어
- 관심 있음(인접): 풀스택 백엔드 비중이 큰 포지션, DevOps/인프라 협업이 많은 플랫폼 팀
- 선호하지 않음: 프론트엔드 전담, 순수 ML/데이터 사이언스, 디자인/기획/마케팅 직무
- 근무 형태: 하이브리드 선호
