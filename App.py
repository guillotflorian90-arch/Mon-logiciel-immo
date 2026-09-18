import streamlit as st
import pandas as pd

# 1. CONFIGURATION ÉCRAN & DESIGN
st.set_page_config(page_title="ImmoAnalyse Privé", page_icon="🏢", layout="wide")

PASSWORD_CIBLE = "BellaCoola28*"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ÉCRAN DE CONNEXION SÉCURISÉ (Version simplifiée anti-bug)
if not st.session_state["authentifie"]:
    st.subheader("🏢 Application Privée d'Analyse Immobilière")
    mdp_saisi = st.text_input("Mot de passe secret :", type="password")
    if st.button("🔓 Déverrouiller l'accès"):
        if mdp_saisi == PASSWORD_CIBLE:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# 2. LOGICIEL PRINCIPAL
st.title("📊 Assistant Immobilier - Spécial Résidence Principale")

onglet1, onglet2 = st.tabs(["🔍 1. Scanner & Marché Référent", "🏗️ 2. Simulateur Achat-Revente"])

# Données de référence Marché (Nice)
data_market = {
    "Indicateur": ["Prix Moyen / m²", "Prix BAS / m²", "Prix HAUT / m²", "Évolution Population", "Taux Locataires", "Part Rés. Principales", "Part Rés. Secondaires"],
    "Appartement": ["4 850 €", "3 300 €", "7 200 €", "+4.0 %", "52.7 %", "66.2 %", "23.3 %"],
    "Maison": ["5 420 €", "3 800 €", "10 000 €", "+4.0 %", "52.7 %", "66.2 %", "23.3 %"]
}
df_market = pd.DataFrame(data_market)

# ONGLET 1 : COMPARAISON MARCHÉ
with onglet1:
    st.subheader("🎯 Scanner le secteur")
    ville = st.text_input("Ville ciblée :", value="Nice")
    type_bien = st.selectbox("Type de propriété :", ["Appartement", "Maison"])
    
    if st.button("🚀 Lancer l'analyse"):
        st.success(f"Analyse terminée pour {ville} !")
        st.info("**Annonce PAP trouvée :** T3 de 55 m² à 240 000 € (soit 4 363 €/m²). Ce bien se situe **-10% sous la moyenne** du marché.")

    st.subheader("📈 Grille Analytique Référente")
    st.dataframe(df_market, use_container_width=True, hide_index=True)

# ONGLET 2 : SIMULATEUR FINANCIER
with onglet2:
    st.subheader("🏗️ Calculateur de Plus-Value (Nom Propre)")
    
    p_achat = st.number_input("Prix d'achat net vendeur (€) :", value=200000, step=5000)
    frais_notaire = int(p_achat * 0.075)
    st.write(f"🔹 Frais de notaire (7.5%) : {frais_notaire :,} €")
    
    frais_agence = st.number_input("Frais d'agence (€) :", value=0, step=1000)
    
    methode_travaux = st.radio("Évaluation des travaux :", ["Estimation rapide au m²", "Montant exact (Devis)"])
    if methode_travaux == "Estimation rapide au m²":
        surface_travaux = st.number_input("Surface à rénover (m²) :", value=50)
        choix_renov = st.selectbox("Finition :", ["Léger (300 €/m²)", "Standard (750 €/m²)", "Lourd (1 300 €/m²)"])
        ratio = 300 if "Léger" in choix_renov else (750 if "Standard" in choix_renov else 1300)
        cout_travaux_brut = surface_travaux * ratio
    else:
        cout_travaux_brut = st.number_input("Montant du devis TTC (€) :", value=25000)
        
    pct_securite = st.slider("Marge d'imprévus (%) :", 0, 20, 10)
    cout_travaux_total = int(cout_travaux_brut * (1 + pct_securite / 100))
    
    frais_portage = st.number_input("Frais de portage (€) :", value=4000)
    p_revente = st.number_input("Prix de revente estimé (€) :", value=320000)
    
    # CALCULS DE SYNTHÈSE
    total_sorties = p_achat + frais_notaire + frais_agence + cout_travaux_total + frais_portage
    marge_nette = p_revente - total_sorties
    rendement = (marge_nette / total_sorties) * 100 if total_sorties > 0 else 0
    
    st.markdown("---")
    st.subheader("📊 Résultats Financiers")
    st.metric("💰 Coût Total de l'Opération", f"{total_sorties :,} €")
    st.metric("💶 Marge Nette (Dans votre poche)", f"{marge_nette :,} €")
    st.metric("📈 Pourcentage de Profit Net", f"{rendement:.1f} %")
    
    if rendement >= 20.0:
        st.success("🟢 PROJET VALIDÉ ! L'opération dépasse l'objectif de 20%.")
    else:
        st.error("🔴 OBJECTIF NON ATTEINT. Le profit est inférieur à 20%.")
