# AGENT_DESIGN_SPEC.md - Danish Tax Administration Platform

## Design Approach Note

This design spec is aligned to:
- `AGENT_REVIEWER_SPEC.md` (2026-02-24 quality gate)
- `AGENT_REVIEW_DESIGNER.md` (designer blockers/actions)
- Latest `AGENT_RESEARCHER_SPEC.md` SKAT VAT benchmark and legal baseline
- Latest `AGENT_ARCHITECT_SPEC.md` API/state contract

Fixed product decisions are hard constraints:
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
- `SUBMITTED_WITH_RECEIPT` -> Submitted with Receipt (`Indberettet med kvittering`)
- `UNDER_REVIEW` -> Under Review (`Under behandling`)
- `ACCEPTED` -> Accepted (`Godkendt`)
- `REJECTED` -> Rejected (`Afvist`)
- `CORRECTED` -> Corrected (`Korrigeret`)
- `PENDING` -> Pending (`Afventende`)
- `COMPLETE` -> Complete (`Afsluttet`)
- `APPEALED` -> Appealed (`Anket`)

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

## 4. Contract Baseline and 4C Filing Enforcement

### 4.1 Baseline Contract Sources

- Architect Section 2.8: authorization and row-level ownership policy
- Architect Section 3.1.1: filing and assessment SSOT transition table
- Architect Section 3.2-3.7: canonical filing model, schema, service, router
- Architect Section 4.2-4.7: assessment model, schema, service, router
- Architect Section 8.1-8.3: endpoint policy, penalty/deadline contract, API parity matrix
- Researcher Section 2 and 3: SKAT benchmark workflow and legal baseline

### 4.2 Canonical Filing UX Rule (4C)

Phase 2 filing UI is fixed-field and Rubrik-first:
- `rubrik_a`, `rubrik_b`, `rubrik_c`, `rubrik_d`, `rubrik_e`
- `momspligtig_omsaetning`, `momsfri_omsaetning`, `eksport`
- Computed and server-trusted `momstilsvar`
- `angivelse_type` fixed to `MOMS` in Phase 2

### 4.3 Non-Canonical Detail Rule

`supplemental_line_items` is optional and non-canonical:
- Allowed as convenience import detail only
- Never replaces fixed VAT field entry
- Manual line-item-first filing interaction is deferred

---

## 5. Page Layouts and Wireframes

### 5a. Login Page

Scope: `In Scope Phase 2`  
Endpoints: `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`

### 5b. Dashboard

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/dashboard/summary`, `GET /api/v1/filings`, `GET /api/v1/parties`

Components:
- Summary cards (server-provided metrics only)
- Recent filings table
- Recent parties table

### 5c. Parties List

Scope: `In Scope Phase 2`  
Endpoint: `GET /api/v1/parties`

### 5d. Party Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/parties/{id}`, `GET /api/v1/parties/{id}/roles`, `POST /api/v1/parties/{id}/roles`

### 5e. Register Party

Scope: `In Scope Phase 2`  
Endpoint: `POST /api/v1/parties`

### 5f. Filings List

Scope: `In Scope Phase 2`  
Endpoint: `GET /api/v1/filings`

### 5g. Filing Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/filings/{id}`, `PATCH /api/v1/filings/{id}/submit`, `GET /api/v1/filings/{id}/assessment`, `POST /api/v1/filings/{id}/correct`

Components:
- Filing metadata (`status`, `version`, period, `se_nummer`, `submitted_at`)
- Fixed VAT field review card
- Receipt panel (`kvitteringsnummer` when present)
- Deadline and late penalty panel (`frist`, `late_filing_days`, `late_filing_penalty`)
- Correction action (eligible statuses only)

### 5h. Create Filing (Rubrik-first)

Scope: `In Scope Phase 2`  
Endpoint: `POST /api/v1/filings`

