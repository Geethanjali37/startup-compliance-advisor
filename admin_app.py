
def admin_page(st, session_state):
    st.title('Admin Panel - Startup Compliance Advisor')
    st.markdown('Upload a new dataset, preview it, and control GPT mode.')
    uploaded = st.file_uploader('Upload new CSV to replace dataset (admin upload)', type=['csv'], key='admin_upload')
    if uploaded is not None:
        from chatbot import Chatbot
        session_state.chatbot = Chatbot(uploaded)
        session_state.searcher = None
        st.success(f'Admin: uploaded dataset with {len(session_state.chatbot.data)} records.')
    if session_state.chatbot and session_state.chatbot.data is not None:
        st.subheader('Dataset preview (first 5 rows)')
        st.dataframe(session_state.chatbot.data.head())
        st.subheader('Dataset stats')
        st.write({'rows': len(session_state.chatbot.data), 'columns': list(session_state.chatbot.data.columns)})
    st.markdown('---')
    st.write('To toggle GPT mode, add/remove OPENAI_API_KEY in Streamlit Secrets.')
