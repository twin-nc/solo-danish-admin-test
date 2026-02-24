# AGENT_DESIGN_SPEC.md - Danish Tax Administration Platform

## Design Approach Note

This design spec is aligned to:
- `AGENT_REVIEWER_SPEC.md` (2026-02-24 quality gate)
- `AGENT_REVIEW_DESIGNER.md` (designer blockers/actions)
- `AGENT_RESEARCHER_SPEC.md` SKAT VAT UX benchmark
- `AGENT_ARCHITECT_SPEC.md` API/state contract (latest in this branch)

Fixed product decisions are applied as hard constraints:
- Legal accuracy first
- UI language mostly English
- Admin pages in scope now
- Filing model `4C`: fixed official VAT fields are primary in Phase 2
- Strict access control now
- Deadline and penalty handling now
- Correctness over speed

---

## 1. Design Principles

### 1.1 Core Principles

**Authoritative and trustworthy**
Visuals remain restrained and government-like. Decisions prioritize legal clarity over decorative styling.

**Clarity over cleverness**
All labels, statuses, and actions are explicit and testable.

**Accessibility by default (WCAG 2.1 AA)**
Keyboard-first navigation, sufficient contrast, and text labels with every status color.

**Desktop-first, responsive down to tablet**
Primary users are officers/admins on desktop; tablet support is required; mobile degrades gracefully.

**Legal and workflow traceability**
Each user action maps to one API entry and one state rule.

---

## 2. Design Tokens

### 2.1 Colour Palette

#### Primary - SKAT Navy Blue

```css
--color-primary-900: #002B52;
--color-primary-800: #003D6E;
--color-primary-700: #004B87;
--color-primary-600: #0059A0;
--color-primary-500: #1A6FB5;
--color-primary-400: #4A90C8;
--color-primary-300: #7BB3D8;
--color-primary-200: #B3D4EC;
--color-primary-100: #D9EAF5;
--color-primary-50:  #EEF6FB;
```

#### Secondary - Warm Grey

```css
--color-secondary-900: #1A1A1A;
--color-secondary-800: #2E2E2E;
--color-secondary-700: #4A4A4A;
--color-secondary-600: #6B6B6B;
--color-secondary-500: #8C8C8C;
--color-secondary-400: #ADADAD;
--color-secondary-300: #C8C8C8;
--color-secondary-200: #E0E0E0;
--color-secondary-100: #F0F0F0;
--color-secondary-50:  #F8F8F8;
```

#### Neutrals

```css
--color-white:    #FFFFFF;
--color-page-bg:  #F4F5F7;
--color-border:   #DDE1E7;
```

#### Status Colours

```css
--color-success-700: #1B6B32;  --color-success-500: #2EA052;
--color-warning-700: #7A4B00;  --color-warning-500: #C27A00;
--color-error-700:   #8B1A1A;  --color-error-500:   #D03030;
--color-info-700:    #005F6E;  --color-info-500:    #0096AA;
```

### 2.2 Typography

```css
--font-family-base: 'Source Sans Pro', 'Helvetica Neue', Arial, sans-serif;
--font-family-mono: 'Source Code Pro', 'Courier New', Courier, monospace;
```

### 2.3 Spacing Scale

```css
--space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
--space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px;
```

---

## 3. Component Library

### 3.1 Button

Variants: `primary`, `secondary`, `ghost`, `danger`  
States: default, hover, focus, disabled, loading

### 3.2 Badge / StatusChip

Canonical backend values with English primary labels and Danish legal aliases:
- `DRAFT` -> Draft (`Kladde`)
- `SUBMITTED` -> Submitted (`Indberettet`)
- `UNDER_REVIEW` -> Under Review (`Under behandling`)
- `ACCEPTED` -> Accepted (`Godkendt`)
- `REJECTED` -> Rejected (`Afvist`)
- `PENDING` -> Pending (`Afventende`)
- `COMPLETE` -> Complete (`Afsluttet`)
- `APPEALED` -> Appealed (`Anket`)
- `IN_BUSINESS` -> Active (`Aktiv`)

### 3.3 DataTable

Dense rows, clear sort states, and empty/loading states. No row action is rendered without API mapping.

### 3.4 FormField

Label + control + helper/error text. Required marker and error icon are mandatory for legal fields.

### 3.5 Card

`default` and `elevated` variants remain unchanged.

### 3.6 PageHeader

Breadcrumb + title + optional status chip + action slot.

### 3.7 SideNav

Role-aware nav rendering. Hidden links are permission-based, not merely disabled.

### 3.8 StatCard

Cards are rendered only when backing data exists.

### 3.9 Modal / Dialog

Used for role assignment and destructive confirmations.

### 3.10 Toast / Notification

Shows API success/error and deterministic failure reasons.

---

## 4. Contract Baseline and 4C Filing Decision

### 4.1 Baseline Contract Sources

- Auth/user contract: Architect Section 2.5 and API summary rows 2-5
- Party/role contract: API summary rows 6-9 plus existing `app/schemas/party.py` and `app/schemas/party_role.py`
- Filing contract and state rule: Architect Section 3.3, 3.5, API rows 10-13
- Assessment contract and state rule: Architect Section 4.3, 4.5, API rows 14-17

### 4.2 Canonical Filing UX Rule (Product Decision 4C)

Phase 2 filing UI is Rubrik-first with fixed official VAT fields:
- Rubrik A, B, C, D, E
- Taxable turnover, VAT-exempt turnover, export
- Computed `momstilsvar`

Line-item free entry is not offered as primary UX.  
Current architect payload (`FilingCreate.line_items`) is handled through a deterministic adapter so fixed fields remain primary in UX.

### 4.3 Adapter Rule Until Architect 4C Schema Is Published

UI model `VatFilingForm` is canonical in frontend. API transport maps as:
- `rubrik_a..rubrik_e` and summary fields -> fixed `line_items[]` descriptions + amounts
- `momstilsvar` -> `FilingCreate.total_amount`
- `filing_type` forced to `VAT`

This keeps UX legally aligned now and avoids free-form line-item entry.

---

## 5. Page Layouts and Wireframes

### 5a. Login Page

Scope: `In Scope Phase 2`  
Endpoints: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`

Primary components:
- Email + password form
- Login submit
- Session-expired banner tied to refresh failure

### 5b. Dashboard

Scope: `In Scope Phase 2` (limited)  
Endpoints: `GET /api/v1/auth/me`, `GET /health`

Primary components:
- Session card (name/role/active)
- System health card
- Quick links to parties, filings, assessments

Deferred widgets:
- Global aggregate counts (no listing endpoint parity in current architect contract)

### 5c. Parties List

Scope: `Deferred`  
Reason: no list endpoint in current architect contract (`GET /api/v1/parties` missing)

### 5d. Party Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/parties/{id}`, `GET /api/v1/parties/{id}/roles`, `POST /api/v1/parties/{id}/roles`

Primary components:
- Party summary card
- Identifier/classification/state/contact/name cards
- Role table and assign-role modal

### 5e. Register Party

Scope: `In Scope Phase 2`  
Endpoint: `POST /api/v1/parties`

Primary components:
- Party type
- Identifier block (display label "CVR/SE Identifier", backend field still `identifierTypeCL`)
- Classification/state/contact/name blocks
- Sticky submit footer

### 5f. Filings List

Scope: `In Scope Phase 2`  
Endpoint: `GET /api/v1/parties/{id}/filings`

Primary components:
- Party-scoped filing table
- Status filter
- "Open filing" row action

### 5g. Filing Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/filings/{id}`, `PATCH /api/v1/filings/{id}/submit`, `GET /api/v1/filings/{id}/assessment`

Primary components:
- Filing metadata card
- Fixed VAT field review card (Rubrik groups rendered from deterministic mapping, not free text)
- State timeline card
- Assessment linkout card

### 5h. Create Filing (Rubrik-first)

Scope: `In Scope Phase 2`  
Endpoint: `POST /api/v1/filings` then `PATCH /api/v1/filings/{id}/submit`

