## File Upload API

### Upload File

* **Endpoint:** `POST /api/upload`
* **Description:** Uploads a raw file to the server. This endpoint is protected by JWT authentication and subject to strict size limitations.

#### Headers

| Header | Type | Description |
| :--- | :--- | :--- |
| `Authorization` | String | **Required.** Bearer token format: `Bearer <JWT_TOKEN>` |

#### Request Body

* **Content-Type:** `multipart/form-data`
* **Parameters:**
  * `file` (File, Required): The binary file to upload.

#### Response Codes

* **`201 Created`**: File successfully uploaded and saved on disk.
  ```json
  {
    "message": "File uploaded successfully",
    "filename": "test.txt"
  }

* **`400 Bad Request`**: Missing file part in the request, empty filename submitted, invalid extension or forbidden MIME type.
```json
  {
    "error": "No file part in the request"
  }
  ```json
  {
    "error": "No selected file"
  }
  ```json
  {
    "error": "File extension not allowed",
    "allowed extensions": [
      "png",
      "jpg",
      "jpeg",
      "gif",
      "webp"
    ]
  }
  {
    "error": "File content type not allowed",
    "allowed mimetypes": [
      "image/png",
      "image/jpeg",
      "image/gif",
      "image/webp"
    ]
  }




* **`401 Unauthorized`**: Missing, invalid, or expired JWT token.

* **`413 Payload Too Large`**: The file exceeds the maximum allowed size limit (MAX_UPLOAD_SIZE).
  ```json
  {
  "error": "File too large (Max 10MB)"
  }

* **`500 Internal Server Error`**: System or disk error during the file save operation (e.g., write permission issues).
  ```json
  {
  "error": "System error while saving the file: ..."
  }

#### Example Request (cURL)
    ```bash
    curl -k -X POST \
        -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
        -F "file=@test.txt" \
        https://localhost/api/upload
