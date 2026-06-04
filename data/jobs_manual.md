# 수동 JD 입력 (Manual JD input)

스크래핑이 실패했거나, 원하는 공고를 직접 넣고 싶을 때 이 파일을 사용하세요.
`data/raw/jobs/` 에 자동 수집된 공고가 있으면 그쪽이 우선 사용되고, 없을 때만 이 파일을 읽습니다.

## 작성 규칙
- 공고 하나를 `=== JOB ===` 줄로 구분합니다.
- 각 공고는 `COMPANY:`, `TITLE:`, `URL:` 머리말 다음에 `TEXT:` 를 쓰고, 그 아래에 JD 전문을 붙여넣습니다.
- `TEXT:` 본문이 비어 있거나 `<paste ...>` 같은 안내문이 그대로 남아 있는 블록은 무시됩니다.

## 예시 (이 줄 아래 형식을 그대로 따라 채우세요)

=== JOB ===
COMPANY: Toss
TITLE: Frontend Developer
URL: https://toss.im/career/job-detail?gh_jid=XXXXXXX
TEXT:
<paste the full job description text here — responsibilities, requirements, preferred, etc.>

=== JOB ===
COMPANY: Daangn
TITLE: Server Developer
URL: https://about.daangn.com/jobs/XXXXXXXXXX/
TEXT:
<paste the full job description text here>
