"""
Router pour la gestion des abonnements et leur expiration automatique
"""
from datetime import date
from fastapi import APIRouter, HTTPException
from config import supabase, logger

router = APIRouter(prefix="/api/abonnements", tags=["Abonnements"])


# ── FONCTION MÉTIER : EXPIRER LES ABONNEMENTS ──
def expirer_abonnements_echus():
    """
    Marque comme 'expire' tous les abonnements dont date_fin < aujourd'hui
    Retourne le nombre d'abonnements expirés
    """
    try:
        aujourd_hui = date.today().isoformat()
        
        # Récupérer les abonnements actifs expirés
        abonnements_a_expirer = supabase.table("abonnements")\
            .select("id, utilisateur_id, date_fin, type_abonnement")\
            .eq("statut", "actif")\
            .lt("date_fin", aujourd_hui)\
            .execute().data or []
        
        if not abonnements_a_expirer:
            return {
                "message": "Aucun abonnement à expirer",
                "nb_expires": 0,
                "abonnements": []
            }
        
        # Marquer comme expirés
        ids_expires = []
        for abo in abonnements_a_expirer:
            supabase.table("abonnements").update({
                "statut": "expire"
            }).eq("id", abo["id"]).execute()
            
            ids_expires.append(abo["id"])
            
            # Log pour suivi
            logger.info("✅ Abonnement %s expiré (user: %s, type: %s)", abo['id'], abo['utilisateur_id'], abo['type_abonnement'])
        
        return {
            "message": f"{len(ids_expires)} abonnement(s) expiré(s)",
            "nb_expires": len(ids_expires),
            "abonnements": abonnements_a_expirer
        }
    
    except Exception as e:
        logger.exception("❌ [ERREUR EXPIRATION ABONNEMENTS] : %s", str(e))
        raise Exception(f"Erreur expiration abonnements : {str(e)}")


# ── ROUTE MANUELLE : EXPIRER LES ABONNEMENTS ──
@router.post("/expirer-echus")
def expirer_abonnements_echus_route():
    """
    Route manuelle pour expirer les abonnements
    Peut être appelée par un CRON externe ou manuellement
    """
    try:
        resultat = expirer_abonnements_echus()
        return resultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── ROUTE : VÉRIFIER STATUT ABONNEMENT ──
@router.get("/statut/{utilisateur_id}")
def verifier_statut_abonnement(utilisateur_id: str):
    """
    Vérifie le statut de l'abonnement d'un utilisateur
    Retourne actif/expire/inexistant
    """
    try:
        aujourd_hui = date.today().isoformat()
        
        # Chercher l'abonnement actif de l'utilisateur
        abonnement = supabase.table("abonnements")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .order("date_fin", desc=True)\
            .limit(1)\
            .execute().data
        
        if not abonnement:
            return {
                "statut": "inexistant",
                "message": "Aucun abonnement trouvé",
                "details": None
            }
        
        abo = abonnement[0]
        
        # Vérifier si expiré
        if abo["date_fin"] < aujourd_hui and abo["statut"] == "actif":
            # Expirer automatiquement
            supabase.table("abonnements").update({
                "statut": "expire"
            }).eq("id", abo["id"]).execute()
            
            abo["statut"] = "expire"
        
        return {
            "statut": abo["statut"],
            "message": f"Abonnement {abo['statut']}",
            "details": {
                "type": abo.get("type_abonnement"),
                "date_debut": abo.get("date_debut"),
                "date_fin": abo.get("date_fin"),
                "jours_restants": (date.fromisoformat(abo["date_fin"]) - date.today()).days if abo["statut"] == "actif" else 0
            }
        }
    
    except Exception as e:
        logger.exception("❌ [ERREUR STATUT ABONNEMENT] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── ROUTE : LISTE DES ABONNEMENTS ACTIFS ──
@router.get("/actifs")
def lister_abonnements_actifs():
    """
    Liste tous les abonnements actifs
    """
    try:
        abonnements = supabase.table("abonnements")\
            .select("*")\
            .eq("statut", "actif")\
            .order("date_fin", desc=False)\
            .execute().data or []
        
        return {
            "total": len(abonnements),
            "abonnements": abonnements
        }
    
    except Exception as e:
        logger.exception("❌ [ERREUR LISTE ABONNEMENTS] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── ROUTE : LISTE DES ABONNEMENTS EXPIRÉS ──
@router.get("/expires")
def lister_abonnements_expires():
    """
    Liste tous les abonnements expirés
    """
    try:
        abonnements = supabase.table("abonnements")\
            .select("*")\
            .eq("statut", "expire")\
            .order("date_fin", desc=True)\
            .execute().data or []
        
        return {
            "total": len(abonnements),
            "abonnements": abonnements
        }
    
    except Exception as e:
        logger.exception("❌ [ERREUR LISTE EXPIRÉS] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ── ROUTE : CRÉER UN ABONNEMENT ──
@router.post("/creer")
def creer_abonnement(utilisateur_id: str, type_abonnement: str, duree_jours: int):
    """
    Crée un nouvel abonnement pour un utilisateur
    duree_jours: nombre de jours de validité (ex: 30, 90, 365)
    """
    try:
        from datetime import timedelta
        
        date_debut = date.today()
        date_fin = date_debut + timedelta(days=duree_jours)
        
        # Désactiver les anciens abonnements de cet utilisateur
        supabase.table("abonnements")\
            .update({"statut": "remplace"})\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("statut", "actif")\
            .execute()
        
        # Créer le nouvel abonnement
        nouvel_abo = supabase.table("abonnements").insert({
            "utilisateur_id": utilisateur_id,
            "type_abonnement": type_abonnement,
            "date_debut": date_debut.isoformat(),
            "date_fin": date_fin.isoformat(),
            "statut": "actif"
        }).execute()
        
        return {
            "message": "Abonnement créé ✅",
            "abonnement": nouvel_abo.data[0]
        }
    
    except Exception as e:
        logger.exception("❌ [ERREUR CRÉATION ABONNEMENT] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
