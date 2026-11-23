# HC 및 Extra HC 모의 활동 이력 수집

\`\`\`mermaid
flowchart LR
  A[가상 관찰 데이터] --> B[유효성 검사]
  B --> C[활동 지표 집계]
  B --> D[가상 링크 정규화]
  C --> E[SQLite 날짜별 스냅샷]
  D --> E
  E --> F[과거 대비 기술 통계]
  E --> G[CSV 내보내기]
\`\`\`

## 실행

\`\`\`bash
python run_history.py --db synthetic_history.sqlite --export history_export.csv
python run_history.py --db synthetic_history.sqlite --export history_export.csv
python -m unittest discover -s tests -v
\`\`\`

포트폴리오용 독립 코드로 날짜별 데이터를 누적하며 동일한 날짜를 다시 수집하면 중복 행이 생기지 않습니다. **성장 예측이나 실제 매출 효과를 입증하는 기능은 아닙니다.** HTTP 요청, 사용자 계정 조회, 개인 이메일 수집은 하지 않습니다.
