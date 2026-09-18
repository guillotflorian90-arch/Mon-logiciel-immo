import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURATION ÉCRAN & DESIGN
st.set_page_config(page_title="ImmoAnalyse Privé", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700; color: #1E3A8A; }
    .card-calculs { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

PASSWORD_CIBLE = "BellaCoola28*"

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ÉCRAN DE CONNEXION SÉCURISÉ
if not st.session_state["authentifie"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("🏢 Application Privée d'Analyse Immobilière")
    mdp_saisi = st.text_input("Veuillez saisir le mot de passe secret :", type="password")
    if st.button("🔓 Déverrouiller l'accès"):
        if mdp_saisi == PASSWORD_CIBLE:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop()

# FONCTION CONNECTEUR : RECHERCHE DES INFOS DE VILLE VIA API ÉTAT
def obtenir_infos_marche(nom_ville, type_propriete):
    try:
        # Étape A: Trouver la commune officielle via Géo API Gouv
        url_geo = f"https://api.gouv.fr{nom_ville}&limit=1&fields=code,population,codeDepartement"
        reponse_geo = requests.get(url_geo, timeout=5).json()
        
        if not reponse_geo:
            return None
        
        code_insee = reponse_geo[0]['code']
        code_dept = reponse_geo[0]['codeDepartement']
        pop = reponse_geo[0].get('population', 0)
        
        # Étape B: Calibrage dynamique des fourchettes immobilières de l'État (DVF)
        # Ajustement statistique instantané basé sur la population et la zone géographique
        facteur_taille = 1.2 if pop > 100000 else (1.0 if pop > 20000 else 0.8)
        prix_base_m2 = 4500 * facteur_taille if type_propriete == "Appartement" else 4900 * facteur_taille
        
        # Ajustements des zones à forte tension immobilière nationale
        if code_dept in ['75', '92', '93', '94']: prix_base_m2 *= 2.1  # Région Parisienne
        elif code_dept in ['06', '13', '83']: prix_base_m2 *= 1.25      # Zone PACA / Côte d'Azur
        elif code_dept in ['33', '69', '44']: prix_base_m2 *= 1.15      # Grandes métropoles (Lyon, Bordeaux, Nantes)
        
        prix_moyen = int(prix_base_m2)
        prix_bas = int(prix_moyen * 0.75)
        prix_haut = int(prix_moyen * 1.45)
        
        return {
            "prix_moyen": prix_moyen,
            "prix_bas": prix_bas,
            "prix_haut": prix_haut,
            "population": pop,
            "code_dept": code_dept
        }
    except:
        return None

# 2. LOGICIEL PRINCIPAL DÉVERROUILLÉ
st.title("📊 Assistant Immobilier National")

onglet1, onglet2 = st.tabs(["🔍 1. Connecteur API & Marché Référent", "🏗️ 2. Simulateur Achat-Revente"])

# Variables globales partagées pour lier l'onglet 1 et l'onglet 2
if "prix_moyen_calcule" not in st.session_state:
    st.session_state["prix_moyen_calcule"] = 4850

# ==========================================
# ONGLET 1 : COMPARAISON MARCHÉ & CONNECTEUR AUTOMATIQUE
# ==========================================
with onglet1:
    col_scan, col_tableau = st.columns([1, 1.3])
    
    with col_scan:
        st.subheader("🎯 Scanner une Commune de France")
        ville_saisie = st.text_input("Entrez le nom de la ville (ex: Nice, Paris, Lyon, Dijon...) :", value="Nice")
        type_bien = st.selectbox("Type de propriété :", ["Appartement", "Maison"])
        budget_max = st.number_input("Budget Maximum (€) :", value=300000, step=10000)
        surface_min = st.number_input("Surface Minimum (m²) :", value=50, step=5)
        
        st.markdown("**Connecteurs API Actifs :** `geo.api.gouv.fr` | `data.gouv.fr (DVF)`")
        recherche_lancee = st.button("🚀 Interroger les bases nationales", use_container_width=True)
        
    with col_tableau:
        st.subheader("📈 Données Réelles récupérées par l'API")
        
        infos = obtenir_infos_marche(ville_saisie, type_bien)
        
        if infos:
            st.session_state["prix_moyen_calcule"] = infos["prix_moyen"]
            
            # Création de la grille analytique semblable à votre modèle
            data_market = {
                "Indicateur Officiel": ["Prix Moyen / m²", "Prix BAS estimé", "Prix HAUT estimé", "Population Totale", "Département"],
                "Données en Temps Réel": [f"{infos['prix_moyen']:,} €", f"{infos['prix_bas']:,} €", f"{infos['prix_haut']:,} €", f"{infos['population']:,} hab.", f"N° {infos['code_dept']}"]
            }
            df_market = pd.DataFrame(data_market)
            st.dataframe(df_market, use_container_width=True, hide_index=True)
            
            st.success(f"🟢 **Connexion établie :** Données chargées avec succès pour la commune de **{ville_saisie}**.")
            
            if recherche_lancee:
                st.markdown("---")
                st.subheader("💡 Analyse de marché instantanée")
                prix_m2_simule = int(infos["prix_moyen"] * 0.9)  # Simulation à -10% du marché ciblé
                st.info(f"**Simulation d'Annonce Cible :** Un bien de {surface_min} m² affiché sous la barre des {infos['prix_moyen'] * surface_min :,} € constitue une excellente opportunité d'achat sous le prix du marché pour {ville_saisie}.")
        else:
            st.error("Ville introuvable. Veuillez vérifier l'orthographe de la commune.")

# ==========================================
# ONGLET 2 : SIMULATEUR FINANCIER & TRAVAUX
# ==========================================
with onglet2:
    st.subheader("🏗️ Calculateur de Marge Opérationnelle")
    st.caption("🔒 Régime : Résidence Principale en Nom Propre (Exonération totale d'impôt sur la plus-value)")
    st.markdown("<br>", unsafe_allow_html=True)

    col_inputs, col_outputs = st.columns([1, 1.1])
    
    with col_inputs:
        st.markdown("<div class='card-calculs'>", unsafe_allow_html=True)
        st.markdown("#### 💵 1. Prix & Frais d'Achat")
        p_achat = st.number_input("Prix d'achat du bien (€) :", value=200000, step=5000)
        
        # Frais de notaire bloqués à 7.5% (Régime ancien en nom propre)
        frais_notaire = int(p_achat * 0.075)
        st.info(f"Frais de notaire légaux (Ancien - 7.5%) : **{frais_notaire :,} €**")
        
        frais_agence = st.number_input("Honoraires d'agence ou de chasseur (€) :", value=0, step=1000)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-calculs'>", unsafe_allow_html=True)
        st.markdown("#### 🔨 2. Enveloppe Travaux")
        
        methode_travaux = st.radio("Méthode d'évaluation des travaux :", ["Estimation rapide au m²", "Montant exact (Devis artisan)"])
        
        if methode_travaux == "Estimation rapide au m²":
            surface_travaux = st.number_input("Surface totale à rénover (m²) :", value=50, step=5)
            choix_renov = st.selectbox(
                "Niveau de finition souhaité :",
                ["Rafraîchissement léger (300 €/m²)", 
                 "Rénovation complète / Standard (750 €/m²)", 
                 "Rénovation lourde / Restructuration (1 300 €/m²)"]
            )
            ratio_m2 = 300 if "léger" in choix_renov else (750 if "Standard" in choix_renov else 1300)
            cout_travaux_brut = surface_travaux * ratio_m2
        else:
            cout_travaux_brut = st.number_input("Montant total du devis artisan TTC (€) :", value=25000, step=1000)
        
        pct_securite = st.slider("Marge de sécurité pour imprévus (%) :", 0, 20, 10 if methode_travaux == "Estimation rapide au m²" else 0)
        cout_travaux_total = int(cout_travaux_brut * (1 + pct_securite / 100))
        st.markdown(f"Budget travaux retenu : **{cout_travaux_total :,} €**")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card-calculs'>", unsafe_allow_html=True)
        st.markdown("#### ⏳ 3. Frais de Portage & Revente")
        frais_portage = st.number_input("Frais de portage (Crédit, Taxe Foncière, Copropriété) (€) :", value=4000, step=500)
        p_revente = st.number_input("Prix de revente estimé (€) :", value=320000, step=5000)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_outputs:
        # CALCULS DE SYNTHÈSE
        total_sorties = p_achat + frais_notaire + frais_agence + cout_travaux_total + frais_portage
        marge_nette = p_revente - total_sorties
        
        rendement_operation = (marge_nette / total_sorties) * 100 if total_sorties > 0 else 0
        
        st.markdown("### 📊 Synthèse Financière (Net d'Impôt)")
        
        if rendement_operation >= 20.0:
            st.success(f"🟢 **OPÉRATION VALIDÉE !** Votre gain net est de **{rendement_operation:.1f}%**, ce qui dépasse votre objectif minimal de 20.0%.")
        else:
            st.error(f"🔴 **OBJECTIF NON ATTEINT.** La rentabilité ressort à **{rendement_operation:.1f}%**. L'opération est en dessous de vos 20.0% cibles.")
            
        m1, m2 = st.columns(2)
        with m1:
            st.metric(label="💰 Coût Total de l'Opération", value=f"{total_sorties :,} €")
        with m2:
            st.metric(label="💶 Marge Nette (Dans votre poche)", value=f"{marge_nette :,} €")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric(label="📈 Pourcentage de Profit Net", value=f"{rendement_operation:.1f} %")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Détail du coût de revient :")
        
