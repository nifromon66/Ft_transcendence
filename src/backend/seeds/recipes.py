import shutil
from extensions import db
from models.recipe import Recipe
from models.recipe_step import RecipeStep
from pathlib import Path
from config import UPLOAD_FOLDER

recipes = [
    Recipe(
        user_id=1,
        category_id=1,
        title="Carbonara classique",
        description="Un plat de pâtes italien traditionnel préparé avec des œufs, du parmesan et de la pancetta.",
        cooking_time=25,
        difficulty="Facile",
        image_filename="carbonara-e1521461363147-1024x670.jpg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire bouillir une grande casserole d'eau salée.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Faire cuire les spaghetti jusqu'à ce qu'ils soient al dente.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire revenir la pancetta dans une poêle jusqu'à ce qu'elle soit croustillante.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Mélanger les œufs avec le parmesan râpé dans un bol.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Égoutter les pâtes et les mélanger avec la pancetta. Retirer du feu et incorporer rapidement le mélange d'œufs et de parmesan.",
                image_filename="",
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
        image_filename="Bruschetta-a-la-tomate.jpg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Couper les tomates en petits dés et les placer dans un bol.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter le basilic haché, l'ail, l'huile d'olive, le sel et le poivre.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire griller les tranches de pain jusqu'à ce qu'elles soient dorées et croustillantes.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Déposer le mélange de tomates sur les tranches de pain grillé et servir immédiatement.",
                image_filename="",
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
        image_filename="crepes.jpeg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Mélanger la farine, le sucre, la levure chimique et le sel.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter le lait, l'œuf et le beurre fondu, puis mélanger jusqu'à obtenir une pâte homogène.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Faire chauffer une poêle légèrement beurrée à feu moyen.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Verser une portion de pâte dans la poêle et faire cuire jusqu'à ce que des bulles apparaissent à la surface.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Retourner la crêpe et poursuivre la cuisson jusqu'à ce qu'elle soit dorée.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=1,
        title="Poulet au curry vert",
        description="Un curry thaïlandais parfumé au lait de coco, piment vert et légumes frais.",
        cooking_time=35,
        difficulty="Moyen",
        image_filename="poulet-au-curry-vert.jpg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Couper le poulet en dés et faire revenir la pâte de curry vert dans de la crème de coco.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter le poulet et cuire pendant 5 minutes.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Verser le reste du lait de coco et porter à ébullition.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Ajouter les aubergines thaïes, la sauce poisson et laisser miroter 15 minutes.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Garnir de basilic thaï et de piment frais avant de servir avec du riz jasmin.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=2,
        title="Tarte Tatin classique",
        description="Une tarte aux pommes caramélisées renversée, symbole de la pâtisserie française.",
        cooking_time=50,
        difficulty="Moyen",
        image_filename="tarte-tatin-1200.jpg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Préparer un caramel ambré dans un moule à manque avec du sucre et du beurre.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Éplucher les pommes et les couper en quartiers épais.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Disposer les pommes serrées sur le caramel.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Recouvrir d'un disque de pâte feuilletée en rentrant les bords vers l'intérieur.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Enfourner 35 minutes à 180°C, puis démouler encore chaud sur un plat.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=3,
        title="Guacamole maison",
        description="Une sauce mexicaine fraîche à base d'avocats, de citron vert et de coriandre.",
        cooking_time=10,
        difficulty="Facile",
        image_filename="",
        steps=[
            RecipeStep(
                step_number=1,
                description="Éplucher et écraser la chair des avocats à la fourchette.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Hacher finement les oignons rouges, les tomates et la coriandre.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Mélanger le tout avec le jus de citron vert.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Assaisonner de sel, poivre et une pincée de piment d'Espelette.",
                image_filename="guacamole-maison-3.jpg",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=1,
        title="Risotto aux champignons",
        description="Un plat de riz crémeux réconfortant parfumé au parmesan et champignons de paris.",
        cooking_time=40,
        difficulty="Moyen",
        image_filename="",
        steps=[
            RecipeStep(
                step_number=1,
                description="Préparer le bouillon de légumes chaud et émincer les champignons.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Faire revenir l'échalote dans l'huile d'olive puis nacrer le riz arborio.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Déglacer au vin blanc et laisser réduire complètement.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Ajouter le bouillon louche par louche en remuant constamment.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Hors du feu, incorporer le beurre, le parmesan et les champignons poêlés.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=4,
        title="Salade Niçoise",
        description="Une salade estivale méditerranéenne complète au thon, œufs durs et olives.",
        cooking_time=20,
        difficulty="Facile",
        image_filename="i34581-salade-nicoise-rapide.jpeg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire cuire les œufs durs pendant 9 minutes puis les refroidir.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Laver et couper les tomates, radis, poivrons verts et cébettes.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Dresser les légumes dans un grand plat avec le thon égoutté et les anchois.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Ajouter les olives de Nice et les quartiers d'œufs durs.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Arroser d'un filet d'huile d'olive, de vinaigre, de sel et de poivre.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=1,
        title="Shakshuka",
        description="Un plat du Moyen-Orient composé d'œufs pochés dans une sauce tomate pimentée.",
        cooking_time=30,
        difficulty="Facile",
        image_filename="shakshuka.webp",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire revenir les oignons et les poivrons dans une grande poêle.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Ajouter l'ail, le cumin, le paprika et les tomates concassées.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Laisser mijoter la sauce jusqu'à ce qu'elle épaississe.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Creuser des petits puits dans la sauce et y casser les œufs.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Couvrir et laisser cuire jusqu'à ce que les blancs soient pris.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=2,
        title="Mousse au chocolat",
        description="Un dessert classique gourmand, aérien et riche en chocolat noir.",
        cooking_time=15,
        difficulty="Facile",
        image_filename="mousse-au-chocolat.webp",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire fondre le chocolat au bain-marie avec le beurre.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Séparer les blancs des jaunes d'œufs et mélanger les jaunes au chocolat.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Monter les blancs en neige ferme avec une pincée de sel.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Incorporer délicatement les blancs en neige au mélange chocolaté.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Répartir dans des ramequins et réserver au frais pendant au moins 4 heures.",
                image_filename="mousse-au-chocolat.webp",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=5,
        title="Soupe à l'oignon gratinée",
        description="Un grand classique français réconfortant surmonté de pain grillé et fromage fondu.",
        cooking_time=60,
        difficulty="Facile",
        image_filename="soupe-oignon-gratinee-delicieuse-et-reconfortante.webp",
        steps=[
            RecipeStep(
                step_number=1,
                description="Émincer les oignons et les faire caraméliser doucement au beurre.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Saupoudrer de farine, bien mélanger et déglacer avec du vin blanc.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Verser le bouillon de bœuf et laisser mijoter 30 minutes à feu doux.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Verser la soupe dans des bols allant au four et déposer une tranche de pain grillé.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Recouvrir généreusement de gruyère râpé et faire gratiner au four.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=1,
        title="Tacos au bœuf",
        description="Des tortillas garnies de viande hachée épicée, de fromage et de condiments frais.",
        cooking_time=20,
        difficulty="Facile",
        image_filename="tacos-au-boeuf-effiloche.jpeg",
        steps=[
            RecipeStep(
                step_number=1,
                description="Faire revenir la viande hachée avec l'ail, le cumin et la poudre de piment.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Réchauffer les tortillas dans une poêle sèche.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Garnir chaque tortilla de viande hachée bien chaude.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Ajouter la salade émincée, les dés de tomates, la crème aigre et le cheddar.",
                image_filename="",
            ),
        ],
    ),
    Recipe(
        user_id=1,
        category_id=1,
        title="Salmon Teriyaki",
        description="Pavé de saumon poêlé et nappé d'une sauce teriyaki sucrée-salée maison.",
        cooking_time=15,
        difficulty="Facile",
        image_filename="salmon-teriyaki-11.webp",
        steps=[
            RecipeStep(
                step_number=1,
                description="Mélanger la sauce soja, le mirin, le saké et le sucre dans un bol.",
                image_filename="",
            ),
            RecipeStep(
                step_number=2,
                description="Saisir les pavés de saumon côté peau dans une poêle bien chaude.",
                image_filename="",
            ),
            RecipeStep(
                step_number=3,
                description="Retourner le saumon et verser la sauce teriyaki dans la poêle.",
                image_filename="",
            ),
            RecipeStep(
                step_number=4,
                description="Laisser réduire la sauce jusqu'à ce qu'elle devienne syropée et en napper le poisson.",
                image_filename="",
            ),
            RecipeStep(
                step_number=5,
                description="Servir saupoudré de graines de sésame et de ciboule émincée.",
                image_filename="",
            ),
        ],
    ),
]


def seed_recipes():
    if db.session.scalar(db.select(Recipe.id).limit(1)) is not None:
        return

    source_folder = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "seed_recipe_images"
    )

    db.session.add_all(recipes)
    db.session.flush()

    for recipe in recipes:
        if not recipe.image_filename:
            continue

        source = source_folder / recipe.image_filename

        destination_folder = (
            Path(UPLOAD_FOLDER)
            / "recipes"
            / str(recipe.id)
            / "cover"
        )

        destination_folder.mkdir(parents=True, exist_ok=True)

        shutil.copy2(
            source,
            destination_folder / recipe.image_filename,
        )

    db.session.commit()
