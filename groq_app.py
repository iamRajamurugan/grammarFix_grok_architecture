import streamlit as st
from groq import Groq
import time

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Synthium Suite Grammar Checker", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

def inject_custom_css():
    """Injects custom CSS for a premium application look and feel."""
    st.markdown("""
        <style>
        /* Hide default Streamlit footer */
        footer {visibility: hidden;}
        
        /* Premium Text Area Styling */
        .stTextArea textarea { 
            border-radius: 12px; 
            border: 1px solid #e0e0e0;
            box-shadow: inset 0px 2px 4px rgba(0,0,0,0.02); 
            font-size: 16px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        .stTextArea textarea:focus {
            border-color: #ff4b4b;
            box-shadow: 0px 0px 8px rgba(255, 75, 75, 0.2);
        }
        
        /* Premium Button Styling */
        .stButton>button { 
            border-radius: 12px; 
            font-weight: 600; 
            font-size: 16px;
            padding: 10px 24px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1); 
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); 
        }
        .stButton>button:hover { 
            transform: translateY(-2px); 
            box-shadow: 0px 6px 15px rgba(0,0,0,0.15); 
        }
        .stButton>button:active {
            transform: translateY(0px);
        }
        
        /* Header styling */
        h1 {
            background: -webkit-linear-gradient(45deg, #ff4b4b, #ff904b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        /* Metric container styling */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #ff4b4b;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# CONFIGURATION & SETUP
# ==========================================

#GROQ_API_KEY = "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"
TARGET_MODEL = "llama-3.1-8b-instant"

# Initialize Client
@st.cache_resource
def get_groq_client():
    """Caches the Groq client initialization to prevent reconnects on every re-render."""
    return Groq(api_key=GROQ_API_KEY)

groq_client = get_groq_client()

# ==========================================
# UI COMPONENTS
# ==========================================
def render_sidebar():
    """Renders the application sidebar with metadata and settings."""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/13/Streamlit_logo.png", width=150)
        st.markdown("### ⚙️ App Metadata")
        st.info(f"**Engine:** Groq LPU™\n\n**Model:** `{TARGET_MODEL}`\n\n**Latency:** Ultra-Low")
        
        st.markdown("### 💡 How it works")
        st.markdown(
            "This application leverages Groq's specialized hardware ("
            "Language Processing Units) to achieve inference speeds "
            "that are physically impossible on traditional GPUs. "
            "The result is instant grammar correction."
        )
        
        st.markdown("---")
        st.caption("Deployed with Streamlit by Rajamurugan")

def main():
    """Main application layout and execution logic."""
    inject_custom_css()
    render_sidebar()
    
    # Header Module
    st.title("⚡ Synthium Suite Grammar Checker")
    st.markdown("Ultra-fast, context-aware grammar correction powered by Groq LPU architecture.")
    st.markdown("---")

    # Workspace columns
    col1, col2 = st.columns([1, 1], gap="large")

    # ----------------Left Workspace----------------
    with col1:
        st.markdown("### 📝 Draft Workspace")
        user_input = st.text_area(
            "Source Text", 
            height=300, 
            label_visibility="collapsed", 
            placeholder="Paste your rough draft here..."
        )
        
        # Word count metric for UX completion
        word_count = len(user_input.split()) if user_input.strip() else 0
        st.caption(f"Input Word Count: **{word_count}** words")
        
        st.markdown("<br>", unsafe_allow_html=True)
        fix_button = st.button("✨ Refine & Polish", type="primary", use_container_width=True)

    # ----------------Right Workspace----------------
    with col2:
        st.markdown("### ✅ Final Output")
        
        if fix_button:
            if not user_input.strip():
                st.warning("⚠️ Please provide some text in the Draft Workspace first.")
                return

            # system_prompt = (
            #     "You are an expert copyeditor. Fix all grammar, spelling, tense, and punctuation errors. "
            #     "Improve flow but keep the original meaning. Respond ONLY with the final corrected text. "
            #     "Do not include quotes, explanations, or conversational filler."
            # )
            system_prompt = (
                "You are an expert copyeditor. Fix all grammar, spelling, tense, and punctuation errors. "
                "Improve flow but keep the original meaning. Respond ONLY with the final corrected text. "
                "Correct only grammar and spelling mistakes."
                "Do not rephrase or improve wording."
                "If text is correct, return it unchanged."
                "Return only the corrected text."
                "Do not include quotes, explanations, or conversational filler."
            )
            
            try:
                start_time = time.time()
                
                with st.spinner("Initializing LPU Compute & Refining text..."):
                    # API Call
                    stream = groq_client.chat.completions.create(
                        model=TARGET_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        temperature=0.01, # Lowered for maximum consistency
                        stream=True
                    )
                
                def stream_generator():
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                # Stream Output permanently to the view (not hidden behind a button)
                output_container = st.empty()
                output_container.write_stream(stream_generator)
                
                elapsed_time = time.time() - start_time
                
                # Display professional metrics persistently
                st.markdown("---")
                st.success("✅ **Optimization Complete!**")
                m1, m2 = st.columns(2)
                m1.metric(label="⏱️ Compute Time", value=f"{elapsed_time:.3f} s")
                m2.metric(label="⚡ Speed Rating", value="Blazing Fast")
                
                st.toast("Text successfully refined!", icon="🎉")
                
            except Exception as e:
                st.error(f"System Error: {str(e)}")
                st.info("Please verify your API key and network connection.")

if __name__ == "__main__":
    main()