Primary components:
- Step 1: Party and filing period
- Step 2: Fixed VAT fields (Rubrik A-E)
- Step 3: Turnover fields + computed `momstilsvar`
- Step 4: Declaration + submit

Validation:
- Required fields enforce numeric >= 0
- `momstilsvar = A + C + E - B`
- API errors displayed verbatim for legal audit trace

### 5i. Assessments List

Scope: `Deferred`  
Reason: no list endpoint in current architect contract (`GET /api/v1/assessments` missing)

### 5j. Assessment Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/assessments/{id}`, `PATCH /api/v1/assessments/{id}/status`

Primary components:
- Assessment metadata
- Tax due and penalties card
- Notes/begrundelse card
- Status transition controls (officer/admin only)

### 5k. Admin Users

Scope: `In Scope Phase 2` (endpoint-backed subset only)  
Endpoints: `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`

In-scope components:
- Current admin session card
- Role policy reference card
- Sign-out action

Deferred components:
- User search/create/update/deactivate (no `/admin/users` API contract yet)

### 5l. Admin Settings

Scope: `In Scope Phase 2` (endpoint-backed subset only)  
Endpoints: `GET /health`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`

In-scope components:
- Health status panel
- Session token status panel
- Refresh session action

Deferred components:
- Writable platform settings (no `/admin/settings` API contract yet)

---

## 6. Navigation Structure

### 6.1 Sidebar Items

| Label | Path | ADMIN | OFFICER | TAXPAYER | Scope |
|---|---|---|---|---|---|
| Dashboard | `/dashboard` | Yes | Yes | Yes | In Scope Phase 2 |
| Parties | `/parties` | Yes | Yes | No | Deferred (list endpoint missing) |
| Register Party | `/parties/new` | Yes | Yes | No | In Scope Phase 2 |
| Party Detail | `/parties/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Filings | `/filings` | Yes | Yes | Yes | In Scope Phase 2 |
| New Filing | `/filings/new` | Yes | Yes | Yes | In Scope Phase 2 |
| Filing Detail | `/filings/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Assessments | `/assessments` | Yes | Yes | No | Deferred (list endpoint missing) |
| Assessment Detail | `/assessments/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Admin Users | `/admin/users` | Yes | No | No | In Scope Phase 2 (subset) |
| Admin Settings | `/admin/settings` | Yes | No | No | In Scope Phase 2 (subset) |

### 6.2 Breadcrumb Patterns

English primary labels:
- Dashboard
- Parties / Party
- Filings / Filing
- Assessments / Assessment
- Admin / Users
- Admin / Settings

---

## 7. User Flows

### 7.1 Officer registers a party

1. `/login` -> submit credentials (`POST /api/v1/auth/login`)
2. `/parties/new` -> fill party payload
3. Submit (`POST /api/v1/parties`) -> redirect `/parties/{id}`
4. Assign role from detail (`POST /api/v1/parties/{id}/roles`)

### 7.2 Taxpayer submits a VAT filing (Rubrik-first)

1. Open `/filings/new`
2. Enter party + period
3. Enter Rubrik A-E and turnover fields
4. Review computed `momstilsvar`
5. Save draft (`POST /api/v1/filings`, status starts `DRAFT`)
6. Submit (`PATCH /api/v1/filings/{id}/submit`)  
State rule reference: Architect FilingService allows submit only from `DRAFT`.

### 7.3 Officer creates and progresses assessment

1. Open filing detail (`GET /api/v1/filings/{id}`)
2. Create assessment (`POST /api/v1/assessments`)
3. Update assessment status (`PATCH /api/v1/assessments/{id}/status`)

State rule reference:
- Allowed assessment transitions: `PENDING -> COMPLETE|APPEALED`, `COMPLETE -> APPEALED`
- No implicit filing status transition is assumed on assessment create/update.

### 7.4 Admin monitoring flows

1. `/admin/users` -> read session and policy (`GET /api/v1/auth/me`)
2. `/admin/settings` -> read health (`GET /health`)
3. Refresh/logout session (`POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`)

---

## 8. Action to API Parity Matrix