Workflow pattern aligned to SKAT benchmark:
- Step 1: party + `se_nummer` + period type + period
- Step 2: fixed VAT fields (`rubrik_a` to `rubrik_e`)
- Step 3: turnover fields and computed preview
- Step 4: declaration and save as draft
- Step 5: submit from detail (`PATCH /filings/{id}/submit`)

Validation and help behavior:
- Required marker on mandatory fields
- Inline helper tooltip per field
- Zero filing is valid
- Final submission blocked if API validation fails

### 5i. Assessments List

Scope: `In Scope Phase 2`  
Endpoint: `GET /api/v1/assessments`

### 5j. Assessment Detail

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/assessments/{id}`, `PATCH /api/v1/assessments/{id}/status`, `POST /api/v1/assessments/{id}/appeal`

Components:
- Assessment core fields (`decision_outcome`, `tax_due`, `surcharge_amount`, `interest_amount`)
- Deadline fields (`payment_deadline`, `appeal_deadline`)
- Appeal action for taxpayer-owned filings only

### 5k. Admin Users

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/admin/users`, `POST /api/v1/admin/users`, `PATCH /api/v1/admin/users/{id}`

### 5l. Admin Settings

Scope: `In Scope Phase 2`  
Endpoints: `GET /api/v1/admin/settings`, `PATCH /api/v1/admin/settings/{key}`

---

## 6. Navigation Structure

### 6.1 Sidebar Items

| Label | Path | ADMIN | OFFICER | TAXPAYER | Scope |
|---|---|---|---|---|---|
| Dashboard | `/dashboard` | Yes | Yes | No | In Scope Phase 2 |
| Parties | `/parties` | Yes | Yes | No | In Scope Phase 2 |
| Register Party | `/parties/new` | Yes | Yes | No | In Scope Phase 2 |
| Party Detail | `/parties/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Filings | `/filings` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| New Filing | `/filings/new` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Filing Detail | `/filings/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Assessments | `/assessments` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Assessment Detail | `/assessments/{id}` | Yes | Yes | Yes (own only) | In Scope Phase 2 |
| Admin Users | `/admin/users` | Yes | No | No | In Scope Phase 2 |
| Admin Settings | `/admin/settings` | Yes | No | No | In Scope Phase 2 |

### 6.2 Breadcrumb Labels

English-first labels:
- Dashboard
- Parties / Party
- Filings / Filing
- Assessments / Assessment
- Admin / Users
- Admin / Settings

---

## 7. User Flows

### 7.1 Officer registers a business party

1. Login (`POST /api/v1/auth/login`)
2. Open `/parties/new`
3. Submit `POST /api/v1/parties`
4. Open detail and assign role (`POST /api/v1/parties/{id}/roles`)

### 7.2 Taxpayer creates and submits VAT filing

1. Open `/filings/new`
2. Enter fixed VAT fields and required period/SE data
3. Save draft (`POST /api/v1/filings`) -> status `DRAFT`
4. Submit (`PATCH /api/v1/filings/{id}/submit`) -> status `SUBMITTED_WITH_RECEIPT`
5. View receipt data (`kvitteringsnummer`) and deadline/late indicators on detail

### 7.3 Officer creates and resolves assessment (SSOT-aligned)

1. Open filing detail (`GET /api/v1/filings/{id}`)
2. Create assessment (`POST /api/v1/assessments`) -> assessment status `PENDING`
3. Update assessment status (`PATCH /api/v1/assessments/{id}/status`) -> assessment status per assessment state rules only

### 7.4 Taxpayer appeals completed assessment

1. Open assessment detail (`GET /api/v1/assessments/{id}`)
2. Submit appeal (`POST /api/v1/assessments/{id}/appeal`) before `appeal_deadline`
3. Resulting state: assessment `COMPLETE -> APPEALED` (no implicit filing state change)

### 7.5 Admin user and setting management

