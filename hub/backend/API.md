# Growery API Documentation

This document describes the REST API endpoints for the Growery application.

## Base URL

All API endpoints are prefixed with `/api`.

## Response Format

All responses are JSON objects. Error responses follow this format:
```json
{
  "error": "Error message description"
}
```

Success responses vary by endpoint (see individual endpoint documentation).

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Plants API

### Get All Plants

**GET** `/api/plants/`

Retrieve all plants in the system.

**Response:**
```json
{
  "plants": [
    {
      "id": 1,
      "nickname": "Basil",
      "species": "Ocimum basilicum",
      "created_at": "2024-01-15T10:30:00Z",
      "photo_histories": [...]
    }
  ],
  "count": 1
}
```

**Status Codes:**
- `200` - Success

---

### Get Plant by ID

**GET** `/api/plants/{plant_id}`

Retrieve a specific plant by its ID.

**Parameters:**
- `plant_id` (path, integer, required) - The ID of the plant

**Response:**
```json
{
  "id": 1,
  "nickname": "Basil",
  "species": "Ocimum basilicum",
  "created_at": "2024-01-15T10:30:00Z",
  "photo_histories": [...]
}
```

**Status Codes:**
- `200` - Success
- `404` - Plant not found

---

### Create Plant

**POST** `/api/plants/`

Create a new plant.

**Request Body:**
```json
{
  "nickname": "Basil",
  "species": "Ocimum basilicum"
}
```

**Parameters:**
- `nickname` (string, required) - The plant's nickname (non-empty)
- `species` (string, required) - The plant's species (non-empty)

**Response:**
```json
{
  "id": 1,
  "nickname": "Basil",
  "species": "Ocimum basilicum",
  "created_at": "2024-01-15T10:30:00Z",
  "photo_histories": []
}
```

**Status Codes:**
- `201` - Plant created successfully
- `400` - Invalid request (missing or empty fields)

**Example:**
```bash
curl -X POST http://localhost:5000/api/plants/ \
  -H "Content-Type: application/json" \
  -d '{"nickname": "Basil", "species": "Ocimum basilicum"}'
```

---

### Delete Plant

**DELETE** `/api/plants/{plant_id}`

Delete a specific plant by its ID.

**Parameters:**
- `plant_id` (path, integer, required) - The ID of the plant to delete

**Response:**
```json
{
  "message": "plant 1 removed"
}
```

**Status Codes:**
- `200` - Plant deleted successfully
- `404` - Plant not found
- `500` - Server error

---

### Delete All Plants

**DELETE** `/api/plants/`

Delete all plants and their photo histories. **Use with caution!**

**Request Body:**
```json
{
  "confirm": true
}
```

**Parameters:**
- `confirm` (boolean, required) - Must be `true` to confirm deletion

**Response:**
```json
{
  "message": "deleted 5 plant(s)"
}
```

**Status Codes:**
- `200` - Plants deleted successfully
- `400` - Confirmation required

---

## Photo Histories API

### Get Photo Histories for Plant

**GET** `/api/plants/{plant_id}/photo_histories`

Retrieve all photo histories for a specific plant, ordered by creation date (newest first).

**Parameters:**
- `plant_id` (path, integer, required) - The ID of the plant

**Response:**
```json
[
  {
    "id": 1,
    "plant_id": 1,
    "image_location": "histories/abc123.jpg",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

**Status Codes:**
- `200` - Success
- `404` - Plant not found

---

### Add Photo History

**POST** `/api/plants/{plant_id}/photo_histories`

Upload a photo for a plant.

**Parameters:**
- `plant_id` (path, integer, required) - The ID of the plant
- `image` (form-data, file, required) - The image file to upload
- `date` (form-data, string, optional) - ISO format date string (e.g., "2024-01-15T10:30:00Z")

**Supported File Types:**
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)

**Note:** If no date is provided, the system will attempt to extract the date from EXIF metadata in the image file. If that fails, it will use the current time.

**Response:**
```json
{
  "id": 1,
  "plant_id": 1,
  "image_location": "histories/abc123.jpg",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201` - Photo history created successfully
- `400` - Invalid file type or no file provided
- `404` - Plant not found
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/api/plants/1/photo_histories \
  -F "image=@photo.jpg" \
  -F "date=2024-01-15T10:30:00Z"
```

---

### Get Photo History Image

**GET** `/api/plants/{plant_id}/photo_histories/{photo_id}`

Retrieve the actual image file for a photo history entry.

**Parameters:**
- `plant_id` (path, integer, required) - The ID of the plant
- `photo_id` (path, integer, required) - The ID of the photo history

**Response:**
- Image file with appropriate MIME type

**Status Codes:**
- `200` - Success
- `404` - Plant, photo history, or image file not found

**Example:**
```bash
curl http://localhost:5000/api/plants/1/photo_histories/1 -o image.jpg
```

---

## Pump Controls API

### Activate Pump

**POST** `/api/pumps/`

Activate the water pump.

**Response:**
```json
{
  "message": "roger roger"
}
```

**Status Codes:**
- `200` - Pump activated successfully
- `500` - Server error

**Example:**
```bash
curl -X POST http://localhost:5000/api/pumps/
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

### Common Error Messages

- `"Resource not found"` - 404 error
- `"Bad request"` - 400 error (invalid input)
- `"Internal server error"` - 500 error
- `"nickname is required and must be a non-empty string"` - Validation error
- `"species is required and must be a non-empty string"` - Validation error
- `"no image file provided"` - Missing file in upload
- `"invalid file type"` - Unsupported file format
- `"plant not found"` - Plant doesn't exist
- `"photo history not found"` - Photo history doesn't exist
- `"image file not found"` - Image file missing from filesystem

---

## Date Format

Dates are returned in ISO 8601 format with UTC timezone:
```
2024-01-15T10:30:00Z
```

When providing dates in requests, you can use:
- ISO format: `2024-01-15T10:30:00Z` or `2024-01-15T10:30:00+00:00`
- The system will automatically convert to UTC

---

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for all origins. This allows frontend applications to make requests from different domains.

---

## Notes

- All timestamps are in UTC
- Photo history images are stored in the `histories/` directory
- Image file paths in the database are relative to the backend directory
- The system automatically extracts dates from EXIF metadata when available
- File uploads are limited to image types: PNG, JPEG, GIF, WebP

