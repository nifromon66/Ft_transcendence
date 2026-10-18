# Permissions et administration

Le schéma est créé avec `db.create_all()` et les seeds après recréation de la base (`make re`). Aucune migration n’est nécessaire pour cette installation. Le compte de test seedé conserve le rôle `user`.

## Premier administrateur

Renseignez ces variables dans `.envs/.env.backend` avant `make re` :

```dotenv
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=choisissez-votre-mot-de-passe
```

Le seed crée ce compte avec le rôle `admin`, après le compte de test. Les trois variables sont facultatives mais doivent être renseignées ensemble ; l’email doit être différent de celui du compte de test. Un exemple figure dans `.envs/.env.backend.example`.

Un compte existant avec cet email n’est pas modifié : le seed ne réinitialise ni son mot de passe, ni son rôle, ni sa suspension à chaque redémarrage. Après une recréation de la base, le compte est créé à nouveau avec les valeurs de l’environnement.

Connectez-vous avec ce compte : les liens **Administration** et **Modération** apparaissent dans le menu.

## Rôles fixes

| Permission | user | moderator | admin |
| --- | --- | --- | --- |
| Publier des recettes | Oui | Oui | Oui |
| Gérer ses propres recettes et son profil | Oui | Oui | Oui |
| Modifier les recettes des autres (texte et images) | Non | Non | Oui |
| Retirer les recettes et commentaires des autres | Non | Oui | Oui |
| Modifier/supprimer les ingrédients partagés | Non | Oui | Oui |
| Gérer les utilisateurs et attribuer les rôles | Non | Non | Oui |

Un visiteur non connecté n’a pas de rôle stocké en base. Les membres peuvent toujours créer un ingrédient depuis le formulaire de recette. Le rôle moderator permet de retirer du contenu ; seul admin peut aussi modifier le texte et les images des recettes des autres auteurs. Un commentaire retiré est remplacé par un texte de modération pour préserver les réponses.

Les rôles et permissions sont définis dans `src/backend/auth_management/permissions.py`. Les rôles personnalisés ne font pas partie de cette implémentation.

## API

Le proxy public ajoute `/api` aux routes Flask ci-dessous.

| Route Flask | Fonction |
| --- | --- |
| `GET /admin/users` | Liste paginée (`q`, `role`, `status`, `page`, `per_page`) |
| `POST /admin/users` | Création avec `username`, `email`, `password`, `role` facultatif |
| `GET /admin/users/<id>` | Informations administratives du compte |
| `PATCH /admin/users/<id>` | Modification de `username`, `email` ou `is_active` |
| `PATCH /admin/users/<id>/role` | Attribution d’un rôle via `role` |
| `DELETE /admin/users/<id>` | Suppression avec anonymisation |
| `GET /admin/moderation` | Contenus paginés (`kind=recipes` ou `kind=comments`) |
| `DELETE /admin/comments/<id>` | Retrait du contenu d’un commentaire |
| `DELETE /recipes/<id>` | Suppression par le propriétaire ou la modération |

Comme pour l’inscription, la création administrative demande un mot de passe non vide, sans longueur minimale. La limite technique de bcrypt est de 72 octets UTF-8.

## Contrôles

- Flask vérifie en base le compte actif et ses permissions sur chaque requête protégée ; Vue adapte la navigation et les boutons.
- Les JWT temporaires de 2FA restent limités à la validation de connexion et sont refusés sur Socket.IO.
- Une rétrogradation prend effet avec les JWT déjà délivrés.
- Une suspension révoque les anciens JWT via `token_version` et ferme toutes les connexions Socket.IO du compte. La réactivation nécessite une nouvelle connexion.
- Une suppression anonymise l’identité et efface le mot de passe, les identifiants OAuth et les secrets 2FA. Les contenus associés restent présents sous le nom « Utilisateur supprimé ».
- Le dernier administrateur actif ne peut être suspendu, supprimé ou rétrogradé, y compris depuis la suppression personnelle. Des verrous PostgreSQL sérialisent ces changements.
- Les profils publics n’exposent ni email, ni configuration d’authentification, ni permissions. `/users/me` et les réponses de connexion utilisent une représentation privée.
- Les actions administratives et les retraits de contenu sont journalisés dans la table `admin_audits`, dans la même transaction que la modification.
