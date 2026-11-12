# 1. Renommer le fichier s'il s'appelle encore "symson.py"
if (Test-Path "symson.py") { Rename-Item "symson.py" "sysmon.py" }

# 2. Créer requirements.txt
@"
PyQt6>=6.6.0
psutil>=5.9.0
GPUtil>=1.4.0
"@ | Out-File -FilePath "requirements.txt" -Encoding utf8

# 3. Créer .gitignore
@"
.venv/
venv/
__pycache__/
*.pyc
config.json
.vscode/
.idea/
Thumbs.db
"@ | Out-File -FilePath ".gitignore" -Encoding utf8

# 4. Créer LICENSE
@"
MIT License

Copyright (c) 2026 TonPseudoGitHub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -FilePath "LICENSE" -Encoding utf8

# 5. Créer README.md
@"
# ⚡ SysMon Widget

Un widget de monitoring système flottant, léger et moderne, affichant en temps réel l'utilisation de vos composants PC (CPU, GPU, RAM, Réseau) sans ouvrir le Gestionnaire des tâches.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fonctionnalités
- 📊 **Monitoring temps réel** : CPU, GPU (NVIDIA), RAM et Réseau.
- 🪟 **Fenêtre flottante** : Sans bordure, toujours au premier plan.
- 🖱️ **Drag & Drop** : Déplaçable librement à la souris.
- 🎨 **Design moderne** : Effet glassmorphism sombre.
- 💾 **Persistance** : Sauvegarde automatique de la position à la fermeture.
- 📌 **System Tray** : Icône dans la barre des tâches pour masquer/quitter.

## 🚀 Installation
1. Clonez le dépôt et allez dans le dossier.
2. Créez un environnement virtuel : \`python -m venv .venv\`
3. Activez-le : \`.venv\\Scripts\\activate\`
4. Installez les dépendances : \`pip install -r requirements.txt\`

## ▶️ Utilisation
Lancez l'application : \`python sysmon.py\`
- **Déplacer** : Clic gauche maintenu n'importe où sur le widget.
- **Quitter** : Alt+F4 ou via l'icône dans la barre des tâches (près de l'heure).

> ⚠️ **Note GPU** : La détection fonctionne actuellement pour les cartes **NVIDIA** (via \`GPUtil\`). Les cartes AMD/Intel afficheront "Non détecté".

## 📄 Licence
Projet open-source sous licence MIT.
"@ | Out-File -FilePath "README.md" -Encoding utf8

# 6. Initialisation Git automatique
git init
git add .
git commit -m "feat: initial commit - MVP floating system monitor widget"
git branch -M main

Write-Host "✅ SUCCÈS ! Tous les fichiers sont créés et le commit Git est fait." -ForegroundColor Green
Write-Host "👉 Prochaine étape : crée ton repo sur GitHub.com, puis lance :" -ForegroundColor Yellow
Write-Host "   git remote add origin https://github.com/TON_PSEUDO/TON_REPO.git" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan