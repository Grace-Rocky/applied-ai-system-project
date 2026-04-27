# System Architecture Diagram

## High-Level Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
│                      (Streamlit Web Application)                    │
│                                                                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐     │
│  │              │              │              │              │     │
│  │ Recommendations │  Agentic    │ Reliability │  RAG Database│     │
│  │     Tab       │  Workflow Tab│  Testing Tab│    Tab       │     │
│  │              │              │              │              │     │
│  └──────────────┴──────────────┴──────────────┴──────────────┘     │
│                              │                                      │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
    ┌───────────▼─────┐  ┌──────▼──────┐ ┌──▼──────────┐
    │  RAG Retriever  │  │  Agent      │ │ Evaluator & │
    │  (OpenContext)  │  │ (Workflows) │ │ Testing     │
    └────────┬────────┘  └──────┬──────┘ └──┬─────────┘
             │                  │            │
             └──────────────────┼────────────┘
                                │
            ┌───────────────────▼──────────────────┐
            │  CORE RECOMMENDER ENGINE             │
            │                                      │
            │  ┌────────────────────────────────┐ │
            │  │  Recommendation Logic:         │ │
            │  │  • load_songs()                │ │
            │  │  • score_song()                │ │
            │  │  • recommend_songs()           │ │
            │  │  • Song + UserProfile classes  │ │
            │  └────────────────────────────────┘ │
            │                                      │
            │  ┌────────────────────────────────┐ │
            │  │  Scoring Components:           │ │
            │  │  • _norm_str()                 │ │
            │  │  • _closeness_score()          │ │
            │  │  • _tempo_similarity()         │ │
            │  │  • DEFAULT_WEIGHTS            │ │
            │  └────────────────────────────────┘ │
            └────────────┬─────────────────────────┘
                         │
            ┌────────────▼──────────────┐
            │    DATA LAYER             │
            │                           │
            │  • songs.csv (18 tracks)  │
            │  • Metadata DB            │
            │  • Weighted coefficients  │
            └───────────────────────────┘
```

## Data Flow: Recommendation Generation

```
    User Input
    (Profile)
         │
         ▼
    ┌─────────────────────────────────────┐
    │ 1. Profile Analysis                 │
    │    Extract & validate preferences   │
    │    Confidence: 0.60-1.00           │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 2. Candidate Retrieval              │
    │    Filter by genre/mood             │
    │    Apply RAG context                │
    │    Confidence: 0.80-1.00           │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 3. Scoring                          │
    │    For each candidate song:         │
    │    • Calculate weighted score       │
    │    • Compute 7 feature similarities │
    │    Confidence: 0.85-1.00           │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 4. Ranking                          │
    │    Sort candidates by score (desc)  │
    │    Select top-k recommendations     │
    │    Confidence: 1.00                │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 5. Verification                     │
    │    Sanity checks:                   │
    │    • All unique songs               │
    │    • Scores in valid range          │
    │    • Explanations present           │
    │    Confidence: 0.70-1.00           │
    └────────────┬────────────────────────┘
                 │
                 ▼
    Ranked Recommendations
    (with RAG context & workflow trace)
```

## RAG Context Flow

```
    Song ID
        │
        ▼
    ┌─────────────────────────────────┐
    │ RAG Metadata Retrieval          │
    │                                 │
    │ retrieve_song_context(song_id)  │
    └────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ┌────────────┐  ┌──────────────────┐
    │Description │  │Audio Features    │
    │            │  │                  │
    │ "Uplifting │  │"high-frequency   │
    │ electronic │  │synths with       │
    │ track with │  │strong beat"      │
    │ vibrant    │  │                  │
    │ synth      │  │                  │
    │ layers"    │  └──────────────────┘
    └────────────┘
        │
        ├─────────────┐
        │             │
        ▼             ▼
    ┌────────┐  ┌──────────────┐
    │ Tags   │  │Artist Style  │
    │        │  │              │
    │ uplifting│ │ "Neon Echo - │
    │ electronic│ │ known for   │
    │ energetic│ │ pop-electronic
    │ urban   │  │ fusion"      │
    └────────┘  └──────────────┘
