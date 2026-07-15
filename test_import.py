#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de test pour vérifier l'architecture modulaire"""

from main import app
from config import ai_provider, CINETPAY_API_KEY, CINETPAY_SITE_ID, logger

logger.info("✅ Application FastAPI chargée avec succès")
logger.info("📋 Routers disponibles:")
for route in app.routes:
    if hasattr(route, 'methods') and route.path != "/openapi.json" and route.path != "/docs" and route.path != "/redoc":
        methods = ", ".join(route.methods)
        logger.info("  [%s] %s", methods, route.path)

logger.info("🎯 Configuration:")
logger.info("  - IA Provider: %s", ai_provider or 'Aucun')
logger.info("  - CinetPay configuré: %s", 'Oui' if CINETPAY_API_KEY else 'Non (mode test)')

logger.info("✨ Tous les tests d'import réussis !")
