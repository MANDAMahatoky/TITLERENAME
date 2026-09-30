# -*- coding: utf-8 -*-
"""Renommer des images avec leur titre (OCR) - interface moderne."""

import io
import os
import re
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image
import pytesseract

# Dossier des langues, à définir AVANT tout appel OCR
os.environ["TESSDATA_PREFIX"] = r"C:\Users\maha700550\tessdata"

st.set_page_config(page_title="TitleRename", page_icon="✨", layout="wide")

# ====================== STYLE ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {font-family: 'Inter', sans-serif;}

/* Fond avec lueurs */
.stApp {
    background:
        radial-gradient(900px 500px at 10% -10%, rgba(139,92,246,.25), transparent 60%),
        radial-gradient(800px 500px at 100% 0%, rgba(236,72,153,.18), transparent 60%),
        radial-gradient(700px 500px at 50% 110%, rgba(59,130,246,.15), transparent 60%),
        #0b0b14;
}

/* Masquer l'interface Streamlit par défaut */
#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
.block-container {padding-top: 2rem; max-width: 1150px;}

/* Bandeau */
.hero {
    padding: 34px 38px; border-radius: 24px; margin-bottom: 26px;
    background: linear-gradient(135deg, rgba(139,92,246,.20), rgba(236,72,153,.10));
    border: 1px solid rgba(255,255,255,.10);
    backdrop-filter: blur(18px);
    box-shadow: 0 20px 50px rgba(0,0,0,.35);
}
.pill {
    display: inline-block; padding: 5px 14px; border-radius: 999px;
    font-size: .78rem; font-weight: 600; letter-spacing: .04em;
    color: #c4b5fd; background: rgba(139,92,246,.18);
    border: 1px solid rgba(139,92,246,.35); margin-bottom: 14px;
}
.hero h1 {
    margin: 0; font-size: 2.6rem; font-weight: 800; letter-spacing: -.03em;
    background: linear-gradient(90deg, #fff, #c4b5fd 60%, #f9a8d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p {margin: 10px 0 0; color: #a5a5c0; font-size: 1.05rem;}

/* Compteurs */
.stat {
    padding: 18px 20px; border-radius: 18px;
    background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
    backdrop-filter: blur(12px);
}
.stat .val {font-size: 2rem; font-weight: 800; letter-spacing: -.02em; color: #fff;}
.stat .lab {font-size: .82rem; color: #9a9ab5; text-transform: uppercase;
            letter-spacing: .08em; font-weight: 600;}

/* Cartes des images */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px !important;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.09) !important;
    backdrop-filter: blur(14px);
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,.55) !important;
    box-shadow: 0 16px 40px rgba(139,92,246,.20);
}
[data-testid="stImage"] img {border-radius: 14px; width: 100%;}
.ancien {font-size: .75rem; color: #8a8aa5; word-break: break-all; margin: 8px 0 6px;}
.badge {display: inline-block; font-size: .72rem; font-weight: 600;
        padding: 3px 10px; border-radius: 999px; margin-top: 6px;}
.ok  {color: #6ee7b7; background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.35);}
.warn{color: #fcd34d; background: rgba(245,158,11,.15); border: 1px solid rgba(245,158,11,.35);}

/* Champs de saisie */
.stTextInput input {
    background: rgba(255,255,255,.06) !important; color: #fff !important;
    border: 1px solid rgba(255,255,255,.12) !important; border-radius: 12px !important;
}
.stTextInput input:focus {border-color: #8b5cf6 !important; box-shadow: 0 0 0 3px rgba(139,92,246,.25) !important;}

/* Zone de dépôt */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,.03); border: 2px dashed rgba(139,92,246,.45);
    border-radius: 20px; padding: 30px; transition: all .2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(139,92,246,.08); border-color: #8b5cf6;
}

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: rgba(255,255,255,.04); padding: 6px;
    border-radius: 14px; width: fit-content;
}
.stTabs [data-baseweb="tab"] {border-radius: 10px; padding: 8px 20px; font-weight: 600; color: #a5a5c0;}
.stTabs [aria-selected="true"] {background: rgba(139,92,246,.25); color: #fff;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none;}

/* Boutons */
.stButton > button, .stDownloadButton > button {
    border-radius: 14px; font-weight: 700; padding: .75rem 1.6rem; border: none;
    background: linear-gradient(90deg, #7c3aed, #db2777); color: white;
    box-shadow: 0 10px 28px rgba(124,58,237,.35);
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 14px 34px rgba(219,39,119,.40); color: white;
}

/* Barre latérale */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,.03); border-right: 1px solid rgba(255,255,255,.07);
}
h2, h3 {letter-spacing: -.02em;}
</style>

<div class="hero">
    <span class="pill">✨ OCR AUTOMATIQUE</span>
    <h1>TitleRename</h1>
    <p>Le titre écrit dans l'image devient son nom de fichier. Déposez, vérifiez, téléchargez.</p>
</div>
""", unsafe_allow_html=True)

# ====================== TESSERACT ======================
CHEMINS_TESSERACT = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files\PDF24\tesseract\tesseract.exe",
]
for c in CHEMINS_TESSERACT:
    if Path(c).exists():
        pytesseract.pytesseract.tesseract_cmd = c
        break
else:
    st.error("Tesseract est introuvable. Vérifiez son installation.")
    st.stop()

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# ====================== FONCTIONS ======================
def nettoyer(texte):
    """Rend le texte valide comme nom de fichier Windows."""
    texte = " ".join(texte.split())
    texte = re.sub(r'[<>:"/\\|?*]', "", texte)
    return texte.strip(" .")[:100]


def unique(nom, ext, utilises):
    """Ajoute (1), (2)... si le nom existe déjà."""
    candidat, n = f"{nom}{ext}", 1
    while candidat.lower() in utilises:
        candidat = f"{nom} ({n}){ext}"
        n += 1
    utilises.add(candidat.lower())
    return candidat


@st.cache_data(show_spinner=False)
def lire_titre(octets, langue, partie):
    """Lit le texte dans la partie haute de l'image (mis en cache)."""
    with Image.open(io.BytesIO(octets)) as img:
        largeur, hauteur = img.size
        zone = img.crop((0, 0, largeur, int(hauteur * partie)))
        return nettoyer(pytesseract.image_to_string(zone, lang=langue))


def compteurs(*items):
    """Rangée de compteurs : (valeur, libellé)."""
    for col, (valeur, libelle) in zip(st.columns(len(items)), items):
        col.markdown(
            f'<div class="stat"><div class="val">{valeur}</div>'
            f'<div class="lab">{libelle}</div></div>',
            unsafe_allow_html=True,
        )


# ====================== BARRE LATÉRALE ======================
with st.sidebar:
    st.markdown("### ⚙️ Réglages")
    langues_dispo = [l for l in pytesseract.get_languages(config="") if l != "osd"]
    langues = st.multiselect(
        "Langue(s) du texte", langues_dispo,
        default=["eng"] if "eng" in langues_dispo else langues_dispo[:1],
    )
    langue = "+".join(langues) if langues else "eng"
    partie = st.slider(
        "Zone lue (depuis le haut)", 0.1, 1.0, 0.30, 0.05,
        help="0.30 = les 30 % du haut. 1.0 = toute l'image.",
    )
    st.caption("💡 Titre mal lu ? Augmentez la zone lue.")

onglet1, onglet2 = st.tabs(["📤  Téléverser", "📁  Dossier local"])

# ====================== ONGLET 1 : TÉLÉVERSEMENT ======================
with onglet1:
    st.write("")
    fichiers = st.file_uploader(
        "Glissez-déposez vos images ici",
        type=[e.strip(".") for e in EXTENSIONS],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if not fichiers:
        st.caption("Formats acceptés : JPG, PNG, WEBP, BMP. Plusieurs images à la fois.")
    else:
        with st.spinner("Lecture des titres..."):
            titres = [lire_titre(f.getvalue(), langue, partie) for f in fichiers]

        st.write("")
        compteurs(
            (len(fichiers), "Images"),
            (sum(1 for t in titres if t), "Titres détectés"),
            (sum(1 for t in titres if not t), "Sans texte"),
        )
        st.write("")
        st.markdown("### Vérifiez et corrigez les noms")

        noms = []
        colonnes = st.columns(3)
        for i, (f, titre) in enumerate(zip(fichiers, titres)):
            with colonnes[i % 3].container(border=True):
                st.image(f.getvalue())
                st.markdown(f'<div class="ancien">📄 {f.name}</div>',
                            unsafe_allow_html=True)
                nom = st.text_input(
                    "Nouveau nom", value=titre or Path(f.name).stem,
                    key=f"nom_{f.file_id}_{langue}_{partie}",
                    label_visibility="collapsed",
                )
                if titre:
                    st.markdown('<span class="badge ok">✓ Titre détecté</span>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge warn">⚠ Aucun texte</span>',
                                unsafe_allow_html=True)
            noms.append(nettoyer(nom) or Path(f.name).stem)

        utilises = set()
        tampon = io.BytesIO()
        with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as z:
            for f, nom in zip(fichiers, noms):
                z.writestr(unique(nom, Path(f.name).suffix.lower(), utilises),
                           f.getvalue())

        st.write("")
        st.download_button(
            "⬇️  Télécharger les images renommées (ZIP)",
            data=tampon.getvalue(), file_name="images_renommees.zip",
            mime="application/zip",
        )

# ====================== ONGLET 2 : DOSSIER LOCAL ======================
with onglet2:
    st.write("")
    dossier = st.text_input(
        "Chemin du dossier", r"C:\Users\maha700550\Pictures\mes_images"
    )
    chemin_dossier = Path(dossier)

    if not chemin_dossier.is_dir():
        st.info("Indiquez un dossier existant.")
    else:
        images = sorted(p for p in chemin_dossier.iterdir()
                        if p.suffix.lower() in EXTENSIONS)
        if not images:
            st.warning("Aucune image dans ce dossier.")
        else:
            utilises = {p.name.lower() for p in images}
            propositions = []
            barre = st.progress(0.0, text="Lecture des images...")
            for i, p in enumerate(images):
                titre = lire_titre(p.read_bytes(), langue, partie)
                if titre and titre.lower() != p.stem.lower():
                    utilises.discard(p.name.lower())
                    nouveau = unique(titre, p.suffix.lower(), utilises)
                else:
                    nouveau = p.name
                propositions.append((p, nouveau))
                barre.progress((i + 1) / len(images))
            barre.empty()

            a_renommer = sum(1 for p, n in propositions if p.name != n)
            compteurs((len(images), "Images"), (a_renommer, "À renommer"))
            st.write("")
            st.dataframe(
                [{"Ancien nom": p.name, "Nouveau nom": n} for p, n in propositions],
                hide_index=True,
            )
            st.warning("Le renommage est direct : testez d'abord sur une copie.")

            if st.button("✅  Renommer maintenant"):
                for p, nouveau in propositions:
                    if p.name != nouveau:
                        p.rename(p.with_name(nouveau))
                st.success("Renommage terminé.")
                st.cache_data.clear()