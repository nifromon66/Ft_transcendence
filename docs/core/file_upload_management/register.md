## Account Registration API

### Create a User

* **Endpoint:** `POST /users` *(ou `/api/users` selon ton préfixe global)*
* **Description:** Creates a new user account in the database.

#### Request Body

* **Content-Type:** `application/json`
* **Parameters (All Required):**
  * `username` (String, Required): The user's username.
  * `email` (String, Required): The user's email address.
  * `password` (String, Required): The user's password.

If any of these fields (`username`, `email`, or `password`) are missing, or if the JSON body is empty, the server will reject the request.

#### Example Request (cURL)

```bash
curl -k -X POST https://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@gmail.com",
    "password": "test1234"
  }'