# CELEBIOS Total Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `www.celebios.com` as an accessible static Vercel site that preserves the public SEO footprint, replaces Wix/Kajabi marketing pages, and presents only Lenguaje y Comunicación de los Gatos as currently available.

**Architecture:** `build.py` remains the only publication entry point. Versioned JSON/CSV files are the source of truth for programs and redirects; static HTML, CSS, and JavaScript are rendered into ignored `site/`, while Vercel Functions under `api/` handle contact and double-opt-in interest capture. Public migration is blocked until GSC and Wix Analytics evidence has been imported and validated.

**Tech Stack:** Python 3 standard library, static HTML/CSS/JavaScript, Node.js Vercel Functions, Resend HTTP API, Vercel bulk redirects, `unittest`/Node test runner, Playwright/Lighthouse-style browser audits.

## Global Constraints

- Work only in the isolated worktree and never alter the user's existing checkout.
- Do not modify `/aula`, Supabase, exams, videos, importers, Kajabi exports, DNS, or Kajabi account state.
- Canonical origin is exactly `https://www.celebios.com`.
- Only `Lenguaje y Comunicación de los Gatos` has `status: "available"`; every other program has `status: "historical"` and no price, enrollment CTA, availability claim, or `Offer` schema.
- Do not publish unverified superlatives, official-validity claims, teacher affiliations, statistics, names, photographs, prices, awards, or recognition.
- Public copy is Spanish, clear, professional, and evidence-led. Interest lists are separated by topic.
- No personal data in URLs, GA4 events, application logs, or committed fixtures.
- Every task follows audit → fix → audit → continue and ends with an atomic commit only after spec and quality review pass.
- Critical/Important findings block progress. Minor findings are recorded for final triage.

---

### Task 1: Public SEO inventory and redirect contract

**Files:**
- Create: `scripts/sync_migration_inventory.py`
- Create: `tests/test_migration_inventory.py`
- Create: `migracion/urls-wix.csv`
- Create: `migracion/urls-kajabi.csv`
- Create: `migracion/redirects.csv`
- Create: `migracion/README.md`

**Interfaces:**
- `normalize_source_url(url: str) -> str`
- `classify_source(path: str, host: str) -> tuple[str, str, str]` returning category, topic/cohort, and destination.
- CSV columns: `source_url,destination_path,status_code,category,topic_or_cohort,clicks,impressions,position,backlinks,priority,confidence,manual_review`.
- `status_code` is `301` or `404`; destinations are root-relative and never the homepage except true home aliases.

- [ ] Write failing tests for canonicalization, semantic mappings, 404 junk, one-hop destinations, CSV fields, duplicate detection, and exact live snapshot counts of 371 Wix plus 15 Kajabi URLs.
- [ ] Run `python -m unittest tests.test_migration_inventory -v` and verify the intended failures.
- [ ] Implement deterministic sitemap ingestion and classification without collecting personal page content.
- [ ] Generate the three CSV snapshots and document that GSC/Wix metrics remain blank until authenticated export is imported.
- [ ] Re-run the focused tests and `python build.py`; verify both pass.
- [ ] Have Claude Opus audit semantic mapping and Claude Sonnet audit mechanical coverage; fix and re-audit until clean.
- [ ] Commit `feat: add complete SEO migration inventory`.

### Task 2: Program data, research register, and static build contract

**Files:**
- Create: `contenido/programas.json`
- Create: `INVESTIGACION.md`
- Create: `tests/test_content_contract.py`
- Modify: `build.py`
- Modify: `package.json`

**Interfaces:**
- Program fields: `slug,title,status,category,topic,summary,evidence,interest_topic`; only available programs may add `offer`.
- `build.py` validates content, renders public sources, emits `sitemap.xml`, `robots.txt`, `404.html`, and `vercel.json`, and references `migracion/redirects.csv` through `bulkRedirectsPath`.
- Optional `GA4_MEASUREMENT_ID` is injected at build time; absent means analytics code is omitted.

- [ ] Write failing tests proving the closed status enum, sole availability of the cat course, forbidden-field rejection on historical programs, evidence requirements, canonical consistency, and redirect configuration.
- [ ] Run focused tests and verify they fail for missing contracts.
- [ ] Add the source-of-truth data and research register using only evidence already present in the repository or authoritative cited sources.
- [ ] Refactor the build minimally to validate and emit the required artifacts while preserving `/aula` and `api/` byte-for-byte.
- [ ] Re-run tests and the full build, audit generated output, fix, and re-audit.
- [ ] Commit `feat: establish verified content and build contracts`.

### Task 3: Lámina Viva design system and public pages

**Files:**
- Modify/Create under: `redesign-v2/`
- Create: `tests/test_public_site.py`

