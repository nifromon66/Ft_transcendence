from models.recipe import Recipe
from models.recipe_step import RecipeStep
from extensions import db


recipes = [
    Recipe(
        user_id=1,
        category_id=1,
        title="Carbonara classique",
        description="Un plat de pâtes italien traditionnel préparé avec des œufs, du parmesan et de la pancetta.",
        cooking_time=25,
        difficulty="Facile",
        image_url="",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire bouillir une grande casserole d'eau salée.",
                image_url="",
            ),
            RecipeStep(
                step_number=2,
                description="Faire cuire les spaghetti jusqu'à ce qu'ils soient al dente.",
                image_url="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire revenir la pancetta dans une poêle jusqu'à ce qu'elle soit croustillante.",
                image_url="",
            ),
            RecipeStep(
                step_number=4,
                description="Mélanger les œufs avec le parmesan râpé dans un bol.",
                image_url="",
            ),
            RecipeStep(
                step_number=5,
                description="Égoutter les pâtes et les mélanger avec la pancetta. Retirer du feu et incorporer rapidement le mélange d'œufs et de parmesan.",
                image_url="",
            ),
        ],
    ),

    Recipe(
        user_id=1,
        category_id=1,
        title="Bruschetta à la tomate",
        description="Une entrée italienne simple préparée avec des tomates fraîches, de l'ail, du basilic et du pain grillé.",
        cooking_time=15,
        difficulty="Facile",
        image_url="",
        steps=[
            RecipeStep(
                step_number=1,
                description="Couper les tomates en petits dés et les placer dans un bol.",
                image_url="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter le basilic haché, l'ail, l'huile d'olive, le sel et le poivre.",
                image_url="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire griller les tranches de pain jusqu'à ce qu'elles soient dorées et croustillantes.",
                image_url="",
            ),
            RecipeStep(
                step_number=4,
                description="Déposer le mélange de tomates sur les tranches de pain grillé et servir immédiatement.",
                image_url="",
            ),
        ],
    ),

    Recipe(
        user_id=1,
        category_id=1,
        title="Crêpes faciles",
        description="De délicieuses crêpes moelleuses, parfaites pour le petit-déjeuner.",
        cooking_time=20,
        difficulty="Facile",
        image_url="",
        steps=[
            RecipeStep(
                step_number=1,
                description="Mélanger la farine, le sucre, la levure chimique et le sel.",
                image_url="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter le lait, l'œuf et le beurre fondu, puis mélanger jusqu'à obtenir une pâte homogène.",
                image_url="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire chauffer une poêle légèrement beurrée à feu moyen.",
                image_url="",
            ),
            RecipeStep(
                step_number=4,
                description="Verser une portion de pâte dans la poêle et faire cuire jusqu'à ce que des bulles apparaissent à la surface.",
                image_url="",
            ),
            RecipeStep(
                step_number=5,
                description="Retourner la crêpe et poursuivre la cuisson jusqu'à ce qu'elle soit dorée.",
                image_url="",
            ),
        ],
    ),
]

def seed_recipes():
    if db.session.scalar(db.select(Recipe.id).limit(1)) is not None:
        return
    db.session.add_all(recipes)
    db.session.commit()