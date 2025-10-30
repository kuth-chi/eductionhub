# Copilot Coding Agent Instructions – EducationHub

Concise, project-specific guidance so an AI agent can be productive immediately. Stick to these established patterns; do not introduce new architectures without discussion.

## 1. Big Picture

- Monorepo-style workspace: Next.js (frontend under `web_frontend/web`) + Django REST backend (`v0.0.2`).
- when access terminal to backend, `cd v0.0.2 && .venv\Scripts\activate` first.
- Core domain: school & education data (schools, branches, majors, degrees, scholarships), plus organization / ads manager, geo (countries, states, cities, villages), authentication & user profiles.
- Frontend uses: Next.js App Router, feature-based modules (`src/modules/<feature>`), tRPC for some internal typing + direct REST calls via `auth-fetch.ts`, TanStack Query for server state, Zod for validation.
- Backend: Django + DRF viewsets registered in `api/urls.py` using a `DefaultRouter` (naming pattern: kebab-case paths e.g. `major-document-requirements`). Ads manager endpoints share `ad-*` prefix.

## 2. Backend Conventions

- Add new REST resources as DRF ViewSets; register in `api/urls.py` with kebab-case route + explicit `basename`.
- Keep authentication-sensitive endpoints aligned with existing patterns: JWT in HttpOnly cookies, auth status at `/api/v1/auth-status/` (see existing auth views in `api/views/auth/`).
- Environment & cross-domain auth: respect vars defined in backend `.env` (`BACKEND_URL`, `FRONTEND_URL`, etc.).
- Cache prevention on auth: follow existing headers & patterns—do not re-enable caching for auth routes.
- File uploads: existing endpoint `upload_file` (see `api/views/upload_views.py`). Reuse rather than reinvent.

## 3. Frontend Conventions

- Feature folders: `modules/<feature>/` contain `api/`, `hooks/`, `services/`, `ui/components/`, `ui/views/`, `schemas.ts`, `types.ts`.
- Shared primitives in `components/` and `components/ui/`; never duplicate a UI primitive—extend via props.
- Always derive backend URLs using env utility `src/lib/env.ts` (e.g. `BACKEND_API_URL`). Do NOT inline `http://localhost`.
- Use `auth-fetch.ts` for authenticated REST calls; ensure cache-prevention headers for auth-sensitive actions.
- Mark auth-related pages & routes with dynamic export flags when necessary (`export const dynamic = 'force-dynamic'` etc.) consistent with docs in `AUTH_CACHE_PREVENTION_SUMMARY.md`.
- Validation: Zod schemas colocated (e.g. `schemas.ts`); reuse in forms + server calls; do not create ad-hoc runtime validators.

### 3.1 SSR-First Architecture (Critical)

**Default to Server Components** — Keep components as server-rendered unless they REQUIRE client-side features.

**When to use `"use client"`:**
- Component uses React hooks (`useState`, `useEffect`, `useContext`, etc.)
- Component needs browser APIs (`window`, `navigator`, `localStorage`, `document`)
- Component has event handlers (`onClick`, `onChange`, `onSubmit`)
- Component uses client-only libraries (chart libraries, animation libs)

**Push `"use client"` down the tree** — Extract interactive parts into separate client components rather than marking entire pages/views as client. Example:
```tsx
// ❌ BAD: Entire page is client
"use client";
export default function Page() {
  return (
    <div>
      <StaticContent />
      <button onClick={...}>Click</button>
    </div>
  );
}

// ✅ GOOD: Only interactive part is client
export default function Page() {
  return (
    <div>
      <StaticContent /> {/* SSR */}
      <InteractiveButton /> {/* Client */}
    </div>
  );
}
```

**Benefits of SSR-first:**
- Better SEO (search engines get full HTML)
- Faster initial page load (less JavaScript)
- Improved Core Web Vitals
- Data fetching happens server-side (faster, more secure)

