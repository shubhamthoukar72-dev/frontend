# JobAI frontend

The React application calls the Django API in `../backend`. Start that backend
at `http://127.0.0.1:8000`, then run the frontend:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_URL` in `.env` to the backend origin (for example,
`http://127.0.0.1:8000`). Restart Vite after changing the value. The backend
provides Gemini-powered resume analysis, job matching, job recommendations, and
the site-wide career assistant; configure `GEMINI_API_KEY` in `backend/.env` to
enable those features. Keep this key on the backend; never add it to a `VITE_`
frontend environment variable.

The Resume AI and AI Job Match pages require a signed-in user with a resume
uploaded to their profile. The floating JobAI Assistant is available throughout
the site and accepts up to 30 messages per hour per user or IP address.

## Sample job and company data

The sample datasets are available as public JSON at `public/data/jobs.json` and
`public/data/companies.json`, as typed arrays in `src/data/mockData.ts`, and as
a standalone SQLite-compatible schema and seed script in
`backend/sample_jobs_companies.sql`. The SQL script creates separate `jobs`
and `companies` tables and inserts five rows into each.

## Vite template notes

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
# job-search-platform
