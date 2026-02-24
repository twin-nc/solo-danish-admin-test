# Danish Tax Administration Platform - Researcher Spec (Revised)

**Document:** AGENT_RESEARCHER_SPEC.md  
**Date:** 2026-02-24  
**Author:** Researcher Agent  
**Status:** Review Round 1 update for Architect/Designer unblock

## 0) Fixed Decisions (Locked)

- Legal accuracy first.
- UI language mostly English (Danish legal terms preserved where required).
- Admin pages are in scope now.
- Filing decision is 4C: Phase 2 uses fixed official VAT fields as canonical model; optional line-item detail can be added later as non-canonical convenience.
- Strict access control now.
- Deadlines and penalties enforced now.
- Correctness over speed.

## 1) Claim-Level Evidence Map

| claim_id | rule | source URL / title | legal section | effective date | confidence |
|---|---|---|---|---|---|
| C01 | VAT registration is mandatory above DKK 50,000 turnover; below is optional. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-registrerer-du-din-virksomhed-for-moms ("Sådan registrerer du din virksomhed for moms") | Momsloven § 48 (registration threshold) | Source retrieved 2026-02-24; law basis: LBK 209 of 2024-02-27 (gældende) | high |
| C02 | VAT filing period assignment thresholds are monthly (>50m), quarterly (5m-50m), semi-annual (<=5m), with legal deadline formulas. | https://www.retsinformation.dk/api/pdf/241297 ("Bekendtgørelse af lov om merværdiafgift") | Momsloven § 57 stk. 2-4 | LBK 209 of 2024-02-27 (gældende; later changes listed through 2025-12-29) | high |
| C03 | Filing/payment calendar dates for 2026/27 are published by SKAT and should be used by default in UX reminders. | https://skat.dk/erhverv/moms/frister-indberet-og-betal-moms ("Frister for moms") | Operational guidance (implements § 57 and payment rules) | Source retrieved 2026-02-24 | high |
| C04 | Filing is required even with no turnover (zero filing). | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-indberetter-du-moms ("Sådan indberetter du moms") and https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-registrerer-du-din-virksomhed-for-moms | Operational guidance | Source retrieved 2026-02-24 | high |
| C05 | Missing a filing deadline triggers provisional assessment fee shown publicly as DKK 1,400 per period. | https://skat.dk/erhverv/moms/tjek-paa-momsen ("Tjek på momsen") and https://skat.dk/erhverv/moms/frister-indberet-og-betal-moms | Operational guidance | Source retrieved 2026-02-24 | medium |
| C06 | Provisional assessment fee exists in law; amount is currently codified in opkrævningsloven and has changed over time. Treat fee amount as policy-configurable. | https://www.retsinformation.dk/api/pdf/244881 ("Bekendtgørelse af lov om opkrævning af skatter og afgifter m.v.") | Opkrævningsloven § 4 stk. 2 | LBK 1040 of 2024-09-13 (gældende; later changes listed through 2025-12-29) | high |
| C07 | Late payment interest is variable (base rate + 0.7 percentage points), computed daily; skattekonto saldo interest accrues daily and is posted monthly. | https://www.retsinformation.dk/api/pdf/244881 | Opkrævningsloven § 7 stk. 1-2 and § 16 c stk. 1 | LBK 1040 of 2024-09-13 | high |
| C08 | Tax/fee amounts cannot be safely hardcoded long term; rates are republished yearly and tied to reference rates. | https://www.retsinformation.dk/api/pdf/244881 | Opkrævningsloven § 7 stk. 2 | LBK 1040 of 2024-09-13 | high |
| C09 | Ordinary VAT reassessment/change window is 3 years from filing deadline; extraordinary reopening is possible under defined conditions. | https://www.retsinformation.dk/eli/lta/2025/1228/pdf ("Bekendtgørelse af skatteforvaltningsloven") | Skatteforvaltningsloven § 31 stk. 1-2 and § 32 stk. 1 | LBK 1228 of 2025-10-13 | high |
| C10 | Correction workflow is explicitly supported in TastSelv; >3 years requires documented exceptional grounds. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-retter-du-din-momsindberetning-eller-betaling | Operational guidance aligned with SFL § 31-32 | Source retrieved 2026-02-24 | high |
| C11 | Filing and payment deadline are the same for a period; payment can be made earliest 5 days before deadline in normal flow. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-betaler-du-moms | Operational guidance | Source retrieved 2026-02-24 | high |
| C12 | Submission flow includes explicit confirmation/receipt state (kvitteringsbillede) and historical receipts can be retrieved. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-indberetter-du-moms and https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-betaler-du-moms | Operational guidance | Source retrieved 2026-02-24 | high |
| C13 | Validation cues visible in public guidance: required fields marked with red star, inline help via blue question marks, explicit draft save before final approval. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-indberetter-du-moms | Operational guidance | Source retrieved 2026-02-24 | high |
| C14 | Refund outcome is explicit: amount appears on skattekonto and is normally paid to NemKonto within 21 days after filing. | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-betaler-du-moms | Operational guidance | Source retrieved 2026-02-24 | high |
| C15 | Authentication/authorization is role/delegation-based (MitID Erhverv + explicit rights/delegations in TastSelv context). | https://skat.dk/erhverv/moms/moms-saadan-goer-du/saadan-indberetter-du-moms | Operational guidance | Source retrieved 2026-02-24 | medium |
| C16 | Public official forms confirm fixed-field rubric style (not free-form line items): salgsmoms/købsmoms and rubrik A/B/C family. | https://skat.dk/media/t4nhivvs/31012_juni_2024-t.pdf ("31.012 Angivelse, lejlighedsvis registrering") | Form-level official structure, references momsbekendtgørelsen | Form version 2024.06 | medium |
| C17 | Payment processing on skattekonto follows oldest-debt-first behavior. | https://www.retsinformation.dk/api/pdf/244881 and https://skat.dk/erhverv/moms/tjek-paa-momsen | Opkrævningsloven § 16 b / § 16 c context + operational guidance | Source retrieved 2026-02-24 | high |
| C18 | If filing date falls on bank closing day, next bank day applies. | https://www.retsinformation.dk/api/pdf/244881 | Opkrævningsloven § 2 stk. 3 | LBK 1040 of 2024-09-13 | high |

