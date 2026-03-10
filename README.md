# Schengen 90/180 Tracker

A Streamlit application that helps travellers calculate their used and remaining Schengen days under the 90/180 rule.  
Created and maintained by **Julian Alexander Colling** under **New Image Designs**.

---

## Overview

The Schengen 90/180 rule can be confusing, especially when managing multiple trips across different months. This tool provides a clear, accurate breakdown of:

- Days spent in the Schengen area
- Days remaining before reaching the 90‑day limit
- A rolling 180‑day window calculation
- Validation for overlapping or invalid trips
- A clean, mobile‑friendly interface

---

## Features

- Add multiple trips with entry and exit dates  
- UK‑style date formatting (DD/MM/YYYY)  
- Automatic validation for:
  - Exit before entry  
  - Overlapping trips  
- Rolling 180‑day window calculation  
- Remaining days forecast  
- Next breach date prediction  
- Trip summaries  
- Hosted on Hugging Face Spaces  

---

## Live App

Use the app here:  
**https://huggingface.co/spaces/juliancolling/schengen-tracker**

---

## Run Locally

```bash
git clone https://github.com/juliancolling/schengen-tracker
cd schengen-tracker

python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

streamlit run schengen_tracker_app.py
