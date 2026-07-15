# 🎨 MOCKUPS ADMIN DASHBOARD - DESIGN PREMIUM

## 📱 VUE DESKTOP (≥ 1024px)

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                                                                                │
│  ┌──────────────────┐  ┌────────────────────────────────────────────────────┐ │
│  │                  │  │  Bonjour Franck 🎯                                 │ │
│  │  FinCoach Admin  │  │  Voici un aperçu de votre plateforme FinCoach     │ │
│  │  Tableau de bord │  │                                                    │ │
│  │                  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│ │
│  ├──────────────────┤  │  │ 👥       │ │ 📈       │ │ 💰       │ │ 💵     ││ │
│  │                  │  │  │ Users    │ │ Objectifs│ │ Épargne  │ │ Revenus││ │
│  │ 📊 Vue d'ensemble│  │  │ inscrits │ │ actifs   │ │ totale   │ │        ││ │
│  │    (bleu actif)  │  │  │          │ │          │ │          │ │        ││ │
│  │                  │  │  │   42     │ │   18     │ │ 1.5M FCFA│ │ 45K    ││ │
│  │ 👥 Utilisateurs  │  │  └──────────┘ └──────────┘ └──────────┘ └────────┘│ │
│  │                  │  │                                                    │ │
│  │ 💰 Caisse        │  │  ┌────────────────────────┐ ┌──────────────────┐  │ │
│  │                  │  │  │ Répartition objectifs  │ │ Activité         │  │ │
│  │                  │  │  │                        │ │ plateforme       │  │ │
│  │ ─────────────    │  │  │ ✅ Atteints    : 12   │ │ 📝 Cotisations   │  │ │
│  │                  │  │  │ 🔵 Actifs      : 18   │ │    effectuées: 156│  │ │
│  │ 🚪 Se déconnecter│  │  │ ⭕ Inactifs    : 3    │ │ 💸 Retraits : 24 │  │ │
│  │   (tout en bas)  │  │  └────────────────────────┘ └──────────────────┘  │ │
│  └──────────────────┘  └────────────────────────────────────────────────────┘ │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Détails des couleurs

```
Sidebar :
  - Background : gradient from-slate-900 to-slate-800
  - Text : white
  - Active : bg-blue-600 + shadow
  - Hover : bg-slate-700/50

Contenu :
  - Background : gradient from-slate-50 to-blue-50
  - Cartes : white + shadow-sm
  - Titre : text-slate-800
  - Sous-titre : text-slate-600
```

---

## 📱 VUE MOBILE (< 1024px)

### État sidebar fermée

```
┌──────────────────────────────┐
│ ☰  Admin FinCoach        [ ] │ ← Header sticky
├──────────────────────────────┤
│                              │
│  Bonjour Franck 🎯           │
│  Voici un aperçu...          │
│                              │
│  ┌──────────────────────┐   │
│  │ 👥                   │   │
│  │ Utilisateurs         │   │
│  │ inscrits             │   │
│  │                      │   │
│  │ 42                   │   │
│  └──────────────────────┘   │
│                              │
│  ┌──────────────────────┐   │
│  │ 📈                   │   │
│  │ Objectifs            │   │
│  │ actifs               │   │
│  │                      │   │
│  │ 18                   │   │
│  └──────────────────────┘   │
│                              │
│  ┌──────────────────────┐   │
│  │ 💰                   │   │
│  │ Épargne totale       │   │
│  │                      │   │
│  │ 1 500 000 FCFA       │   │
│  └──────────────────────┘   │
│                              │
│  [Contenu continue...]       │
│                              │
│                              │
└──────────────────────────────┘
```

### État sidebar ouverte (overlay)

```
┌──────────────────────────────┐
│█████████████│                │
│ FinCoach   │×│                │
│ Admin      │ │                │
│            │ │                │
│ 📊 Vue     │ │  [Overlay     │
│ d'ensemble │ │   sombre      │
│            │ │   50% opacité]│
│ 👥 Utilisa │ │                │
│ teurs      │ │                │
│            │ │                │
│ 💰 Caisse  │ │                │
│            │ │                │
│            │ │                │
│ 🚪 Déco    │ │                │
│            │ │                │
└─────────────┴────────────────┘
```

---

## 🖥️ PAGE LOGIN ADMIN

