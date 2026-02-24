# Reviewer Agent — Phase 1 Review

**Document:** AGENT_REVIEWER_SPEC.md
**Date:** 2026-02-24
**Author:** Reviewer Agent
**Input specs reviewed:**
- AGENT_RESEARCHER_SPEC.md (Revised, 2026-02-24)
- AGENT_ARCHITECT_SPEC.md (Pass-3 + Micro-fix, 2026-02-24)
- AGENT_DESIGN_SPEC.md (Pass-3 + Micro-fix, 2026-02-24)
- AGENT_ROLES.md (authoritative role definitions)
- app/models/party.py (existing Party model)

---

## Executive Summary

**Overall verdict: CONDITIONAL — Do not start Phase 2 until the seven required actions in Section 7 are resolved.**

The three Phase 1 specs are substantially better than a first draft would typically be. The Architect has incorporated nearly all Researcher field-level corrections. The Designer has correctly mapped its UI fields to the Architect's schema names. The state machine is coherent and the canonical Rubrik model is correctly implemented. These are real achievements.

However, several issues are serious enough to block code quality or legal correctness in Phase 2:

1. The UniqueConstraint on Filing uses `version` as a fourth key, which makes it structurally incapable of preventing duplicate canonical filings for the same period. This is the single most important blocker.
2. The Party model (existing code, `app/models/party.py`) stores neither `cvr_nummer`, `se_nummer`, nor `afregningsperiode_type` as first-class columns. The Researcher mandated these. The Architect has not addressed the Party model gap — it has only added them to the Filing model. A developer reading the specs today would not know whether to modify the Party model or leave it as a generic EAV structure.
3. The Researcher's formula `momstilsvar = A + C + E - B` is in the AGENT_ROLES.md (Section 5, Backend Coder responsibilities) and in the Architect's service code, but the Architect spec text never explicitly states the formula — only the code does. The formula also does not appear in the Designer spec. This is an incomplete verification chain.
4. The deadline calculation hardcodes specific day-of-month values (25th for monthly, 10th for quarterly, 1st for semi-annual) that have no legal citation in the Architect spec.
5. `kvitteringsnummer` is generated internally by the platform (not by SKAT), a significant domain decision that is never explicitly stated or justified anywhere.
6. Key operational gaps exist: no filtering or pagination on list endpoints; no endpoint to assign an officer (`assigned_officer_id` is absent from the Assessment model entirely); no specification of what happens when a filing is submitted after `frist`.
7. The agterskrivelse concept mentioned in AGENT_ROLES.md (Frontend Coder responsibilities) has no corresponding endpoint in the Architect spec. The Designer also removed agterskrivelse from its explicit flows, but AGENT_ROLES.md still references it as a Frontend Coder responsibility.

---

## Section 1 — Cross-Spec Coherence

**FINDING 1 | Severity: BLOCKER | Spec: Architect Section 3.2 / Researcher Section 4.1**

The UniqueConstraint on `filings` is defined as `(se_nummer, filing_period, angivelse_type, version)` (Architect Section 3.2, `__table_args__`, and confirmed in Migration 0003). Adding `version` as a fourth key means two correction filings for the same `(se_nummer, filing_period, angivelse_type)` at version 1 are structurally identical and would conflict — but the intent is precisely that a correction creates a new version. More critically, this constraint does not prevent two independent users from creating duplicate version-1 canonical filings for the same period if they race. The Researcher (Section 4.1) specifies the uniqueness rule as: "One canonical filing per `(se_number, period_key)` unless filed as correction." The constraint must be on `(se_nummer, filing_period, angivelse_type)` alone, with `korrektionsangivelse=True` filings excluded from it (partial index), or the version increment logic must be the sole duplication guard with no DB-level safety net. As written, the DB constraint is both wrong in its key set and inconsistent with the Researcher's stated rule.

**FINDING 2 | Severity: BLOCKER | Spec: Architect Section 3.2 vs. Researcher Section 4.1 / existing app/models/party.py**

The Researcher (Section 4.1) mandated that the Party model include `cvr_number`, `se_number`, `vat_period_type`, and `vat_registration_active` as first-class fields. The existing `app/models/party.py` uses a generic EAV (Entity-Attribute-Value) pattern: identifiers are stored in `party_identifiers` rows using `identifier_type_cl` and `identifier_value`. The Architect has not addressed the Party model at all — Section 3 and the migration plan make no mention of altering the `parties` or `party_identifiers` tables. The Filing model denormalizes `se_nummer` onto the filing row (correct for filing lookup), but the Party model has no queryable `afregningsperiode_type` column either. A developer implementing the filing service today cannot look up a party's VAT period type from the Party model — there is no such column. The Architect spec must either (a) add these columns to `Party` / `party_identifiers`, or (b) explicitly document that period type is always provided by the caller at filing creation time and never derived from the Party record, and accept that inconsistency with the Researcher's mandate.

