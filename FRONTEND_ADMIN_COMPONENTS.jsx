// ============================================
// COMPOSANTS ADMIN FINCOACH - DESIGN PREMIUM
// ============================================
// À placer dans : frontend/src/components/admin/

import { useState, useEffect } from 'react';
import { 
  Users, DollarSign, TrendingUp, Activity, 
  LogOut, Menu, X, AlertCircle, CheckCircle 
} from 'lucide-react';

// ── CONFIGURATION API ──
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================
// COMPOSANT PRINCIPAL : VueAdmin
// ============================================

export default function VueAdmin() {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [stats, setStats] = useState(null);
  const [utilisateurs, setUtilisateurs] = useState([]);
  const [caisse, setCaisse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [adminName, setAdminName] = useState('Admin');

  // ── CHARGEMENT DES DONNÉES ──
  useEffect(() => {
    chargerDonneesAdmin();
  }, []);

  const chargerDonneesAdmin = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Récupérer le token admin du localStorage
      const token = localStorage.getItem('admin_token');
      const userName = localStorage.getItem('admin_name') || 'Admin';
      setAdminName(userName);

      const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      };

      // Charger les statistiques
      const statsRes = await fetch(`${API_URL}/api/admin/stats`, { headers });
      if (!statsRes.ok) throw new Error('Erreur chargement stats');
      const statsData = await statsRes.json();
      setStats(statsData);

      // Charger les utilisateurs
      const usersRes = await fetch(`${API_URL}/api/admin/utilisateurs`, { headers });
      if (!usersRes.ok) throw new Error('Erreur chargement utilisateurs');
      const usersData = await usersRes.json();
      setUtilisateurs(usersData.utilisateurs || []);

      // Charger la caisse
      const caisseRes = await fetch(`${API_URL}/api/admin/caisse`, { headers });
      if (!caisseRes.ok) throw new Error('Erreur chargement caisse');
      const caisseData = await caisseRes.json();
      setCaisse(caisseData);

      setLoading(false);
    } catch (err) {
      console.error('Erreur chargement admin:', err);
      setError('Impossible de charger les données admin. Vérifiez que le backend est lancé.');
      setLoading(false);
    }
  };

  // ── DÉCONNEXION ──
  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_name');
    window.location.href = '/admin/login';
  };

  // ── TOGGLE SIDEBAR MOBILE ──
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // ── FORMATAGE MONTANT ──
  const formatMontant = (montant) => {
    return new Intl.NumberFormat('fr-FR').format(montant || 0) + ' FCFA';
  };

  // ── CAPITALISER ──
  const capitalizeFirstLetter = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      
      {/* ── SIDEBAR ADMIN ── */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-72 bg-gradient-to-b from-slate-900 to-slate-800 text-white
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        shadow-2xl flex flex-col
      `}>
        {/* Logo / Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                FinCoach Admin
              </h1>
              <p className="text-sm text-slate-400 mt-1">Tableau de bord</p>
            </div>
            <button 
              onClick={toggleSidebar}
              className="lg:hidden p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`
              w-full flex items-center gap-3 px-4 py-3.5 rounded-xl
              text-lg font-medium transition-all duration-200
              ${activeTab === 'overview' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' 
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'}
            `}
          >
            <Activity size={22} />
            <span>Vue d'ensemble</span>
          </button>

          <button
            onClick={() => setActiveTab('utilisateurs')}
            className={`
              w-full flex items-center gap-3 px-4 py-3.5 rounded-xl
              text-lg font-medium transition-all duration-200
              ${activeTab === 'utilisateurs' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' 
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'}
            `}
          >
            <Users size={22} />
            <span>Utilisateurs</span>
          </button>

          <button
            onClick={() => setActiveTab('caisse')}
            className={`
              w-full flex items-center gap-3 px-4 py-3.5 rounded-xl
              text-lg font-medium transition-all duration-200
              ${activeTab === 'caisse' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30' 
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'}
            `}
          >
            <DollarSign size={22} />
            <span>Caisse</span>
          </button>
        </nav>

        {/* Déconnexion */}
        <div className="p-4 border-t border-slate-700 mt-auto">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3.5 rounded-xl
                     bg-red-600 hover:bg-red-700 text-white font-medium
                     transition-all duration-200 shadow-lg hover:shadow-red-600/30"
          >
            <LogOut size={20} />
            <span>Se déconnecter</span>
          </button>
        </div>
      </aside>

      {/* ── CONTENU PRINCIPAL ── */}
      <main className="flex-1 overflow-y-auto">
        {/* Header mobile */}
        <div className="lg:hidden bg-white border-b border-slate-200 p-4 sticky top-0 z-40">
          <div className="flex items-center justify-between">
            <button 
              onClick={toggleSidebar}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <Menu size={24} />
            </button>
            <h2 className="font-semibold text-slate-800">Admin FinCoach</h2>
            <div className="w-10"></div>
          </div>
        </div>

        {/* Contenu */}
        <div className="p-6 lg:p-8 pb-24">
          {/* Message de bienvenue */}
          <div className="mb-8">
            <h1 className="text-3xl lg:text-4xl font-bold text-slate-800 mb-2">
              Bonjour {capitalizeFirstLetter(adminName)} 🎯
            </h1>
            <p className="text-slate-600 text-lg">
              Voici un aperçu de votre plateforme FinCoach
            </p>
          </div>

          {/* Message d'erreur */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-800 font-medium">Erreur de connexion</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
                <button 
                  onClick={chargerDonneesAdmin}
                  className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
                >
                  Réessayer
                </button>
              </div>
            </div>
          )}

          {/* Chargement */}
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
            </div>
          )}

          {/* Contenu selon l'onglet actif */}
          {!loading && !error && (
            <>
              {activeTab === 'overview' && stats && (
                <VueOverview stats={stats} formatMontant={formatMontant} />
              )}
              {activeTab === 'utilisateurs' && (
                <VueUtilisateurs utilisateurs={utilisateurs} formatMontant={formatMontant} />
              )}
              {activeTab === 'caisse' && caisse && (
                <VueCaisse caisse={caisse} formatMontant={formatMontant} />
              )}
            </>
          )}
        </div>
      </main>

      {/* Overlay mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleSidebar}
        ></div>
      )}
    </div>
  );
}

// ============================================
// VUE D'ENSEMBLE
// ============================================

function VueOverview({ stats, formatMontant }) {
  const cartes = [
    {
      titre: 'Utilisateurs inscrits',
      valeur: stats.utilisateurs.total,
      icon: Users,
      couleur: 'blue',
      suffix: ''
    },
    {
      titre: 'Objectifs actifs',
      valeur: stats.objectifs.actifs,
      icon: TrendingUp,
      couleur: 'green',
      suffix: ''
    },
    {
      titre: 'Épargne totale',
      valeur: formatMontant(stats.epargne.montant_total),
      icon: DollarSign,
      couleur: 'purple',
      suffix: '',
      isMonetary: true
    },
    {
      titre: 'Revenus (pénalités)',
      valeur: formatMontant(stats.epargne.montant_caisse_admin),
      icon: Activity,
      couleur: 'orange',
      suffix: '',
      isMonetary: true
    }
  ];

  const couleurs = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    orange: 'from-orange-500 to-orange-600'
  };

  return (
    <div>
      {/* Cartes statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cartes.map((carte, idx) => {
          const Icon = carte.icon;
          return (
            <div 
              key={idx}
              className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-shadow duration-300 overflow-hidden"
            >
              <div className={`h-2 bg-gradient-to-r ${couleurs[carte.couleur]}`}></div>
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${couleurs[carte.couleur]} shadow-lg`}>
                    <Icon className="text-white" size={24} />
                  </div>
                </div>
                <p className="text-sm text-slate-600 font-medium mb-2">{carte.titre}</p>
                <p className={`text-3xl font-bold text-slate-800 ${carte.isMonetary ? 'text-2xl' : ''}`}>
                  {carte.valeur}{carte.suffix}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Statistiques détaillées */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Objectifs */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="text-xl font-bold text-slate-800 mb-4">Répartition des objectifs</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-green-50 rounded-xl">
              <span className="font-medium text-slate-700">Objectifs atteints</span>
              <span className="text-lg font-bold text-green-600">{stats.objectifs.atteints}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-xl">
              <span className="font-medium text-slate-700">Objectifs actifs</span>
              <span className="text-lg font-bold text-blue-600">{stats.objectifs.actifs}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-xl">
              <span className="font-medium text-slate-700">Objectifs inactifs</span>
              <span className="text-lg font-bold text-slate-600">{stats.objectifs.inactifs}</span>
            </div>
          </div>
        </div>

        {/* Activité */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h3 className="text-xl font-bold text-slate-800 mb-4">Activité plateforme</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-xl">
              <span className="font-medium text-slate-700">Cotisations effectuées</span>
              <span className="text-lg font-bold text-purple-600">{stats.activite.cotisations_effectuees}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-orange-50 rounded-xl">
              <span className="font-medium text-slate-700">Retraits effectués</span>
              <span className="text-lg font-bold text-orange-600">{stats.activite.retraits_effectues}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-red-50 rounded-xl">
              <span className="font-medium text-slate-700">Pénalités collectées</span>
              <span className="text-lg font-bold text-red-600">{formatMontant(stats.activite.montant_total_penalites)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================
// VUE UTILISATEURS
// ============================================

function VueUtilisateurs({ utilisateurs, formatMontant }) {
  return (
    <div>
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-slate-800">
            Liste des utilisateurs ({utilisateurs.length})
          </h3>
        </div>

        {/* Table responsive */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b-2 border-slate-200">
                <th className="text-left py-4 px-4 text-sm font-semibold text-slate-600">Utilisateur</th>
                <th className="text-left py-4 px-4 text-sm font-semibold text-slate-600">Email</th>
                <th className="text-right py-4 px-4 text-sm font-semibold text-slate-600">Solde libre</th>
                <th className="text-right py-4 px-4 text-sm font-semibold text-slate-600">Épargne</th>
                <th className="text-center py-4 px-4 text-sm font-semibold text-slate-600">Objectifs</th>
              </tr>
            </thead>
            <tbody>
              {utilisateurs.map((user, idx) => (
                <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                  <td className="py-4 px-4">
                    <div>
                      <p className="font-medium text-slate-800">
                        {user.prenom} {user.nom}
                      </p>
                      <p className="text-sm text-slate-500">ID: {user.id.substring(0, 8)}...</p>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-slate-600">{user.email}</td>
                  <td className="py-4 px-4 text-right font-semibold text-blue-600">
                    {formatMontant(user.solde_libre)}
                  </td>
                  <td className="py-4 px-4 text-right font-semibold text-green-600">
                    {formatMontant(user.montant_epargne)}
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-purple-100 text-purple-600 font-bold text-sm">
                      {user.nb_objectifs}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {utilisateurs.length === 0 && (
          <div className="text-center py-12">
            <Users className="mx-auto text-slate-300 mb-4" size={48} />
            <p className="text-slate-500">Aucun utilisateur inscrit</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================
// VUE CAISSE
// ============================================

function VueCaisse({ caisse, formatMontant }) {
  return (
    <div className="space-y-6">
      {/* Résumé */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg p-6 text-white">
          <p className="text-green-100 mb-2">Montant total</p>
          <p className="text-4xl font-bold">{formatMontant(caisse.montant_total)}</p>
        </div>
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg p-6 text-white">
          <p className="text-blue-100 mb-2">Nombre d'entrées</p>
          <p className="text-4xl font-bold">{caisse.nb_entrees}</p>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
          <p className="text-purple-100 mb-2">Sources</p>
          <p className="text-4xl font-bold">{Object.keys(caisse.par_source).length}</p>
        </div>
      </div>

      {/* Répartition par source */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <h3 className="text-2xl font-bold text-slate-800 mb-6">Répartition par source</h3>
        <div className="space-y-3">
          {Object.entries(caisse.par_source).map(([source, data], idx) => (
            <div key={idx} className="flex justify-between items-center p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors">
              <div>
                <p className="font-semibold text-slate-800 capitalize">{source.replace('_', ' ')}</p>
                <p className="text-sm text-slate-600">{data.count} entrée(s)</p>
              </div>
              <p className="text-xl font-bold text-green-600">{formatMontant(data.montant)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Dernières entrées */}
      <div className="bg-white rounded-2xl shadow-sm p-6">
        <h3 className="text-2xl font-bold text-slate-800 mb-6">Dernières entrées</h3>
        <div className="space-y-2">
          {caisse.dernieres_entrees.map((entree, idx) => (
            <div key={idx} className="flex justify-between items-center p-3 border-b border-slate-100 last:border-0">
              <div>
                <p className="font-medium text-slate-800 capitalize">{entree.source.replace('_', ' ')}</p>
                <p className="text-sm text-slate-500">{entree.date}</p>
              </div>
              <p className="font-bold text-green-600">{formatMontant(entree.montant)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
