#!/bin/bash
# Launch the Semantic BI Layer demo application
cd "$(dirname "$0")"
pip install -q -r requirements.txt
streamlit run app/main.py --server.port 8501
