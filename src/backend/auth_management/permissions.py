"""Fixed roles shared by API authorization and the connected user's response."""

ROLES = ("user", "moderator", "admin")
ROLE_PERMISSIONS = {
    "user": frozenset({"recipes.create"}),
    "moderator": frozenset(
        {"recipes.create", "content.moderate", "ingredients.manage"}
    ),
    "admin": frozenset(
        {
            "recipes.create",
            "recipes.edit_any",
            "content.moderate",
            "ingredients.manage",
            "users.read",
            "users.create",
            "users.update",
            "users.delete",
            "roles.assign",
        }
    ),
}


def permissions_for(role):
    return ROLE_PERMISSIONS.get(role, frozenset())
