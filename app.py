
import streamlit as st
from chatbot import Chatbot
import os
from tfidf_search import TFIDFSearcher

st.set_page_config(page_title="Startup Compliance Advisor", page_icon="⚖️", layout="wide")

def init_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'searcher' not in st.session_state:
        st.session_state.searcher = None
    if 'query' not in st.session_state:
        st.session_state.query = ""

def main():
    init_state()
    st.title("⚖️ Startup Compliance Advisor")
    st.markdown("Upload a compliance CSV, load the included dataset, or provide a dataset URL. Optional GPT enhancement if OPENAI_API_KEY is set in Streamlit Secrets.")

    with st.sidebar:
        st.header("Dataset & Settings")
        st.markdown("You can: upload CSV, load local bundled file, or provide an external CSV URL.")
        uploaded = st.file_uploader('Upload compliance CSV', type=['csv'])
        url = st.text_input('Or dataset URL (raw CSV link)', value='')
        if uploaded is not None:
            st.session_state.chatbot = Chatbot(uploaded)
            st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
            st.success('Dataset loaded from upload.')
        if st.button('Load bundled dataset (local)'):
            local_path = os.path.join(os.path.dirname(__file__), 'Enriched_Legal_Compliances_Dataset_10000.csv')
            st.session_state.chatbot = Chatbot(local_path)
            st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
            st.success('Bundled dataset loaded.')
        if url:
            try:
                st.session_state.chatbot = Chatbot(url)
                st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
                st.success('Dataset loaded from URL.')
            except Exception as e:
                st.error(f'Failed to load from URL: {e}')
        st.markdown('---')
        openai_key = None
        try:
            openai_key = st.secrets.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        except Exception:
            openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            st.success('GPT enhancement: ENABLED')
        else:
            st.info('GPT enhancement: DISABLED (add OPENAI_API_KEY in Streamlit Secrets to enable)')
        if st.session_state.chatbot and st.session_state.chatbot.data is not None:
            st.success(f"Database ready: {len(st.session_state.chatbot.data)} records")
        else:
            st.warning('No dataset loaded.')
        if st.button('Open Admin Page'):
            st.experimental_set_query_params(page='admin')
            st.experimental_rerun()

    # Admin routing
    params = st.experimental_get_query_params()
    if params.get('page', [''])[0] == 'admin':
        st.experimental_set_query_params()  # clear params after entering admin
        from admin_app import admin_page
        admin_page(st, st.session_state)
        return

    st.header('Ask about legal compliance')
    query = st.text_input('Enter your question (e.g., What is DIR-3 KYC?)', value=st.session_state.get('query',''), key='query_input')
    if st.button('Search'):
        q = query.strip()
        if not q:
            st.warning('Please enter a question.')
        else:
            st.session_state.messages.append({'role':'user','content':q})
            if st.session_state.chatbot is None or st.session_state.chatbot.data is None:
                resp = '⚠️ No dataset loaded. Please upload, load bundled dataset or provide URL.'
                st.session_state.messages.append({'role':'assistant','content':resp})
            else:
                # Use TF-IDF searcher if available
                if st.session_state.searcher is None:
                    st.session_state.searcher = TFIDFSearcher(st.session_state.chatbot.data)
                with st.spinner('Searching...'):
                    # get top rows and format using chatbot's formatter
                    top = st.session_state.searcher.search(q, top_k=3)
                    if not top:
                        resp = "Sorry, no matching compliance found. Try specific form names like DIR-3 KYC, AOC-04, MGT-07, ADT-01."
                    else:
                        resp = st.session_state.chatbot.format_compliance_info(top[0])
                        if len(top) > 1:
                            resp += '\n\n**🔗 Related Compliances:**'
                            for i, r in enumerate(top[1:], 1):
                                resp += f"\n{i}. **{r.get('Form Name','N/A')}** - {r.get('Compliance Title','N/A')}"
                        # optionally enhance with GPT
                        try:
                            enhanced = st.session_state.chatbot._enhance_with_gpt(q, resp)
                            if enhanced and enhanced.strip():
                                resp = enhanced
                        except Exception:
                            pass
                    st.session_state.messages.append({'role':'assistant','content':resp})
            st.session_state.query = ''

    # Render messages
    for msg in st.session_state.messages:
        role = msg.get('role','user')
        if role == 'user':
            st.markdown(f"**You:** {msg.get('content')}")
        else:
            st.info(msg.get('content'))

if __name__ == '__main__':
    main()
