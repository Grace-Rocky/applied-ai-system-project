from pathlib import Path
import streamlit as st
import logging

from src.recommender import load_songs, recommend_songs
from src.rag_retriever import RAGRetriever
from src.agent import RecommendationAgent
from src.evaluation import ReliabilityEvaluator, run_reliability_tests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration with enhanced styling
st.set_page_config(
    page_title="🎵 Advanced Music Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    :root {
        --primary-color: #1DB954;
        --secondary-color: #191414;
        --accent-color: #1ed760;
    }
    
    .main {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    
    .stTitle {
        color: #1DB954;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #1DB954 0%, #1aa34a 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 4px solid #1ed760;
    }
    
    .metric-box {
        background-color: #282828;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1DB954;
        margin: 10px 0;
    }
    
    .workflow-step {
        background-color: #1a1a1a;
        padding: 15px;
        border-left: 3px solid #1ed760;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_retriever' not in st.session_state:
    st.session_state.rag_retriever = RAGRetriever()
if 'agent' not in st.session_state:
    st.session_state.agent = RecommendationAgent()
if 'evaluator' not in st.session_state:
    st.session_state.evaluator = ReliabilityEvaluator()

# Load data
songs_path = Path(__file__).parent / "data" / "songs.csv"
songs = load_songs(str(songs_path))

# Main header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🎵 Advanced Music Recommender")
    st.markdown("##### *Powered by RAG, Agentic Workflow & AI Intelligence*")

st.divider()

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Recommendations",
    "🤖 Agentic Workflow",
    "📊 Reliability Testing",
    "📚 RAG Database",
    "ℹ️ About"
])

# ============ TAB 1: RECOMMENDATIONS ============
with tab1:
    st.markdown("### Get Your Perfect Song Recommendations")
    
    col_profile1, col_profile2 = st.columns(2)
    
    with col_profile1:
        st.markdown("#### Your Music Taste Profile")
        profile = {
            "genre": st.selectbox(
                "🎸 Favorite Genre",
                sorted({str(song["genre"]) for song in songs}),
                index=0,
            ),
            "mood": st.selectbox(
                "😊 How are you feeling?",
                sorted({str(song["mood"]) for song in songs}),
                index=0,
            ),
        }
    
    with col_profile2:
        st.markdown("#### Fine-tune Your Preferences")
        profile["energy"] = st.slider("⚡ Energy Level", 0.0, 1.0, 0.75, 0.05)
        profile["valence"] = st.slider("✨ Positivity (Valence)", 0.0, 1.0, 0.70, 0.05)
        profile["danceability"] = st.slider("💃 Danceability", 0.0, 1.0, 0.75, 0.05)
        profile["likes_acoustic"] = st.checkbox("🎸 Prefer Acoustic Sound?", value=False)
    
    col_rec1, col_rec2, col_rec3 = st.columns(3)
    with col_rec1:
        k = st.slider("🔝 Top K Recommendations", 1, 10, 5)
    with col_rec2:
        use_rag = st.checkbox("🧠 Use RAG Enhancement", value=True)
    with col_rec3:
        use_agent = st.checkbox("🤖 Use Agentic Workflow", value=False)
    
    # Generate recommendations
    if use_agent:
        with st.spinner("🤖 Agent reasoning in progress..."):
            recommendations, workflow = st.session_state.agent.run_workflow(
                profile, songs, lambda p, s: __import__('src.recommender', fromlist=['score_song']).score_song(p, s),
                k=k,
                rag_retriever=st.session_state.rag_retriever if use_rag else None
            )
    else:
        recommendations = recommend_songs(
            profile, songs, k=k,
            use_rag=use_rag,
            rag_retriever=st.session_state.rag_retriever if use_rag else None
        )
    
    st.markdown("---")
    st.markdown("### 🎵 Your Top Recommendations")
    
    for idx, (song, score, explanation) in enumerate(recommendations, start=1):
        with st.container():
            col_num, col_content, col_score = st.columns([0.5, 3, 1.2])
            
            with col_num:
                st.markdown(f"### #{idx}")
            
            with col_content:
                st.markdown(f"#### {song['title']}")
                st.markdown(f"**Artist:** {song['artist']} | **Genre:** {song['genre']} | **Mood:** {song['mood']}")
                
                col_metrics = st.columns(4)
                with col_metrics[0]:
                    st.metric("Energy", f"{float(song['energy']):.2f}")
                with col_metrics[1]:
                    st.metric("Valence", f"{float(song['valence']):.2f}")
                with col_metrics[2]:
                    st.metric("Danceability", f"{float(song['danceability']):.2f}")
                with col_metrics[3]:
                    st.metric("Acousticness", f"{float(song['acousticness']):.2f}")
                
                with st.expander("📖 Why this match?"):
                    explanation_text = explanation if isinstance(explanation, str) else "; ".join(explanation)
                    for reason in explanation_text.split(";"):
                        st.write(f"✓ {reason.strip()}")
            
            with col_score:
                st.markdown(f"<div class='metric-box'><h3 style='color: #1ed760;'>{score:.2f}</h3><p>Match Score</p></div>", unsafe_allow_html=True)
            
            st.divider()

