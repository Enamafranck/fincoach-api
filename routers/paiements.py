"""
Router pour la gestion des paiements Smobilpay (Maviance)
Flux réel S3P : quote -> collect (push USSD) -> verify (polling)
Documentation officielle : https://apidocs.smobilpay.com
"""
import uuid
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import date
import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from config import (
    supabase,
    SMOBILPAY_API_KEY,
    SMOBILPAY_API_SECRET,
    SMOBILPAY_API_URL,
    SMOBILPAY_API_VERSION,
    SMOBILPAY_PAYITEM_CASHIN_MTN,
    SMOBILPAY_PAYITEM_CASHIN_ORANGE,
    SMOBILPAY_PAYITEM_CASHOUT_MTN,
    SMOBILPAY_PAYITEM_CASHOUT_ORANGE,
    FRONTEND_URL,
    BACKEND_URL,
    logger,
)

router = APIRouter(prefix="/api/paiements", tags=["Paiements"])


# ── MODÈLES ──
class InitierPaiementRequest(BaseModel):
    user_id: str
    montant: int
    sens: str          # "depot" ou "retrait"
    methode: str        # "mtn" ou "orange" (la carte n'est pas supportée par Smobilpay)
    numero: str         # ✅ numéro Mobile Money de l'utilisateur, requis pour le push USSD
    objectif_id: str = ""


# ── SIGNATURE S3P (HMAC-SHA1, standard officiel Maviance) ──
def _generer_signature(http_method: str, url: str, params: dict, secret: str) -> str:
    """
    Implémente l'algorithme de signature S3P Auth documenté par Maviance :
    https://apidocs.smobilpay.com/s3papi/Authentication.html
    1. Trier les paramètres alphabétiquement par clé
    2. Construire la chaîne "clé=valeur" jointe par "&", encodée en URL
    3. Concaténer HTTP_METHOD & URL & chaîne_paramètres
    4. Signer en HMAC-SHA1 avec le secret, encoder en base64
    """
    parametres_tries = sorted(params.items())
    chaine_params = "&".join(
        f"{urllib.parse.quote(str(k), safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in parametres_tries
    )
    base_string = f"{http_method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(chaine_params, safe='')}"

    signature_brute = hmac.new(
        secret.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1
    ).digest()

    return base64.b64encode(signature_brute).decode("utf-8")


def _construire_auth_header(http_method: str, url: str, params: dict) -> str:
    """Construit l'en-tête Authorization au format s3pAuth requis par l'API."""
    nonce = str(int(time.time() * 1000))
    timestamp = str(int(time.time()))

    parametres_auth = {
        "s3pAuth_nonce": nonce,
        "s3pAuth_signature_method": "HMAC-SHA1",
        "s3pAuth_timestamp": timestamp,
        "s3pAuth_token": SMOBILPAY_API_KEY,
    }

    tous_parametres = {**params, **parametres_auth}
    signature = _generer_signature(http_method, url, tous_parametres, SMOBILPAY_API_SECRET)

    return (
        f's3pAuth,s3pAuth_nonce="{nonce}",'
        f's3pAuth_signature="{signature}",'
        f's3pAuth_signature_method="HMAC-SHA1",'
        f's3pAuth_timestamp="{timestamp}",'
        f's3pAuth_token="{SMOBILPAY_API_KEY}"'
    )


def _appel_s3p(http_method: str, endpoint: str, params: dict = None) -> dict:
    """Effectue un appel authentifié vers l'API S3P."""
    params = params or {}
    url_complete = f"{SMOBILPAY_API_URL}{endpoint}"

    headers = {
        "Authorization": _construire_auth_header(http_method, url_complete, params),
        "X-Api-Version": SMOBILPAY_API_VERSION,
    }

    with httpx.Client(timeout=15.0) as client:
        if http_method == "GET":
            response = client.get(url_complete, params=params, headers=headers)
        else:
            # ✅ L'API S3P attend des données en form (application/x-www-form-urlencoded), pas du JSON
            response = client.post(url_complete, data=params, headers=headers)

    response.raise_for_status()
    return response.json()


