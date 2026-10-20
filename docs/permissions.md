# Permissions and administration

The schema is created using `db.create_all()` and seeds after recreating the database (`make re`). No migration is required for this installation. The seeded test account keeps the `user` role.

## First administrator

Set these variables in `.envs/.env.backend` before running `make re`:

```dotenv
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=choose-your-password
```

The seed creates this account with the `admin` role after the test account. All three variables are optional, but must be provided together; the email must differ from the test account's email. An example is available in `.envs/.env.backend.example`.

An existing account with this email is left unchanged: the seed does not reset its password, role, or suspension status on each restart. After the database is recreated, the account is created again using the environment values.

Sign in with this account: the **Administration** and **Moderation** links appear in the menu.

## Fixed roles

| Permission | user | moderator | admin |
| --- | --- | --- | --- |
| Publish recipes | Yes | Yes | Yes |
| Manage own recipes and profile | Yes | Yes | Yes |
| Edit other users' recipes (text and images) | No | No | Yes |
| Remove other users' recipes and comments | No | Yes | Yes |
| Edit/delete shared ingredients | No | Yes | Yes |
| Manage users and assign roles | No | No | Yes |

A visitor who is not signed in has no role stored in the database. Members can still create ingredients from the recipe form. The `moderator` role allows content removal; only `admin` can also edit the text and images of other authors' recipes. A removed comment is replaced with a moderation message to preserve replies.

Roles and permissions are defined in `src/backend/auth_management/permissions.py`. Custom roles are outside the scope of this implementation.

## API

The public proxy prefixes the Flask routes below with `/api`.

| Flask route | Purpose |
| --- | --- |
| `GET /admin/users` | Paginated list (`q`, `role`, `status`, `page`, `per_page`) |
| `POST /admin/users` | Create an account with `username`, `email`, `password`, and optional `role` |
| `GET /admin/users/<id>` | Administrative account information |
| `PATCH /admin/users/<id>` | Update `username`, `email`, or `is_active` |
| `PATCH /admin/users/<id>/role` | Assign a role using `role` |
| `DELETE /admin/users/<id>` | Delete with anonymization |
| `GET /admin/moderation` | Paginated content (`kind=recipes` or `kind=comments`) |
| `DELETE /admin/comments/<id>` | Remove a comment's content |
| `DELETE /recipes/<id>` | Delete by the owner or moderation staff |

As with registration, administrative account creation requires a non-empty password, with no minimum length. The technical bcrypt limit is 72 UTF-8 bytes.

## Enforcement

- Flask checks the active account and its permissions in the database on every protected request; Vue adjusts navigation and buttons accordingly.
- Temporary 2FA JWTs remain restricted to login verification and are rejected on Socket.IO.
- A role downgrade takes effect even for JWTs that have already been issued.
- Suspending an account revokes previous JWTs through `token_version` and closes all of the account's Socket.IO connections. Reactivation requires signing in again.
- Deletion anonymizes the identity and clears the password, OAuth credentials, and 2FA secrets. Associated content remains under the name “Deleted user”.
- The last active administrator cannot be suspended, deleted, or downgraded, including through self-deletion. PostgreSQL locks serialize these changes.
- Public profiles expose neither email addresses, authentication configuration, nor permissions. `/users/me` and login responses use a private representation.
