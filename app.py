import streamlit as st
from chatbot import Chatbot
import os
from tfidf_search import TFIDFSearcher

st.set_page_config(page_title="Startup Compliance Advisor", page_icon="⚖️", layout="wide")

def init_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chatbot' not in st.session_state:
        # Load default bundled dataset on startup
        local_path = os.path.join(os.path.dirname(__file__), 'Enriched_Legal_Compliances_Dataset_10000.csv')
        st.session_state.chatbot = Chatbot(local_path)
        st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
    if 'gpt_enabled' not in st.session_state:
        st.session_state.gpt_enabled = False

def main():
    init_state()
    st.title("⚖️ Startup Compliance Advisor")
    st.markdown(
        "<small style='color:gray;'>Ask about legal compliance for Indian startups — default dataset already loaded.</small>",
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.header("Dataset & Settings")
        st.markdown("Upload CSV, load bundled dataset, or provide an external CSV URL.")

        uploaded = st.file_uploader('Upload compliance CSV', type=['csv'])
        url = st.text_input('Or dataset URL (raw CSV link)', value='')

        if uploaded is not None:
            st.session_state.chatbot = Chatbot(uploaded)
            st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
            st.success('✅ Dataset loaded from upload.')

        if st.button('Load bundled dataset (default)'):
            local_path = os.path.join(os.path.dirname(__file__), 'Enriched_Legal_Compliances_Dataset_10000.csv')
            st.session_state.chatbot = Chatbot(local_path)
            st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
            st.success('✅ Bundled dataset loaded.')

        if url:
            try:
                st.session_state.chatbot = Chatbot(url)
                st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
                st.success('✅ Dataset loaded from URL.')
            except Exception as e:
                st.error(f'❌ Failed to load from URL: {e}')

        st.markdown('---')
        # GPT Toggle
        st.session_state.gpt_enabled = st.checkbox("Enable GPT Enhancement", value=st.session_state.gpt_enabled)

        if st.session_state.chatbot and st.session_state.chatbot.data is not None:
            st.success(f"📊 Database ready: {len(st.session_state.chatbot.data)} records")
        else:
            st.warning('⚠️ No dataset loaded.')

    # Chat UI
    st.header('💬 Ask about Legal Compliance')
    query = st.text_input('Enter your question (e.g., What is DIR-3 KYC?)', key='query_input')
    if st.button('🔍 Search'):
        q = query.strip()
        if not q:
            st.warning('Please enter a question.')
        else:
            st.session_state.messages.append({'role':'user','content':q})
            if st.session_state.chatbot is None or st.session_state.chatbot.data is None:
                resp = '⚠️ No dataset loaded. Please upload, load bundled dataset or provide URL.'
            else:
                if st.session_state.searcher is None:
                    st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
                with st.spinner('Searching...'):
                    top = st.session_state.searcher.search(q, top_k=3)
                    if not top:
                        resp = "Sorry, no matching compliance found. Try specific form names like DIR-3 KYC, AOC-04, MGT-07, ADT-01."
                    else:
                        resp = st.session_state.chatbot.format_compliance_info(top[0])
                        if len(top) > 1:
                            resp += '\n\n**🔗 Related Compliances:**'
                            for i, r in enumerate(top[1:], 1):
                                resp += f"\n{i}. **{r.get('Form Name','N/A')}** - {r.get('Compliance Title','N/A')}"

                        # Apply GPT enhancement if enabled
                        if st.session_state.gpt_enabled:
                            try:
                                enhanced = st.session_state.chatbot._enhance_with_gpt(q, resp)
                                if enhanced and enhanced.strip():
                                    resp = enhanced
                            except Exception as e:
                                st.warning(f"⚠️ GPT enhancement failed: {e}")

            st.session_state.messages.append({'role':'assistant','content':resp})

    # Render chat history
    for msg in st.session_state.messages:
        if msg.get('role') == 'user':
            st.markdown(f"**You:** {msg.get('content')}")
        else:
            st.info(msg.get('content'))

if __name__ == '__main__':
    main()
