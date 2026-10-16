"""XP rewards shared by server-side actions."""

from sqlalchemy import case, func, update

from extensions import db
from models.user import User

RECIPE_CREATED_XP = 30
RECIPE_RATED_XP = 5


def add_xp(user_id: int, amount: int) -> int:
    """Atomically add positive integer XP and return the new total.

    The caller must commit (or roll back) together with the rewarded action.
    Raises ValueError for an invalid amount and NoResultFound for a missing user.
    """
    if type(amount) is not int or amount <= 0:
        raise ValueError("XP amount must be a positive integer")

    return db.session.execute(
        update(User)
        .where(User.id == user_id)
        .values(xp=func.coalesce(User.xp, 0) + amount)
        .returning(User.xp)
    ).scalar_one()


def remove_xp(user_id: int, amount: int) -> int:
    """Atomically subtract positive integer XP, clamping the total to zero.

    The caller must commit (or roll back) together with the deleted action.
    Raises ValueError for an invalid amount and NoResultFound for a missing user.
    """
    if type(amount) is not int or amount <= 0:
        raise ValueError("XP amount must be a positive integer")

    remaining = func.coalesce(User.xp, 0) - amount
    return db.session.execute(
        update(User)
        .where(User.id == user_id)
        .values(xp=case((remaining > 0, remaining), else_=0))
        .returning(User.xp)
    ).scalar_one()
