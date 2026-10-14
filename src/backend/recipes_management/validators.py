class RecipeValidationError(ValueError):
    pass


ALLOWED_DIFFICULTIES = {"facile", "moyen", "difficile"}


def validate_recipe_fields(data):
    if not isinstance(data, dict):
        raise RecipeValidationError("Aucune donnée JSON valide fournie")

    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        raise RecipeValidationError("Le titre est requis")

    title = title.strip()

    if len(title) > 150:
        raise RecipeValidationError("Le titre ne peut pas dépasser 150 caractères")

    category_id = data.get("category_id")

    if not isinstance(category_id, int) or isinstance(category_id, bool):
        raise RecipeValidationError("La catégorie est requise")

    description = data.get("description")

    if description is not None:
        if not isinstance(description, str):
            raise RecipeValidationError("La description doit être du texte")

        description = description.strip() or None

        if description is not None and len(description) > 100:
            raise RecipeValidationError(
                "La description ne peut pas dépasser 100 caractères"
            )

    cooking_time = data.get("cooking_time")

    if cooking_time is not None and (
        not isinstance(cooking_time, int)
        or isinstance(cooking_time, bool)
        or cooking_time < 0
    ):
        raise RecipeValidationError(
            "Le temps de préparation doit être un entier positif"
        )

    difficulty = data.get("difficulty")

    if difficulty == "":
        difficulty = None

    if difficulty is not None and (
        not isinstance(difficulty, str) or difficulty not in ALLOWED_DIFFICULTIES
    ):
        raise RecipeValidationError("La difficulté est invalide")

    return {
        "title": title,
        "category_id": category_id,
        "description": description,
        "cooking_time": cooking_time,
        "difficulty": difficulty,
    }


def validate_steps(data):
    steps_data = data.get("steps")

    if not isinstance(steps_data, list) or not steps_data:
        raise RecipeValidationError("La recette doit contenir au moins une étape")

    entries = []
    persisted_ids = set()

    for index, step_data in enumerate(steps_data, start=1):
        if not isinstance(step_data, dict):
            raise RecipeValidationError(f"L'étape {index} est invalide")

        step_id = step_data.get("id")

        if step_id is not None:
            if (
                not isinstance(step_id, int)
                or isinstance(step_id, bool)
                or step_id <= 0
            ):
                raise RecipeValidationError(
                    f"L'identifiant de l'étape {index} est invalide"
                )

            if step_id in persisted_ids:
                raise RecipeValidationError(
                    "Une étape ne peut pas apparaître deux fois"
                )

            persisted_ids.add(step_id)

        description = step_data.get("description")

        if not isinstance(description, str) or not description.strip():
            raise RecipeValidationError(
                f"La description de l'étape {index} est requise"
            )

        entries.append(
            {
                "id": step_id,
                "description": description.strip(),
            }
        )

    return entries


def validate_ingredients(data):
    ingredients_data = data.get("ingredients")

    if not isinstance(ingredients_data, list) or not ingredients_data:
        raise RecipeValidationError("La recette doit contenir au moins un ingrédient")

    entries = []
    selected_ids = set()

    for index, ingredient_data in enumerate(ingredients_data, start=1):
        if not isinstance(ingredient_data, dict):
            raise RecipeValidationError(f"L'ingrédient {index} est invalide")

        ingredient_id = ingredient_data.get("ingredient_id")

        if not isinstance(ingredient_id, int) or isinstance(ingredient_id, bool):
            raise RecipeValidationError(f"L'ingrédient {index} est requis")

        if ingredient_id in selected_ids:
            raise RecipeValidationError(
                "Un ingrédient ne peut pas être ajouté deux fois"
            )

        quantity = ingredient_data.get("quantity")

        if quantity is not None:
            if not isinstance(quantity, str):
                raise RecipeValidationError(
                    f"La quantité de l'ingrédient {index} est invalide"
                )

            quantity = quantity.strip() or None

        selected_ids.add(ingredient_id)

        entries.append(
            {
                "ingredient_id": ingredient_id,
                "quantity": quantity,
            }
        )

    return entries


def validate_id_list(
    data,
    field_name,
    empty_message,
    invalid_message,
    duplicate_message,
):
    ids = data.get(field_name)

    if not isinstance(ids, list) or not ids:
        raise RecipeValidationError(empty_message)

    if any(
        not isinstance(item_id, int) or isinstance(item_id, bool) for item_id in ids
    ):
        raise RecipeValidationError(invalid_message)

    if len(set(ids)) != len(ids):
        raise RecipeValidationError(duplicate_message)

    return ids


def validate_recipe_payload(data):
    validated = validate_recipe_fields(data)

    step_entries = validate_steps(data)

    validated["steps"] = step_entries
    validated["step_descriptions"] = [entry["description"] for entry in step_entries]

    validated["ingredients"] = validate_ingredients(data)

    validated["tag_ids"] = validate_id_list(
        data,
        "tag_ids",
        "La recette doit contenir au moins un tag",
        "Un ou plusieurs tags sont invalides",
        "Un tag ne peut pas être ajouté deux fois",
    )

    return validated