```
┌────────────────────────────────────────────────────┐
│                                                    │
│         [Fond gradient bleu nuit + effets]         │
│                                                    │
│              ┌─────────────────────┐              │
│              │                     │              │
│              │  ┌───────────┐     │              │
│              │  │    🔒     │     │ ← Icon blanc │
│              │  └───────────┘     │   sur fond   │
│              │                     │   semi-trans │
│              │  Administration     │              │
│              │  Connectez-vous à   │              │
│              │  votre espace admin │              │
│              ├─────────────────────┤              │
│              │                     │              │
│              │  📧 Adresse email   │              │
│              │  [              ]   │              │
│              │                     │              │
│              │  🔒 Mot de passe    │              │
│              │  [              ] 👁│              │
│              │                     │              │
│              │  ┌───────────────┐ │              │
│              │  │ Se connecter  │ │ ← Bouton     │
│              │  └───────────────┘ │   gradient   │
│              │                     │   bleu       │
│              │  Mot de passe       │              │
│              │  oublié ?           │              │
│              ├─────────────────────┤              │
│              │ FinCoach Admin • V26│              │
│              └─────────────────────┘              │
│                                                    │
│         🔓 Comptes de test :                       │
│         admin@fincoach.cm / admin123               │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 📊 VUE UTILISATEURS - DÉTAIL

```
┌────────────────────────────────────────────────────────────────────┐
│  Liste des utilisateurs (42)                                       │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Utilisateur    Email              Solde    Épargne  Objectifs│ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ Franck Mbarga  franck@...         50,000   150,000    [3]   │ │
│  │ ID: 12ab34cd                                                 │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ Marie Dupont   marie@...          30,000   80,000     [2]   │ │
│  │ ID: 56ef78gh                                                 │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ Paul Kamga     paul@...           75,000   200,000    [5]   │ │
│  │ ID: 90ij12kl                                                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  [Pagination ou scroll infini]                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 💰 VUE CAISSE - DÉTAIL

```
┌────────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│  │ Montant total│ │ Nb entrées   │ │ Sources      │              │
│  │              │ │              │ │              │              │
│  │ 45 000 FCFA  │ │     24       │ │      2       │              │
│  └──────────────┘ └──────────────┘ └──────────────┘              │
│                                                                    │
│  Répartition par source                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Pénalité retrait               40 000 FCFA      (20 entrées) │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ Frais service                   5 000 FCFA       (4 entrées) │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  Dernières entrées                                                │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Pénalité retrait    2026-06-27               2 500 FCFA      │ │
│  │ Pénalité retrait    2026-06-26               1 800 FCFA      │ │
│  │ Frais service       2026-06-25               1 000 FCFA      │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 PALETTE DE COULEURS EXACTE

### Couleurs principales

```css
/* ── SIDEBAR ── */
--sidebar-bg-start: #0f172a  /* slate-900 */
--sidebar-bg-end: #1e293b    /* slate-800 */
--sidebar-text: #ffffff
--sidebar-text-inactive: #cbd5e1  /* slate-300 */
--sidebar-hover: rgba(30, 41, 59, 0.5)  /* slate-700/50 */
--sidebar-active: #2563eb  /* blue-600 */
--sidebar-active-shadow: rgba(37, 99, 235, 0.3)

/* ── FOND GÉNÉRAL ── */
--body-bg-start: #f8fafc  /* slate-50 */
--body-bg-end: #eff6ff    /* blue-50 */

/* ── CARTES ── */
--card-bg: #ffffff
--card-border: transparent
--card-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05)  /* shadow-sm */
--card-shadow-hover: 0 20px 25px -5px rgb(0 0 0 / 0.1)  /* shadow-xl */
--card-radius: 16px  /* rounded-2xl */

/* ── TEXTE ── */
--text-primary: #1e293b   /* slate-800 */
--text-secondary: #64748b  /* slate-600 */
--text-tertiary: #94a3b8   /* slate-400 */

/* ── COULEURS STATISTIQUES ── */
--stat-blue-start: #3b82f6   /* blue-500 */
--stat-blue-end: #2563eb     /* blue-600 */

--stat-green-start: #22c55e  /* green-500 */
--stat-green-end: #16a34a    /* green-600 */

--stat-purple-start: #a855f7 /* purple-500 */
--stat-purple-end: #9333ea   /* purple-600 */

--stat-orange-start: #f97316 /* orange-500 */
--stat-orange-end: #ea580c   /* orange-600 */

/* ── ÉTATS ── */
--success: #22c55e    /* green-500 */
--warning: #f59e0b    /* amber-500 */
--error: #ef4444      /* red-500 */
--info: #3b82f6       /* blue-500 */
```

---

## 📐 DIMENSIONS ET ESPACEMENTS

### Layout

```css
/* ── SIDEBAR ── */
--sidebar-width: 288px  /* 18rem / w-72 */
--sidebar-padding: 24px  /* p-6 */

/* ── CARTES STATS ── */
--stat-card-min-height: 140px
--stat-card-padding: 24px  /* p-6 */
--stat-card-gap: 24px  /* gap-6 */

