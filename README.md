# Générateur de devis PDF

Ce projet génère des devis automatiquement en PDF via une API et un CLI.

## Démarrage rapide

1) Créer un environnement virtuel.
2) Installer les dépendances avec: python -m pip install -r requirements.txt
3) Lancer l’API avec: python -m uvicorn src.app.main:app --reload
4) Générer un PDF avec: python -m src.app.cli --input data/sample_quote.json --output devis.pdf

## Utilisation API

- Endpoint: POST /quote
- Corps JSON: modèle de devis (voir data/sample_quote.json) avec champs premium (SIRET/TVA/IBAN/BIC, statut, conditions)
- Réponse: PDF (application/pdf)

## Utilisation CLI

- Entrée: data/sample_quote.json
- Sortie: un fichier PDF local

## Structure

- src/app: API, modèles, génération PDF
- data: exemple de devis

COMMANDE POUR LANCER LE SCRIPT VIA CMD : 

py -m src.app.cli --input "C:\Users\S_VJEUDY\Desktop\Projetperso\data\sample_quote.json" --output "C:\Users\S_VJEUDY\Desktop\Projetperso\devis.pdf"