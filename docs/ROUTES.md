# API Routes

## Root

### GET /

**Summary:** Read Root  
**Responses:**
- `200 OK` – JSON object

---

## Auth

### POST /auth/login

**Summary:** Login  
**Request Body:** `LoginRequest`  
**Responses:**
- `200 OK` – `LoginResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### POST /auth/register

**Summary:** Register  
**Request Body:** `RegisterRequest`  
**Responses:**
- `200 OK` – `RegisterResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### POST /auth/validate

**Summary:** Validate  
**Request Body:** `ValidateRequest`  
**Responses:**
- `200 OK` – `ValidateResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### POST /auth/refresh

**Summary:** Refresh Token  
**Request Body:** `RefreshRequest`  
**Responses:**
- `200 OK` – `RefreshResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### GET /auth/logout

**Summary:** Logout  
**Responses:**
- `204 No Content`

## Users

### GET /users/me

**Summary:** Get Current User Profile  
**Responses:**
- `200 OK` – `UserProfileResponse`

## Messages

### GET /messages/

**Summary:** Get Messages  
**Query Parameters:**
- `conversation_id` (uuid | null)
- `message_id` (uuid | null)
- `limit` (integer, default 50)
- `offset` (integer, default 0)
- `before` (datetime | null)  

**Responses:**
- `200 OK` – Array of `GetMessagesResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### POST /messages/send

**Summary:** Send Message  
**Request Body:** `SendMessageRequest`  
**Responses:**
- `200 OK` – `SendMessageResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### PATCH /messages/edit

**Summary:** Edit Message  
**Request Body:** `EditMessageRequest`  
**Responses:**
- `200 OK` – `EditMessageResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### DELETE /messages/delete

**Summary:** Delete Message  
**Request Body:** `DeleteMessageRequest`  
**Responses:**
- `204 No Content`
- `422 Unprocessable Entity` – `HTTPValidationError`

## Conversations

### GET /conversations/

**Summary:** Get Conversations  
**Query Parameters:**
- `conversation_id` (uuid | null)
- `limit` (integer, default 50)
- `offset` (integer, default 0)  

**Responses:**
- `200 OK` – Array of `GetConversationsResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### POST /conversations/create

**Summary:** Create Conversation  
**Request Body:** `CreateConversationRequest`  
**Responses:**
- `200 OK` – `CreateConversationResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### PATCH /conversations/edit

**Summary:** Edit Conversation  
**Request Body:** `EditConversationRequest`  
**Responses:**
- `200 OK` – `EditConversationResponse`
- `422 Unprocessable Entity` – `HTTPValidationError`

### DELETE /conversations/delete

**Summary:** Delete Conversation  
**Request Body:** `DeleteConversationRequest`  
**Responses:**
- `204 No Content`
- `422 Unprocessable Entity` – `HTTPValidationError`