**Interfaces:**
- Required navigation destinations: `/`, `/cursos`, `/curso-lenguaje-felino`, `/historia`, `/egresados`, `/practicas-de-campo`, `/docentes`, `/admisiones`, `/contacto`, `/aviso-de-privacidad`.
- Shared tokens use accessible deep navy, purple, cyan, and green; bright logo colors are accents, not body text on light backgrounds.
- The visual signature is a field-journal “living plate” composition with restrained labeled observations and no species claim that lacks MVZ review.

- [ ] Write failing structural tests for required pages, navigation, landmarks, one H1, canonical, meta description, no forbidden claims, no historical offer/enrollment copy, and exact available-course status.
- [ ] Run tests and verify failures before page implementation.
- [ ] Build the shared responsive shell, course catalog, cat-course page, historical archive, trajectory, graduates, field practices, teachers, admissions, contact, privacy, and real 404 page.
- [ ] Use existing rights-safe brand assets; generated animal illustrations must be saved in the project, documented with prompts, and marked pending MVZ approval until reviewed.
- [ ] Run structural/build tests, keyboard/contrast audit, desktop/mobile screenshots, and a qualitative Opus review; fix and re-audit.
- [ ] Commit `feat: rebuild public site in Lamina Viva system`.

### Task 4: Waitlist, contact, Resend, and privacy-safe analytics

**Files:**
- Create: `api/waitlist.js`
- Create: `api/confirm-waitlist.js`
- Create: `api/contact.js`
- Create: `api/lib/http.js`
- Create: `api/lib/tokens.js`
- Create: `tests/api/*.test.js`

**Interfaces:**
- `POST /api/waitlist`: JSON `{email, topic, consent, company?, startedAt}`; success response never echoes email.
- `GET /api/confirm-waitlist?token=...`: verifies an expiring HMAC token and creates the contact in the Resend audience mapped to the topic.
- `POST /api/contact`: JSON `{name, email, message, consent, company?, startedAt}`; sends to the configured CELEBIOS inbox without logging fields.
- Required env vars: `RESEND_API_KEY`, `RESEND_FROM`, `CONTACT_TO`, `WAITLIST_TOKEN_SECRET`, and topic-specific audience IDs. Missing configuration returns a generic `503`.

- [ ] Write failing Node tests for success, validation, honeypot, too-fast submission, duplicate/expired token, provider failure, IP throttling, safe responses, and absence of PII logging.
- [ ] Run focused tests and verify intended failures.
- [ ] Implement small dependency-injected handlers and connect forms with accessible inline states.
- [ ] Add GA4 events containing only fixed event names and topic slugs.
- [ ] Re-run API and site tests, audit privacy/security, fix, and re-audit.
- [ ] Commit `feat: add consented interest and contact flows`.

### Task 5: Migration generation and release gates

**Files:**
- Create: `scripts/audit_release.py`
- Create: `tests/test_release_audit.py`
- Modify: `build.py`
- Modify: `migracion/README.md`

**Interfaces:**
- `python scripts/audit_release.py --site site --redirects migracion/redirects.csv` exits nonzero for uncovered sources, chains, cycles, missing destinations, duplicate canonicals, forbidden claims, invalid structured data, or any available program other than the cat course.
- Cutover mode additionally requires imported GSC/Wix metrics and configured GA4/Resend environment identifiers; preview mode reports those external gaps without mutating services.

- [ ] Write failing tests for every release-gate failure mode.
- [ ] Implement the audit and wire generated bulk redirects, sitemap, robots, security headers, and real 404 behavior.
- [ ] Run preview audit, build, unit suites, and redirect simulation; fix and re-audit until no code-controlled P0/P1/P2 findings remain.
- [ ] Commit `feat: enforce migration release gates`.

### Task 6: Full visual, accessibility, performance, and branch review

**Files:**
- Create: `AUDITORIA-FINAL.md`
- Modify only files implicated by verified findings.

- [ ] Serve `site/` locally and capture desktop/mobile screenshots for each page template.
- [ ] Verify keyboard navigation, visible focus, reduced motion, semantic landmarks, WCAG 2.2 AA contrast, zero console errors, and form states.
- [ ] Measure representative pages against LCP ≤ 2.5 s, INP ≤ 200 ms, and CLS ≤ 0.1; record lab limitations rather than claiming field p75.
- [ ] Run `python build.py`, all Python/Node tests, `python scripts/audit_release.py`, and the complete redirect simulation.
- [ ] Dispatch a final Claude Opus whole-branch review; send all findings to one Sonnet fix wave, then one scoped Opus re-review.
- [ ] Record external blockers separately: GSC/Wix authenticated evidence, MVZ biological approval, production Resend/GA4 configuration, preview deployment, and DNS cutover.
- [ ] Commit `docs: record final migration audit`.

