<!-- Synthetic resume for algorithm evaluation. Not a real person. -->
# 배준호 (Junho Bae) — DevOps / Infra Engineer (Security-adjacent)

> Synthetic resume for algorithm evaluation. Not a real person.

## Summary
클라우드 인프라/플랫폼 엔지니어로 약 4년간 AWS 기반 서비스 인프라, 컨테이너 오케스트레이션, CI/CD,
관측성(observability), 장애 대응을 담당했습니다. Terraform으로 인프라를 코드화하고 Kubernetes 위에서
서비스를 운영한 경험이 있습니다. 보안 운영(취약점 관리, 접근 통제, 침해 알람 대응)에도 일부 관여했으나,
깊은 모의해킹/익스플로잇 개발 전문가는 아닙니다. 애플리케이션 기능 개발 비중은 낮습니다.

## Skills
- Cloud: AWS (EC2, EKS, VPC, IAM, S3, RDS, CloudFront, Route53)
- Containers/Orchestration: Docker, Kubernetes, Helm
- IaC/Automation: Terraform, Ansible, GitHub Actions, ArgoCD
- Observability: Prometheus, Grafana, Loki, ELK(Elasticsearch/Kibana), CloudWatch
- OS/Networking: Linux, Bash, TCP/IP, Nginx, 로드밸런싱
- Security (adjacent): IAM 최소권한 설계, 취약점 스캔(Trivy), Secrets 관리(Vault), 침해 알람 1차 대응
- Languages: Python, Go (운영 도구 수준), YAML, SQL(기본)

## Experience
### 모빌리티 플랫폼 — Infra / DevOps Engineer (2022.01 ~ 현재, 2년 5개월)
- 수동 배포 환경을 GitHub Actions + ArgoCD 기반 GitOps로 전환, 배포 리드타임을 평균 35분 → 6분으로 단축.
- EKS 클러스터의 오토스케일링(HPA/Cluster Autoscaler)과 리소스 리밋을 재설계해 월 인프라 비용 약 23% 절감.
- Prometheus/Grafana/Loki로 통합 관측성 스택을 구축, 평균 장애 감지 시간(MTTD)을 12분 → 3분으로 단축.
- 보안팀과 협업해 IAM 권한을 최소권한 원칙으로 재설계하고 Trivy 이미지 스캔을 CI에 통합.

### 호스팅/IDC 회사 — Systems Engineer (2020.03 ~ 2021.12, 1년 10개월)
- 온프레미스 → AWS 마이그레이션 프로젝트에서 Terraform 모듈을 작성해 VPC/서브넷/보안그룹을 코드화.
- 야간 온콜 로테이션 참여, 침해 의심 알람 1차 트리아지 및 에스컬레이션 절차 문서화. 본격 포렌식은 보안 전문팀이 수행.

## Projects
### 사내 IaC 표준 모듈화 (2023)
- 반복되던 Terraform 코드를 재사용 가능한 모듈로 표준화하고 리뷰 가이드를 작성, 신규 서비스 인프라 구축 시간을 약 절반으로 단축.

### 토이: 쿠버네티스 홈랩 (2022)
- 라즈베리파이 3대로 K3s 클러스터를 구성하고 ArgoCD/Prometheus를 올려 GitOps 흐름을 학습.

## Education
- OO대학교 정보통신공학 학사 (2014.03 ~ 2020.02, 군 복무 포함)
- 자격: AWS Certified Solutions Architect – Associate, CKA(Certified Kubernetes Administrator)

## Preferences
- 희망 직무: DevOps / Infra / SRE / AIOps / Cloud Infra / Platform Engineer
- 관심 있음(인접): 보안 탐지·대응(detection/response), 백엔드 플랫폼
- 약함: 프론트엔드, 순수 ML/AI, 데이터 분석
- 선호하지 않음: 디자인/기획/마케팅 직무
- 근무 형태: 온콜 가능, 하이브리드 선호
