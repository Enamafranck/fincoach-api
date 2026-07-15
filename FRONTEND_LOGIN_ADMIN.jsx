// ============================================
// LOGIN ADMIN - DESIGN PREMIUM
// ============================================
// À placer dans : frontend/src/pages/admin/LoginAdmin.jsx

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, AlertCircle, Eye, EyeOff } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function LoginAdmin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // ── OPTION 1 : Login avec endpoint dédié (à créer backend) ──
      /*
      const res = await fetch(`${API_URL}/api/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!res.ok) {
        throw new Error('Identifiants incorrects');
      }

      const data = await res.json();
      localStorage.setItem('admin_token', data.token);
      localStorage.setItem('admin_name', data.name || 'Admin');
      */

      // ── OPTION 2 : Login basique pour développement ──
      // À remplacer par une vraie authentification en production
      const adminsAutorises = [
        { email: 'admin@fincoach.cm', password: 'admin123', name: 'Franck' },
        { email: 'franck@fincoach.cm', password: 'franck123', name: 'Franck' }
      ];

      const admin = adminsAutorises.find(
        a => a.email === email && a.password === password
      );

      if (!admin) {
        throw new Error('Email ou mot de passe incorrect');
      }

      // Simuler un token (en production, utiliser un vrai JWT)
      const fakeToken = btoa(JSON.stringify({ email, timestamp: Date.now() }));
      
      localStorage.setItem('admin_token', fakeToken);
      localStorage.setItem('admin_name', admin.name);

      // Rediriger vers le dashboard
      navigate('/admin');
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 px-4">
      {/* Décoration d'arrière-plan */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-cyan-500/10 rounded-full blur-3xl"></div>
      </div>

      {/* Carte de login */}
      <div className="relative w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-2xl backdrop-blur-sm mb-4">
              <Lock className="text-white" size={32} />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Administration
            </h1>
            <p className="text-blue-100">
              Connectez-vous à votre espace admin
            </p>
          </div>

          {/* Formulaire */}
          <div className="p-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3 animate-shake">
                <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <div>
                  <p className="text-red-800 font-medium">Erreur de connexion</p>
                  <p className="text-red-600 text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Adresse email
                </label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                    <Mail size={20} />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 border-2 border-slate-200 rounded-xl
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             transition-all duration-200 text-slate-800"
                    placeholder="admin@fincoach.cm"
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              {/* Mot de passe */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                    <Lock size={20} />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-12 py-3.5 border-2 border-slate-200 rounded-xl
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             transition-all duration-200 text-slate-800"
                    placeholder="••••••••"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={togglePasswordVisibility}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Bouton de connexion */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 bg-gradient-to-r from-blue-600 to-cyan-600 
                         hover:from-blue-700 hover:to-cyan-700 text-white font-semibold 
                         rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5
                         transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                         disabled:transform-none"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Connexion en cours...
                  </span>
                ) : (
                  'Se connecter'
                )}
              </button>
            </form>

            {/* Lien mot de passe oublié (optionnel) */}
            <div className="mt-6 text-center">
              <a 
                href="#"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Mot de passe oublié ?
              </a>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-slate-50 px-8 py-4 text-center border-t border-slate-200">
            <p className="text-sm text-slate-600">
              FinCoach Admin Dashboard • Version 2026
            </p>
          </div>
        </div>

        {/* Info dev */}
        <div className="mt-6 text-center text-white/80 text-sm">
          <p className="mb-2">🔓 Comptes de test (développement) :</p>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 space-y-2">
            <div>
              <p className="font-mono">admin@fincoach.cm / admin123</p>
            </div>
            <div>
              <p className="font-mono">franck@fincoach.cm / franck123</p>
            </div>
          </div>
          <p className="mt-4 text-xs text-white/60">
            ⚠️ En production, remplacer par une vraie authentification JWT
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================
// ROUTE BACKEND À CRÉER (PRODUCTION)
// ============================================

/*
Pour une vraie authentification, crée cette route dans routers/admin.py :

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

router = APIRouter(prefix="/api/admin", tags=["Admin Auth"])

# Configuration JWT
SECRET_KEY = "ta_cle_secrete_super_longue_et_aleatoire"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 heures

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_admin(credentials: LoginRequest):
    # Liste des admins autorisés (en production, utiliser une table BDD)
    admins = [
        {"email": "admin@fincoach.cm", "password": "hash_du_mot_de_passe", "name": "Admin"},
        {"email": "franck@fincoach.cm", "password": "hash_du_mot_de_passe", "name": "Franck"}
    ]
    
    # Vérifier les credentials
    admin = next((a for a in admins if a["email"] == credentials.email), None)
    
    if not admin:
        raise HTTPException(status_code=401, detail="Email incorrect")
    
    # En production, utiliser bcrypt pour vérifier le hash
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # if not pwd_context.verify(credentials.password, admin["password"]):
    #     raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    
    # Créer le JWT token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": admin["email"],
        "name": admin["name"],
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "token": token,
        "name": admin["name"],
        "email": admin["email"]
    }

# Middleware pour protéger les routes admin
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

# Utiliser dans les routes admin :
@router.get("/stats")
def obtenir_statistiques_globales(admin = Depends(verify_admin_token)):
    # admin contient les infos du token
    ...
*/
