# Projet v0

Ce projet a été créé avec v0 et utilise Next.js 16, React 19, et Tailwind CSS v4.

## Installation

1. Téléchargez le fichier ZIP du projet
2. Extrayez le contenu dans votre dossier de projet
3. Installez les dépendances :

\`\`\`bash
npm install
\`\`\`

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