**FINDING 3 | Severity: MAJOR | Spec: Architect Section 3.2 vs. Researcher Section 4.1**

The Researcher (Section 4.1) uses the field names `cvr_number` and `se_number` (English, no trailing `r`). The Architect uses `se_nummer` (Danish, with `r`) on the Filing model. This is a deliberate Architect choice that is not documented as an intentional deviation. The inconsistency will cause confusion when Coder agents read both specs: the Researcher says `se_number`, the Architect says `se_nummer`. One of the two must be declared authoritative.

**FINDING 4 | Severity: MAJOR | Spec: Architect Section 3.5 / Researcher Section 4.1 and 4.2**

The Researcher (Section 4.1) lists `corrected_from_filing_id` as the field name on `VatFiling`. The Architect (Section 3.2) names it `original_filing_id`. These refer to the same concept. The name difference is not documented as an intentional deviation. The Designer correctly uses `original_filing_id` (aligned to the Architect). The inconsistency is between the Researcher and Architect; it must be resolved by declaring one canonical name.

**FINDING 5 | Severity: MAJOR | Spec: Architect Section 3.2 vs. Researcher Section 4.1**

The Researcher (Section 4.1) specifies `receipt_id` (English) on the VatFiling model. The Architect uses `kvitteringsnummer` (Danish). Both the Architect and the Designer are aligned on `kvitteringsnummer`. However, the Researcher's internal schema reference uses `receipt_id`. An intentional deviation from the Researcher's English field naming is not documented. This also means the Architect has no field named `receipt_id` — the `FilingReceiptRead` schema uses `receipt_id` as a response field name aliased from `kvitteringsnummer`. This is coherent internally, but the deviation from the Researcher's schema spec should be acknowledged.

**FINDING 6 | Severity: MAJOR | Spec: Architect Section 4.2 vs. Researcher Section 4.1 and Roles (Backend Coder)**

The Assessment model (`TaxAssessment`, Architect Section 4.2) has no `agterskrivelse_sent_at` field and no `klage_frist` field. The AGENT_ROLES.md (Researcher responsibilities and Frontend Coder responsibilities) explicitly lists `agterskrivelse` as a domain concept. The Frontend Coder responsibilities state: "Implement all Assessment views: Assessments List, Assessment Detail, Status update, Agterskrivelse action." This implies a UI action and a backend endpoint exist. Neither exists in the Architect spec. The Designer (Section 7.3 and Section 8) has removed the agterskrivelse action from its own flows and API parity matrix, but the role definition still lists it as a Frontend Coder deliverable. This is an unresolved gap that spans all three specs.

**FINDING 7 | Severity: MAJOR | Spec: Architect Section 4.2 vs. Designer Section 9 / Roles**

The Assessment model has no `assigned_officer_id` field (distinct from `assessed_by`). The concept of assigning an officer to an assessment exists in the AGENT_ROLES.md (Reviewer responsibilities). The Architect only tracks `assessed_by` (the creator of the assessment). There is no endpoint to re-assign or update the responsible officer. This is a gap that the Architect has not addressed or explicitly deferred.

**FINDING 8 | Severity: MINOR | Spec: Designer Section 5h vs. Architect Section 3.1.1**

The Designer (Section 5h) lists the submit action as `PATCH /api/v1/filings/{id}/submit`. The Architect (Section 3.1.1 state transition table and Section 8.1) correctly lists this as `PATCH`. The Designer's Section 7.2 (user flow, step 4) also correctly uses `PATCH`. The Designer's Section 8 Action-to-API Parity Matrix lists the submit action consistently. **Verified pass.**

**FINDING 9 | Severity: MINOR | Spec: Designer Section 5b vs. Architect Section 8.1**

The Designer (Section 5b, Dashboard) references `GET /api/v1/dashboard/summary`. This endpoint appears in the Architect's API contract summary (Section 8.1) but has no corresponding Router section, no Pydantic schema, no service, and no repository defined anywhere in the Architect spec. A coder picking up the Architect spec would have no idea what `summary` returns or how to implement it.

**FINDING 10 | Severity: MINOR | Spec: Designer Section 3.2 (StatusChip) vs. Architect Section 3.2 (Filing status values)**