## 2) SKAT VAT Filing UX Benchmark (Public, Official)

### 2.1 End-to-End Filing Journey (Observed)

| step | public observation from official sources | evidence |
|---|---|---|
| 1 | Business is VAT-registered via virk.dk / Erhvervsstyrelsen path, then files in TastSelv Erhverv. | C01 |
| 2 | In TastSelv flow: `Moms -> Momsindberetning -> Indberet moms -> choose period -> fill fields -> Godkend`. | C12 |
| 3 | Required fields use visible required marker (`*`), with inline helper cues (`?`). | C13 |
| 4 | User may save draft (`kladde`) and complete later; draft is not a submission. | C13 |
| 5 | On submit, a receipt/confirmation screen is shown with pay/receive outcome; receipt history is accessible later. | C12 |
| 6 | If amount is payable: pay to skattekonto using payment line; if credit: normal NemKonto payout in <=21 days. | C14 |
| 7 | Corrections are supported as a distinct path, with stricter handling after 3 years. | C10 |

### 2.2 Field Model and Interaction Style

| area | benchmark finding | implication for Phase 2 |
|---|---|---|
| Canonical input style | Official filings use fixed VAT fields/rubriks, not free-form line-item narratives. | Canonical DB/API model must be fixed-field (4C decision), line-items only as optional derived convenience layer later. |
| Minimum publicly verifiable fields | `salgsmoms` and `kobsmoms` are explicitly central in current public guidance; official form evidence also exposes rubrik A/B/C style fields. | Phase 2 canonical payload must include fixed fields for sales VAT, purchase VAT, and EU/zero-rate rubric group fields supported by current official documentation. |
| Required-mark behavior | Required fields are explicitly marked and validated before approval. | UI must show required marker and block final submission when mandatory fields are absent. |
| Help behavior | Inline helper cues exist in flow. | Add inline field hints and legal context tooltips for each fixed field. |
| Confirmation | Explicit kvittering state with payment/refund implications. | Persist immutable `receipt_id`, `submitted_at`, and `submission_outcome` in backend. |
| Correction state | Correction path is first-class and time-window dependent. | Implement correction workflow with policy checks (`<=3y`, `>3y exceptional`). |

### 2.3 Validation / Error Cues (Publicly Verifiable)

