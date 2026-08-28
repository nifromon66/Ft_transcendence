import os
import requests

class VaultError(Exception):
    """Raised when Vault authentication or secret retrieval fails."""

class VaultClient:
    def __init__(self):
        self._addr = os.environ.get("BACKEND_VAULT_ADDR")
        self._role_id_path = os.environ.get("BACKEND_VAULT_ROLE_ID_PATH")
        self._secret_id_path = os.environ.get("BACKEND_VAULT_SECRET_ID_PATH")
        self._token = None

    def _read_file(self, path):
        try:
            with open(path, "r") as file:
                value = file.read().strip()
        except OSError as error:
            raise VaultError("Unable to read Vault credential file: {}".format(path)) from error
        if not value:
            raise VaultError("Vault credential file is empty: {}".format(path))
        return value

    def authenticate(self):
        role_id = self._read_file(self._role_id_path)
        secret_id = self._read_file(self._secret_id_path)

        response = requests.post(
            self._addr + os.environ.get("BACKEND_VAULT_LOGIN_PATH"),
            json={
                "role_id": role_id,
                "secret_id": secret_id,
            },
            verify=os.environ["BACKEND_VAULT_CA_CERT"],
            timeout=5,
        )

        if response.status_code != 200:
            raise VaultError("Vault AppRole authentication failed: HTTP {}".format(response.status_code))
        data = response.json()
        try:
            self._token = data["auth"]["client_token"]
        except (KeyError, TypeError):
            raise VaultError("Vault authentication response did not contain a token.")

    def get_secret(self, path):
        if self._token is None:
            self.authenticate()

        response = requests.get(
            self._addr + os.environ.get("BACKEND_VAULT_GET_SECRET_DATA_PATH") + path,
            headers={
                "X-Vault-Token": self._token,
            },
            verify=os.environ["BACKEND_VAULT_CA_CERT"],
            timeout=5,
        )

        if response.status_code != 200:
            raise VaultError("Vault secret retrieval failed for '{}': HTTP {}".format(path, response.status_code))

        try:
            return response.json()["data"]["data"]
        except (KeyError, TypeError):
            raise VaultError("Invalid response receive from Vault for '{}'.".format(path))
        
    def load_secrets(self):
        return {
            "database": self.get_secret("database"),
            "flask": self.get_secret("flask"),
            "jwt": self.get_secret("jwt"),
            "oauth": self.get_secret("oauth"),
            "smtp": self.get_secret("smtp"),

        }