// ============================================
// CONFIGURATION DES ROUTES ADMIN
// ============================================
// À intégrer dans : frontend/src/App.jsx ou frontend/src/router.jsx

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Import des composants admin
import LoginAdmin from './pages/admin/LoginAdmin';
import VueAdmin from './pages/admin/VueAdmin';

// ── COMPOSANT : ROUTE PROTÉGÉE ──
function ProtectedAdminRoute({ children }) {
  const token = localStorage.getItem('admin_token');
  
  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }
  
  return children;
}

// ── CONFIGURATION COMPLÈTE DES ROUTES ──
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── ROUTES PUBLIQUES ── */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* ── ROUTES UTILISATEUR (protégées) ── */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/objectifs" element={<ProtectedRoute><Objectifs /></ProtectedRoute>} />
        <Route path="/caisse" element={<ProtectedRoute><VueCaisse /></ProtectedRoute>} />
        <Route path="/historique" element={<ProtectedRoute><Historique /></ProtectedRoute>} />
        
        {/* ── ROUTES ADMIN ── */}
        <Route path="/admin/login" element={<LoginAdmin />} />
        <Route 
          path="/admin" 
          element={
            <ProtectedAdminRoute>
              <VueAdmin />
            </ProtectedAdminRoute>
          } 
        />
        
        {/* ── ROUTE 404 ── */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

// ============================================
// VERSION ALTERNATIVE : REACT ROUTER v6.4+
// ============================================

import { createBrowserRouter, RouterProvider } from 'react-router-dom';

// Loader pour vérifier l'authentification
const adminLoader = () => {
  const token = localStorage.getItem('admin_token');
  if (!token) {
    return redirect('/admin/login');
  }
  return null;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/dashboard',
    element: <Dashboard />,
    loader: userLoader,
  },
  {
    path: '/admin',
    children: [
      {
        path: 'login',
        element: <LoginAdmin />,
      },
      {
        path: '',
        element: <VueAdmin />,
        loader: adminLoader,
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}

// ============================================
// LAYOUT ADMIN AVEC NAVIGATION
// ============================================

// Si tu veux un layout avec plusieurs pages admin :

import { Outlet, NavLink } from 'react-router-dom';

function AdminLayout() {
  return (
    <div className="flex h-screen">
      <aside className="w-72 bg-slate-900 text-white">
        <div className="p-6">
          <h1 className="text-2xl font-bold">FinCoach Admin</h1>
        </div>
        <nav className="p-4 space-y-2">
          <NavLink 
            to="/admin" 
            end
            className={({ isActive }) => 
              `block px-4 py-3 rounded-xl ${isActive ? 'bg-blue-600' : 'hover:bg-slate-700'}`
            }
          >
            Vue d'ensemble
          </NavLink>
          <NavLink 
            to="/admin/utilisateurs" 
            className={({ isActive }) => 
              `block px-4 py-3 rounded-xl ${isActive ? 'bg-blue-600' : 'hover:bg-slate-700'}`
            }
          >
            Utilisateurs
          </NavLink>
          <NavLink 
            to="/admin/caisse" 
            className={({ isActive }) => 
              `block px-4 py-3 rounded-xl ${isActive ? 'bg-blue-600' : 'hover:bg-slate-700'}`
            }
          >
            Caisse
          </NavLink>
        </nav>
      </aside>
      
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

// Routes avec layout :
const router = createBrowserRouter([
  {
    path: '/admin',
    element: <AdminLayout />,
    loader: adminLoader,
    children: [
      {
        path: '',
        element: <VueOverview />,
      },
      {
        path: 'utilisateurs',
        element: <VueUtilisateurs />,
      },
      {
        path: 'caisse',
        element: <VueCaisse />,
      },
    ],
  },
]);

// ============================================
// HOOKS PERSONNALISÉS
// ============================================

// Hook pour vérifier si l'utilisateur est admin
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function useAdminAuth() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  const [adminName, setAdminName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    const name = localStorage.getItem('admin_name');
    
    if (!token) {
      navigate('/admin/login');
      setLoading(false);
      return;
    }
    
    // Optionnel : vérifier la validité du token auprès du backend
    // verifyToken(token).then(...)
    
    setIsAdmin(true);
    setAdminName(name || 'Admin');
    setLoading(false);
  }, [navigate]);

  const logout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_name');
    navigate('/admin/login');
  };

  return { isAdmin, loading, adminName, logout };
}

// Utilisation dans un composant :
function VueAdmin() {
  const { isAdmin, loading, adminName, logout } = useAdminAuth();
  
  if (loading) {
    return <div>Chargement...</div>;
  }
  
  return (
    <div>
      <h1>Bonjour {adminName}</h1>
      <button onClick={logout}>Se déconnecter</button>
      {/* ... */}
    </div>
  );
}

// ============================================
// STRUCTURE DE FICHIERS RECOMMANDÉE
// ============================================

/*
frontend/src/
├── App.jsx                     # Configuration routes principales
├── main.jsx                    # Point d'entrée
│
├── pages/
│   ├── Home.jsx               # Page d'accueil
│   ├── Login.jsx              # Login utilisateur
│   ├── Dashboard.jsx          # Dashboard utilisateur
│   │
│   └── admin/
│       ├── LoginAdmin.jsx     # Login admin
│       └── VueAdmin.jsx       # Dashboard admin (tout-en-un)
│       
│       # OU version éclatée :
│       ├── AdminLayout.jsx    # Layout avec sidebar
│       ├── VueOverview.jsx    # Vue d'ensemble
│       ├── VueUtilisateurs.jsx # Liste utilisateurs
│       └── VueCaisse.jsx      # Détails caisse
│
├── components/
│   ├── Navbar.jsx
│   ├── Sidebar.jsx
│   └── admin/
│       ├── StatCard.jsx       # Carte statistique
│       ├── AdminSidebar.jsx   # Sidebar admin
│       └── UserTable.jsx      # Table utilisateurs
│
├── hooks/
│   ├── useAuth.js             # Auth utilisateur
│   └── useAdminAuth.js        # Auth admin
│
└── utils/
    ├── api.js                 # Fonctions API
    └── constants.js           # Constantes

*/

// ============================================
// EXEMPLE : FONCTION API CENTRALISÉE
// ============================================

// frontend/src/utils/api.js

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchAdminStats() {
  const token = localStorage.getItem('admin_token');
  const res = await fetch(`${API_URL}/api/admin/stats`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error('Erreur chargement stats');
  return res.json();
}

export async function fetchAdminUtilisateurs() {
  const token = localStorage.getItem('admin_token');
  const res = await fetch(`${API_URL}/api/admin/utilisateurs`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error('Erreur chargement utilisateurs');
  return res.json();
}

export async function fetchAdminCaisse() {
  const token = localStorage.getItem('admin_token');
  const res = await fetch(`${API_URL}/api/admin/caisse`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  if (!res.ok) throw new Error('Erreur chargement caisse');
  return res.json();
}

// Utilisation dans VueAdmin.jsx :
import { fetchAdminStats, fetchAdminUtilisateurs, fetchAdminCaisse } from '@/utils/api';

const chargerDonneesAdmin = async () => {
  try {
    const [statsData, usersData, caisseData] = await Promise.all([
      fetchAdminStats(),
      fetchAdminUtilisateurs(),
      fetchAdminCaisse()
    ]);
    setStats(statsData);
    setUtilisateurs(usersData.utilisateurs);
    setCaisse(caisseData);
  } catch (err) {
    setError(err.message);
  }
};