1. Admin opens `/admin/users` and fetches users (`GET /api/v1/admin/users`)
2. Admin creates user (`POST /api/v1/admin/users`) or updates (`PATCH /api/v1/admin/users/{id}`)
3. Admin opens `/admin/settings` and fetches settings (`GET /api/v1/admin/settings`)
4. Admin updates a setting (`PATCH /api/v1/admin/settings/{key}`)

---

## 8. Action to API Parity Matrix

| Screen Action | Endpoint | Request | Response | Roles | Scope |
|---|---|---|---|---|---|
| Login submit | `POST /api/v1/auth/login` | `LoginRequest` | message + cookies | Public | In Scope Phase 2 |
| Refresh session | `POST /api/v1/auth/refresh` | none | message + cookies | Cookie | In Scope Phase 2 |
| Logout | `POST /api/v1/auth/logout` | none | message | A,O,T | In Scope Phase 2 |
| Load dashboard summary | `GET /api/v1/dashboard/summary` | none | summary payload | A,O | In Scope Phase 2 |
| Load recent parties | `GET /api/v1/parties` | none | `list[PartyRead]` | A,O | In Scope Phase 2 |
| Load recent filings | `GET /api/v1/filings` | none | `list[FilingRead]` | A,O,T-own | In Scope Phase 2 |
| Register party | `POST /api/v1/parties` | `PartyCreate` | `PartyRead` | A,O | In Scope Phase 2 |
| Open party detail | `GET /api/v1/parties/{id}` | none | `PartyRead` | A,O,T-own | In Scope Phase 2 |
| List party roles | `GET /api/v1/parties/{id}/roles` | none | `list[PartyRoleRead]` | A,O,T-own | In Scope Phase 2 |
| Assign party role | `POST /api/v1/parties/{id}/roles` | `PartyRoleCreate` | `PartyRoleRead` | A,O | In Scope Phase 2 |
| List filings | `GET /api/v1/filings` | none | `list[FilingRead]` | A,O,T-own | In Scope Phase 2 |
| List filings by party | `GET /api/v1/parties/{id}/filings` | none | `list[FilingRead]` | A,O,T-own | In Scope Phase 2 |
| Create filing draft | `POST /api/v1/filings` | `FilingCreate` | `FilingRead` | A,O,T-own | In Scope Phase 2 |
| Open filing detail | `GET /api/v1/filings/{id}` | none | `FilingRead` | A,O,T-own | In Scope Phase 2 |
| Submit filing | `PATCH /api/v1/filings/{id}/submit` | none | `FilingRead` | A,O,T-own | In Scope Phase 2 |
| Correct filing | `POST /api/v1/filings/{id}/correct` | `FilingCreate` | `FilingRead` | A,O,T-own | In Scope Phase 2 |
| List assessments | `GET /api/v1/assessments` | none | `list[AssessmentRead]` | A,O,T-own | In Scope Phase 2 |
| Create assessment | `POST /api/v1/assessments` | `AssessmentCreate` | `AssessmentRead` | A,O | In Scope Phase 2 |
| Open assessment | `GET /api/v1/assessments/{id}` | none | `AssessmentRead` | A,O,T-own | In Scope Phase 2 |
| Open assessment from filing | `GET /api/v1/filings/{id}/assessment` | none | `AssessmentRead` | A,O,T-own | In Scope Phase 2 |
| Update assessment status | `PATCH /api/v1/assessments/{id}/status` | `AssessmentStatusUpdate` | `AssessmentRead` | A,O | In Scope Phase 2 |
| Appeal assessment | `POST /api/v1/assessments/{id}/appeal` | `AssessmentAppealCreate` | `AssessmentRead` | T-own | In Scope Phase 2 |
| Load admin users | `GET /api/v1/admin/users` | none | `list[AdminUserRead]` | A | In Scope Phase 2 |
| Create admin user | `POST /api/v1/admin/users` | admin user create payload | `AdminUserRead` | A | In Scope Phase 2 |
| Update admin user | `PATCH /api/v1/admin/users/{id}` | admin user patch payload | `AdminUserRead` | A | In Scope Phase 2 |
| Load admin settings | `GET /api/v1/admin/settings` | none | `list[AdminSettingRead]` | A | In Scope Phase 2 |
| Update admin setting | `PATCH /api/v1/admin/settings/{key}` | admin setting patch payload | `AdminSettingRead` | A | In Scope Phase 2 |