| Screen Action | Endpoint | Request Schema | Response Schema | Roles | Scope |
|---|---|---|---|---|---|
| Login submit | `POST /api/v1/auth/login` | `LoginRequest` | `{"message":"ok"}` + cookies | Public | In Scope Phase 2 |
| Session refresh | `POST /api/v1/auth/refresh` | none | `{"message":"ok"}` + cookies | Cookie auth | In Scope Phase 2 |
| Logout | `POST /api/v1/auth/logout` | none | `{"message":"ok"}` | Any authenticated | In Scope Phase 2 |
| Register party | `POST /api/v1/parties` | `PartyCreate` | `PartyRead` | A,O,T | In Scope Phase 2 |
| Open party detail | `GET /api/v1/parties/{id}` | none | `PartyRead` | Any (ownership enforced) | In Scope Phase 2 |
| Assign role | `POST /api/v1/parties/{id}/roles` | `PartyRoleCreate` | `PartyRoleRead` | A,O,T | In Scope Phase 2 |
| List roles | `GET /api/v1/parties/{id}/roles` | none | `list[PartyRoleRead]` | Any (ownership enforced) | In Scope Phase 2 |
| List filings by party | `GET /api/v1/parties/{id}/filings` | none | `list[FilingRead]` | Any (ownership enforced) | In Scope Phase 2 |
| Create filing draft | `POST /api/v1/filings` | `FilingCreate` | `FilingRead` | A,O,T | In Scope Phase 2 |
| Open filing | `GET /api/v1/filings/{id}` | none | `FilingRead` | Any (ownership enforced) | In Scope Phase 2 |
| Submit filing | `PATCH /api/v1/filings/{id}/submit` | none | `FilingRead` | A,O,T | In Scope Phase 2 |
| Create assessment | `POST /api/v1/assessments` | `AssessmentCreate` | `AssessmentRead` | A,O | In Scope Phase 2 |
| Open assessment | `GET /api/v1/assessments/{id}` | none | `AssessmentRead` | Any (ownership enforced) | In Scope Phase 2 |
| Open assessment by filing | `GET /api/v1/filings/{id}/assessment` | none | `AssessmentRead` | Any (ownership enforced) | In Scope Phase 2 |
| Update assessment status | `PATCH /api/v1/assessments/{id}/status` | `AssessmentStatusUpdate` | `AssessmentRead` | A,O | In Scope Phase 2 |
| Dashboard health check | `GET /health` | none | `{"status":"ok"}` | Public | In Scope Phase 2 |

Deferred actions (not rendered as active controls):
- Parties list query (missing `GET /api/v1/parties`)
- Assessments list query (missing `GET /api/v1/assessments`)
- Admin user CRUD (missing `/admin/users` API contract)
- Admin writable settings (missing `/admin/settings` API contract)

---

## 9. Data Contract Alignment Table

