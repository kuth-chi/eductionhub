# Resume/CV API Documentation

This document describes the new Resume/CV API endpoints that allow users to manage their professional profiles, work history, education, skills, and more.

## Overview

The Resume API provides RESTful endpoints for managing all aspects of a user's curriculum vitae (CV/resume). All endpoints require authentication, and users can only access and modify their own data.

## Base URL

All endpoints are prefixed with `/api/v1/`

## Authentication

All endpoints require authentication via JWT tokens (HttpOnly cookies). Users can only access their own resume data.

## API Endpoints

### 1. Experience Management

**Endpoint:** `/api/v1/user-experiences/`

Manage work experience entries.

**Fields:**
- `id` (read-only): Unique identifier
- `title`: Job title
- `organization`: Organization object (read-only)
- `organization_uuid`: UUID of the organization (write-only)
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `responsibilities`: Job responsibilities description
- `attachments`: Array of attachment objects (read-only)
- `attachment_ids`: Array of attachment IDs (write-only)

**Operations:**
- `GET /api/v1/user-experiences/` - List all experiences
- `POST /api/v1/user-experiences/` - Create new experience
- `GET /api/v1/user-experiences/{id}/` - Retrieve specific experience
- `PATCH /api/v1/user-experiences/{id}/` - Update experience
- `DELETE /api/v1/user-experiences/{id}/` - Delete experience

---

### 2. Education Management

**Endpoint:** `/api/v1/user-education/`

Manage education history entries.

**Fields:**
- `id` (read-only): Unique identifier
- `institution`: School object (read-only)
- `institution_uuid`: UUID of the school (write-only)
- `degree`: Degree name
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `description`: Education description
- `attachments`: Array of attachment objects (read-only)
- `attachment_ids`: Array of attachment IDs (write-only)

**Operations:**
- `GET /api/v1/user-education/` - List all education entries
- `POST /api/v1/user-education/` - Create new education
- `GET /api/v1/user-education/{id}/` - Retrieve specific education
- `PATCH /api/v1/user-education/{id}/` - Update education
- `DELETE /api/v1/user-education/{id}/` - Delete education

---

### 3. Skills Management

**Endpoint:** `/api/v1/user-skills/`

Manage user skills.

**Fields:**
- `id` (read-only): Unique identifier
- `name`: Skill name
- `level`: Proficiency level
- `attachments`: Array of attachment objects (read-only)
- `attachment_ids`: Array of attachment IDs (write-only)

**Operations:**
- `GET /api/v1/user-skills/` - List all skills
- `POST /api/v1/user-skills/` - Create new skill
- `GET /api/v1/user-skills/{id}/` - Retrieve specific skill
- `PATCH /api/v1/user-skills/{id}/` - Update skill
- `DELETE /api/v1/user-skills/{id}/` - Delete skill

---

### 4. Languages Management

**Endpoint:** `/api/v1/user-languages/`

Manage user language proficiencies.

**Fields:**
- `id` (read-only): Unique identifier
- `name`: Language name
- `level`: Proficiency level
- `is_native`: Boolean indicating if it's a native language
- `attachments`: Array of attachment objects (read-only)
- `attachment_ids`: Array of attachment IDs (write-only)

**Operations:**
- `GET /api/v1/user-languages/` - List all languages
- `POST /api/v1/user-languages/` - Create new language
- `GET /api/v1/user-languages/{id}/` - Retrieve specific language
- `PATCH /api/v1/user-languages/{id}/` - Update language
- `DELETE /api/v1/user-languages/{id}/` - Delete language

---

### 5. Hobbies Management

**Endpoint:** `/api/v1/user-hobbies/`

Manage user hobbies and interests.

**Fields:**
- `id` (read-only): Unique identifier
- `name`: Hobby name

**Operations:**
- `GET /api/v1/user-hobbies/` - List all hobbies
- `POST /api/v1/user-hobbies/` - Create new hobby
- `GET /api/v1/user-hobbies/{id}/` - Retrieve specific hobby
- `PATCH /api/v1/user-hobbies/{id}/` - Update hobby
- `DELETE /api/v1/user-hobbies/{id}/` - Delete hobby

---

### 6. References Management

**Endpoint:** `/api/v1/user-references/`

Manage professional references.

**Fields:**
- `id` (read-only): Unique identifier
- `name`: Reference's name
- `position`: Job position
- `company`: Organization object (read-only)
- `company_uuid`: UUID of the organization (write-only)
- `relationship`: Relationship to the user
- `phone`: Contact phone number
- `email`: Contact email
- `attachments`: Array of attachment objects (read-only)
- `attachment_ids`: Array of attachment IDs (write-only)

**Operations:**
- `GET /api/v1/user-references/` - List all references
- `POST /api/v1/user-references/` - Create new reference
- `GET /api/v1/user-references/{id}/` - Retrieve specific reference
- `PATCH /api/v1/user-references/{id}/` - Update reference
- `DELETE /api/v1/user-references/{id}/` - Delete reference

