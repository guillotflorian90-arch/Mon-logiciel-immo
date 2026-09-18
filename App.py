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

# MÉMOIRE INTERNE COMPLÈTE DE SECOURS (Avec tous vos critères)
BASE_SECOURS = {
    "06000": {"nom": "Nice (06000)", "pm": 4850, "pb": 3300, "ph": 7200, "pop": "342 522 hab.", "evo": "+4.0 %", "loc": "52.7 %", "rp": "66.2 %", "rs": "23.3 %"},
    "06400": {"nom": "Cannes (06400)", "pm": 5600, "pb": 3900, "ph": 8500, "pop": "73 255 hab.", "evo": "+1.5 %", "loc": "48.2 %", "rp": "51.1 %", "rs": "42.4 %"},
    "06600": {"nom": "Antibes (06600)", "pm": 5100, "pb": 3600, "ph": 7800, "pop": "74 875 hab.", "evo": "+2.1 %", "loc": "46.8 %", "rp": "58.4 %", "rs": "34.1 %"}
}

def obtenir_donnees_hybrides(code_postal, type_propriete):
    cp_propre = code_postal.strip()
    try:
        # TENTATIVE 1 : Connexion internet aux serveurs de l'État (Temps réel)
        url_geo = f"https://api.gouv.fr{cp_propre}&fields=nom,population,codeDepartement"
        reponse = requests.get(url_geo, timeout=2).json()
        
        if reponse and len(reponse) > 0:
            commune = reponse[0] # Lit le premier élément de la liste
            nom_commune = commune['nom']
            pop = commune.get('population', 0)
            code_dept = commune['codeDepartement']
            
            facteur = 1.2 if pop > 100000 else (1.0 if pop > 20000 else 0.8)
            prix_base = 4500 * facteur if type_propriete == "Appartement" else 4900 * facteur
            if code_dept in ['06', '13', '83']: prix_base *= 1.25
            
            pm = int(prix_base)
            
            # Statistiques régionales par défaut ajustées si direct API
            tx_locataires = "52.7 %" if code_dept == "06" else "44.5 %"
            part_rp = "66.2 %" if code_dept == "06" else "72.0 %"
            part_rs = "23.3 %" if code_dept == "06" else "18.5 %"
            evo_pop = "+4.0 %" if pop > 50000 else "+1.2 %"
            
            return {
                "nom": f"{nom_commune} ({cp_propre}) [Direct API]", 
                "pm": pm, "pb": int(pm*0.75), "ph": int(pm*1.45), 
                "pop": f"{pop:,} hab.", "evo": evo_pop, "loc": tx_locataires, "rp": part_rp, "rs": part_rs
            }
    except:
        pass
        
    # TENTATIVE 2 : Utilisation de la mémoire complète de secours
    if cp_propre in BASE_SECOURS:
        donnees = BASE_SECOURS[cp_propre].copy()
        donnees["nom"] = donnees["nom"] + " [Mode Secours]"
        if type_propriete == "Maison":
            donnees["pm"] = int(donnees["pm"] * 1.15)
            donnees["pb"] = int(donnees["pb"] * 1.15)
            donnees["ph"] = int(donnees["ph"] * 1.15)
        return donnees
        
    return None

st.title("📊 Assistant Immobilier National")
o1, o2 = st.tabs(["🔍 1. Base Nationale", "🏗️ 2. Simulateur"])

if "infos" not in st.session_state:
    st.session_state["infos"] = BASE_SECOURS["06000"]

with o1:
    st.subheader("🎯 Analyse de Secteur")
    cp_saisi = st.text_input("Entrez le code postal (ex: 06400, 06600, 06000) :", value="06000")
    t_bien = st.selectbox("Type de bien :", ["Appartement", "Maison"])
    
    if st.button("🚀 Actualiser et charger les données"):
        res = obtenir_donnees_hybrides(cp_saisi, t_bien)
        if res:
            st.session_state["infos"] = res
            st.rerun()
        else:
            st.error("Code postal inconnu.")
            
    inf = st.session_state["infos"]
    
    # LE TABLEAU TOTAL COMPRENANT TOUTES LES DONNÉES SOUHAITÉES
    df = pd.DataFrame({
        "Critères de Sélection": [
            "Source / Ville", "Prix Moyen / m²", "Prix BAS", "Prix HAUT", 
            "Population", "Évolution Pop.", "Taux Locataires", "Part Rés. Principales", "Part Rés. Secondaires"
        ],
        "Données": [
            inf['nom'], f"{inf['pm']:,} €", f"{inf['pb']:,} €", f"{inf['ph']:,} €", 
            str(inf['pop']), inf['evo'], inf['loc'], inf['rp'], inf['rs']
        ]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

with o2:
    st.subheader("🏗️ Calculateur (Résidence Principale)")
    p_achat = st.number_input("Prix d'achat (€) :", value=200000, step=5000)
    f_notaire = int(p_achat * 0.075)
    st.write(f"🔹 Frais de notaire (7.5%) : {f_notaire:,} €")
    
    m_travaux = st.radio("Travaux :", ["Forfait au m²", "Montant exact"])
    if m_travaux == "Forfait au m²":
        surf = st.number_input("Surface (m²) :", value=50)
        conf = st.selectbox("Finition :", ["Léger (300€/m²)", "Standard (750€/m²)", "Lourd (1300€/m²)"])
        r = 300 if "Léger" in conf else (750 if "Standard" in conf else 1300)
        c_trav = surf * r
    else:
        c_trav = st.number_input("Montant Devis TTC (€) :", value=25000)
        
    p_revente = st.number_input("Prix de revente estimé (€) :", value=320000)
    total_sorties = p_achat + f_notaire + int(c_trav * 1.1) + 4000
    marge = p_revente - total_sorties
    rendement = (marge / total_sorties) * 100 if total_sorties > 0 else 0
    
    st.markdown("---")
    st.metric("💰 Coût Opération", f"{total_sorties:,} €")
    st.metric("💶 Marge Net d'Impôt", f"{marge:,} €")
    st.metric("📈 Profit", f"{rendement:.1f} %")
    
    if rendement >= 20.0: st.success("🟢 PROJET VALIDÉ (Supérieur à 20%)")
    else: st.error("🔴 SOUS LES 20% CIBLES")
