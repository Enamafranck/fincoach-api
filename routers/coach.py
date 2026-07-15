"""
Router pour le Coach IA
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import SYSTEM_PROMPT, ai_client, ai_provider, supabase, logger

router = APIRouter(prefix="/api/coach", tags=["Coach IA"])


class MessageAPI(BaseModel):
    role: str
    content: str


class CoachRequest(BaseModel):
    system_prompt: str = SYSTEM_PROMPT
    messages: List[MessageAPI]
    user_id: str = ""


@router.post("/chat")
def coach_chat(req: CoachRequest):
    if not ai_provider:
        raise HTTPException(status_code=500, detail="Aucune clé API d'IA configurée.")

    try:
        profil = supabase.from_("utilisateurs")\
            .select("solde_libre, prenom")\
            .eq("id", req.user_id)\
            .single()\
            .execute().data

        objectifs = supabase.from_("objectifs")\
            .select("nom, montant_actuel, montant_cible, statut")\
            .eq("utilisateur_id", req.user_id)\
            .execute().data or []

        prenom = profil.get("prenom", "l'utilisateur") if profil else "l'utilisateur"
        solde  = int(float(profil.get("solde_libre", 0))) if profil else 0

        lignes_objectifs = []
        for o in objectifs:
            montant_actuel = int(float(o["montant_actuel"]))
            montant_cible  = int(float(o["montant_cible"]))
            pct = int((montant_actuel / montant_cible) * 100) if montant_cible > 0 else 0
            atteint = "OUI" if o["statut"] == "atteint" else "NON"
            lignes_objectifs.append(
                f"- {o['nom']} : {montant_actuel} FCFA épargnés sur {montant_cible} FCFA visés ({pct}%). Objectif atteint : {atteint}."
            )

        # ✅ Contexte restructuré : sections séparées et étiquetées sans ambiguïté,
        # avec une règle de raisonnement explicite pour éviter que le modèle confonde
        # le solde libre (argent disponible immédiatement) avec l'argent bloqué en objectifs.
        contexte = f"""Prénom : {prenom}

SOLDE LIBRE DISPONIBLE MAINTENANT (argent que l'utilisateur peut dépenser librement, hors épargne) : {solde} FCFA

OBJECTIFS D'ÉPARGNE EN COURS (cet argent est bloqué, séparé du solde libre) :
{chr(10).join(lignes_objectifs) if lignes_objectifs else "Aucun objectif créé pour le moment."}

RÈGLE DE RAISONNEMENT OBLIGATOIRE :
- Si on te demande si l'utilisateur "peut se permettre" un achat, compare le prix UNIQUEMENT au solde libre disponible ci-dessus. Ne mélange jamais cette question avec les objectifs d'épargne.
- Si on te demande de retirer un objectif précis, vérifie le statut "Objectif atteint" de CET objectif uniquement, pas des autres. Ne mentionne jamais un autre objectif que celui demandé, sauf si l'utilisateur le demande explicitement.
- Ne te contredis jamais dans la même réponse (ex: dire qu'un objectif est atteint puis dire qu'on ne peut pas le retirer)."""

    except Exception:
        contexte = "Contexte financier non disponible pour le moment."

    prompt_actif = SYSTEM_PROMPT.replace("{contexte_utilisateur}", contexte)

    try:
        if ai_provider == "groq":
            formatted_messages = [{"role": "system", "content": prompt_actif}]
            for m in req.messages:
                role = "assistant" if m.role in ["assistant", "model", "coach", "reponse"] else "user"
                formatted_messages.append({"role": role, "content": m.content})

            response = ai_client.chat.completions.create(
                # ✅ Modèle plus robuste pour le raisonnement financier
                # (llama-3.1-8b-instant confondait trop souvent les objectifs)
                model="llama-3.3-70b-versatile",
                messages=formatted_messages,
                max_tokens=500,  # ✅ augmenté pour éviter les réponses tronquées
                temperature=0.5,  # ✅ réduit pour plus de rigueur factuelle
            )
            texte = response.choices[0].message.content

        elif ai_provider == "gemini":
            full_prompt = f"{prompt_actif}\n\n"
            for m in req.messages:
                full_prompt += f"{m.role}: {m.content}\n"
            response = ai_client.generate_content(full_prompt)
            texte = response.text

        elif ai_provider == "anthropic":
            response = ai_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=500,
                system=prompt_actif,
                messages=[
                    {
                        "role": "assistant" if m.role in ["assistant", "model", "coach"] else "user",
                        "content": m.content
                    }
                    for m in req.messages
                ],
            )
            texte = next((b.text for b in response.content if b.type == "text"), "")

        return {"reponse": texte, "content": texte}

    except Exception as e:
        logger.exception("❌ [ERREUR COACH CHAT] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur IA: {str(e)}")