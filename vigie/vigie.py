#!/usr/bin/env python3
"""
Vigie — Agent de veille des appels d'offre
Univers Soleil SARL, Pourrières (83910, PACA)

Exécuté chaque mardi à 5h36 via GitHub Actions.
"""

import anthropic
import smtplib
import os
import sys
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

RECIPIENT = "contact@universsoleil.fr"
AGENT_FIRSTNAME = "Vigie"

SYSTEM_PROMPT = """Tu es Vigie, l'agent de veille des appels d'offre pour Univers Soleil SARL.

Univers Soleil est un installateur certifié d'énergies renouvelables basé à Pourrières (83910, PACA), fondé en 2007, avec plus de 600 installations. Domaines d'expertise : pompes à chaleur (M-TEC), chaudières biomasse/granulés (ÖkoFEN), solaire thermique, batteries solaires (Tesla Powerwall 3), onduleurs (Fronius), systèmes solaires hybrides.

Ton rôle est de repérer les opportunités de marchés publics (appels d'offre, consultations, MAPA) publiés dans les 7 derniers jours et correspondant exactement aux compétences d'Univers Soleil.

IMPORTANT : Les Contrats de Performance Énergétique (CPE) et Marchés Globaux de Performance (MGP) sont très pertinents car ils incluent systématiquement l'installation d'équipements ENR (PAC, biomasse, solaire thermique). Ne pas les ignorer même si le titre ne mentionne pas explicitement le type d'équipement."""


def build_prompt(today: str) -> str:
    return f"""Date du jour : {today}

Effectue une veille complète des appels d'offre publics publiés cette semaine sur :
- boamp.fr (Bulletin Officiel des Annonces des Marchés Publics)
- marches-publics.gouv.fr
- achatpublic.com
- klekoon.com
- francemarches.com
- Google (requêtes ciblées listées ci-dessous)

## Critères de sélection

**ZONE 1 — Rayon 150 km de Pourrières (dép. 83, 13, 84, 04, 06, 05, 34, 30, 07)**
- Entretien et maintenance de solaire thermique (panneaux, ballons, circuits)
- Entretien et maintenance de chaudières biomasse / granulés / bois énergie
- Contrat de Performance Énergétique (CPE) ou Marché Global de Performance (MGP) incluant PAC, biomasse ou solaire thermique

**ZONE 2 — Dép. 13 (Bouches-du-Rhône), 82 (Tarn-et-Garonne) et Corse (2A, 2B)**
- Installation de solaire thermique
- Installation de batteries solaires / systèmes de stockage d'énergie
- Installation de pompes à chaleur (air/eau, eau/eau, géothermique)
- Installation de chaudières biomasse / granulés / bois énergie
- CPE / MGP / rénovation énergétique globale incluant équipements ENR

**ZONE 3 — France entière**
- Projets solaire hybride (PV + thermique, ou PV + stockage)
- Fourniture et installation de batteries solaires / systèmes de stockage d'énergie renouvelable
- CPE / MGP de grande envergure avec composante ENR significative (PAC, biomasse, solaire thermique)
- Marchés de transition énergétique incluant remplacement de chauffage par ENR

## Requêtes Google à effectuer
1. site:boamp.fr "solaire thermique" OR "chaudière biomasse" OR "pompe à chaleur" 2026
2. site:boamp.fr "contrat de performance énergétique" OR "CPE" OR "marché global de performance" 2026
3. "appel d'offre" "pompe à chaleur" OR "biomasse" OR "solaire thermique" PACA OR "Bouches-du-Rhône" OR "Var" 2026
4. "marché public" "CPE" OR "performance énergétique" "pompe à chaleur" OR "biomasse" OR "solaire" 2026
5. "appel d'offre" "solaire hybride" OR "batterie solaire" OR "stockage énergie" France 2026
6. site:achatpublic.com "énergie renouvelable" OR "ENR" OR "biomasse" OR "solaire thermique" 2026
7. site:klekoon.com "pompe à chaleur" OR "chaudière biomasse" OR "solaire thermique" PACA 2026

## Points d'attention spécifiques
- Les CPE (Contrats de Performance Énergétique) portent souvent des titres génériques comme "rénovation énergétique", "efficacité énergétique" ou "transition énergétique" — vérifier le contenu pour détecter la présence d'équipements ENR
- Les codes CPV pertinents : 09331000 (panneaux solaires), 42511110 (pompes à chaleur), 09111400 (combustibles à base de bois), 45331000 (installation chauffage), 45261215 (travaux de couverture solaire)
- Rechercher aussi : "rénovation thermique", "décarbonation", "sortie des énergies fossiles"

## Format de réponse attendu

Pour CHAQUE appel d'offre pertinent, fournis un bloc structuré :

**[N°]. [TITRE EXACT DU MARCHÉ]**
- **Acheteur :** nom complet de l'organisme public
- **Localisation :** ville, département
- **Prestation :** description courte et précise
- **Montant estimé :** montant HT si disponible, sinon "Non communiqué"
- **Date limite de réponse :** JJ/MM/AAAA (ou "Non précisée")
- **Pourquoi sélectionné :** 1-2 phrases reliant l'AO aux compétences d'Univers Soleil
- **Lien source :** URL directe vers l'annonce

---

Si aucun appel d'offre correspondant n'est trouvé cette semaine, indique-le clairement en listant les sources consultées et les requêtes effectuées.

Termine par une synthèse en 2-3 phrases des opportunités de la semaine, puis signe de ton prénom."""


