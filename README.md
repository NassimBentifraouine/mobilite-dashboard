# Tableau de bord Mobilité France

**Par Bentifraouine Nassim** | Décembre 2024

## C'est quoi ce projet ?

Une application web qui montre les problèmes de transport dans les communes françaises. Elle permet de voir rapidement quelles zones sont mal desservies et où il faut investir dans les transports.

## Ce que ça fait

✅ Analyse automatique des données de mobilité  
✅ Carte interactive pour voir les zones en difficulté  
✅ Graphiques clairs et faciles à comprendre  
✅ Export PDF pour faire des rapports  
✅ Fonctionne sur téléphone, tablette et ordinateur  

## Lancer le projet

**Ce qu'il faut** : Python 3.8+ installé

**Étape 1** - Aller dans le dossier :
```bash
cd mobilite-dashboard
```

**Étape 2** - Créer l'environnement virtuel :
```bash
python3 -m venv venv
```

**Étape 3** - Activer l'environnement :
```bash
# Mac/Linux :
source venv/bin/activate

# Windows :
venv\Scripts\activate
```

**Étape 4** - Installer les dépendances :
```bash
pip install -r requirements.txt
```

**Étape 5** - Démarrer :
```bash
python run.py
```

**Étape 6** - Ouvrir le navigateur sur : **http://localhost:8080**

Et voilà ! 🎉

## Comment l'utiliser

### 📊 Page d'accueil
Les chiffres importants en un coup d'œil :
- Combien de personnes ont accès aux transports
- Temps moyen des trajets
- Qui utilise vélo/transport/voiture

### 🗺️ Carte interactive
- **Vert** = commune bien desservie
- **Rouge** = problème de transport
- Cliquez sur un point pour les détails
- Filtres par département ou ville/campagne

### 📈 Analyse
- Classement des départements
- Top 10 des zones prioritaires
- Recommandations

### 💾 Export
- **CSV** pour Excel
- **PDF** pour imprimer

## Comment ça marche

```
app/
├── data/          → Fichiers CSV avec les données
├── analysis.py    → Calcule les statistiques (Pandas)
├── visualizations.py → Crée cartes et graphiques
├── routes.py      → Gère les pages web (Flask)
└── templates/     → Pages HTML (Bootstrap)
```

**Le principe** :
1. Données dans des CSV (comme Excel)
2. Python lit et calcule les stats
3. Flask transforme ça en site web
4. Bootstrap rend ça joli

## Les données

**communes.csv** : infos de base (nom, population, GPS)  
**transport.csv** : données mobilité (accès, temps trajet, modes)

Les données actuelles sont des exemples (47 communes) pour que ça marche direct. Vous pouvez les remplacer.

## Les indicateurs

**Taux de couverture** : % de personnes avec accès aux transports  
**Temps moyen** : durée domicile-travail  
**Mobilité verte** : % vélo + transports en commun  
**Zones prioritaires** : communes sans transport ou temps trop long  

## Technologies utilisées

- **Python** : langage de programmation
- **Flask** : framework web
- **Pandas** : analyse de données
- **Folium** : cartes interactives
- **Matplotlib & Seaborn** : graphiques
- **Bootstrap** : design responsive

## Problèmes courants

**Port déjà utilisé** : Désactiver AirPlay sur Mac ou changer le port dans `run.py`

**"python not found"** : Utiliser `python3` au lieu de `python`

**Carte ne s'affiche pas** : Vérifier la connexion internet

**Projet réalisé par Bentifraouine Nassim**  
Formation en data analysis et développement web Python
