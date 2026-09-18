import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ImmoAnalyse Privé", page_icon="🏢", layout="wide")

PASSWORD_CIBLE = "BellaCoola28*"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if not st.session_state["authentifie"]:
    st.subheader("🏢 Application Privée d'Analyse Immobilière")
    mdp_saisi = st.text_input("Veuillez saisir le mot de passe secret :", type="password")
    if st.button("🔓 Déverrouiller l'accès"):
        if mdp_saisi == PASSWORD_CIBLE:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# FONCTION API ADRESSE ET ESTIMATION
def obtenir_donnees_api(code_postal, type_propriete):
    cp = code_postal.strip()
    try:
        url = f"https://data.gouv.fr{cp}&postcode={cp}&type=municipality&limit=1"
        reponse = requests.get(url, timeout=3).json()
        if reponse and 'features' in reponse and len(reponse['features']) > 0:
            props = reponse['features']['properties']
            nom_ville = props['city']
            dept = props['context'].split(',')[1].strip()
            
            if dept == "75": prix = 10100
            elif dept in ["92", "94", "78"]: prix = 6100
            elif dept == "06":
                if cp in ["06400", "06250"]: prix = 5750
                elif cp == "06600": prix = 5200
                elif cp == "06790": prix = 4150
                else: prix = 4900
            elif dept in ["13", "83", "69", "33"]: prix = 4400
            else: prix = 2950
            
            if type_propriete == "Maison": prix = int(prix * 1.18)
            
            return {
                "nom": f"{nom_ville} ({cp})", "pm": prix, "pb": int(prix*0.75), "ph": int(pm*1.45) if 'pm' in locals() else int(prix*1.45),
                "pop": "OK", "evo": "+3.8 %", "loc": "52.7 %" if dept == "06" else "41.5 %",
                "rp": "66.2 %" if dept == "06" else "76.0 %", "rs": "23.3 %" if dept == "06" else "14.2 %"
            }
    except: pass
    return {"nom": f"Secteur {cp}", "pm": 4500, "pb": 3200, "ph": 6500, "pop": "--", "evo": "--", "loc": "45%", "rp": "70%", "rs": "20%"}

# STRUCTURE DES ONGLETS
st.title("📊 Assistant Immobilier Tout-en-Un")
o1, o2, o3 = st.tabs(["🔍 1. Base Marché", "🏗️ 2. Simulateur Achat-Revente", "📋 3. Passerelle Annonces"])

if "pm_global" not in st.session_state: st.session_state["pm_global"] = 4500

# ONGLET 1 : BASE MARCHÉ
with o1:
    st.subheader("🎯 Secteur Référent")
    cp_input = st.text_input("Code postal :", value="06000")
    t_bien = st.selectbox("Type de bien :", ["Appartement", "Maison"], key="t1")
    inf = obtenir_donnees_api(cp_input, t_bien)
    st.session_state["pm_global"] = inf["pm"]
    
    df = pd.DataFrame({"Critères": ["Secteur", "Prix Moyen / m²", "Prix BAS", "Prix HAUT", "Taux Locataires", "Part RS"], "Données": [inf['nom'], f"{inf['pm']:,} €", f"{inf['pb']:,} €", f"{inf['ph']:,} €", inf['loc'], inf['rs']]})
    st.dataframe(df, use_container_width=True, hide_index=True)

# ONGLET 2 : SIMULATEUR
with o2:
    st.subheader("🏗️ Calculateur Financier (Nom Propre)")
    p_achat = st.number_input("Prix d'achat net vendeur (€) :", value=200000, step=5000)
    f_notaire = int(p_achat * 0.075)
    f_banque = st.number_input("Frais bancaires (€) :", value=2500)
    
    m_travaux = st.radio("Travaux :", ["Forfait au m²", "Montant exact"])
    if m_travaux == "Forfait au m²":
        surf = st.number_input("Surface (m²) :", value=50, key="s2")
        conf = st.selectbox("Finition :", ["Rafraîchissement (300€/m²)", "Standard (750€/m²)", "Lourd (1300€/m²)"])
        r = 300 if "Rafraîchissement" in conf else (750 if "Standard" in conf else 1300)
        c_trav = surf * r
    else:
        c_trav = st.number_input("Montant devis TTC (€) :", value=25000)
        
    p_revente = st.number_input("Prix de revente estimé (€) :", value=320000)
    total_sorties = p_achat + f_notaire + f_banque + int(c_trav * 1.1) + 4000
    marge = p_revente - total_sorties
    rendement = (marge / total_sorties) * 100 if total_sorties > 0 else 0
    
    st.markdown("---")
    st.metric("💰 Coût global opération", f"{total_sorties:,} €")
    st.metric("💶 Marge bénéficiaire (Net)", f"{marge:,} €")
    st.metric("📈 Profit", f"{rendement:.1f} %")

# ONGLET 3 : LA RECHERCHE EN DIRECT SÉCURISÉE
with o3:
    st.subheader("📋 Générateur de Recherche Immobilière Multi-Sites")
    st.write("Entrez vos critères ci-dessous. Le logiciel va construire les liens de recherche exacts sans risque de blocage informatique.")
    
    cp_s = st.text_input("Code postal visé :", value="06400")
    t_s = st.selectbox("Catégorie :", ["Appartement", "Maison"], key="ts")
    budget_s = st.number_input("Budget Max (€) :", value=300000, step=10000)
    surf_s = st.number_input("Surface Min (m²) :", value=50, step=5)
    
    # Génération des liens de recherche dynamiques réels
    cat_lbc = "1" if t_s == "Appartement" else "2" # Codes catégories Leboncoin
    link_lbc = f"https://leboncoin.fr_{cp_s}&price=min-{budget_s}&square=min-{surf_s}&real_estate_type={cat_lbc}"
    link_bienici = f"https://bienici.com{cp_s}/{t_s}s?prix-max={budget_s}&surface-min={surf_s}"
    link_pap = f"https://pap.fr{t_s}s-{cp_s}-prix-jusqua-{budget_s}-surface-au-moins-{surf_s}"
    
    st.markdown("---")
    st.markdown("### 🚀 Ouvrir les résultats filtrés en 1 clic :")
    
    st.link_button("👉 Ouvrir la recherche sur LEBONCOIN.fr", link_lbc, use_container_width=True)
    st.link_button("👉 Ouvrir la recherche sur BIENICI.com (Agences)", link_bienici, use_container_width=True)
    st.link_button("👉 Ouvrir la recherche sur PAP.fr (Particuliers)", link_pap, use_container_width=True)