The Designer's StatusChip lists `CORRECTION_PENDING` as a status value (Section 3.2). This value does not exist in the Architect's Filing model valid status values (Section 3.2, "Valid field values" table) or in the state transition table (Section 3.1.1). The Architect uses `CORRECTED` for the prior filing version and starts a new `DRAFT` for the correction. `CORRECTION_PENDING` is a Researcher concept that the Architect dropped without documenting the reason. The Designer has partially retained it in the StatusChip component but removed it from its own flow/state tables. This must be resolved: either reintroduce `CORRECTION_PENDING` as an active state with a defined trigger, or explicitly remove it from the Designer's StatusChip component.

**FINDING 11 | Severity: MINOR | Spec: Designer Section 3.2 vs. Architect Section 3.1.1 and 4.2**

The Designer's StatusChip (Section 3.2) lists `PENDING`, `COMPLETE`, and `APPEALED` as valid Assessment status values. The Architect confirms them in Section 4.2. The Designer also lists `UNDER_REVIEW` as reserved/deferred (consistent with Architect). The status vocabularies are aligned across Architect and Designer for the active set. The only residual issue is `CORRECTION_PENDING` noted in Finding 10.

**FINDING 12 | Severity: MINOR | Spec: Designer Section 9 (Data Contract) vs. Architect Section 4.2**

The Designer (Section 9, AssessmentForm) references `agterskrivelse_sent_at` and `klage_frist` implicitly via terminology — but these fields do not appear explicitly in the Designer's data contract table, and the Assessment model has no `agterskrivelse_sent_at`. The Designer has implicitly deferred this concept, but AGENT_ROLES.md has not updated its Frontend Coder scope accordingly.

---

## Section 2 — Domain Accuracy

**FINDING 13 | Severity: MAJOR | Spec: Architect Section 3.5 (_compute_deadline) / Researcher Section 1 (C02, C03, C18)**

The Architect's `_compute_deadline` method hardcodes:
- Monthly: deadline is the 25th of the following month.
- Quarterly: deadline is the 10th of the second month after quarter end (e.g. Q1 ends March → deadline May 10).
- Semi-annual: H1 → September 1; H2 → March 1 of the following year.

The Researcher (C02, C03) cites Momsloven §57 stk. 2-4 as the source for period assignment thresholds and deadline formulas, and C03 cites SKAT's published calendar. The Researcher does not reproduce the exact day-of-month values in the spec text — it references the legal section and says "legal period rules + bank-day handling" (Section 4.2). The Architect has chosen specific dates without citing which part of §57 or the operational calendar supports them. The Architect spec must add a legal citation for each day-of-month value used in `_compute_deadline`, or the Researcher must verify and endorse those values with a claim reference.

**FINDING 14 | Severity: MAJOR | Spec: Architect Section 3.5 / Researcher Section 3 (MVP Legal Baseline)**

The Researcher (Section 4.2) states: "Deadline check must be deterministic using legal period rules + bank-day handling." The Architect's `_next_bank_day` defers entirely to `VatPolicyRepository.get_next_open_bank_day(candidate, db)`. However, the Architect spec includes no definition of the `VatPolicyRepository` interface or schema beyond its name in the dependency list and its usage in the service. The Coder agent cannot implement `get_next_open_bank_day` without knowing: (a) what table stores bank holidays, (b) the migration for that table, and (c) whether the initial seed data is in scope.

**FINDING 15 | Severity: MAJOR | Spec: Architect Section 3.5 / Researcher Section 3 (Required now: enforce late behavior)**

The Researcher (Section 3, Required now) mandates: "Keep monetary sanctions/rates configurable (not hardcoded)." The Architect implements this via `VatPolicyRepository.get_active_policy(submitted_at.date(), db)` and references the `late_filing_fee_amount` field. However, the `VatPolicyRepository` and its underlying model are never defined in the Architect spec. There is no `VatPolicy` model, no migration for a policy table, and no schema definition. The Coder agent would have to invent this entirely.

**FINDING 16 | Severity: MINOR | Spec: Architect Section 3.5 (_compute_momstilsvar) / Researcher Section 4.1 / AGENT_ROLES.md Section 5**

The momstilsvar formula `A + C + E - B` appears correctly in three places: the Architect's `_compute_momstilsvar` method (Section 3.5), the AGENT_ROLES.md Backend Coder responsibilities, and the Researcher's AGENT_ROLES description. However, the formula is never stated explicitly in the Architect spec text outside of a code block — there is no plain-text "the formula is A + C + E - B" statement. The Designer does not state the formula at all. For a compliance platform this formula is a legal anchor — it should appear as a named rule in the spec, not only in a code implementation.

**FINDING 17 | Severity: MINOR | Spec: Architect Section 3.2 / Researcher Section 4.1**

The Researcher (Section 4.1) specifies the field `period_key` (not `filing_period`) and `period_type` (not `afregningsperiode_type`) on the VatFiling model. The Architect uses `filing_period` and `afregningsperiode_type`. These are not wrong choices — they may be deliberately more descriptive — but they deviate from the Researcher's naming without documented justification. The Designer correctly uses `filing_period` and `afregningsperiode_type` (aligned to the Architect). The gap is Researcher vs. Architect, not Designer vs. Architect.

