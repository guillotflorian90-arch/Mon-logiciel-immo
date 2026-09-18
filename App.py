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

def obtenir_infos_marche(nom_ville, type_propriete):
    try:
        # Requête à l'API Géo de l'État
        url_geo = f"https://api.gouv.fr{nom_ville.strip()}&fields=code,population,codeDepartement&limit=5"
        reponse_geo = requests.get(url_geo, timeout=5).json()
        
        # SÉCURITÉ FIXE : Si l'API ne renvoie rien ou une liste vide
        if not reponse_geo or len(reponse_geo) == 0: 
            return None
        
        # CORRECTION DÉFINITIVE : On extrait le premier élément [0] de la liste de résultats
        commune = reponse_geo[0]
        pop = commune.get('population', 0)
        code_dept = commune['codeDepartement']
        
        # Calcul des prix selon la taille de la commune
        f_taille = 1.2 if pop > 100000 else (1.0 if pop > 20000 else 0.8)
        prix_base = 4500 * f_taille if type_propriete == "Appartement" else 4900 * f_taille
        
        # Ajustement des zones tendues
        if code_dept in ['75', '92', '93', '94']: prix_base *= 2.1
        elif code_dept in ['06', '13', '83']: prix_base *= 1.25
        
        pm = int(prix_base)
        
        # Statistiques Insee simulées de manière cohérente pour la zone
        tx_locataires = "52.7 %" if code_dept == "06" else "42.5 %"
        part_rp = "66.2 %" if code_dept == "06" else "81.0 %"
        part_rs = "23.3 %" if code_dept == "06" else "11.5 %"
        evo_pop = "+4.0 %" if pop > 50000 else "+1.2 %"
        
        return {
            "nom": commune['nom'], "pm": pm, "pb": int(pm*0.75), "ph": int(pm*1.45), 
            "pop": pop, "dept": code_dept, "evo": evo_pop, "loc": tx_locataires, 
            "rp": part_rp, "rs": part_rs
        }
    except Exception as e:
        return None

st.title("📊 Assistant Immobilier National")
o1, o2 = st.tabs(["🔍 1. Base Nationale", "🏗️ 2. Simulateur"])

# Valeurs de départ (Nice)
if "infos" not in st.session_state:
    st.session_state["infos"] = {
        "nom": "Nice", "pm": 4850, "pb": 3300, "ph": 7200, "pop": 340000, 
        "dept": "06", "evo": "+4.0 %", "loc": "52.7 %", "rp": "66.2 %", "rs": "23.3 %"
    }

with o1:
    v_saisie = st.text_input("Ville :", value="Nice")
    t_bien = st.selectbox("Type :", ["Appartement", "Maison"])
    
    if st.button("🚀 Interroger les bases"):
        res = obtenir_infos_marche(v_saisie, t_bien)
        if res: 
            st.session_state["infos"] = res
            st.rerun()
        else: 
            st.error("Ville introuvable. Vérifiez l'orthographe.")
    
    inf = st.session_state["infos"]
    
    # Affichage du tableau complet
    df = pd.DataFrame({
        "Critères de Sélection": [
            "Ville / Quartier", "Prix Moyen / m²", "Prix BAS", "Prix HAUT", 
            "Évolution Pop.", "Taux Locataires", "Part Rés. Principales", "Part Rés. Secondaires"
        ],
        "Données": [
            inf['nom'], f"{inf['pm']:,} €", f"{inf['pb']:,} €", f"{inf['ph']:,} €", 
            inf['evo'], inf['loc'], inf['rp'], inf['rs']
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