| Page Component Field | Display Label | Endpoint/Schema | Architect Field | Scope | Notes |
|---|---|---|---|---|---|
| Login.email | Email | `POST /api/v1/auth/login` `LoginRequest` | `email` | In Scope Phase 2 | Direct |
| Login.password | Password | `POST /api/v1/auth/login` `LoginRequest` | `password` | In Scope Phase 2 | Direct |
| Session.name | Full Name | `GET /api/v1/auth/me` `UserRead` | `full_name` | In Scope Phase 2 | Direct |
| Session.role | Role | `GET /api/v1/auth/me` `UserRead` | `role` | In Scope Phase 2 | Direct |
| Session.active | Active | `GET /api/v1/auth/me` `UserRead` | `is_active` | In Scope Phase 2 | Direct |
| PartyForm.partyType | Party Type | `POST /api/v1/parties` `PartyCreate` | `partyTypeCode` | In Scope Phase 2 | Backend default `ORGADM1` |
| PartyForm.identifierType | Identifier Type | `POST /api/v1/parties` | `identifiers[].identifierTypeCL` | In Scope Phase 2 | UI label "CVR/SE Identifier Type" |
| PartyForm.identifierValue | Identifier Value | `POST /api/v1/parties` | `identifiers[].identifierValue` | In Scope Phase 2 | UI label "CVR/SE Identifier" |
| PartyForm.businessSize | Business Size | `POST /api/v1/parties` | `classifications[].classificationValue` | In Scope Phase 2 | Type `BUSINESS_SIZE` |
| PartyForm.state | Party State | `POST /api/v1/parties` | `states[].partyStateCL` | In Scope Phase 2 | `IN_BUSINESS` etc |
| PartyForm.contactEmail | Contact Email | `POST /api/v1/parties` | `contacts[].contactValue` | In Scope Phase 2 | Direct |
| PartyForm.legalName | Legal Name | `POST /api/v1/parties` | `names[].name` + `isAlias=false` | In Scope Phase 2 | Direct |
| RoleForm.roleType | Role Type | `POST /api/v1/parties/{id}/roles` | `party_role_type_code` | In Scope Phase 2 | UI shows mapped label |
| RoleForm.roleState | Role State | `POST /api/v1/parties/{id}/roles` | `states[].partyRoleStateCL` | In Scope Phase 2 | Direct |
| RoleForm.primaryIdentifier | Primary Identifier | `POST /api/v1/parties/{id}/roles` | `eligible_identifiers[].party_identifier_id` + `primary` | In Scope Phase 2 | Direct |
| RoleForm.primaryContact | Primary Contact | `POST /api/v1/parties/{id}/roles` | `eligible_contacts[].party_contact_id` + `primary` | In Scope Phase 2 | Direct |
| FilingForm.partyId | Party | `POST /api/v1/filings` `FilingCreate` | `party_id` | In Scope Phase 2 | Direct |
| FilingForm.period | Filing Period | `POST /api/v1/filings` | `filing_period` | In Scope Phase 2 | Direct |
| FilingForm.type | Filing Type | `POST /api/v1/filings` | `filing_type` | In Scope Phase 2 | Fixed to `VAT` in Phase 2 |
| FilingForm.rubrikA | Output VAT (Rubrik A) | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `RUBRIK_A` |
| FilingForm.rubrikB | Input VAT (Rubrik B) | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `RUBRIK_B` |
| FilingForm.rubrikC | EU Acquisition VAT (Rubrik C) | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `RUBRIK_C` |
| FilingForm.rubrikD | EU Sales (Rubrik D) | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `RUBRIK_D` |
| FilingForm.rubrikE | Import VAT (Rubrik E) | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `RUBRIK_E` |
| FilingForm.taxableTurnover | Taxable Turnover | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `MOMSPLIGTIG` |
| FilingForm.exemptTurnover | VAT-exempt Turnover | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `MOMSFRI` |
| FilingForm.exports | Export | `POST /api/v1/filings` | `line_items[].amount` | In Scope Phase 2 | Adapter row description `EKSPORT` |
| FilingForm.momstilsvar | Net VAT (computed) | `POST /api/v1/filings` | `total_amount` | In Scope Phase 2 | `A + C + E - B` |
| FilingDetail.statusChip | Filing Status | `GET /api/v1/filings/{id}` | `status` | In Scope Phase 2 | Direct |
| FilingDetail.submittedAt | Submitted At | `GET /api/v1/filings/{id}` | `submitted_at` | In Scope Phase 2 | Direct |
| FilingSubmit.action | Submit Filing | `PATCH /api/v1/filings/{id}/submit` | n/a (state mutation) | In Scope Phase 2 | Allowed from `DRAFT` only |
| AssessmentForm.filingId | Filing | `POST /api/v1/assessments` | `filing_id` | In Scope Phase 2 | Direct |
| AssessmentForm.date | Assessment Date | `POST /api/v1/assessments` | `assessment_date` | In Scope Phase 2 | String per architect |
| AssessmentForm.taxDue | Tax Due | `POST /api/v1/assessments` | `tax_due` | In Scope Phase 2 | Direct |
| AssessmentForm.penalties | Penalties | `POST /api/v1/assessments` | `penalties` | In Scope Phase 2 | Direct |
| AssessmentForm.notes | Reasoning/Notes | `POST /api/v1/assessments` | `notes` | In Scope Phase 2 | Direct |
| AssessmentStatus.action | Update Status | `PATCH /api/v1/assessments/{id}/status` | `status` | In Scope Phase 2 | Constrained transitions |
| AdminUsers.health | Health | `GET /health` | `status` | In Scope Phase 2 | Endpoint-backed |
| AdminUsers.currentUser | Current Admin | `GET /api/v1/auth/me` | `id`,`email`,`role`,`is_active` | In Scope Phase 2 | Endpoint-backed |
| AdminUsers.manageUser | User CRUD | n/a | n/a | Deferred | No architect endpoint |
| AdminSettings.save | Save Settings | n/a | n/a | Deferred | No architect endpoint |

