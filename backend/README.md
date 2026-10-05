# Django API

This Django REST API is designed for the React job portal in the parent folder.
It listens at `http://127.0.0.1:8000`, which is the API address currently used by
the frontend. SQLite is used locally; resume uploads are written to `media/`.

## Setup (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver 127.0.0.1:8000
```

Set `GOOGLE_CLIENT_ID` to the same OAuth client ID used by the frontend to enable
Google admin sign-in. Add a Gemini API key to `GEMINI_API_KEY` in `backend/.env`
to enable real AI matching and resume feedback. `GEMINI_MODEL` defaults to
`gemini-2.5-flash`. Keep `DJANGO_DEBUG=true` only for local development and set a
private random `DJANGO_SECRET_KEY` before deployment.

## Included API

- Authentication: `POST /auth/register`, `POST /auth/login`, `POST /auth/google`
- Jobs and companies: public read, admin-only create/update/delete
- Users: admin-only user listing and management
- Applications: submit as the signed-in user, view own applications, manage all as admin
- Saved jobs: create/list/remove for the signed-in user
- Resume upload: authenticated PDF/DOC/DOCX upload with a 5 MB limit
- Gemini AI: resume analysis and job recommendations from selectable-text PDF or DOCX
  resumes; legacy DOC uploads remain available for job applications but cannot be
  analyzed by the AI endpoint
- Platform settings: admin-only read and update

All authenticated routes use `Authorization: Bearer <access_token>`. Registration
always creates a regular user; create the first administrator with `createsuperuser`.
Resume text sent to Gemini is used to generate the requested analysis. Configure
your Google AI API key privately in `.env`; never commit that key to source control.
