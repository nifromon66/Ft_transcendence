import click
from extensions import db
from flask.cli import with_appcontext
from models import Category
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


DEFAULT_CATEGORIES = ("Entrée", "Plat principal", "Dessert")


@click.command("seed-categories")
@with_appcontext
def seed_categories():
    """Create the default recipe categories when they do not exist."""
    existing_names = set(
        db.session.execute(
            select(Category.name).where(Category.name.in_(DEFAULT_CATEGORIES))
        ).scalars()
    )

    missing_names = [
        name for name in DEFAULT_CATEGORIES if name not in existing_names
    ]

    if not missing_names:
        click.echo("Toutes les catégories existent déjà.")
        return

    try:
        db.session.add_all([Category(name) for name in missing_names])
        db.session.commit()
    except SQLAlchemyError as error:
        db.session.rollback()
        raise click.ClickException(
            "Impossible d'initialiser les catégories."
        ) from error

    click.echo(f"Catégories créées : {', '.join(missing_names)}")