---

## 10. Screen and Action Scope Classification

| Screen/Action | Scope | Rationale |
|---|---|---|
| Login | In Scope Phase 2 | Full API contract exists |
| Dashboard (session + health) | In Scope Phase 2 | Endpoint-backed via `/auth/me` and `/health` |
| Dashboard aggregate stats | Deferred | No list endpoints for global counts |
| Parties list page | Deferred | No `GET /api/v1/parties` endpoint |
| Register party | In Scope Phase 2 | `POST /api/v1/parties` exists |
| Party detail | In Scope Phase 2 | `GET /api/v1/parties/{id}` exists |
| Assign role modal | In Scope Phase 2 | `POST /api/v1/parties/{id}/roles` exists |
| Filings list (party-scoped) | In Scope Phase 2 | `GET /api/v1/parties/{id}/filings` exists |
| Filing detail | In Scope Phase 2 | `GET /api/v1/filings/{id}` exists |
| Create filing (Rubrik-first) | In Scope Phase 2 | `POST /api/v1/filings` exists, adapter used |
| Filing submit | In Scope Phase 2 | `PATCH /api/v1/filings/{id}/submit` exists |
| Assessments list page | Deferred | No `GET /api/v1/assessments` endpoint |
| Assessment detail | In Scope Phase 2 | `GET /api/v1/assessments/{id}` exists |
| Create assessment | In Scope Phase 2 | `POST /api/v1/assessments` exists |
| Assessment status updates | In Scope Phase 2 | `PATCH /api/v1/assessments/{id}/status` exists |
| Admin users (session/policy only) | In Scope Phase 2 | Endpoint-backed subset only |
| Admin settings (health/session only) | In Scope Phase 2 | Endpoint-backed subset only |
| Admin user management | Deferred | Missing API contract |
| Admin writable settings | Deferred | Missing API contract |

---

## 11. Access Control and State Rule References

### 11.1 Strict Access Control

Frontend enforces role-based navigation plus ownership gating:
- TAXPAYER can only access own party/filing/assessment links.
- OFFICER and ADMIN can access officer flows.
- ADMIN-only routes are `/admin/users` and `/admin/settings`.

Backend remains the source of truth. On unauthorized access:
- `403` -> permission denied screen
- `404` -> resource hidden/not found

### 11.2 Filing State Rules (Architect Section 3.5)

- Filing created as `DRAFT`
- Submit allowed only when current status is `DRAFT`
- No UI assumption of post-assessment filing status mutation

### 11.3 Assessment State Rules (Architect Section 4.5)

- Allowed transitions:
  - `PENDING -> COMPLETE`
  - `PENDING -> APPEALED`
  - `COMPLETE -> APPEALED`
- Duplicate assessment for same filing returns `409`

### 11.4 Deadlines and Penalties

- Penalties are in-scope and rendered from `Assessment.penalties`.
- Deadline enforcement is required by product direction; UI handles deadline/late-file errors returned from filing endpoints as authoritative backend outcomes.
- No client-side legal deadline calculation is used as source of truth.

---

## 12. Terminology Map (Domain Value -> Display Label)

### 12.1 Status and Workflow Terms

