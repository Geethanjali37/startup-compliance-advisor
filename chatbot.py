
import pandas as pd
import re, os, io, requests
from typing import Union
import streamlit as st

def _openai_available():
    try:
        import openai  # type: ignore
        return True
    except Exception:
        return False

class Chatbot:
    def __init__(self, source: Union[str,'UploadedFile']):
        self.data = None
        self.source = source
        self.openai_key = None
        try:
            self.openai_key = st.secrets.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        except Exception:
            self.openai_key = os.getenv('OPENAI_API_KEY')
        self.load_dataset()

    def load_dataset(self):
        try:
            if hasattr(self.source, 'read'):
                self.data = pd.read_csv(self.source)
                st.sidebar.success(f"Loaded {len(self.data)} records from uploaded file.")
            elif str(self.source).startswith('http'):
                # download CSV from URL
                r = requests.get(self.source, timeout=30)
                r.raise_for_status()
                self.data = pd.read_csv(io.StringIO(r.text))
                st.sidebar.success(f"Loaded {len(self.data)} records from URL.")
            else:
                self.data = pd.read_csv(self.source)
                st.sidebar.success(f"Loaded {len(self.data)} records from file: {self.source}")
        except Exception as e:
            st.sidebar.error(f"Error loading dataset: {e}")
            self.data = None

    def format_compliance_info(self, row: pd.Series) -> str:
        def g(k): return row.get(k,'N/A')
        return f"""**📋 {g('Form Name')}** - {g('Compliance Title')}

**📝 Description:** {g('Description')}

**📅 Due Date:** {g('Due Date')}

**💰 Penalty:** {g('Penalty')}

**🏢 Applicable to:** {g('Applicable Entity Types')}

**📊 Frequency:** {g('Frequency')}

**👤 Responsible Party:** {g('Responsible Party')}

**📎 Documents Required:** {g('Documents Required')}

**📋 Filing Steps:** {g('Filing Steps')}

**🌐 Filing Portal:** {g('Filing Portal')}
""".strip()

    def _enhance_with_gpt(self, query: str, base_answer: str) -> str:
        if not self.openai_key:
            return base_answer
        if not _openai_available():
            st.sidebar.warning('openai package not installed; GPT disabled.')
            return base_answer
        try:
            import openai
            openai.api_key = self.openai_key
            prompt = f"""You are a legal compliance assistant for Indian startups.
User question: {query}
Dataset answer: {base_answer}

Please improve the dataset answer with brief, accurate clarifications, actionable steps and links where relevant. Keep it concise and in markdown."""
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini' if 'gpt-4o-mini' in [m.id for m in openai.Model.list().data] else 'gpt-4o',
                messages=[{'role':'system','content':'You are a helpful legal assistant.'},{'role':'user','content':prompt}],
                temperature=0.2,
                max_tokens=400
            )
            # extract message content
            if isinstance(resp, dict):
                choices = resp.get('choices', [])
                if choices:
                    return choices[0].get('message', {}).get('content') or choices[0].get('text') or base_answer
            return base_answer
        except Exception as e:
            st.sidebar.warning(f'GPT enhancement failed: {e}')
            return base_answer
