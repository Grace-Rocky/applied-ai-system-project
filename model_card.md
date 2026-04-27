# Model Card: PulseMetal Music Intelligence

## 1. System Summary

- Model Type: Rule-based content recommender with weighted similarity scoring
- Interface: Flask web app + API endpoints
- Catalog Size: 338 songs
- Core AI Features: Agentic workflow, RAG evidence retrieval, reliability fact-checking
- Visual Style: Glossy cinematic dashboard with chart-driven panels and mobile tuning
- Release Date: 2026-04-27

## 2. Intended Use

This system is intended for educational and portfolio demonstration of transparent recommendation architecture. It is suitable for:
- Demonstrating explainable recommendation scoring
- Showing agentic reasoning traces
- Testing reliability and fact-check style verification in recommender outputs
- Presenting an intentionally polished product UI with charts and motion

It is not intended for production music licensing, personal profiling, or safety-critical decisions.

## 3. Data Profile

The catalog combines:
- 18 hand-authored seed songs with curated metadata
- 320+ generated songs with structured audio feature variation

Data fields:
- id, title, artist, genre, mood
- energy, tempo_bpm, valence, danceability, acousticness

Coverage:
- 19 genres
- 13 moods
- 240+ artists

## 4. How the System Works

1. User profile is captured (genre, mood, energy, valence, danceability, acoustic preference).
2. Songs are scored with weighted feature matching.
3. Agent mode can expose traceable multi-step reasoning (analyze, retrieve, score, rank, verify).
4. RAG layer attaches contextual metadata and semantic evidence.
5. Reliability module evaluates consistency, diversity, coverage, confidence, fact-check score, and baseline overlap.
6. The frontend turns these results into a cinematic dashboard with charts, cards, and motion.

## 5. Evaluation and Verification

### Reliability Metrics
- Consistency: repeat-run overlap
- Coverage: recommendation spread relative to catalog
- Diversity: variation across genre, mood, and artist
- Confidence: normalized score confidence

### Fact-Check Metrics
- Checks explanation claims against actual song facts:
  - genre match claim
  - mood match claim
  - energy closeness claim

### Baseline Cross-Verification
- Compares current recommender output with a baseline variant (mood-disabled scoring) to quantify behavioral drift and stability.

## 6. Strengths

- High transparency: every recommendation includes explanation and optional workflow trace.
- Auditable RAG: evidence and metadata sources are visible.
- Better test realism than tiny-catalog demos due to larger dataset.
- Premium presentation layer makes the product easier to understand and demo.

## 7. Limitations

- Catalog is still synthetic and not user-listening driven.
- No collaborative filtering or sequence modeling.
- Semantic retrieval is lexical and lightweight, not embedding-based.
- Fact-checking validates supported claims only, not broader music semantics.

## 8. Bias and Risk Considerations

- Synthetic generation can encode template bias in feature distributions.
- Genre and mood labels are simplified and may flatten cultural nuance.
- Weight choices reflect design decisions, not learned personalization.

Mitigation:
- Keep scoring weights documented.
- Keep verification details visible per scenario.
- Encourage human review for interpretation of recommendations.

## 9. Safety and Misuse

Potential misuse:
- Overstating recommendation certainty
- Treating synthetic evaluation as real-world personalization quality

Mitigations:
- Confidence and fact-check scores are shown separately.
- Documentation distinguishes demo reliability from production validity.
- Workflow traces expose reasoning instead of hiding it.

## 10. Future Work

- Add user feedback loops and calibration from real interactions.
- Add embedding-based retrieval for richer semantic matching.
- Add fairness diagnostics across genre/mood cohorts.
- Add richer motion, transitions, and visual storytelling for the web experience.

## 11. Human + AI Collaboration Notes

Useful AI-assisted outcomes:
- Rapid iteration on architecture decomposition
- Faster bug diagnosis and workflow instrumentation
- Strong draft support for documentation and test ideas

Human-owned decisions remained critical for:
- Scope control
- Avoiding unnecessary infrastructure
- Interpreting metrics in product context

## 12. Testing Results

The system was validated with both unit tests and API smoke tests.

Observed results:
- Unit tests: 2 passing in `tests/test_recommender.py`
- Recommendation API: returned the requested number of ranked songs
- RAG API: returned semantic matches and mood-based matches
- Evaluation API: returned 5 scenario results with summary metrics
- Overall evaluation score observed in smoke testing: approximately 0.75

Representative scenario findings:
- Consistency stayed at 1.00 in the current smoke runs because repeated runs stayed stable within each scenario.
- Fact-check score stayed at 1.00 because explanation claims matched supported song facts.
- Baseline overlap varied by scenario, which is useful because it shows the system is not simply reproducing one fixed ranking pattern.

What surprised me:
- Increasing the catalog size made the reliability tab more meaningful because the metrics now reflect a wider candidate space.
- The cross-check layer was most useful when it exposed claim validation details directly instead of only showing aggregate scores.

## 13. Reflection Prompt Answers

### AI Collaboration

What helped:
- The AI was helpful for decomposing the system into clear modules and for surfacing likely failure points.
- It was especially useful when designing explanation, retrieval, and testing flows that needed to be easy to inspect.

What did not help as much:
- It tended to suggest heavier infrastructure than the project needed for this catalog size.
- It sometimes pushed optimization or model complexity before the product problem was clear.

How I used it responsibly:
- I treated AI output as a critique and drafting tool, not an authority.
- I kept the final architectural choices aligned with the project scale and demo goals.
- I validated the implementation with tests and API smoke checks rather than trusting the design on paper.

### Biases

Main biases present in the system:
- Catalog bias: the dataset is synthetic and not representative of real-world taste diversity.
- Label bias: genre and mood categories are simplified and can flatten nuance.
- Scoring bias: hand-set weights reflect design choices, not learned personalization.
- Retrieval bias: the RAG layer is lexical and may favor obvious keyword matches.

Mitigations:
- The model card documents the limitations openly.
- The UI shows explanations and evidence instead of hiding logic.
- The evaluator checks whether claims actually match catalog facts.

### Testing Results

- The system was tested with multiple user profiles and the outputs were reviewed for both ranking quality and factual consistency.
- The expanded catalog improved the usefulness of testing because it created more varied retrieval and ranking behavior.
- The evaluation suite now verifies that the system is stable, diverse enough, and internally consistent.

## Status

Ready for portfolio review and demonstration.
