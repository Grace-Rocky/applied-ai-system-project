# PulseMetal Music Intelligence

An advanced music recommendation system presented as a cinematic web product.

## Base Project

This project is based on the CodePath AI110 Module 3 music recommender simulation starter. The original classroom recommender was extended into a larger portfolio-grade system with a bigger catalog, agentic workflow, RAG evidence retrieval, reliability cross-checking, and a premium website-style interface.

## Highlights

- 338-song catalog for meaningful ranking and testing behavior
- Agentic workflow with visible reasoning and confidence traces
- RAG evidence layer with semantic search and metadata hydration
- Reliability suite with fact-check scoring and baseline cross-verification
- Premium glossy UI with animated panels, interactive charts, and mobile-friendly layout

## Product Experience

The project is now centered on a Flask-based website rather than a plain demo page. The interface uses glassmorphism, motion, and chart-driven visuals to make the system feel like a polished music product.

Key visual features:
- Animated hero section and background orbs
- Live catalog distribution charts
- Featured-track spotlight cards
- Glass recommendation panels with hover motion
- Reliability radar chart and RAG energy donut chart
- Mobile layout tuning for narrow screens

## Architecture

- Backend API: [app_web.py](app_web.py)
- Frontend: [templates/index.html](templates/index.html), [static/styles.css](static/styles.css), [static/app.js](static/app.js)
- Core Scoring Engine: [src/recommender.py](src/recommender.py)
- Agent Workflow: [src/agent.py](src/agent.py)
- RAG Retrieval: [src/rag_retriever.py](src/rag_retriever.py)
- Evaluation + Fact Check: [src/evaluation.py](src/evaluation.py)
- Catalog Data: [data/songs.csv](data/songs.csv)

## Assets and Diagrams

System diagrams and future demo screenshots are organized under [assets](assets). The repository now keeps diagram material in a dedicated visual assets area so presentation files stay separate from code.

### Request Flow

1. User submits a taste profile.
2. The backend generates recommendations using direct scoring or agentic workflow mode.
3. RAG enriches each result with metadata, semantic evidence, and contextual notes.
4. The evaluator cross-checks recommendation claims against song facts and baseline behavior.
5. The UI renders cards, charts, workflow traces, and retrieval evidence.

## Reliability and Fact Checking

The evaluation layer now measures:
- Consistency
- Coverage
- Diversity
- Confidence
- Fact Check Score
- Baseline Overlap

These values are blended into a single overall score so the dashboard can show both quality and trust signals.

## Setup

### 1. Clone

```bash
git clone https://github.com/Grace-Rocky/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Create and activate environment

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run

### Recommended web experience

```bash
python app_web.py
```

Then open http://localhost:8000.

### Optional legacy Streamlit view

```bash
streamlit run app.py
```

## Test

```bash
pytest tests/test_recommender.py -v
```

## API Endpoints

- `POST /api/recommend`
  - Inputs: profile, k, use_rag, use_agent
  - Returns: recommendations plus optional workflow trace

- `POST /api/evaluate`
  - Runs the full reliability suite over predefined scenarios
  - Returns: aggregate metrics and fact-check details

- `POST /api/rag/search`
  - Inputs: semantic query and/or mood
  - Returns: semantic and mood retrieval matches with metadata

- `GET /api/catalog/insights`
  - Returns catalog distribution data and featured tracks for charts

## Current Dataset Profile

- Songs: 338
- Genres: 19
- Moods: 13
- Artists: 240+

## Notes

- The expanded catalog is synthetic but structured to mimic realistic variation.
- RAG uses curated metadata for seed songs and generated metadata for expanded catalog entries.
- Fact-checking is rule-based and auditable.
- The visual system is intentionally bold and mobile-responsive to feel like a real product.


## 🎥 Presentation Video

The presentation video is available here:  
👉 https://www.loom.com/share/415eaf21462b4f669b26a067b111d7be
