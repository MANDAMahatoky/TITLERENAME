# TitleRename

Renomme des images avec le titre lu par OCR (Tesseract + Streamlit).

## Installation
1. Installer Python 3.10+ et Tesseract OCR.
2. Télécharger les langues (eng, fra) depuis https://github.com/tesseract-ocr/tessdata
   et adapter `TESSDATA_PREFIX` dans `app.py`.
3. `python -m pip install -r requirements.txt`

## Lancer
`python -m streamlit run app.py`