Deferred actions:
- Dedicated receipt retrieval endpoint action (`GET /api/v1/filings/{id}/receipt`) is not in architect contract
- Dedicated deadline calculator endpoint action (`GET /api/v1/vat-deadlines`) is not in architect contract
- Manual line-item-first filing editor (non-canonical by decision)

---

## 9. Data Contract Alignment Table

| Page Component Field | Display Label | Endpoint/Schema | Architect Field | Scope | Notes |
|---|---|---|---|---|---|
| Login.email | Email | `POST /api/v1/auth/login` | `email` | In Scope Phase 2 | direct |
| Login.password | Password | `POST /api/v1/auth/login` | `password` | In Scope Phase 2 | direct |
| Dashboard.summaryKey | Metric Label | `GET /api/v1/dashboard/summary` | response key | In Scope Phase 2 | server-driven key/value |
| Dashboard.summaryValue | Metric Value | `GET /api/v1/dashboard/summary` | response value | In Scope Phase 2 | server-driven key/value |
| PartyForm.partyType | Party Type | `POST /api/v1/parties` | `partyTypeCode` | In Scope Phase 2 | direct |
| PartyForm.identifierType | Identifier Type | `POST /api/v1/parties` | `identifiers[].identifierTypeCL` | In Scope Phase 2 | CVR/SE label in UI |
| PartyForm.identifierValue | Identifier Value | `POST /api/v1/parties` | `identifiers[].identifierValue` | In Scope Phase 2 | direct |
| PartyForm.state | Party State | `POST /api/v1/parties` | `states[].partyStateCL` | In Scope Phase 2 | direct |
| RoleForm.roleType | Role Type | `POST /api/v1/parties/{id}/roles` | `party_role_type_code` | In Scope Phase 2 | direct |
| FilingForm.partyId | Party | `POST /api/v1/filings` | `party_id` | In Scope Phase 2 | direct |
| FilingForm.seNummer | SE Number | `POST /api/v1/filings` | `se_nummer` | In Scope Phase 2 | fixed-length 8 |
| FilingForm.periodType | Period Type | `POST /api/v1/filings` | `afregningsperiode_type` | In Scope Phase 2 | MONTHLY/QUARTERLY/SEMI_ANNUAL |
| FilingForm.period | Filing Period | `POST /api/v1/filings` | `filing_period` | In Scope Phase 2 | format by type |
| FilingForm.angivelseType | Return Type | `POST /api/v1/filings` | `angivelse_type` | In Scope Phase 2 | fixed `MOMS` |
| FilingForm.rubrikA | Output VAT | `POST /api/v1/filings` | `rubrik_a` | In Scope Phase 2 | canonical |
| FilingForm.rubrikB | Input VAT | `POST /api/v1/filings` | `rubrik_b` | In Scope Phase 2 | canonical |
| FilingForm.rubrikC | EU Purchase VAT | `POST /api/v1/filings` | `rubrik_c` | In Scope Phase 2 | canonical |
| FilingForm.rubrikD | EU Sales Value | `POST /api/v1/filings` | `rubrik_d` | In Scope Phase 2 | canonical |
| FilingForm.rubrikE | Import VAT | `POST /api/v1/filings` | `rubrik_e` | In Scope Phase 2 | canonical |
| FilingForm.taxableTurnover | Taxable Turnover | `POST /api/v1/filings` | `momspligtig_omsaetning` | In Scope Phase 2 | canonical |
| FilingForm.exemptTurnover | VAT-exempt Turnover | `POST /api/v1/filings` | `momsfri_omsaetning` | In Scope Phase 2 | canonical |
| FilingForm.export | Export | `POST /api/v1/filings` | `eksport` | In Scope Phase 2 | canonical |
| FilingForm.supplemental | Optional Detail | `POST /api/v1/filings` | `supplemental_line_items` | In Scope Phase 2 | non-canonical |
| FilingDetail.status | Filing Status | `GET /api/v1/filings/{id}` | `status` | In Scope Phase 2 | direct |
| FilingDetail.version | Version | `GET /api/v1/filings/{id}` | `version` | In Scope Phase 2 | correction chain |
| FilingDetail.momstilsvar | Net VAT | `GET /api/v1/filings/{id}` | `momstilsvar` | In Scope Phase 2 | server computed |
| FilingDetail.deadline | Filing Deadline | `GET /api/v1/filings/{id}` | `frist` | In Scope Phase 2 | deterministic service rule |
| FilingDetail.lateDays | Late Days | `GET /api/v1/filings/{id}` | `late_filing_days` | In Scope Phase 2 | direct |
| FilingDetail.latePenalty | Late Penalty | `GET /api/v1/filings/{id}` | `late_filing_penalty` | In Scope Phase 2 | direct |
| FilingDetail.receiptNo | Receipt Number | `GET /api/v1/filings/{id}` | `kvitteringsnummer` | In Scope Phase 2 | no separate receipt endpoint |
| FilingDetail.correctedFlag | Correction Flag | `GET /api/v1/filings/{id}` | `korrektionsangivelse` | In Scope Phase 2 | direct |
| FilingCorrection.originalId | Original Filing | `GET /api/v1/filings/{id}` | `original_filing_id` | In Scope Phase 2 | direct |
| AssessmentForm.filingId | Filing | `POST /api/v1/assessments` | `filing_id` | In Scope Phase 2 | direct |
| AssessmentForm.assessmentDate | Assessment Date | `POST /api/v1/assessments` | `assessment_date` | In Scope Phase 2 | typed date |
| AssessmentForm.outcome | Decision Outcome | `POST /api/v1/assessments` | `decision_outcome` | In Scope Phase 2 | ACCEPTED/ADJUSTED/REJECTED |
| AssessmentForm.taxDue | Tax Due | `POST /api/v1/assessments` | `tax_due` | In Scope Phase 2 | direct |
| AssessmentForm.surcharge | Surcharge | `POST /api/v1/assessments` | `surcharge_amount` | In Scope Phase 2 | separate from interest |
| AssessmentForm.interest | Interest | `POST /api/v1/assessments` | `interest_amount` | In Scope Phase 2 | separate from surcharge |
| AssessmentForm.paymentDeadline | Payment Deadline | `POST /api/v1/assessments` | `payment_deadline` | In Scope Phase 2 | must be >= assessment_date |
| AssessmentForm.appealDeadline | Appeal Deadline | `POST /api/v1/assessments` | `appeal_deadline` | In Scope Phase 2 | must be >= assessment_date |
| AssessmentForm.notes | Notes | `POST /api/v1/assessments` | `notes` | In Scope Phase 2 | direct |
| AssessmentStatus.newStatus | Status | `PATCH /api/v1/assessments/{id}/status` | `status` | In Scope Phase 2 | SSOT transition-constrained |
| AssessmentAppeal.reason | Appeal Reason | `POST /api/v1/assessments/{id}/appeal` | `reason` | In Scope Phase 2 | taxpayer-owned only |
| AdminUsers.row.email | Email | `GET /api/v1/admin/users` | `email` | In Scope Phase 2 | from `AdminUserRead` |
| AdminUsers.row.name | Full Name | `GET /api/v1/admin/users` | `full_name` | In Scope Phase 2 | from `AdminUserRead` |
| AdminUsers.row.role | Role | `GET /api/v1/admin/users` | `role` | In Scope Phase 2 | from `AdminUserRead` |
| AdminUsers.row.active | Active | `GET /api/v1/admin/users` | `is_active` | In Scope Phase 2 | from `AdminUserRead` |
| AdminSettings.row.key | Setting Key | `GET /api/v1/admin/settings` | `key` | In Scope Phase 2 | from `AdminSettingRead` |
| AdminSettings.row.value | Setting Value | `GET /api/v1/admin/settings` | `value` | In Scope Phase 2 | from `AdminSettingRead` |
| AdminSettings.row.updatedAt | Updated At | `GET /api/v1/admin/settings` | `updated_at` | In Scope Phase 2 | from `AdminSettingRead` |

