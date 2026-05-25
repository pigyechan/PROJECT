# Career Planner Pipeline

채용공고 텍스트 → 시장 패턴 분석 + StoryBrand 포지셔닝 초안 생성 파이프라인.

## 시작하기

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key"
```

### 3. 채용공고 입력

```bash
cd pipeline
python create_input.py
```

채용 사이트에서 공고 텍스트를 복사해서 붙여넣으세요 (20~30개 권장).

### 4. 파이프라인 실행

```bash
python main.py ../inputs/input_{hash}.json
```

## 출력 파일

`runs/{실행ID}/` 폴더에 생성됩니다.

| 파일 | 내용 |
|---|---|
| `01_input.json` | 입력 채용공고 원본 |
| `02_analysis.json` | 분류 + 숨은 기대치 분석 |
| `02b_report.md` | **시장 패턴 리포트** |
| `03_draft.md` | **포지셔닝 초안** |
| `memo_template.md` | **소화 메모 템플릿 (직접 작성)** |

## 파이프라인 구조

```
채용공고 입력
    ↓
Analyze  — 분류 + 표면 스킬 + 숨은 기대치 해석
    ↓
Report   — 시장 패턴 리포트 (마크다운)
    ↓
Draft    — StoryBrand 7요소 포지셔닝 초안
    ↓
Critique — 약점 3개 추출
    ↓
Eval     — 루브릭 채점 (6축)
    ↓ REJECT (최대 3회)
Refine   — 약점 반영 재작성
```