def _payitem_pour(methode: str, sens: str) -> str:
    """Retourne le bon payItemId Maviance selon l'opérateur et le sens de la transaction."""
    table = {
        ("mtn", "depot"):    SMOBILPAY_PAYITEM_CASHIN_MTN,
        ("orange", "depot"): SMOBILPAY_PAYITEM_CASHIN_ORANGE,
        ("mtn", "retrait"):    SMOBILPAY_PAYITEM_CASHOUT_MTN,
        ("orange", "retrait"): SMOBILPAY_PAYITEM_CASHOUT_ORANGE,
    }
    payitem = table.get((methode, sens))
    if not payitem:
        raise HTTPException(
            status_code=400,
            detail=f"Aucun payItemId configuré pour {methode}/{sens}. Contacte Maviance pour l'obtenir."
        )
    return payitem


# ── ROUTES ──
@router.post("/initier")
def initier_paiement(req: InitierPaiementRequest):
    if req.methode not in ("mtn", "orange"):
        raise HTTPException(status_code=400, detail="Smobilpay ne supporte que MTN et Orange Money.")

    reference = f"FC-{uuid.uuid4().hex[:12].upper()}"

    supabase.from_("transactions_paiement").insert({
        "utilisateur_id"  : req.user_id,
        "montant"         : req.montant,
        "methode"         : req.methode,
        "operateur"       : "smobilpay",
        "sens"            : req.sens,
        "statut"          : "en_attente",
        "reference_api"   : reference,
        "date_initiation" : date.today().isoformat(),
    }).execute()

    # ── MODE TEST (sans clés Smobilpay configurées) ──
    if not SMOBILPAY_API_KEY or not SMOBILPAY_API_SECRET:
        logger.warning("⚠️ Mode test : simulation Smobilpay pour %s", reference)
        return {
            "mode"      : "test",
            "reference" : reference,
            "message"   : "Mode test actif — aucune clé Smobilpay configurée. Aucun push USSD envoyé."
        }

    try:
        payitem_id = _payitem_pour(req.methode, req.sens)

        # ── Étape 1 : obtenir un devis (quote) ──
        quote = _appel_s3p("POST", "/quotestd", {
            "payItemId": payitem_id,
            "amount"   : req.montant,
        })
        quote_id = quote.get("quoteId")
        if not quote_id:
            raise HTTPException(status_code=400, detail="Smobilpay n'a pas pu générer de devis.")

        # ── Étape 2 : confirmer la collecte (déclenche le push USSD sur le téléphone) ──
        collecte = _appel_s3p("POST", "/collectstd", {
            "quoteId"             : quote_id,
            "customerPhonenumber" : req.numero,
            "customerEmailaddress": "user@fincoach.cm",
            "serviceNumber"       : req.numero,
        })
        ptn = collecte.get("ptn")  # Payment Transaction Number — identifiant unique Smobilpay

        supabase.from_("transactions_paiement").update({
            "reference_api": ptn or reference,
        }).eq("reference_api", reference).execute()

        return {
            "mode"      : "production",
            "reference" : ptn or reference,
            "message"   : f"Une demande de paiement a été envoyée sur le {req.numero}. Valide-la via le code USSD reçu."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ [ERREUR SMOBILPAY INITIER] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur Smobilpay : {str(e)}")


@router.get("/statut/{reference}")
def verifier_statut_paiement(reference: str):
    """
    ✅ Route centrale pour Smobilpay : contrairement à CinetPay, il n'y a pas
    de garantie de webhook fiable en temps réel — Maviance recommande
    officiellement le polling via /verifytx comme source de vérité principale.
    Le frontend (ModalRetrait.jsx / DepotForm.jsx) appelle déjà cette route
    toutes les 3 secondes, donc aucun changement frontend n'est nécessaire.
    """
    tx = supabase.from_("transactions_paiement")\
        .select("*")\
        .eq("reference_api", reference)\
        .single()\
        .execute().data

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction introuvable.")

    # Mode test : on simule une confirmation immédiate
    if not SMOBILPAY_API_KEY or not SMOBILPAY_API_SECRET:
        if tx["statut"] == "en_attente":
            _confirmer_transaction(tx, reference)
        return {
            "reference": reference, "statut": "confirme",
            "montant": tx["montant"], "sens": tx["sens"], "methode": tx["methode"],
        }

    try:
        historique = _appel_s3p("GET", "/verifytx", {"ptn": reference})
        if isinstance(historique, list) and historique:
            statut_smobilpay = historique[0].get("status", "").upper()

            if statut_smobilpay == "SUCCESS" and tx["statut"] == "en_attente":
                _confirmer_transaction(tx, reference)
                tx["statut"] = "confirme"
            elif statut_smobilpay in ("FAILED", "CANCELLED") and tx["statut"] == "en_attente":
                supabase.from_("transactions_paiement").update({"statut": "echoue"})\
                    .eq("reference_api", reference).execute()
                tx["statut"] = "echoue"

    except Exception as e:
        logger.warning("⚠️ Vérification Smobilpay impossible pour le moment : %s", str(e))

    return {
        "reference": reference,
        "statut"   : tx["statut"],
        "montant"  : tx["montant"],
        "sens"     : tx["sens"],
        "methode"  : tx["methode"],
    }


def _confirmer_transaction(tx: dict, reference: str):
    """Applique les effets métier (créditer/débiter le solde) une fois le paiement confirmé."""
    supabase.from_("transactions_paiement").update({
        "statut"           : "confirme",
        "date_confirmation": date.today().isoformat(),
    }).eq("reference_api", reference).execute()

    profil = supabase.from_("utilisateurs")\
        .select("solde_libre")\
        .eq("id", tx["utilisateur_id"])\
        .single()\
        .execute().data

    solde_actuel = int(float(profil["solde_libre"]))

    if tx["sens"] == "depot":
        nouveau_solde = solde_actuel + int(tx["montant"])
        supabase.from_("utilisateurs").update({"solde_libre": nouveau_solde})\
            .eq("id", tx["utilisateur_id"]).execute()

        supabase.from_("cotisations").insert({
            "utilisateur_id": tx["utilisateur_id"],
            "objectif_id"   : None,
            "montant"       : tx["montant"],
            "type"          : "mise_de_cote",
            "statut"        : "effectuee",
        }).execute()

        logger.info("✅ Dépôt Smobilpay confirmé : +%s FCFA", tx["montant"])

    elif tx["sens"] == "retrait":
        logger.info("✅ Retrait Smobilpay confirmé : %s FCFA", tx["montant"])


@router.post("/webhook")
async def webhook_smobilpay(request: Request):
    """
    ⚠️ Le format exact du callback Smobilpay doit être confirmé avec Maviance
    (document d'intégration partenaire, section "Using Callback"). Ce endpoint
    est prévu en best-effort : la source de vérité reste /statut/{reference}
    (polling), déjà utilisée par le frontend. Ne pas bloquer le projet sur
    ce webhook — le polling suffit pour la soutenance et la production initiale.
    """
    body = await request.json()
    logger.info("📩 Webhook Smobilpay reçu : %s", body)

    ptn = body.get("ptn", "")
    statut = str(body.get("status", "")).upper()

    if not ptn:
        return {"message": "Payload webhook invalide"}

    tx = supabase.from_("transactions_paiement")\
        .select("*")\
        .eq("reference_api", ptn)\
        .single()\
        .execute().data

    if not tx:
        return {"message": "Transaction introuvable"}

    if statut == "SUCCESS" and tx["statut"] == "en_attente":
        _confirmer_transaction(tx, ptn)
    elif statut in ("FAILED", "CANCELLED"):
        supabase.from_("transactions_paiement").update({"statut": "echoue"})\
            .eq("reference_api", ptn).execute()

    return {"message": "Webhook traité"}