---

## 10. Screen and Action Scope Classification

| Screen/Action | Scope | Rationale |
|---|---|---|
| Login | In Scope Phase 2 | full auth contract exists |
| Dashboard | In Scope Phase 2 | summary + recent activity endpoints exist |
| Parties list | In Scope Phase 2 | `GET /api/v1/parties` exists |
| Register party | In Scope Phase 2 | `POST /api/v1/parties` exists |
| Party detail | In Scope Phase 2 | `GET /api/v1/parties/{id}` exists |
| Party role assignment | In Scope Phase 2 | `POST /api/v1/parties/{id}/roles` exists |
| Filings list | In Scope Phase 2 | `GET /api/v1/filings` exists |
| Filing create/submit | In Scope Phase 2 | `POST /filings` and `PATCH /filings/{id}/submit` exist |
| Filing correction | In Scope Phase 2 | `POST /filings/{id}/correct` exists |
| Assessments list | In Scope Phase 2 | `GET /api/v1/assessments` exists |
| Assessment create/status | In Scope Phase 2 | `POST` and `PATCH` endpoints exist |
| Assessment appeal | In Scope Phase 2 | `POST /assessments/{id}/appeal` exists |
| Admin users | In Scope Phase 2 | `GET/POST/PATCH /api/v1/admin/users...` exists |
| Admin settings | In Scope Phase 2 | `GET/PATCH /api/v1/admin/settings...` exists |
| Dedicated receipt retrieval view | Deferred | no receipt endpoint in architect contract |
| Manual line-item editor | Deferred | non-canonical by 4C decision |