**FINDING 18 | Severity: MINOR | Spec: Researcher Section 2.4 / Architect Section 3.2 / Designer Section 3.2**

The Researcher (Section 2.4) lists `CORRECTION_REQUESTED`, `CORRECTION_ACCEPTED`, and `CORRECTION_REJECTED` as post-submission states. The Architect has not implemented any of these; it uses `CORRECTED` for the prior version and starts a new `DRAFT`. The Researcher's states describe a different workflow model — a correction submitted for review — rather than the Architect's immediate-correction-as-new-version model. The Architect's choice may be operationally simpler, but the deviation from the Researcher's workflow model is not documented as a deliberate decision.

**FINDING 19 | Severity: MINOR | Spec: Architect Section 3.2 / Researcher Section 2.4**

The Researcher (Section 2.4) lists `SUBMITTED_WITH_RECEIPT` as the correct submitted state. The Architect uses exactly this value. The Designer uses exactly this value. **Verified pass — all three specs are aligned on this critical status value.**

**FINDING 20 | Severity: MINOR | Spec: Architect Section 3.5 / Researcher C12**

The Researcher (C12) states that "historical receipts can be retrieved." The Architect implements `GET /api/v1/filings/{id}/receipt` which retrieves a receipt for one filing by ID. This satisfies the minimum requirement. However, there is no endpoint to list all receipts for a party or a time period — only per-filing retrieval. The Architect has not explicitly deferred this.

---

## Section 3 — Decision Justification

**DECISION: JWT in HttpOnly cookies for auth**
Verdict: **JUSTIFIED**

The Architect (Section 2.1) uses JWT HS256 with 15-minute access tokens and 7-day refresh tokens, stored in HttpOnly, Secure, SameSite=Lax cookies. The rationale (preventing XSS access to tokens) is explicitly stated. SameSite=Lax provides CSRF protection for most browser-initiated requests. This is a well-understood, defensible pattern. The one gap is that the Architect does not address refresh token rotation or revocation — once a refresh token is issued, it is valid for 7 days regardless of logout. The logout endpoint clears the cookie client-side but does not invalidate the JWT server-side. For an internal admin tool this is acceptable at Phase 2, but the spec should acknowledge this limitation explicitly.

**DECISION: InMemoryEventBus for development/test**
Verdict: **QUESTIONABLE**

The Architect (Section 5, main.py wiring) uses `InMemoryEventBus` with no indication of whether this is the production bus or only a development/test bus. The class name says "InMemory" but the spec never explicitly states "this will be replaced by a durable broker in production." For an internal tool handling legal tax filings, lost events (e.g. on process restart) could mean lost penalty accrual notifications. The decision is operationally risky unless the spec explicitly states that all critical business logic is synchronous (persistence happens before event publishing) and events are only used for notifications/logging, which appears to be the current design. The Architect must add one sentence: "All critical business logic is transactional and completed before events are published; events are used only for logging and cross-module notification at Phase 2. A durable broker is a Phase 3 concern."

**DECISION: `se_nummer` stored on the Filing model (denormalized from Party)**
Verdict: **JUSTIFIED**

Storing `se_nummer` on the filing row is the correct approach for a legal filing record. A filing is a legal document with a specific SE number at a point in time. If a party's SE number changes (rare but legally possible), historical filings must retain the SE number they were filed under. Denormalization here is the legally correct choice, not a shortcut. The Researcher (Section 4.1) explicitly includes `se_number` on the `VatFiling` model. The Designer correctly includes `se_nummer` as a Filing form field. This decision is sound.

**DECISION: UniqueConstraint allowing korrektionsangivelse**
Verdict: **UNJUSTIFIED as implemented**

See Finding 1. The constraint `(se_nummer, filing_period, angivelse_type, version)` uses `version` as the fourth key. This means two independent users racing to create a version-1 filing for the same period would not be blocked by the constraint — they would get different UUIDs as primary keys and the same version=1, satisfying the unique constraint on two different rows. Only the application-level check in `create_filing` prevents this, but it is not race-condition safe (no SELECT ... FOR UPDATE or equivalent). The constraint must be redesigned: use a partial unique index `WHERE korrektionsangivelse = false` on `(se_nummer, filing_period, angivelse_type)` to enforce uniqueness for canonical filings only.

**DECISION: Next.js App Router for a mostly authenticated admin tool**
Verdict: **QUESTIONABLE**

