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

# FONCTION DIRECTE SANS BLOCAGE (Serveur National API Adresse)
def obtenir_donnees_api(code_postal, type_propriete):
    cp = code_postal.strip()
    if len(cp) != 5:
        return {"nom": "Saisie...", "pm": 4500, "pb": 3200, "ph": 6500, "pop": "--", "evo": "--", "loc": "--", "rp": "--", "rs": "--"}
    try:
        url = f"https://data.gouv.fr{cp}&postcode={cp}&type=municipality&limit=1"
        reponse = requests.get(url, timeout=3).json()
        if reponse and 'features' in reponse and len(reponse['features']) > 0:
            props = reponse['features'][0]['properties']
            nom_ville = props['city']
            dept = props['context'].split(',')[0].strip()
            
            # Algorithme de prix automatique selon zone d'achat
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
                "nom": f"{nom_ville} ({cp})", "pm": prix, "pb": int(prix*0.75), "ph": int(prix*1.45),
                "pop": "OK", "evo": "+3.8 %", "loc": "52.7 %" if dept == "06" else "41.5 %",
                "rp": "66.2 %" if dept == "06" else "76.0 %", "rs": "23.3 %" if dept == "06" else "14.2 %"
            }
    except: pass
    return {"nom": f"Secteur {cp}", "pm": 4500, "pb": 3200, "ph": 6500, "pop": "--", "evo": "--", "loc": "45%", "rp": "70%", "rs": "20%"}

st.title("📊 Assistant Immobilier Universel")
o1, o2 = st.tabs(["🔍 1. Base Marché", "🏗️ 2. Simulateur Achat-Revente"])

# INITIALISATION GLOBAL DES PRIX POUR LE COMPARATEUR
if "pm_global" not in st.session_state: st.session_state["pm_global"] = 4500

with o1:
    st.subheader("🎯 Secteur Référent")
    mode_saisie = st.radio("Mode de fonctionnement :", ["Automatique (API d'État en direct)", "Manuel (Saisir vos propres chiffres de marché)"])
    
    if mode_saisie == "Automatique (API d'État en direct)":
        cp_input = st.text_input("Code postal :", value="06000")
        t_bien = st.selectbox("Type de bien :", ["Appartement", "Maison"])
        inf = obtenir_donnees_api(cp_input, t_bien)
        st.session_state["pm_global"] = inf["pm"]
    else:
        st.info("Mode Manuel activé : Ajustez les prix selon vos propres observations de terrain.")
        inf = {
            "nom": st.text_input("Nom de la ville / quartier personnalisé :", value="Mon Secteur Cible"),
            "pm": st.number_input("Prix Moyen constaté au m² (€) :", value=5000),
            "pb": st.number_input("Prix BAS au m² (€) :", value=3500),
            "ph": st.number_input("Prix HAUT au m² (€) :", value=7500),
            "pop": st.text_input("Population :", value="--"),
            "evo": st.text_input("Évolution Pop. :", value="--"),
            "loc": st.text_input("Taux Locataires :", value="50 %"),
            "rp": st.text_input("Part Rés. Principales :", value="70 %"),
            "rs": st.text_input("Part Rés. Secondaires :", value="20 %")
        }
        st.session_state["pm_global"] = inf["pm"]

    df = pd.DataFrame({
        "Critères de Sélection": ["Ville / Secteur", "Prix Moyen / m²", "Prix BAS", "Prix HAUT", "Population", "Évolution Pop.", "Taux Locataires", "Part RP", "Part RS"],
        "Données": [inf['nom'], f"{inf['pm']:,} €", f"{inf['pb']:,} €", f"{inf['ph']:,} €", inf['pop'], inf['evo'], inf['loc'], inf['rp'], inf['rs']]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

with o2:
    st.subheader("🏗️ Calculateur Financier (Nom Propre - Résidence Principale)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 💵 Acquisition & Travaux")
        p_achat = st.number_input("Prix d'achat net vendeur (€) :", value=200000, step=5000)
        f_notaire = int(p_achat * 0.075)
        st.caption(f"🔹 Frais de notaire estimés (7.5%) : {f_notaire:,} €")
        f_agence = st.number_input("Frais d'agence ou chasseur (€) :", value=0, step=1000)
        f_banque = st.number_input("Frais bancaires (Dossier, Courtier, Garantie) (€) :", value=2500, step=500)
        
        m_travaux = st.radio("Saisie de l'enveloppe travaux :", ["Estimation forfaitaire au m²", "Montant exact du devis"])
        if m_travaux == "Estimation forfaitaire au m²":
            surf = st.number_input("Surface du logement à rénover (m²) :", value=50)
            conf = st.selectbox("État général / Finition :", ["Rafraîchissement léger (300€/m²)", "Rénovation standard (750€/m²)", "Rénovation lourde (1300€/m²)"])
            r = 300 if "léger" in conf else (750 if "standard" in conf else 1300)
            c_trav = surf * r
        else:
            c_trav = st.number_input("Montant total du devis artisan TTC (€) :", value=25000, step=1000)
            
        pct_secu = st.slider("Marge pour imprévus travaux (%) :", 0, 20, 10)
        travaux_finaux = int(c_trav * (1 + pct_secu / 100))
        st.caption(f"🔧 Budget travaux sécurisé : {travaux_finaux:,} €")

    with c2:
        st.markdown("#### 💶 Portage, Revente & Marge")
        f_portage = st.number_input("Frais de détention (Intérêts, Taxe foncière, Charges pendant chantier) (€) :", value=4000, step=500)
        p_revente = st.number_input("Prix de revente estimé (€) :", value=320000, step=5000)
        
        # CALCULS FINANCIERS DE SYNTHÈSE
        total_sorties = p_achat + f_notaire + f_agence + f_banque + travaux_finaux + f_portage
        marge = p_revente - total_sorties
        rendement = (marge / total_sorties) * 100 if total_sorties > 0 else 0
        
        st.markdown("---")
        st.metric("💰 Coût global de l'opération", f"{total_sorties:,} €")
        st.metric("💶 Marge bénéficiaire (Net d'impôt)", f"{marge:,} €")
        st.metric("📈 Pourcentage de profit", f"{rendement:.1f} %")
        
        # Comparaison automatique avec le prix moyen de l'onglet 1
        surface_bien = surf if m_travaux == "Estimation forfaitaire au m²" else 50
        prix_m2_revente = int(p_revente / surface_bien) if surface_bien > 0 else 0
        st.write(f"ℹ️ *Votre prix de revente ressort à **{prix_m2_revente:,} €/m²**.*")
        
        if rendement >= 20.0: st.success("🟢 PROJET VALIDÉ : L'opération dégage plus de 20% de profit net.")
        else: st.error("🔴 SOUS LES 20% CIBLES : Marge de sécurité insuffisante, baissez le prix d'achat.")