- Required field markers and helper cues are visible in official step guide (C13).
- Zero filing is explicitly guided and auto-zero behavior is described for no-activity periods (C04).
- Missing filing leads to provisional assessment path and fee exposure (C05/C06).
- Payment sequence constraints and debt allocation behavior are explicit (C11/C17).

### 2.4 Submission Outcomes and Post-Submission States

- `DRAFT` (saved but not submitted) (C13)
- `SUBMITTED_WITH_RECEIPT` (kvittering issued) (C12)
- `PAYABLE` / `REFUNDABLE` as outcome branch on receipt (C14)
- `CORRECTION_REQUESTED` / `CORRECTION_ACCEPTED` / `CORRECTION_REJECTED` based on timing and grounds (C10)

### 2.5 What Is Public vs Login-Gated

Publicly confirmed:
- High-level sequence, required-marker behavior, draft/approve pattern, receipt/retrieval, correction gates, deadlines, and payment/refund outcomes.

Not fully public without active login and profile-specific context:
- Exact authenticated screen layout by taxpayer type.
- Full current set of all rubric labels/ordering for every company profile.
- Exact in-session validation message catalog and code-level error taxonomy.

## 3) MVP Legal Baseline (Phase Discipline)

| bucket | item | why | evidence |
|---|---|---|---|
| Required now | Fixed canonical VAT filing fields (no free-form line-item-only filing). | 4C decision + official fixed-field pattern. | C16 |
| Required now | Enforce filing frequency + deadlines by party profile and period. | Statutory compliance. | C02, C03, C18 |
| Required now | Require submission even for zero activity period. | Explicit obligation in guidance. | C04 |
| Required now | Enforce strict taxpayer-data isolation and delegated access checks at API layer. | Product decision + official delegation pattern. | C15 |
| Required now | Persist receipt state and expose retrieval. | Official submission outcome behavior. | C12 |
| Required now | Enforce late behavior: provisional assessment trigger and interest/fee policy hooks. | Compliance and product decision. | C05, C06, C07 |
| Required now | Keep monetary sanctions/rates configurable (not hardcoded). | Legal rates/fees can change. | C06, C08 |
| Recommended now | Include explicit correction workflow statuses and >3y exceptional-grounds path. | Avoid legal ambiguity in amendments. | C09, C10 |
| Recommended now | Add reminder/calendar UX using published date tables. | Reduce filing defects; aligns with SKAT behavior. | C03 |
| Recommended now | Add validation hint text per fixed field. | Matches public SKAT interaction cues. | C13 |
| Defer | Non-canonical line-item convenience layer and bookkeeping import drill-downs. | Not required for legal sufficiency in Phase 2. | 4C decision |
| Defer | High-fidelity visual mimicry of protected SKAT branding/assets. | Not required; legal and UX parity does not require asset copying. | replication policy |
| Defer | Full parity with every profile-specific authenticated screen variation. | Login-gated and not fully publicly verifiable. | uncertainty section |

## 4) Architect Unblock Package (Phase 2 Mandatory Only)

### 4.1 Mandatory Canonical Model Fields

`Party` (minimum)
- `party_id` (UUID)
- `cvr_number` (string, 8 digits)
- `se_number` (string, 8 digits)
- `vat_period_type` (`MONTHLY | QUARTERLY | SEMI_ANNUAL`)
- `vat_registration_active` (bool)

`VatFiling` (minimum)
- `filing_id` (UUID)
- `party_id` (FK)
- `se_number` (string)
- `period_key` (string; `YYYY-MM` or `YYYY-Qn` or `YYYY-Hn`)
- `period_type` (`MONTHLY | QUARTERLY | SEMI_ANNUAL`)
- `sales_vat_amount` (decimal)  # salgsmoms
- `purchase_vat_amount` (decimal)  # kobsmoms
- `eu_purchase_goods_value` (decimal, rubric A goods)
- `eu_purchase_services_value` (decimal, rubric A services)
- `eu_sales_goods_value` (decimal, rubric B goods)
- `eu_sales_services_value` (decimal, rubric B services)
- `other_out_of_scope_value` (decimal, rubric C style)
- `net_vat_amount` (decimal, computed)
- `status` (`DRAFT | SUBMITTED | CORRECTION_PENDING | CORRECTION_ACCEPTED | CORRECTION_REJECTED`)
- `submitted_at` (datetime, nullable)
- `receipt_id` (string, nullable)
- `corrected_from_filing_id` (UUID, nullable)

