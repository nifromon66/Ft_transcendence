"""Validate new ingredients before saving them."""

import json

from flask import current_app, jsonify

from recipes_management.analysis import AnalysisUnavailable, analyze_content

INGREDIENT_CATEGORY_RULES = {
    "Légumes": (
        "Légumes utilisés en cuisine, y compris les tomates, "
        "champignons, pommes de terre, oignons, ail et tubercules."
    ),
    "Fruits": (
        "Fruits frais, secs, surgelés ou transformés, "
        "y compris fraises, agrumes, pommes, avocats et fruits à coque."
    ),
    "Herbes et épices": (
        "Herbes aromatiques, épices, mélanges d'épices, "
        "sel, poivre et assaisonnements secs."
    ),
    "Viandes": (
        "Viandes de toutes espèces comestibles, volailles, charcuteries et abats."
    ),
    "Poissons": ("Poissons, crustacés, coquillages et autres fruits de mer."),
    "Œufs et produits laitiers": (
        "Œufs, lait, fromages, yaourts, beurre, crème et produits dérivés du lait."
    ),
    "Céréales et féculents": (
        "Céréales, farines, riz, pâtes, pains, semoules "
        "et préparations principalement à base de céréales."
    ),
    "Épicerie": (
        "Huiles, vinaigres, sucres, sauces, conserves, "
        "lait de coco et produits d'épicerie "
        "ne relevant pas d'une catégorie plus spécifique."
    ),
    "Autres": (
        "Uniquement les ingrédients alimentaires qui ne correspondent "
        "à aucune autre catégorie disponible."
    ),
}

""" def check_ingredient_analysis(name, category_name):
    content = json.dumps({"name": name, "category": category_name}, ensure_ascii=False)
    try:
        verdict = analyze_content(content, (
            "Vérifie que le nom désigne un ingrédient culinaire comestible, "
            "que son orthographe est correcte et que la catégorie choisie "
            "n'est pas manifestement incohérente. Verifie qu'il n'existe pas une catégorie plus adaptée."
            "Accepte les ingrédients rares, régionaux, les variantes de noms usuelles et les mélanges "
            "culinaires. Refuse les objets non alimentaires, les phrases sans "
            "rapport et les noms inventés sans sens culinaire. "
            "Ne propose aucune amélioration si l'ingrédient est valide."
        ))
    except AnalysisUnavailable:
        current_app.logger.warning("Analyse IA d'ingrédient indisponible ou réponse invalide")
        return jsonify(success=False, error=(
            "La vérification de l'ingrédient est momentanément indisponible. Réessaie plus tard."
        )), 503
    if not verdict["accepted"]:
        return jsonify(success=False, error=(
            "L'ingrédient doit être corrigé : " + verdict["reason"].strip()
        )), 422
    return None
 """


def check_ingredient_analysis(name, category_name):
    content = json.dumps(
        {
            "name": name,
            "category": category_name,
            "categories": INGREDIENT_CATEGORY_RULES,
        },
        ensure_ascii=False,
    )

    instructions = (
        "Tu valides des ingrédients pour un site de recettes.\n"
        "Le JSON contient un ingrédient, sa catégorie choisie "
        "et les catégories autorisées avec leurs définitions.\n"
        "Vérifie les règles suivantes :\n"
        "1. L'ingrédient doit être réel et utilisable en cuisine.\n"
        "2. Son nom doit être correctement orthographié.\n"
        "3. Sa catégorie doit être la plus adaptée parmi celles disponibles.\n"
        "4. Les descriptions des catégories définissent la classification "
        "du site. Elles ne sont pas des listes exhaustives.\n"
        "5. Si une autre catégorie est clairement plus adaptée, refuse.\n"
        "6. Accepte les noms régionaux, ingrédients rares et mélanges culinaires.\n"
        "7. La catégorie Autres est autorisée uniquement si aucune "
        "autre catégorie ne convient.\n"
        "8. En cas de refus, explique brièvement le problème et "
        "indique la bonne catégorie si nécessaire.\n"
        "9. En cas d'acceptation, reason doit être vide.\n"
        "Exemples :\n"
        "Fraise / Fruits : accepté.\n"
        "Fraise / Légumes : refusé.\n"
        "Fraise / Autres : refusé.\n"
        "Tomate / Légumes : accepté.\n"
        "Avocat / Fruits : accepté.\n"
        "Saumon / Viandes : refusé.\n"
    )

    try:
        verdict = analyze_content(content, instructions)
    except AnalysisUnavailable:
        current_app.logger.warning(
            "Analyse IA d'ingrédient indisponible ou réponse invalide"
        )
        return jsonify(
            success=False,
            error="La vérification de l'ingrédient est momentanément indisponible. Réessaie plus tard.",
        ), 200

    if not verdict["accepted"]:
        return jsonify(
            success=False,
            error="L'ingrédient doit être corrigé : " + verdict["reason"].strip(),
        ), 200

    return None
