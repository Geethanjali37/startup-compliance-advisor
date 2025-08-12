import streamlit as st
import pandas as pd
import os
from chatbot import Chatbot
import openai

# Page configuration
st.set_page_config(
    page_title="Startup Compliance Advisor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# Get query parameters (no deprecation warning)
query_params = st.query_params

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'chatbot' not in st.session_state:
        # Initialize chatbot with dataset path
        dataset_path = 'attached_assets/Enriched_Legal_Compliances_Dataset_10000_1754808121550.csv'
        st.session_state.chatbot = Chatbot(dataset_path)
    
    if 'clear_input_flag' not in st.session_state:
        st.session_state.clear_input_flag = False

def clear_input():
    """Callback to clear the input field."""
    st.session_state.clear_input_flag = True

def gpt_enhance(query, base_answer):
    """Enhance the base answer with GPT if API key is available."""
    if not openai.api_key:
        return base_answer  # Skip if no key
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful legal compliance assistant for Indian startups."},
                {"role": "user", "content": f"Enhance and explain this compliance info in simpler terms:\n\n{base_answer}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return base_answer + f"\n\n⚠️ GPT Enhancement failed: {str(e)}"

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("⚖️ Startup Compliance Advisor")
    st.markdown(
        "<small style='color:gray;'>Ask about legal compliance for Indian startups — dataset already loaded.</small>",
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This AI assistant helps Indian startup founders understand and manage legal compliance requirements.
        
        **Features:**
        - Intelligent search through 10,000+ compliance records
        - Natural language query understanding
        - Structured compliance information
        - Filing guidance and portal links
        - Optional GPT enhancement if `OPENAI_API_KEY` is set
        """)
        
        st.header("Sample Queries")
        st.markdown("""
        - "What is DIR-3 KYC?"
        - "Penalty for missing MGT-07?"
        - "How to file AOC-04?"
        - "GST return filing requirements"
        - "Due date for AOC-04"
        - "What is ADT-01?"
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Display dataset status
        if st.session_state.chatbot and st.session_state.chatbot.data is not None:
            st.success(f"✅ Database loaded: {len(st.session_state.chatbot.data)} records")
        else:
            st.error("❌ Database not loaded")
        
        # GPT status
        if openai.api_key:
            st.info("✨ GPT enhancement enabled")
        else:
            st.warning("GPT enhancement disabled — add `OPENAI_API_KEY` in Streamlit Secrets to enable")

    # Main interface
    st.header("💬 Ask about Legal Compliance")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input field
    col1, col2 = st.columns([4, 1])
    with col1:
        input_value = "" if st.session_state.clear_input_flag else st.session_state.get("query_input_value", "")
        query = st.text_input(
            "Ask about legal compliance",
            placeholder="e.g., What is DIR-3 KYC?",
            key="query_input",
            value=input_value
        )
    with col2:
        search_button = st.button("🔍 Search", type="primary", on_click=clear_input)
    
    if st.session_state.clear_input_flag:
        st.session_state.clear_input_flag = False
        st.session_state.query_input_value = ""
    else:
        st.session_state.query_input_value = query
    
    if search_button and query.strip():
        process_query(query)

def process_query(query: str):
    """Process a user query and display the response."""
    st.session_state.messages.append({"role": "user", "content": query})
    
    if st.session_state.chatbot is None:
        error_msg = "❌ Chatbot not initialized. Please check dataset path."
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        return
    
    with st.spinner("Searching compliance database..."):
        try:
            answer = st.session_state.chatbot.search_and_respond(query)
            answer = gpt_enhance(query, answer)  # Enhance with GPT if key available
            
            with st.container():
                st.info(answer)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            error_msg = f"❌ Sorry, I encountered an error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()