The Architect (Section 1.1) chooses Next.js 14+ with App Router. The majority of the platform is authenticated-only content served to officers and admins. App Router's primary benefits (streaming, React Server Components, layout nesting) are most valuable for public-facing, content-heavy pages. For an internal admin tool with mostly form-heavy, authenticated interactions, the App Router adds complexity (server/client component boundary management, cookie handling from middleware, RSC hydration) without a clear benefit over the Pages Router or a pure SPA. The decision is not wrong, but it is not justified in the spec. The Architect should add one sentence explaining why App Router was chosen over the simpler Pages Router for this authenticated tool.

**DECISION: No FilingLineItem abstraction (flat Rubrik fields instead)**
Verdict: **JUSTIFIED**

The Researcher (Section 2.2, 4C decision) mandates: "Canonical DB/API model must be fixed-field." The Architect implements exactly this: five Rubrik fields plus turnover fields as direct columns on the Filing model. The optional `supplemental_line_items` JSON column allows bookkeeping import convenience without replacing the canonical model. The Researcher, Architect, and Designer are all aligned on this decision. It correctly models how SKAT's actual form works (fixed field positions, not free-form line items). Justified.

---

## Section 4 — Gap Analysis

**GAP 1 | Responsible spec: Architect | VatPolicyRepository is undefined**

The `VatPolicyRepository` is referenced in the Architect's `FilingService` constructor and called in `_next_bank_day` and `_late_penalty`, but the class is never defined in the spec. There is no `VatPolicy` ORM model, no schema, and no migration. The file `repositories/policy.py` appears in the file manifest (Appendix A) but is never defined.

Recommended resolution: The Architect spec must add a `VatPolicy` model definition (fields: `id`, `effective_from`, `late_filing_fee_amount`, `late_interest_base_rate`, `late_interest_margin`, bank holiday table), a corresponding migration, and the full `VatPolicyRepository` class definition.

**GAP 2 | Responsible spec: Architect | `frist` calculation uses hardcoded dates with no legal citation**

The `_compute_deadline` method uses the 25th of the following month (monthly), the 10th of the second month after quarter end (quarterly), and September 1 / March 1 (semi-annual). No legal citation in the spec supports these values.

