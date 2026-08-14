## Authentication & JWT Token Guide

To interact with protected endpoints (such as file uploads), you must first authenticate and obtain a JWT access token.

### 1. Account Creation
Before logging in, make sure you have already registered an account on the platform using the appropriate registration endpoint.

### 2. Requesting an Access Token
Send a `POST` request to the login endpoint with your account credentials in JSON format.

* **Endpoint:** `POST /api/login`
* **Content-Type:** `application/json`

#### Example Request (cURL)

```bash
curl -k -X POST https://localhost/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@gmail.com", "password": "test1234"}'