def get_monday_of_week() -> str:
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%d/%m/%Y")


def run_vigie_search() -> str:
    client = anthropic.Anthropic()
    today_str = datetime.now().strftime("%d/%m/%Y")

    messages = [{"role": "user", "content": build_prompt(today_str)}]

    print(f"[Vigie] Démarrage de la veille — {today_str}")
    iterations = 0
    max_iterations = 25

    while iterations < max_iterations:
        iterations += 1

        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 20,
            }],
            messages=messages,
        )

        for block in response.content:
            if hasattr(block, "type") and block.type == "tool_use":
                query = block.input.get("query", "") if hasattr(block, "input") else ""
                print(f"  → Recherche : {query[:100]}")

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            text = "".join(
                block.text for block in response.content
                if hasattr(block, "text") and block.text
            )
            print(f"[Vigie] Recherche terminée ({iterations} itération(s)).")
            return text

        tool_use_ids = [
            block.id for block in response.content
            if hasattr(block, "type") and block.type == "tool_use"
        ]
        if tool_use_ids:
            existing_results = {
                block.tool_use_id for block in response.content
                if hasattr(block, "type") and block.type == "tool_result"
            }
            missing = [uid for uid in tool_use_ids if uid not in existing_results]
            if missing:
                messages.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": uid, "content": ""}
                    for uid in missing
                ]})

    print("[Vigie] AVERTISSEMENT : nombre maximum d'itérations atteint.", file=sys.stderr)
    last_text = ""
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            content = msg["content"]
            if isinstance(content, list):
                last_text = "".join(
                    b.text for b in content if hasattr(b, "text") and b.text
                )
            break
    return last_text or "Erreur : la recherche n'a pas pu aboutir."


def _md_to_html(text: str) -> str:
    lines = text.split("\n")
    html_parts = []
    in_list = False

    for line in lines:
        if line.strip() == "---":
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append('<hr style="border:none;border-top:1px solid #e0e0e0;margin:16px 0;">')
            continue

        if line.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            content = _inline_md(line[3:])
            html_parts.append(f'<h3 style="color:#2c6e49;border-bottom:1px solid #c8e6c9;padding-bottom:6px;margin-top:24px;">{content}</h3>')
            continue

        if re.match(r"^\*\*[^*]+\*\*$", line.strip()):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            content = _inline_md(line.strip())
            html_parts.append(f'<h4 style="color:#1b4332;margin:20px 0 6px;">{content}</h4>')
            continue

        if line.startswith("- "):
            if not in_list:
                html_parts.append('<ul style="margin:4px 0 4px 20px;padding:0;">')
                in_list = True
            content = _inline_md(line[2:])
            html_parts.append(f'<li style="margin:3px 0;">{content}</li>')
            continue

        if in_list:
            html_parts.append("</ul>")
            in_list = False

        if not line.strip():
            html_parts.append('<div style="height:8px;"></div>')
            continue

        content = _inline_md(line)
        html_parts.append(f'<p style="margin:4px 0;">{content}</p>')

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def _inline_md(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


def build_html_email(report: str, week_start: str) -> str:
    body = _md_to_html(report)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;color:#333;">
<div style="max-width:780px;margin:24px auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
  <div style="background:#2c6e49;padding:24px 28px;">
    <h1 style="margin:0;color:#fff;font-size:20px;font-weight:700;">Veille Appels d'Offre</h1>
    <p style="margin:4px 0 0;color:#a8d5b5;font-size:14px;">Semaine du {week_start} &nbsp;·&nbsp; Univers Soleil SARL</p>
  </div>
  <div style="padding:28px;">
    {body}
  </div>
  <div style="background:#f9f9f9;border-top:1px solid #e0e0e0;padding:12px 28px;font-size:11px;color:#999;">
    Email généré automatiquement par {AGENT_FIRSTNAME}, agent de veille d'Univers Soleil SARL
  </div>
</div>
</body>
</html>"""


def send_email(html_body: str, plain_body: str, week_start: str) -> None:
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT") or "587")
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Veille appels d'offre – semaine du {week_start}"
    msg["From"] = f"{AGENT_FIRSTNAME} – Univers Soleil <{smtp_user}>"
    msg["To"] = RECIPIENT

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    print(f"[Vigie] Envoi de l'email à {RECIPIENT}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print(f"[Vigie] Email envoyé — semaine du {week_start}.")


def main() -> None:
    print(f"\n{'='*55}")
    print(f"  VIGIE — Démarrage {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*55}\n")

    week_start = get_monday_of_week()
    report = run_vigie_search()

    if not report.strip():
        print("[Vigie] ERREUR : aucun rapport généré.", file=sys.stderr)
        sys.exit(1)

    html_body = build_html_email(report, week_start)
    send_email(html_body, report, week_start)

    print(f"\n{'='*55}")
    print(f"  VIGIE — Terminé {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