Notes:
- This is intentionally minimal and strictly sourced from publicly verifiable official guidance/forms.
- Additional rubric variants (if any in logged-in profile views) must be additive and backward compatible.

### 4.2 Mandatory Validation and Policy Rules

- One canonical filing per `(se_number, period_key)` unless filed as correction.
- `period_key` must match `vat_period_type`.
- Deadline check must be deterministic using legal period rules + bank-day handling.
- Zero filing must be accepted and must still create receipt state when submitted.
- `net_vat_amount` must be computed server-side from canonical fields (no client trust).
- Fee/interest parameters must be pulled from configurable policy store (`late_filing_fee_amount`, `late_interest_formula`, `effective_from`).
- Access control:
  - taxpayer users can only access filings for owned/authorized `party_id`/`se_number`
  - delegated users need explicit granted rights
  - admin roles require explicit audit logging for read/write access

### 4.3 Mandatory Endpoint Constraints (API Contract Minimum)

- `POST /api/v1/vat-filings` (create draft; ownership check)
- `POST /api/v1/vat-filings/{id}/submit` (deadline + required-field validation + receipt issuance)
- `POST /api/v1/vat-filings/{id}/correct` (time-window and grounds validation)
- `GET /api/v1/vat-filings?party_id=&period=` (scoped listing)
- `GET /api/v1/vat-filings/{id}/receipt` (receipt retrieval)
- `GET /api/v1/vat-deadlines?party_id=&period=` (deterministic deadline computation)

## 5) Decision Defense Package

| decision challenge | selected approach | rejected alternative(s) | rationale / tradeoff |
|---|---|---|---|
| Filing schema (`line_items` vs fixed rubrik fields) | Fixed canonical fields for Phase 2. | Free-form line-items as canonical. | Legal/official filing pattern is fixed-field; line-items remain optional convenience later (4C). |
| Terminology persistence vs UI labels | Persist stable English technical enum keys; expose Danish legal labels at API/UI boundary mapping. | Persist only Danish labels in DB; or only English labels in UI. | Keeps schema stability and migration safety while preserving legal wording where needed. |
| Penalties/rates implementation | Config-driven policy values with effective dates and audit trail. | Hardcode fee/rate constants in business logic. | Statutory rates/fees and guidance amounts can change; config avoids emergency code redeploys. |
| Access policy strictness | Row-level tenant scoping + explicit delegation checks + admin audit logs. | Broad role access without ownership checks. | Product decision mandates strict isolation now; reduces legal/security risk. |
| UX replication fidelity | Replicate workflow/state patterns only; avoid copying SKAT branding/assets verbatim. | Pixel-copy SKAT UI. | Meets usability goal without IP/brand copying risk and without reliance on protected assets. |

## 6) Intentional Uncertainty (Explicit)

Areas not fully publicly verifiable without active TastSelv login are intentionally marked as uncertain and must not be guessed:

1. Exact current authenticated field ordering and wording across all taxpayer profiles.
2. Full validation/error message catalog and server error codes shown in-session.
3. Whether additional rubrik groups beyond publicly documented set are conditionally shown for specific registration types.

Implementation rule:
- Treat uncertain items as feature-flagged extensions, not as Phase 2 blockers.
- Preserve additive schema strategy so new official fields can be added without breaking canonical payloads.

## 7) Replication Policy Note

Replicate SKAT workflow and interaction patterns (step order, required-field behavior, validation, confirmation/receipt, correction gating), but do not copy protected branding, logos, icons, or proprietary visual assets verbatim.

## 8) Changelog (This Revision)

- Replaced broad narrative with source-traceable implementation spec.
- Added claim-level evidence table with claim IDs, legal anchors, dates, confidence.
- Added SKAT VAT Filing UX benchmark with flow, controls, states, and limits.
- Added strict `Required now / Recommended now / Defer` MVP legal baseline.
- Added Architect Unblock Package (mandatory Phase 2 fields/rules/endpoints only).
- Marked policy-variable fee/rate values as configurable (not hardcoded).
- Added explicit uncertainty section for login-gated/non-public details.
- Added replication policy to prevent branding/IP overreach.
- Kept phase discipline aligned with fixed product decisions.