---

## 11. Access Control and State Rule References

### 11.1 Strict Access Control

Applied as UI guardrails with backend as source of truth:
- `ADMIN`: full app access
- `OFFICER`: parties, filings, assessments, dashboard
- `TAXPAYER`: own party/filings/assessments only

Failure handling:
- `401` unauthenticated -> login redirect
- `403` forbidden -> permission screen
- `404` ownership-protected missing resource -> not found screen

### 11.2 Filing and Assessment SSOT (Architect 3.1.1)

- `POST /filings`: `NONE -> DRAFT`
- `PATCH /filings/{id}/submit`: `DRAFT -> SUBMITTED_WITH_RECEIPT`
- `POST /filings/{id}/correct`: previous filing `-> CORRECTED`, new version starts `DRAFT`
- `POST /assessments`: filing `NO_CHANGE`, assessment `NONE -> PENDING`
- `PATCH /assessments/{id}/status`: filing `NO_CHANGE`, assessment `PENDING -> COMPLETE` or `COMPLETE -> APPEALED`
- `POST /assessments/{id}/appeal`: filing `NO_CHANGE`, assessment `COMPLETE -> APPEALED`

Assessment actions must not implicitly mutate filing state.  
Filing state transitions occur only through explicit filing endpoints.

### 11.3 Deadline and Penalty Handling

- Filing deadline and late penalty are displayed from `frist`, `late_filing_days`, `late_filing_penalty`
- Assessment deadlines are displayed from `payment_deadline` and `appeal_deadline`
- Surcharge and interest are separate and shown as separate amounts

---

## 12. Terminology Map (Domain Value -> Display Label)

### 12.1 Filing Domain

