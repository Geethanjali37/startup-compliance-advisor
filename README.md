
Startup Compliance Advisor - Final bundle (TF-IDF + optional GPT + Admin)
Files:
- app.py (main app)
- chatbot.py (dataset loader and GPT enhancer)
- tfidf_search.py (TF-IDF searcher)
- admin_app.py (admin utilities)
- Enriched_Legal_Compliances_Dataset_10000.csv (10k dataset included locally)
- requirements.txt

Deployment instructions:
1. Extract this archive and push to GitHub or upload to Streamlit Cloud.
2. Streamlit will install dependencies from requirements.txt.
3. Open the app. In the sidebar you can 'Load bundled dataset' to load the included 10k CSV, or upload a CSV or provide a raw CSV URL.
4. To enable GPT hybrid mode, add OPENAI_API_KEY in Streamlit Secrets (do NOT commit the key to the repo).
5. For smaller repo size, you may delete the CSV from the repo after first deployment and use an external hosting URL or upload at runtime.

Note: This bundle includes the 10k dataset locally for convenience. If you want me to host the CSV externally (GitHub Release / Google Drive) and remove it from the repo, tell me and I will upload and provide a raw URL, then create a new zip without the CSV included.