| Domain Value | Display Label (English first) |
|---|---|
| `DRAFT` | Draft (`Kladde`) |
| `SUBMITTED` | Submitted (`Indberettet`) |
| `UNDER_REVIEW` | Under Review (`Under behandling`) |
| `ACCEPTED` | Accepted (`Godkendt`) |
| `REJECTED` | Rejected (`Afvist`) |
| `PENDING` | Pending (`Afventende`) |
| `COMPLETE` | Complete (`Afsluttet`) |
| `APPEALED` | Appealed (`Anket`) |

### 12.2 Filing Terms

| Domain Value | Display Label |
|---|---|
| `filing_type = VAT` | VAT Return (`Momsangivelse`) |
| `line_items` (transport) | Fixed VAT Fields (Rubrik A-E and summaries) |
| `total_amount` | Net VAT (`Momstilsvar`) |

### 12.3 Party and Role Terms

| Domain Value | Display Label |
|---|---|
| `identifierTypeCL = TIN` | CVR/SE Identifier (backend code `TIN`) |
| `partyStateCL = IN_BUSINESS` | Active (`Aktiv`) |
| `party_role_type_code = BUSINSSDM1` | VAT Registered Business Role |
| `partyTypeCode = ORGADM1` | Business Organization |

---

## 13. SKAT VAT UX Benchmark Alignment and Deviations

### 13.1 Alignment to SKAT Workflow

The filing UX mirrors the benchmark sequence:
1. Open new VAT filing
2. Select party/period
3. Enter Rubrik A-E
4. Review computed `momstilsvar`
5. Submit and show receipt state

Required-field markers, grouped field cards, and confirmation review follow the same workflow shape.

### 13.2 Explicit Deviations From SKAT Workflow

| Deviation | Why | Scope |
|---|---|---|
| English-first labels with Danish aliases | Product policy is mostly English UI while preserving legal terminology traceability | In Scope Phase 2 |
| Internal auth flow (email/password) instead of MitID Erhverv | Current architect contract defines internal auth only | In Scope Phase 2 |
| No PDF receipt download action | No receipt/PDF endpoint in architect contract | Deferred |
| No dedicated correction filing action | `POST /filings/{id}/correct` not in architect contract | Deferred |
| No Listesystem integration action when Rubrik D > 0 | Endpoint/event not in architect contract | Deferred |
| Admin pages limited to endpoint-backed subset | Admin CRUD/settings APIs are missing | In Scope Phase 2 subset + deferred full feature set |

---

## 14. Responsive Behaviour

| Breakpoint | Sidebar | Tables | Stat Cards | Forms |
|---|---|---|---|---|
| Desktop >1024px | 256px expanded | Full columns | 3-4 cards | 2-column where appropriate |
| Tablet 768-1024px | Collapsible icon sidebar | Horizontal scroll | 2 cards | 1-column forms |
| Mobile <768px | Overlay nav | Card list fallback | 1 card | 1-column forms |

---

## 15. Frontend File Structure

```text
frontend/
  app/
    (auth)/login/page.tsx
    (app)/dashboard/page.tsx
    (app)/parties/new/page.tsx
    (app)/parties/[id]/page.tsx
    (app)/filings/page.tsx
    (app)/filings/new/page.tsx
    (app)/filings/[id]/page.tsx
    (app)/assessments/[id]/page.tsx
    (app)/admin/users/page.tsx
    (app)/admin/settings/page.tsx
  components/
    filings/
      CreateFilingRubrikForm.tsx
      FilingRubrikSummaryCard.tsx
      FilingStatusTimeline.tsx
    assessments/
      CreateAssessmentForm.tsx
      AssessmentStatusTimeline.tsx
    parties/
      RegisterPartyForm.tsx
      AssignRoleModal.tsx
    admin/
      AdminSessionCard.tsx
      AdminHealthCard.tsx
  lib/api/
    auth.ts
    parties.ts
    filings.ts
    assessments.ts
  lib/mappers/
    filingRubrikAdapter.ts
```

Notes:
- `filingRubrikAdapter.ts` is mandatory to keep fixed-field UX while current architect payload uses `line_items`.
- Deferred features remain physically separated behind feature flags until endpoints are added.
