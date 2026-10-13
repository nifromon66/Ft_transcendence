"""Run with backend dependencies; all data lives in an in-memory SQLite DB."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/backend"))

from extensions import db, jwt
from flask import Flask
from flask_jwt_extended import create_access_token
from models import (
    Category,
    Ingredient,
    IngredientCategory,
    Rating,
    Recipe,
    Tag,
    User,
    Utensil,
)
from recipe_management.routes import recipe_bp
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from user_xp_management.experience import add_xp, remove_xp


class ExperienceTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite://",
            JWT_SECRET_KEY="test-secret-key-for-experience-tests-only",
            BCRYPT_LOG_ROUNDS=4,
        )
        db.init_app(app)
        jwt.init_app(app)
        app.register_blueprint(recipe_bp)
        self.context = app.app_context()
        self.context.push()
        db.create_all()
        # Avoid password hashing: these fixtures only use JWT authentication.
        db.session.execute(
            User.__table__.insert(),
            [
                dict(
                    id=1,
                    username="author",
                    email="author@test.local",
                    password_hash="unused",
                ),
                dict(
                    id=2,
                    username="reader",
                    email="reader@test.local",
                    password_hash="unused",
                ),
            ],
        )
        db.session.add_all(
            [
                Category("Test", id=1),
                IngredientCategory(id=1, name="Test"),
                Ingredient("Test", id=1, category_id=1),
                Tag("Test"),
                Utensil("Test"),
            ]
        )
        db.session.commit()
        self.client = app.test_client()
        self.headers = {
            user_id: {
                "Authorization": "Bearer " + create_access_token(identity=str(user_id))
            }
            for user_id in (1, 2)
        }
        self.payload = {
            "title": "Test recipe",
            "category_id": 1,
            "steps": [{"description": "Mix ingredients"}],
            "ingredients": [{"ingredient_id": 1, "quantity": "100 g"}],
            "utensil_ids": [1],
            "tag_ids": [1],
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def xp(self, user_id=1):
        db.session.expire_all()
        return db.session.get(User, user_id).xp

    def publish(self):
        response = self.client.post(
            "/recipes", json=self.payload, headers=self.headers[1]
        )
        self.assertEqual(response.status_code, 201, response.json)
        return response.json["id"]

    def test_add_xp_accumulates_and_supports_rollback(self):
        self.assertEqual(add_xp(1, 30), 30)
        self.assertEqual(add_xp(1, 5), 35)
        db.session.commit()
        self.assertEqual(self.xp(), 35)
        add_xp(1, 10)
        db.session.rollback()
        self.assertEqual(self.xp(), 35)

    def test_invalid_amounts_and_missing_user(self):
        for amount in (0, -5, True, 1.5, "30", None):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                add_xp(1, amount)
        with self.assertRaises(NoResultFound):
            add_xp(999, 5)
        self.assertIsNone(self.xp())

    def test_recipe_creation_and_edit(self):
        recipe_id = self.publish()
        self.assertEqual(self.xp(), 30)
        response = self.client.put(
            f"/recipes/{recipe_id}", json=self.payload, headers=self.headers[1]
        )
        self.assertEqual(response.status_code, 200, response.json)
        self.assertEqual(self.xp(), 30)
        self.publish()
        self.assertEqual(self.xp(), 60)

    def test_rating_creation_duplicate_and_edit(self):
        recipe_id = self.publish()
        url = f"/recipes/{recipe_id}/ratings"
        response = self.client.post(url, json={"score": 4}, headers=self.headers[2])
        self.assertEqual(response.status_code, 201, response.json)
        self.assertEqual(self.xp(2), 5)
        response = self.client.post(url, json={"score": 4}, headers=self.headers[2])
        self.assertEqual(response.status_code, 409)
        response = self.client.put(url, json={"score": 5}, headers=self.headers[2])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.xp(2), 5)
        self.assertEqual(self.xp(1), 30)

    def test_invalid_actions_award_nothing(self):
        response = self.client.post("/recipes", json={}, headers=self.headers[1])
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(self.xp())
        recipe_id = self.publish()
        url = f"/recipes/{recipe_id}/ratings"
        self.assertEqual(
            self.client.post(
                url, json={"score": 5}, headers=self.headers[1]
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                url, json={"score": 6}, headers=self.headers[2]
            ).status_code,
            400,
        )
        self.assertIsNone(self.xp(2))
        self.assertEqual(self.xp(1), 30)

    def test_failed_commit_rolls_back_recipe_and_xp(self):
        with patch.object(
            db.session, "commit", side_effect=SQLAlchemyError("test failure")
        ):
            response = self.client.post(
                "/recipes", json=self.payload, headers=self.headers[1]
            )
        self.assertEqual(response.status_code, 500)
        self.assertIsNone(self.xp())
        self.assertEqual(db.session.scalars(select(Recipe)).all(), [])

    def test_failed_commit_rolls_back_rating_and_xp(self):
        recipe_id = self.publish()
        with patch.object(
            db.session, "commit", side_effect=SQLAlchemyError("test failure")
        ):
            response = self.client.post(
                f"/recipes/{recipe_id}/ratings",
                json={"score": 4},
                headers=self.headers[2],
            )
        self.assertEqual(response.status_code, 500)
        self.assertIsNone(self.xp(2))
        self.assertEqual(db.session.scalars(select(Rating)).all(), [])

    def test_remove_xp_and_floor(self):
        self.assertEqual(remove_xp(1, 5), 0)  # Legacy NULL XP.
        add_xp(1, 40)
        self.assertEqual(remove_xp(1, 30), 10)
        db.session.commit()
        self.assertEqual(self.xp(), 10)
        self.assertEqual(remove_xp(1, 30), 0)
        db.session.rollback()
        self.assertEqual(self.xp(), 10)

    def test_remove_xp_invalid_amounts_and_missing_user(self):
        for amount in (0, -5, True, 1.5, "30", None):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                remove_xp(1, amount)
        with self.assertRaises(NoResultFound):
            remove_xp(999, 5)
        self.assertIsNone(self.xp())

    def test_recipe_deletion_removes_only_author_reward(self):
        recipe_id = self.publish()
        self.publish()
        url = f"/recipes/{recipe_id}"
        self.client.post(url + "/ratings", json={"score": 4}, headers=self.headers[2])
        self.assertEqual(
            self.client.delete(url, headers=self.headers[2]).status_code, 403
        )
        self.assertEqual(self.xp(), 60)
        self.assertEqual(
            self.client.delete(url, headers=self.headers[1]).status_code, 200
        )
        self.assertEqual(self.xp(), 30)
        self.assertEqual(self.xp(2), 5)
        self.assertIsNone(db.session.get(Recipe, recipe_id))
        self.assertEqual(
            self.client.delete(url, headers=self.headers[1]).status_code, 404
        )
        self.assertEqual(self.xp(), 30)

    def test_rating_deletion_and_recreation(self):
        recipe_id = self.publish()
        url = f"/recipes/{recipe_id}/ratings"
        self.assertEqual(
            self.client.post(
                url, json={"score": 4}, headers=self.headers[2]
            ).status_code,
            201,
        )
        self.assertEqual(
            self.client.delete(url, headers=self.headers[1]).status_code, 404
        )
        self.assertEqual(self.xp(), 30)
        self.assertEqual(
            self.client.delete(url, headers=self.headers[2]).status_code, 200
        )
        self.assertEqual(self.xp(2), 0)
        self.assertEqual(
            self.client.delete(url, headers=self.headers[2]).status_code, 404
        )
        self.assertEqual(self.xp(2), 0)
        self.assertEqual(
            self.client.post(
                url, json={"score": 5}, headers=self.headers[2]
            ).status_code,
            201,
        )
        self.assertEqual(self.xp(2), 5)

    def test_failed_recipe_deletion_restores_xp_and_recipe(self):
        recipe_id = self.publish()
        with patch.object(
            db.session, "commit", side_effect=SQLAlchemyError("test failure")
        ):
            response = self.client.delete(
                f"/recipes/{recipe_id}", headers=self.headers[1]
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.xp(), 30)
        self.assertIsNotNone(db.session.get(Recipe, recipe_id))

    def test_failed_rating_deletion_restores_xp_and_rating(self):
        recipe_id = self.publish()
        url = f"/recipes/{recipe_id}/ratings"
        self.client.post(url, json={"score": 4}, headers=self.headers[2])
        with patch.object(
            db.session, "commit", side_effect=SQLAlchemyError("test failure")
        ):
            response = self.client.delete(url, headers=self.headers[2])
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.xp(2), 5)
        self.assertIsNotNone(db.session.scalar(select(Rating)))


if __name__ == "__main__":
    unittest.main()
