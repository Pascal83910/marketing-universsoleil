# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du projet

Ce dépôt est une **base de connaissances documentaire** pour Univers Soleil SARL, entreprise installateur d'équipements d'énergie renouvelable en région PACA (fondée 2007, 600+ installations). Il n'y a pas de code source, pas de build, pas de tests — uniquement des documents Markdown structurés pour alimenter des agents IA.

## Architecture des documents

Tous les documents de référence se trouvent dans `Contexte/`. Ils forment une pyramide de contexte :

| Fichier | Rôle |
|---|---|
| `univers_soleil_contexte_entreprise.md` | Socle : identité légale, historique, SAV, RH, IT, aides financières |
| `univers_soleil_produits_vente_marketing.md` | Catalogue produits (PAC M-TEC, ÖkoFEN, Powerwall 3, Fronius, SOLINK), stratégie commerciale, processus de vente |
| `univers_soleil_voix_marque_communication.md` | Guide de ton et de style éditorial : vocabulaire validé, CTAs éprouvés, formats par canal (web, réseaux, email, blog) |
| `univers_soleil_strategie_croissance_marketing.md` | Feuille de route 2026–2029 : axes stratégiques, segments cibles, KPIs, scénarios de croissance |

Les dossiers `Data/`, `Exemples/`, `POS/`, `Reseaux/`, `Trimestre/` sont vides — réservés à de futurs contenus.

## Usage attendu

Ces documents servent de **contexte à des agents IA** pour produire :
- Emails de prospection et de suivi client
- Réponses SAV et accompagnement technique
- Posts réseaux sociaux, articles de blog, contenus web
- Argumentaires commerciaux et comparatifs concurrentiels
- Informations sur les aides financières (MaPrimeRénov', CEE, éco-PTZ)

Pour toute production de contenu, lire d'abord `univers_soleil_voix_marque_communication.md` pour respecter le ton de marque, puis s'appuyer sur les autres documents selon le sujet traité.

## Langue et ton

Toutes les communications Univers Soleil sont en **français**. Le ton est professionnel, chaleureux, ancré localement (PACA), avec une posture d'expert pédagogue. Éviter le jargon technique brut ; toujours relier les caractéristiques techniques aux bénéfices concrets pour le client.