/* ── GRID ── */
--grid-cols-mobile: 1
--grid-cols-tablet: 2
--grid-cols-desktop: 4
--grid-gap: 24px  /* gap-6 */

/* ── CONTENU PRINCIPAL ── */
--content-padding-mobile: 24px  /* p-6 */
--content-padding-desktop: 32px  /* p-8 */
--content-padding-bottom: 96px  /* pb-24 */
```

### Typographie

```css
/* ── TITRES ── */
--h1-size-mobile: 30px    /* text-3xl */
--h1-size-desktop: 36px   /* text-4xl */
--h1-weight: 700          /* font-bold */

--h2-size: 24px           /* text-2xl */
--h2-weight: 700          /* font-bold */

--h3-size: 20px           /* text-xl */
--h3-weight: 700          /* font-bold */

/* ── CORPS ── */
--body-size: 16px         /* text-base */
--body-weight: 400        /* font-normal */

--sidebar-nav-size: 18px  /* text-lg */
--sidebar-nav-weight: 500 /* font-medium */

--small-size: 14px        /* text-sm */

/* ── CHIFFRES STATS ── */
--stat-big: 30px          /* text-3xl */
--stat-medium: 24px       /* text-2xl */
--stat-small: 18px        /* text-lg */
--stat-weight: 700        /* font-bold */
```

---

## 🔍 DÉTAILS INTERACTIFS

### Boutons

```css
/* ── BOUTON NAVIGATION ── */
Inactif:
  - bg: transparent
  - text: slate-300
  - hover: bg-slate-700/50, text-white

Actif:
  - bg: blue-600
  - text: white
  - shadow: shadow-lg shadow-blue-600/30

/* ── BOUTON DÉCONNEXION ── */
Normal:
  - bg: red-600
  - text: white
  - hover: bg-red-700
  - shadow: shadow-lg hover:shadow-red-600/30

/* ── BOUTON PRIMAIRE (Login) ── */
Normal:
  - bg: gradient from-blue-600 to-cyan-600
  - text: white
  - hover: from-blue-700 to-cyan-700
  - transform: hover:-translate-y-0.5
```

### Animations

```css
/* ── TRANSITIONS ── */
--transition-all: all 0.2s ease
--transition-colors: colors 0.2s ease
--transition-shadow: shadow 0.3s ease
--transition-transform: transform 0.2s ease

/* ── HOVER EFFECTS ── */
Cartes: shadow-sm → shadow-xl (duration-300)
Sidebar items: bg transparent → bg-slate-700/50 (duration-200)
Boutons: translateY(0) → translateY(-2px) (duration-200)

/* ── LOADING SPINNER ── */
Animation: spin (animate-spin)
Duration: 1s linear infinite
Border: 4px solid blue-600, border-t transparent
```

---

## 💡 ÉTAT D'ERREUR

```
┌────────────────────────────────────────┐
│  ⚠️  Erreur de connexion               │
│                                        │
│  Impossible de charger les données     │
│  admin. Vérifiez que le backend        │
│  est lancé.                            │
│                                        │
│  [ Réessayer ]  ← Bouton rouge         │
└────────────────────────────────────────┘

Couleurs:
- Fond: bg-red-50
- Bordure: border-red-200
- Icon: text-red-600
- Titre: text-red-800
- Text: text-red-600
- Bouton: bg-red-600 hover:bg-red-700
```

---

## ✨ ÉTAT DE CHARGEMENT

```
┌────────────────────────────────────────┐
│                                        │
│              ⏳                        │
│       [Spinner animé]                  │
│                                        │
│    Chargement des données...           │
│                                        │
└────────────────────────────────────────┘

Spinner:
- Taille: 48px (h-12 w-12)
- Couleur: border-blue-600
- Animation: spin (1s)
```

---

## 📱 BREAKPOINTS RESPONSIVE

```
/* Mobiles (portrait) */
< 640px (sm)
  - Sidebar: Overlay
  - Cartes: 1 colonne
  - Padding: p-6
  - Font: réduction 10%

/* Mobiles (landscape) / Tablettes (portrait) */
640px - 1024px (sm-lg)
  - Sidebar: Overlay
  - Cartes: 2 colonnes
  - Padding: p-6

/* Tablettes (landscape) / Desktop */
≥ 1024px (lg)
  - Sidebar: Fixe
  - Cartes: 4 colonnes
  - Padding: p-8

/* Large desktop */
≥ 1280px (xl)
  - Même layout
  - Espacement accru
```

---

**Mockups créés pour FinCoach Admin Dashboard 2026** 🎨