---

### 7. Letters/Cover Letters Management

**Endpoint:** `/api/v1/user-letters/`

Manage cover letters and other written documents.

**Fields:**
- `id` (read-only): Unique identifier
- `user`: User object (read-only)
- `title`: Letter title
- `content`: Letter content
- `created_date` (read-only): Creation timestamp
- `updated_date` (read-only): Last update timestamp
- `is_active`: Active status

**Operations:**
- `GET /api/v1/user-letters/` - List all letters
- `POST /api/v1/user-letters/` - Create new letter
- `GET /api/v1/user-letters/{id}/` - Retrieve specific letter
- `PATCH /api/v1/user-letters/{id}/` - Update letter
- `DELETE /api/v1/user-letters/{id}/` - Delete letter

---

### 8. Profile Contacts Management

**Endpoint:** `/api/v1/user-contacts/`

Manage user's contact profiles on various platforms (LinkedIn, GitHub, etc.).

**Fields:**
- `uuid` (read-only): Unique identifier
- `platform`: Platform object (read-only)
- `platform_id`: Platform ID (write-only)
- `profile_url`: Profile URL on the platform
- `username`: Username or handle
- `privacy`: Privacy level (0=Public, 1=Connected, 2=Private)
- `created_date` (read-only): Creation timestamp
- `updated_date` (read-only): Last update timestamp
- `is_active`: Active status

**Operations:**
- `GET /api/v1/user-contacts/` - List all contact profiles
- `POST /api/v1/user-contacts/` - Create new contact profile
- `GET /api/v1/user-contacts/{uuid}/` - Retrieve specific contact profile
- `PATCH /api/v1/user-contacts/{uuid}/` - Update contact profile
- `DELETE /api/v1/user-contacts/{uuid}/` - Delete contact profile
- `GET /api/v1/user-contacts/by-platform/{platform_id}/` - Get contact by platform

---

### 9. Attachments Management

**Endpoint:** `/api/v1/user-attachments/`

Manage file attachments (certificates, documents, etc.).

**Fields:**
- `id` (read-only): Unique identifier
- `file`: File upload
- `file_url` (read-only): Full URL to the file
- `name`: File name
- `uploaded_at` (read-only): Upload timestamp
- `content_type` (read-only): MIME type

**Operations:**
- `GET /api/v1/user-attachments/` - List all attachments
- `POST /api/v1/user-attachments/` - Upload new attachment
- `GET /api/v1/user-attachments/{id}/` - Retrieve specific attachment
- `DELETE /api/v1/user-attachments/{id}/` - Delete attachment

---

## Security & Permissions

- All endpoints require authentication (JWT via HttpOnly cookies)
- Users can only access and modify their own data
- Attempting to access another user's data returns 404 Not Found
- All file uploads are validated for content type
- Attachments are only deleted if not in use by other resume items

## Example Usage

### Creating an Experience Entry

```bash
POST /api/v1/user-experiences/
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "organization_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "responsibilities": "Led development of microservices architecture, managed team of 5 engineers"
}
```

### Creating an Education Entry

```bash
POST /api/v1/user-education/
Content-Type: application/json

{
  "institution_uuid": "987fcdeb-51a2-43f1-b2c3-789012345678",
  "degree": "Master of Science in Computer Science",
  "start_date": "2018-09-01",
  "end_date": "2020-06-30",
  "description": "Focus on Machine Learning and Distributed Systems"
}
```

### Adding a Skill

```bash
POST /api/v1/user-skills/
Content-Type: application/json

{
  "name": "Python",
  "level": "Expert"
}
```

## Notes

- All date fields use ISO 8601 format (YYYY-MM-DD)
- UUIDs are used for referencing related entities (organizations, schools)
- Attachments can be linked to multiple resume items
- File uploads should use multipart/form-data encoding
- All responses are in JSON format

## Integration with Frontend

Frontend developers should:

1. Use `auth-fetch.ts` for all API calls (handles authentication)
2. Create service layer in `src/modules/resume/services/`
3. Define TypeScript types in `src/modules/resume/types.ts`
4. Add Zod schemas in `src/modules/resume/schemas.ts`
5. Create TanStack Query hooks in `src/modules/resume/hooks/`
6. Build UI components in `src/modules/resume/ui/components/`

Example service structure:
```typescript
// src/modules/resume/services/experience-service.ts
import { authFetch } from "@/lib/auth-fetch";

export class ExperienceService {
  static async getAll() {
    const response = await authFetch("/api/v1/user-experiences/");
    return response.json();
  }
  
  static async create(data) {
    const response = await authFetch("/api/v1/user-experiences/", {
      method: "POST",
      body: JSON.stringify(data),
    });
    return response.json();
  }
  
  // ... other methods
}
```