```

## Module Dependencies

```
app.py (Main UI)
    ├─ recommender.py
    │  ├─ dataclasses (Song, UserProfile)
    │  ├─ csv (load_songs)
    │  └─ logging
    │
    ├─ rag_retriever.py
    │  ├─ SONG_METADATA dict
    │  └─ RAGRetriever class
    │
    ├─ agent.py
    │  ├─ Enum (AgentStep)
    │  ├─ dataclass (WorkflowAction)
    │  ├─ RecommendationAgent class
    │  └─ score_song (from recommender.py)
    │
    └─ evaluation.py
       ├─ dataclass (EvaluationResult)
       ├─ ReliabilityEvaluator class
       ├─ TEST_SCENARIOS dict
       └─ run_reliability_tests()
```

## Scoring System Weights

```
Final Score = Σ(weight × metric_contribution)

Where:
┌────────────────────┬────────┬──────────────────┐
│ Metric             │ Weight │ Calculation      │
├────────────────────┼────────┼──────────────────┤
│ Genre Match        │  2.0   │ +2.0 if exact match │
│ Mood Match         │  1.0   │ +1.0 if exact match │
│ Energy Similarity  │  2.0   │ 2.0 × (1 - |gap|) │
│ Valence Similarity │  0.8   │ 0.8 × (1 - |gap|) │
│ Tempo Similarity   │  0.6   │ 0.6 × similarity  │
│ Danceability Sim   │  0.7   │ 0.7 × (1 - |gap|) │
│ Acousticness Pref  │  0.5   │ 0.5 × score       │
└────────────────────┴────────┴──────────────────┘

Example Score Calculation:
  User: Pop, Happy, Energy=0.85, Valence=0.80, Danceability=0.85
  Song: Pop, Happy, Energy=0.82, Valence=0.84, Danceability=0.79
  
  Score = 2.0 + 1.0 
         + (2.0 × (1 - |0.85-0.82|))    = 2.0 × 0.97 = 1.94
         + (0.8 × (1 - |0.80-0.84|))    = 0.8 × 0.96 = 0.77
         + tempo_similarity              = 0.55
         + (0.7 × (1 - |0.85-0.79|))    = 0.7 × 0.94 = 0.66
         + acoustic_pref                 = 0.15
  ─────────────────────────────────────────────────
  Total Score ≈ 8.07 out of 10.0
```

## Reliability Evaluation Metrics

```
┌─────────────────────────────────────────────────┐
│ CONSISTENCY SCORE (0.0-1.0)                     │
├─────────────────────────────────────────────────┤
│ Jaccard Similarity between runs                 │
│ |A ∩ B| / |A ∪ B|                             │
│ • 1.0 = identical recommendations every run    │
│ • 0.5 = only 50% overlap between runs         │
│ • Target: > 0.85                              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ COVERAGE SCORE (0.0-1.0)                        │
├─────────────────────────────────────────────────┤
│ Unique songs / Min(total_songs, benchmark)     │
│ • 1.0 = unlimited catalog variety              │
│ • 0.5 = using only half the catalog           │
│ • Target: > 0.70                              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ DIVERSITY SCORE (0.0-1.0)                       │
├─────────────────────────────────────────────────┤
│ (Unique Genres + Unique Moods) / (2 × K)      │
│ • 1.0 = every recommendation different genre   │
│ • 0.5 = only 50% recommend different genres   │
│ • Target: > 0.60                              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ CONFIDENCE SCORE (0.0-1.0)                      │
├─────────────────────────────────────────────────┤
│ Avg(Min(score/10, 1.0) for all recommendations)│
│ • 1.0 = all recommendations perfect match       │
│ • 0.5 = average score ~5.0 out of 10          │
│ • Target: > 0.75                              │
└─────────────────────────────────────────────────┘
```

---

**Architecture Documentation**  
Generated: April 27, 2026
