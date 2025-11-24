# Projet mit sur pieds par les étudiants de 3IL3 dans le cadre du cours de prompt engineering

Ce projet  utilise Next.js 16, React 19, et Tailwind CSS v4.

## Installation

1. Clonez le repo sur votre pc
2. Installez les dépendances :

\`\`\`bash
npm install vaul@latest
\`\`\`

\`\`\`bash
npm install
\`\`\`

3. Créez la base de données :

   Installez puis ouvrez Xampp Panel controller, démarer les services "Apache" puis "MySQL", lancez phpMyAdmin en cliquant sur le bouton "Admin" sur la ligne de "mySQL", créez une nouvelle base de donnée nommée "memory_ai", et en importez y le dossier "memory_ia.sql".

## Démarrage

Lancez le serveur de développement :

\`\`\`bash
npm run dev
\`\`\`

Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

## Structure du projet

- \`app/\` - Pages et layouts Next.js (App Router)
- \`components/ui/\` - Composants UI shadcn/ui
- \`lib/\` - Utilitaires (fonction cn pour les classes CSS)
- \`hooks/\` - Hooks React personnalisés

## Configuration des alias

Les alias sont configurés dans \`tsconfig.json\` :

- \`@/*\` pointe vers la racine du projet
- Tous les imports utilisent \`@/\` pour une meilleure organisation

## Technologies

- **Next.js 16** - Framework React avec App Router
- **React 19** - Bibliothèque UI
- **Tailwind CSS v4** - Framework CSS utilitaire
- **shadcn/ui** - Composants UI réutilisables
- **TypeScript** - Typage statique
- **Lucide React** - Icônes

## Commandes disponibles

- \`npm run dev\` - Démarre le serveur de développement
- \`npm run build\` - Compile le projet pour la production
- \`npm run start\` - Démarre le serveur de production
- \`npm run lint\` - Vérifie le code avec ESLint

#####################################################################################################

start le serveur fastAPI.py  
ai_memoria\Memory AI\backend\app\models>  uvicorn fastAPI:app --reload --host 127.0.0.1 --port 8000

##### start le serveur ollama 
ollama serve

### gestion d'erreur du serveur ollama : port par defaut deja utiliser 
taskkill /PID <PID> /F

###### start Xampp