Recommended resolution: The Architect spec must add a legal citation (Momsloven §57 stk. X or SKAT's published deadline calendar) for each day-of-month value, or the Researcher must add a claim entry (C19+) that explicitly endorses these values.

**GAP 3 | Responsible spec: Architect | `kvitteringsnummer` is platform-generated with no justification**

The receipt number is generated as `f"KVIT-{filing.se_nummer}-{filing.filing_period}-{int(submitted_at.timestamp())}"` (Architect Section 3.5). The Researcher (C12) confirms that SKAT issues a kvittering after submission, but it is unclear whether the platform is intended to generate this locally or receive it from an integration. No spec states this is intentional or explains the format.

Recommended resolution: The Architect spec must add one explicit statement: "In Phase 2, `kvitteringsnummer` is generated locally by the platform as a deterministic reference string. SKAT integration for external receipt numbers is deferred to Phase 3." The format should also be specified as stable so tests can assert on it.

**GAP 4 | Responsible spec: Architect | No endpoint to assign or reassign an officer to an assessment**

The Assessment model has `assessed_by` (the creator). There is no endpoint to change the responsible officer after creation.

Recommended resolution: Either add `PATCH /api/v1/assessments/{id}/assign` with an `AssessmentAssignUpdate` schema, or explicitly defer this and document the deferral in Architect Section 4.

**GAP 5 | Responsible spec: Architect / Designer | Agterskrivelse concept unresolved across specs**

AGENT_ROLES.md (Frontend Coder responsibilities) lists "Agterskrivelse action" as a deliverable. The Designer has removed it from the action-to-API parity matrix. The Architect has no endpoint, no model field, and no service method for agterskrivelse. No spec has explicitly deferred or cancelled this responsibility.

Recommended resolution: The orchestrator must make an explicit product decision: (a) defer agterskrivelse to Phase 3 — update AGENT_ROLES.md to remove it from Frontend Coder scope; or (b) define it in the Architect spec with a field (`agterskrivelse_sent_at`) on `TaxAssessment`, an endpoint (`POST /api/v1/assessments/{id}/agterskrivelse`), and a Designer parity row.

**GAP 6 | Responsible spec: Architect | No error response envelope standardised**

The Architect spec defines HTTP status codes per endpoint but does not define a standardised error response body. The client-side TypeScript type `ApiErrorDetail` (Appendix C) uses `{ detail: string | ValidationError[] }`, which matches FastAPI's default. However, this is never stated as the canonical error format in the spec text.

Recommended resolution: The Architect spec should add one paragraph in Section 8 explicitly stating: "All error responses use FastAPI's default error envelope: `{ detail: string }` for operational errors, or `{ detail: [{ type, loc, msg, input }] }` for validation errors (HTTP 422)."

**GAP 7 | Responsible spec: Architect | No filtering or pagination on list endpoints**

`GET /api/v1/filings`, `GET /api/v1/assessments`, and `GET /api/v1/parties` have no query parameters for filtering (by period, status, party) or pagination (offset/limit). The Researcher (Section 4.3) includes `GET /api/v1/vat-filings?party_id=&period=` as a mandatory endpoint with filtering. The Architect's list routers implement no query parameters at all — they return all filings for the role, producing unbounded result sets in production.

Recommended resolution: The Architect spec must define at minimum: `GET /api/v1/filings?party_id=&period=&status=&limit=&offset=` with the corresponding repository methods.

**GAP 8 | Responsible spec: Architect / Designer | No specification of what happens when a filing is submitted after `frist`**

The Architect's `submit_filing` service method computes `late_days` and `late_penalty` and publishes `FilingPenaltyAccrued`. However, the spec does not state: (a) whether late submission is blocked or only flagged; (b) whether the filing status after late submission is the same `SUBMITTED_WITH_RECEIPT`; (c) whether any additional workflow step is triggered.

Recommended resolution: The Architect spec must add a subsection "Late Submission Behaviour" stating: (a) late filings are accepted (not blocked) in Phase 2; (b) `late_filing_days` and `late_filing_penalty` are set on the filing; (c) `FilingPenaltyAccrued` is published; (d) automatic provisional assessment creation is deferred to Phase 3.

**GAP 9 | Responsible spec: Architect | `GET /api/v1/dashboard/summary` has no implementation spec**

The endpoint appears in the API contract table (Section 8.1) and the Designer references it for the Dashboard page (Section 5b), but the Architect provides no router, service, schema, or repository for it.

Recommended resolution: The Architect spec must define the dashboard summary response schema and the router stub. At minimum: `{ total_parties: int, total_filings: int, pending_assessments: int, late_filings: int }`.

**GAP 10 | Responsible spec: Architect | No `TAXPAYER.party_id` linkage defined**

The authorization policy (Section 2.8) states `filing.party_id == current_user.party_id` as the TAXPAYER ownership predicate. However, the `User` model (Section 2.2) has no `party_id` field. The `FilingService.list_filings` method (Section 3.5) calls `self._repo.list_filings_by_party(current_user.party_id, db)` for TAXPAYER users, but `current_user.party_id` does not exist on the `User` model. This is a code-level bug in the spec that would fail at runtime with `AttributeError`.

Recommended resolution: The `User` model must add an optional `party_id: UUID | None` FK to `parties.id`. A migration for this field must be added.

---

## Section 5 — Missing From All Specs

**MISSING 1: Bank holiday calendar**
The Architect delegates bank-day adjustment to `VatPolicyRepository.get_next_open_bank_day`, which must check against a bank holiday calendar. No spec defines who populates this calendar, what source it comes from (Denmark's official holiday list), what table it lives in, or how it is seeded. This is a runtime dependency without a definition.

**MISSING 2: Zero-filing confirmation behavior**
The Researcher (C04, Section 2.3) mandates that zero filings must be accepted and must create a receipt state. The Architect's submit flow correctly handles this (momstilsvar=0.00 → outcome `NIL`). However, no spec defines whether the UI should show a specific confirmation message for zero filings distinct from the standard receipt display. The Designer does not address this case.

**MISSING 3: CVR number validation (modulus-11)**
AGENT_ROLES.md (Researcher responsibilities) explicitly states: "Research Danish business registration: CVR number format and validation (8-digit, modulus-11)." No spec specifies that CVR must pass a modulus-11 check. The Architect enforces only string length. The Designer does not mention CVR field validation behaviour.

**MISSING 4: SE number validation rules**
No spec defines what constitutes a valid SE number beyond "8 digits" (Researcher Section 4.1). The Architect enforces `min_length=8, max_length=8` on `se_nummer`. No modulus check or format rule is specified.

**MISSING 5: Session/token invalidation on user deactivation**
The `User` model has `is_active: bool`. The auth dependency checks `User.is_active == True` on every request. However, if an admin deactivates a user mid-session, the access token (valid for 15 minutes) will continue to work until expiry. No spec addresses this gap or documents it as an accepted limitation.

**MISSING 6: Audit log for admin reads/writes**
The Researcher (Section 4.2) mandates: "admin roles require explicit audit logging for read/write access." The Architect has no audit log table, no audit log model, no middleware for admin audit logging, and no spec section addressing this. The requirement is stated but never implemented or deferred.

**MISSING 7: `vat_registration_active` on Party**
The Researcher (Section 4.1) mandates `vat_registration_active: bool` on the Party model. The existing `app/models/party.py` uses `PartyState` rows to represent state (EAV pattern). No spec defines how to derive or store this boolean, or whether it should be added as a first-class column. The Architect has not addressed Party model modifications at all.

**MISSING 8: Correction time-window enforcement (3-year rule)**
The Researcher (C09, C10) mandates: corrections within 3 years use ordinary path; beyond 3 years require documented exceptional grounds. The Architect's `correct_filing` service method (Section 3.5) applies no time-window check whatsoever — it allows corrections for any filing regardless of age. The Researcher marked this as "Recommended now" (Section 3), but no spec implements or explicitly defers the 3-year window check.

**MISSING 9: NemKonto refund notification**
The Researcher (C14) states: "amount appears on skattekonto and is normally paid to NemKonto within 21 days after filing." When `submission_outcome = REFUNDABLE`, no spec defines any integration, notification, or audit trail for this refund obligation. There is no `FilingRefundPending` event to match the `FilingPenaltyAccrued` event on the penalty side.

**MISSING 10: Dual-endpoint proliferation — `vat_router` alias rationale**
The Architect registers both `/api/v1/filings*` and `/api/v1/vat-filings*` as equivalent endpoints. No spec explains why both prefixes are needed, who uses which, and whether the `vat_router` alias will be kept permanently or is a transitional compatibility shim. This doubles the number of registered routes and will cause confusion in testing and documentation.

---

## Section 6 — Section Verdicts

| Spec | Section | Verdict | Notes |
|---|---|---|---|
| Researcher | Section 1 (Claim-Level Evidence) | PASS | Claims are well-sourced with legal citations and confidence levels. |
| Researcher | Section 2 (SKAT UX Benchmark) | PASS | Flow, states, and field model are accurate and useful for implementors. |
| Researcher | Section 3 (MVP Legal Baseline) | PASS | Required/Recommended/Defer buckets are clear and actionable. |
| Researcher | Section 4.1 (Architect Unblock Package — fields) | FLAG | Field names diverge from Architect's implementation without mutual acknowledgment. |
| Researcher | Section 4.2 (Validation/Policy Rules) | FLAG | Correction 3-year rule is "Recommended now" but not implemented by any spec. |
| Researcher | Section 4.3 (Endpoint Constraints) | PASS | Endpoints are correctly specified; Architect has implemented them all. |
| Researcher | Section 5 (Decision Defense) | PASS | Decisions are well-reasoned. |
| Researcher | Section 6 (Uncertainty) | PASS | Correctly scoped what is and isn't publicly verifiable. |
| Architect | Section 1 (Frontend Architecture) | PASS | Next.js setup is complete and internally coherent. |
| Architect | Section 2 (Authentication) | FLAG | Missing `party_id` on `User` model (Finding 10 / GAP 10). |
| Architect | Section 3.1.1 (State Transition SSOT) | PASS | State machine is coherent. Assessment decoupling from filing is correctly enforced. |
| Architect | Section 3.2 (Filing Model) | BLOCKER | UniqueConstraint is wrong (Finding 1). |
| Architect | Section 3.5 (FilingService) | FLAG | VatPolicyRepository undefined (GAP 1), deadline dates uncited (GAP 2), kvitteringsnummer format undocumented (GAP 3). |
| Architect | Section 4.2 (Assessment Model) | FLAG | Missing `agterskrivelse_sent_at`, `klage_frist`, `assigned_officer_id` (Findings 6, 7). |
| Architect | Section 4.5 (AssessmentService) | PASS | Status transitions and appeal deadline enforcement are correct. |
| Architect | Section 5 (main.py wiring) | PASS | Wiring is complete and follows existing patterns. |
| Architect | Section 6 (Migrations) | FLAG | VatPolicy table and bank holiday table are missing from the migration plan. |
| Architect | Section 8.1 (API Contract) | FLAG | No pagination or filtering query parameters. `dashboard/summary` unimplemented (GAP 9). |
| Architect | Section 8.2 (Deadline/Penalty Contract) | FLAG | Late submission behaviour not fully specified (GAP 8). |
| Designer | Section 3.2 (StatusChip) | FLAG | `CORRECTION_PENDING` appears in StatusChip but not in Architect status values (Finding 10). |
| Designer | Section 4 (4C Filing Enforcement) | PASS | Rubrik fields correctly named and mapped to Architect schema. |
| Designer | Section 5h (Create Filing) | PASS | Rubrik A-E fields explicitly listed; workflow mirrors SKAT benchmark. |
| Designer | Section 7 (User Flows) | PASS | Flows are coherent and every step maps to a defined API endpoint. |
| Designer | Section 8 (Action-to-API Parity Matrix) | FLAG | References `GET /api/v1/dashboard/summary` which has no implementation in Architect. |
| Designer | Section 9 (Data Contract) | PASS | All Designer field names match Architect schema field names. |
| Designer | Section 11.2 (Filing/Assessment SSOT) | PASS | State rules correctly reproduced; no implicit filing mutation from assessment actions. |
| Designer | Section 13.2 (Explicit Deviations) | PASS | English-first UI, internal auth, and admin pages are all documented as intentional deviations. |

---

## Section 7 — Required Actions Before Phase 2

Listed in priority order. Items 1–5 are blocking; items 6–7 are conditional.

**ACTION 1 — Fix the Filing UniqueConstraint (BLOCKER)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 3.2 and Migration 0003.
Change `UniqueConstraint("se_nummer", "filing_period", "angivelse_type", "version", ...)` to a partial unique index `WHERE korrektionsangivelse = false` on `(se_nummer, filing_period, angivelse_type)`. Update the migration accordingly. The application-level duplicate check in `FilingService.create_filing` should remain but must be made race-condition safe (e.g. by catching `IntegrityError` rather than relying on a prior SELECT).

**ACTION 2 — Add `party_id` FK to the User model (BLOCKER)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 2.2.
Add `party_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parties.id", ondelete="SET NULL"), nullable=True)` to the `User` model. Add migration column. Update the `UserCreate` schema to accept an optional `party_id`. Without this, the TAXPAYER authorization predicate `filing.party_id == current_user.party_id` references a field that does not exist on `User`, causing a runtime `AttributeError`.

**ACTION 3 — Define `VatPolicyRepository` and `VatPolicy` model (BLOCKER)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 3.5 and Appendix A.
Add a `VatPolicy` SQLAlchemy model with fields: `id (UUID PK)`, `effective_from (Date)`, `late_filing_fee_amount (Numeric)`, `late_interest_base_rate (Numeric)`, `late_interest_margin (Numeric)`. Add the table to the migration plan. Define the full `VatPolicyRepository` class with `get_active_policy(as_of: date, db: Session) -> VatPolicy` and `get_next_open_bank_day(candidate: date, db: Session) -> date`. Add a seeding strategy or note that initial policy values must be populated before Phase 2 tests run.

**ACTION 4 — Define `GET /api/v1/dashboard/summary` response schema and router stub (BLOCKER)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 8.1 / AGENT_DESIGN_SPEC.md, Section 5b.
Add a `DashboardSummaryRead` Pydantic schema with at minimum: `total_parties: int`, `total_filings: int`, `pending_assessments: int`, `late_filings: int`. Add a router stub and a service/repository query method. Without this, the Designer's Dashboard page has no backing endpoint.

**ACTION 5 — Resolve agterskrivelse scope (BLOCKER for AGENT_ROLES.md alignment)**
Spec: AGENT_ROLES.md (Frontend Coder responsibilities) / AGENT_DESIGN_SPEC.md / AGENT_ARCHITECT_SPEC.md.
The orchestrator must make an explicit decision: (a) defer agterskrivelse to Phase 3 — update AGENT_ROLES.md to remove it from Frontend Coder scope and explicitly note the deferral; or (b) define it in the Architect spec with a field (`agterskrivelse_sent_at` on `TaxAssessment`), an endpoint (`POST /api/v1/assessments/{id}/agterskrivelse`), and a Designer parity row. Leaving AGENT_ROLES.md out of sync with the Architect and Designer specs will cause the Frontend Coder to either implement something undefined or miss a required deliverable.

**ACTION 6 — Add legal citations for deadline day-of-month values (CONDITIONAL — required before legal sign-off)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 3.5 (`_compute_deadline`).
Add a comment or spec paragraph citing the legal basis: "Monthly deadline is the 25th of the following month per [Momsloven §57 stk. X / SKAT calendar]. Quarterly deadline is the 10th of the second month after quarter-end per [cite]. Semi-annual: H1 is September 1, H2 is March 1 per [cite]." If the Researcher cannot verify these dates from already-cited sources, add new claim entries (C19–C21) and confirm with high confidence.

**ACTION 7 — Add filtering and pagination to list endpoints (CONDITIONAL — required before performance sign-off)**
Spec: AGENT_ARCHITECT_SPEC.md, Section 3.7, Section 4.7.
Add query parameters `party_id`, `period`, `status`, `limit` (default 50, max 200), `offset` (default 0) to `GET /api/v1/filings` and `GET /api/v1/assessments`. Update the repository methods accordingly. Update the Designer's Filings List and Assessments List page specs to reference these filter parameters. Without this, production list endpoints will return unbounded result sets.