# ============ TAB 2: AGENTIC WORKFLOW ============
with tab2:
    st.markdown("### 🤖 AI Agent Reasoning Process")
    st.info("Watch how the AI agent thinks through its recommendation logic step by step.")
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        agent_genre = st.selectbox(
            "Choose Genre (Workflow)",
            sorted({str(song["genre"]) for song in songs}),
            index=1,
            key="agent_genre"
        )
    with col_a2:
        agent_mood = st.selectbox(
            "Choose Mood (Workflow)",
            sorted({str(song["mood"]) for song in songs}),
            index=1,
            key="agent_mood"
        )
    
    if st.button("🚀 Run Agentic Workflow"):
        agent_prefs = {
            "genre": agent_genre,
            "mood": agent_mood,
            "energy": 0.6,
            "valence": 0.6,
            "danceability": 0.6,
            "likes_acoustic": False,
        }
        
        with st.spinner("🤖 Agent is thinking..."):
            recommendations, workflow = st.session_state.agent.run_workflow(
                agent_prefs, songs,
                lambda p, s: __import__('src.recommender', fromlist=['score_song']).score_song(p, s),
                k=5,
                rag_retriever=st.session_state.rag_retriever
            )
        
        st.markdown("### Workflow Execution Trace")
        
        for i, action in enumerate(workflow, 1):
            with st.expander(f"Step {i}: {action.step.value.replace('_', ' ').title()}"):
                col_step1, col_step2 = st.columns(2)
                
                with col_step1:
                    st.markdown(f"**Confidence:** {action.confidence:.2%}")
                    st.markdown(f"**Reasoning:**")
                    st.write(action.reasoning)
                
                with col_step2:
                    st.markdown("**Output Data:**")
                    st.json(action.output_data)
        
        st.markdown("---")
        st.markdown("### Final Recommendations from Agent")
        for idx, (song, score, _) in enumerate(recommendations, 1):
            st.write(f"{idx}. **{song['title']}** by {song['artist']} (Score: {score:.2f})")

# ============ TAB 3: RELIABILITY TESTING ============
with tab3:
    st.markdown("### 📊 AI Reliability & Evaluation Framework")
    st.info("Test the consistency, coverage, diversity, and confidence of the recommender system.")
    
    if st.button("🧪 Run Full Reliability Test Suite"):
        with st.spinner("Running comprehensive tests..."):
            from src.recommender import recommend_songs as rec_func
            test_results = run_reliability_tests(rec_func, songs, st.session_state.evaluator)
        
        summary = st.session_state.evaluator.get_summary()
        
        # Display summary metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("Total Evaluations", summary['total_evaluations'])
        with col_m2:
            st.metric("Avg Overall Score", f"{summary['average_overall_score']:.3f}")
        with col_m3:
            st.metric("Avg Consistency", f"{summary['average_consistency']:.3f}")
        with col_m4:
            st.metric("Avg Coverage", f"{summary['average_coverage']:.3f}")
        
        st.divider()
        st.markdown("### Test Results by Scenario")
        
        for scenario_name, result in test_results.items():
            with st.expander(f"📍 {scenario_name.replace('_', ' ').title()}"):
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                
                with col_r1:
                    st.metric("Consistency", f"{result.consistency_score:.3f}")
                with col_r2:
                    st.metric("Coverage", f"{result.coverage_score:.3f}")
                with col_r3:
                    st.metric("Diversity", f"{result.diversity_score:.3f}")
                with col_r4:
                    st.metric("Overall Score", f"{result.overall_score:.3f}")
                
                st.markdown("**Recommendations:**")
                for rec in result.recommendations[:3]:
                    st.write(f"- {rec['title']} (Score: {rec['score']:.2f})")

