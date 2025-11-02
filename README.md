# Projet mit sur pieds par les étudiants de 3IL3 dans le cadre du cours de prompt engineering

Ce projet  utilise Next.js 16, React 19, et Tailwind CSS v4.

## Prérequis

Avoir installé sur son pc Node.js et git.

Vérifier si c'est deja le cas avec:

\`\`\`bash

node --version
git --version
npm --version

\`\`\`

Si vous obtennez un resultat similaire à :
" v24.11.0
v22.11.0
10.9.0" 
c'est bon, si non installez les.
Node.js: https://nodejs.org
git: https://git-scm.com/downloads

## Installation

1. Clonez le repo sur votre pc

\`\`\`bash

mkdir c:\memory_ai
cd c:\memory_ai 
git clone https://github.com/vald657/Memory-AI.git

\`\`\`
   
3. Installez les dépendances :

\`\`\`bash

npm install vaul@latest

\`\`\`

\`\`\`bash

npm install

\`\`\`

4. Créez le fichier ".env.local" dans la racine du projet

Y coller :

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=memory_ai

NEXT_PUBLIC_APP_URL=http://localhost:3000


5. Créez la base de données :

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