| Domain Value | Display Label (English first) |
|---|---|
| `angivelse_type = MOMS` | VAT Return (`Momsangivelse`) |
| `rubrik_a` | Output VAT |
| `rubrik_b` | Input VAT |
| `rubrik_c` | EU Purchase VAT |
| `rubrik_d` | EU Sales Value |
| `rubrik_e` | Import VAT |
| `momstilsvar` | Net VAT Amount |
| `kvitteringsnummer` | Receipt Number (`Kvitteringsnummer`) |
| `supplemental_line_items` | Optional Detail Lines (non-canonical) |

### 12.2 Status Domain

| Domain Value | Display Label |
|---|---|
| `DRAFT` | Draft (`Kladde`) |
| `SUBMITTED_WITH_RECEIPT` | Submitted with Receipt (`Indberettet med kvittering`) |
| `UNDER_REVIEW` | Under Review (`Under behandling`) |
| `ACCEPTED` | Accepted (`Godkendt`) |
| `REJECTED` | Rejected (`Afvist`) |
| `CORRECTED` | Corrected (`Korrigeret`) |
| `PENDING` | Pending (`Afventende`) |
| `COMPLETE` | Complete (`Afsluttet`) |
| `APPEALED` | Appealed (`Anket`) |

### 12.3 Assessment Domain

| Domain Value | Display Label |
|---|---|
| `decision_outcome = ACCEPTED` | Outcome: Accepted |
| `decision_outcome = ADJUSTED` | Outcome: Adjusted |
| `decision_outcome = REJECTED` | Outcome: Rejected |
| `surcharge_amount` | Surcharge |
| `interest_amount` | Interest |

---

## 13. SKAT Benchmark Alignment and Explicit Deviations

### 13.1 Alignment

Filing UX mirrors the benchmark behavior from researcher Section 2:
1. Fixed VAT fields, not free-form canonical entry
2. Required markers and inline helper cues
3. Draft first, submit second
4. Confirmation/receipt state after submission
5. Correction path supported
6. Payment/refund implications exposed from submission outcome fields

### 13.2 Explicit Deviations

| Deviation | Why | Scope |
|---|---|---|
| English-first UI with Danish legal aliases | fixed product decision | In Scope Phase 2 |
| Internal email/password auth, not MitID Erhverv | current architect contract | In Scope Phase 2 |
| Stable English enum persistence | architect contract stability | In Scope Phase 2 |
| Optional supplemental detail lines | bookkeeping convenience, non-canonical | In Scope Phase 2 |
| Admin pages included | fixed product decision | In Scope Phase 2 |

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
    (app)/parties/page.tsx
    (app)/parties/new/page.tsx
    (app)/parties/[id]/page.tsx
    (app)/filings/page.tsx
    (app)/filings/new/page.tsx
    (app)/filings/[id]/page.tsx
    (app)/assessments/page.tsx
    (app)/assessments/[id]/page.tsx
    (app)/admin/users/page.tsx
    (app)/admin/settings/page.tsx
  components/
    filings/
      CreateFilingRubrikForm.tsx
      FilingRubrikSummaryCard.tsx
      FilingStatusTimeline.tsx
      FilingCorrectionPanel.tsx
    assessments/
      CreateAssessmentForm.tsx
      AssessmentStatusTimeline.tsx
      AssessmentAppealPanel.tsx
    admin/
      AdminUsersTable.tsx
      AdminSettingsTable.tsx
```

Notes:
- `supplemental_line_items` support is import-style and non-canonical.
- No manual line-item-first filing editor is included in Phase 2.

---

## 16. Pass-3 Delta (State-Policy Alignment)

- Removed all assessment flow statements that implied filing-state mutation.
- Aligned filing status terminology to canonical `SUBMITTED_WITH_RECEIPT` (replacing legacy `SUBMITTED` where it represented filing domain state).
- Updated SSOT/state and terminology sections to enforce: only filing endpoints mutate filing state.