# ============ TAB 4: RAG DATABASE ============
with tab4:
    st.markdown("### 📚 RAG Metadata & Song Information")
    st.info("Retrieval-Augmented Generation: Rich contextual information about songs.")
    
    selected_song_id = st.selectbox(
        "Select a Song",
        options=[s['id'] for s in songs],
        format_func=lambda x: next((s['title'] + ' - ' + s['artist'] for s in songs if s['id'] == x), str(x))
    )
    
    metadata = st.session_state.rag_retriever.retrieve_song_context(int(selected_song_id))
    
    if metadata:
        col_rag1, col_rag2 = st.columns(2)
        
        with col_rag1:
            st.markdown(f"### {metadata['title']}")
            st.markdown(f"**Description:** {metadata['description']}")
            st.markdown(f"**Audio Features:** {metadata['audio_features']}")
        
        with col_rag2:
            st.markdown("**Tags:**")
            tags_html = " ".join([f"<span style='background-color:#1DB954; padding:5px 10px; border-radius:5px; margin:5px;'>{tag}</span>" for tag in metadata['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown(f"**Artist Style:** {metadata['artist_style']}")

# ============ TAB 5: ABOUT ============
with tab5:
    st.markdown("### About This AI System")
    
    st.markdown("""
    ## 🎯 Project Overview
    
    This is an **advanced AI-powered music recommendation system** built with three core features:
    
    ### 1. 🧠 RAG (Retrieval-Augmented Generation)
    - Retrieves rich metadata about songs including descriptions, tags, and audio features
    - Enhances recommendations with contextual information
    - Provides transparent explanations for why songs are recommended
    
    ### 2. 🤖 Agentic Workflow
    - Observable multi-step reasoning process
    - Shows exactly how the AI analyzes your profile
    - Demonstrates candidate retrieval, scoring, ranking, and verification
    - Each step includes confidence scores and reasoning
    
    ### 3. 📊 Reliability & Testing Framework
    - Measures consistency: same user gets similar recommendations repeatedly
    - Evaluates coverage: recommendations span the catalog appropriately
    - Analyzes diversity: recommendations vary in genre and mood
    - Calculates confidence: how sure the AI is about its recommendations
    """)
    
    st.divider()
    
    st.markdown("""
    ## 🔧 Technical Architecture
    
    - **Base Algorithm:** Content-based filtering with weighted similarity scoring
    - **Scoring Metrics:** Genre, mood, energy, valence, tempo, danceability, acousticness
    - **Data:** 18 carefully curated songs with diverse characteristics
    - **UI:** Streamlit for responsive web interface
    - **Logging:** Comprehensive event tracking for reliability measurement
    """)
    
    st.divider()
    
    st.markdown("""
    ## 📈 Key Features
    
    ✅ **Transparent Explanations** - Know exactly why each song matches  
    ✅ **Multiple Reasoning Paths** - See step-by-step AI thinking  
    ✅ **Confidence Scoring** - Understand AI certainty levels  
    ✅ **Reliability Tests** - Built-in evaluation framework  
    ✅ **Professional UI** - Beautiful, intuitive interface  
    ✅ **RAG Enhancement** - Rich contextual recommendations  
    """)
    
    st.divider()
    
    col_about1, col_about2, col_about3 = st.columns(3)
    with col_about1:
        st.metric("Songs in Catalog", len(songs))
    with col_about2:
        st.metric("Scoring Features", 7)
    with col_about3:
        st.metric("AI Modules", 3)