**Reference implementation:** See `modules/events/ui/views/event-detail-page-view.tsx` and its extracted client components (`event-management-menu.tsx`, `event-share-button.tsx`, `event-tabs-section.tsx`) for the pattern. Documentation in `docs/EVENT_DETAIL_SSR_OPTIMIZATION.md`.

## 4. Naming & Routing Patterns

- Backend routes: kebab-case plural nouns (`educational-levels`, `school-branches`, `ad-campaigns`). Match existing prefixes when extending a domain (e.g. `ad-` for ads, `school-` for school-scoped resources).
- Frontend module filenames: `kebab-case` for folders, PascalCase for React components, `snake_case` not used.
- Keep new tRPC routers under `src/server/api/routers/` and add to `root.ts`.

## 5. Authentication & Security

- Tokens: handled via HttpOnly cookies—never access directly in client JS. Use existing auth service / hooks.
- Cross-subdomain cookies: honor domain logic from production fix (see `AUTHENTICATION_PRODUCTION_FIX.md`). When modifying login/logout flows, replicate cookie domain + SameSite settings.
- Always include cache-prevention headers for auth endpoints and avoid localStorage for sensitive data.

## 6. Environment & Config

- Centralized environment access only via `src/lib/env.ts`; add new vars with validation & defaults there plus docs in `ENV_CONFIG.md`.
- Keep parity between frontend `NEXT_PUBLIC_*` and backend `.env` when introducing cross-surface config.

## 7. Data & Types

- Reuse TypeScript types in `types/` or feature `types.ts`; ensure API response shapes align with DRF serializers.
- When adding backend serializers/models, mirror fields in frontend types + adjust Zod schemas.
- Prefer incremental schema evolution (add fields, avoid breaking renames unless coordinated).

## 8. Adding a New Resource (Example Workflow)

1. Backend: model + serializer + viewset → register in `api/urls.py` (`router.register('resource-name', ResourceViewSet, basename='resource-name')`).
2. Frontend: add `modules/<resource>/` with `schemas.ts`, `types.ts`, `api/<resource>-client.ts` using `auth-fetch.ts`.
3. Create hooks (`use<Resource>Query`, `useCreate<Resource>Mutation`) leveraging TanStack Query.
4. Build UI components under `ui/components/` and page/view under `ui/views/` or App Router route.
5. Update navigation if needed via existing layout components.

## 9. Testing & Quality

- Lint with `npm run lint` (frontend) before committing UI logic changes.
- Keep console clean—repository includes scripts to strip stray `console.log` calls; prefer debug utilities.
- For backend changes touching auth or cookies, manually verify headers + cookie attributes.

## 10. Performance & Maps

- Large/map components: load dynamically (see geo module patterns like `map-client-only.tsx`).
- Avoid blocking bundle: prefer dynamic import for heavy libs or rarely used admin panels.

## 11. What NOT to Do

- Do NOT bypass env utility for URLs.
- Do NOT store JWTs or sensitive tokens in localStorage/sessionStorage.
- Do NOT introduce a new state management library (Redux, MobX) without justification.
- Do NOT create duplicate UI primitives—extend existing components.
- Do NOT add `"use client"` to components that don't need it—default to server components for better performance and SEO.

## 12. Quick Reference Key Files

- Backend routing: `v0.0.2/api/urls.py`
- Auth cache prevention patterns: `docs/AUTH_CACHE_PREVENTION_SUMMARY.md`
- Frontend architecture: `docs/FRONTEND_ARCHITECTURE.md`
- SSR optimization patterns: `docs/EVENT_DETAIL_SSR_OPTIMIZATION.md`
- Environment config: `docs/ENV_CONFIG.md`, `src/lib/env.ts`
- Auth production fixes: `docs/AUTHENTICATION_PRODUCTION_FIX.md`
- Upload utility: `src/lib/file-upload.ts`

---

If a needed pattern isn't documented here, search existing feature modules first and mirror their structure. Ask for clarification before introducing divergent patterns.
