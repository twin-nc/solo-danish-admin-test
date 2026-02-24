# AGENT_REVIEWER_SPEC.md - Phase 1 Quality Gate Review

**Date:** 2026-02-24  
**Reviewer:** Reviewer Agent  
**Inputs reviewed:** `AGENT_ARCHITECT_SPEC.md`, `AGENT_DESIGN_SPEC.md`, `AGENT_RESEARCHER_SPEC.md`  
**Gate mode:** Strict Blocking

## Product Owner Direction (2026-02-24)

The following product decisions are now fixed unless explicitly changed by the product owner:

1. High legal accuracy first.
2. UI language mostly English.
3. Admin pages are in scope now.
4. VAT filing model is `4C` (hybrid phased):
   - Phase 2 canonical filing uses fixed official VAT fields.
   - Optional line-item detail can be added later as a convenience layer.
5. Strict access control now (taxpayer data isolation).
6. Deadlines and penalties enforced now.
7. Correctness over speed when tradeoffs occur.
8. Assessment actions must **not** implicitly mutate filing status.
   - Filing and assessment state machines are decoupled by policy.
   - Any filing status change must occur through explicit filing endpoints only.
9. Filing status `UNDER_REVIEW` is **reserved/deferred** in Phase 2.
   - Keep it as a forward-compatible status label/type only.
   - Do not include it in active Phase 2 transition paths.

New mandatory direction:
- Researcher must benchmark the **current SKAT VAT filing style in TastSelv Erhverv** and provide a replication brief (flow, field structure, controls, states, and terminology), based on official sources.

## Executive Summary

**Overall verdict: BLOCKED (Phase 2 must not start yet).**

The three Phase 1 specs are substantial and useful, but they are not yet decision-coherent as a set. The largest blockers are:

1. The Filing domain model is inconsistent across specs (generic line-item model vs Danish VAT Rubrik model).
2. The Designer flows require endpoints and backend behavior not fully defined in the Architect API contract.
3. Several high-risk domain claims in Researcher output are not anchored to explicit source links/effective dates in the document itself.

## Reviewer Quality Bar (Non-Negotiable)

1. **Decision completeness:** Updated specs must not leave hidden implementation choices to coders.
2. **Legal traceability:** Every behavior-driving legal claim must have an explicit source anchor and effective date.
3. **Interoperability:** Every UI action must map to one defined API contract entry and role rule.
4. **Testability:** Every major rule must be written in a way that can be tested with deterministic pass/fail criteria.
5. **Scope discipline:** Features outside Phase 2 scope must be explicitly marked deferred with rationale.

## Decision Interrogation Matrix (Agents Must Justify)

| Decision Area | Owner(s) | Required Justification |
|---|---|---|
| Filing schema (`line_items` vs Rubrik fields) | Architect + Researcher | Why selected model best fits Danish VAT filing obligations in this phase; why rejected alternatives are inferior. |
| Status terminology policy (Danish vs English vs dual mapping) | Architect + Designer + Researcher | Persistence-language decision, UI display policy, and migration impact. |
| Admin page scope (`/admin/users`, `/admin/settings`) | Architect + Designer | In-scope or deferred, with API readiness and dependency analysis. |
| Filing status transitions on assessment events | Architect + Designer | Single canonical state machine and side-effect ownership. |
| Filing status set scope (`UNDER_REVIEW`) | Architect + Designer | Keep status declared but reserved/deferred in Phase 2 unless explicit transition contract is added. |
| Authorization and ownership rules | Architect | Row-level access policy by role and threat/risk rationale. |

## Cross-Spec Coherence Findings

### Blockers

1. **Filing model mismatch (core domain conflict)**  
   - Architect defines `FilingLineItem` and generic `filing_type` (`VAT`, `INCOME_TAX`): `AGENT_ARCHITECT_SPEC.md:706`, `:716`, `:733`, `:1765`  
   - Designer filing flow is line-item based: `AGENT_DESIGN_SPEC.md:575`, `:589`  
   - Researcher explicitly flags this as fundamentally wrong for Danish momsangivelse and proposes fixed Rubrik fields: `AGENT_RESEARCHER_SPEC.md:315`, `:317`, `:391`

2. **UI/API contract mismatch for navigation and list workflows**  
   - Designer defines admin pages and navigation (`/admin/users`, `/admin/settings`): `AGENT_DESIGN_SPEC.md:530`, `:531`, `:605`  
   - Architect API contract summary does not define endpoints for these pages: `AGENT_ARCHITECT_SPEC.md:1668-1688`

3. **Workflow mismatch on assessment side effects**  
   - Product policy now fixed: no implicit filing mutation from assessment actions.  
   - Architect and Designer must reflect this exact rule consistently.

### Flags

1. **Status and terminology drift**  
   - Designer uses mostly English status chips (`SUBMITTED`, `ACCEPTED`): `AGENT_DESIGN_SPEC.md:206`, `:208`, `:581`  
   - Researcher recommends Danish-aligned terms and `angivelse_type` naming: `AGENT_RESEARCHER_SPEC.md:372-377`

2. **Identifier model drift**  
   - Existing design/flows continue using `TIN` and `BUSINSSDM1`: `AGENT_DESIGN_SPEC.md:559`, `:563`  
   - Researcher recommends first-class CVR/SE concepts and Danish role codes: `AGENT_RESEARCHER_SPEC.md:339`, `:392`, `:420`

## Domain Accuracy Findings

### Blockers

1. **Missing citation precision for high-impact legal claims**  
   Researcher document has a source list, but claims that drive system behavior (deadline calculations, penalties, reassessment windows, and rates) are not line-level linked to specific legal text versions/effective dates.  
   - Evidence sections: `AGENT_RESEARCHER_SPEC.md:55-80`, `:493`

### Flags

1. **Scope coupling risk in legal recommendations**  
   Researcher includes strong recommendations that materially expand phase scope (beyond minimal Filing MVP) and need explicit prioritization into "required now" vs "later".  
   - Evidence: `AGENT_RESEARCHER_SPEC.md:387-426`

## Decision Justification Findings

### Blockers

1. **Architect does not justify why Filing includes mixed tax-return abstraction in this phase**  
   - `filing_type` includes `INCOME_TAX` while phase intent is VAT-first: `AGENT_ARCHITECT_SPEC.md:733`, `:1765`

2. **Role-based access model lacks explicit ownership rules for "Any" read paths**  
   - API summary grants many endpoints to `Any` role without data-scoping specification: `AGENT_ARCHITECT_SPEC.md:1676-1688`

### Flags

1. **Assessment date modeled as string without rationale**  
   - `assessment_date: Mapped[str]`: `AGENT_ARCHITECT_SPEC.md:1063`

## Gap Analysis

1. **Owner selected `4C`, but the decision is not yet reflected consistently in all specs.**
2. **No explicit mapping from UI pages to concrete API endpoints for admin module pages.**
3. **No explicit, testable ownership rules per role for sensitive resources (especially taxpayer access).**
4. **No resolved terminology policy (Danish-first vs English-first with mapping).**

## Section Verdicts

### AGENT_ARCHITECT_SPEC.md

| Section | Verdict | Notes |
|---|---|---|
| 1. Frontend Architecture | Flag | Reasonable structure; needs API/page parity check with Designer. |
| 2. Authentication System | Flag | Needs explicit ownership/authorization rules by resource. |
| 3. Tax Filing Module | Reject | Core model conflicts with Researcher legal model. |
| 4. Tax Assessment Module | Flag | Type/transition concerns and side-effect ambiguity. |
| 5. app/main.py wiring | Pass | Internally coherent as wiring blueprint. |
| 6. Alembic Plan | Flag | Depends on unresolved Filing canonical model. |
| 7. Event Flow | Flag | Depends on unresolved status transitions and Filing model. |
| 8. API Contract Summary | Reject | Missing endpoints/behavior required by Designer flows. |

### AGENT_DESIGN_SPEC.md

| Section | Verdict | Notes |
|---|---|---|
| 1-3 Principles/Tokens/Components | Pass | Strong and implementable visual system. |
| 4 Page layouts | Flag | Filing/assessment screens assume unresolved data model semantics. |
| 5 Navigation | Reject | Includes admin pages not mapped to Architect API/backend scope. |
| 6 User flows | Reject | Contains backend side effects not specified by Architect. |
| 7 Responsive behavior | Pass | Clear and usable. |
| 8 File structure | Flag | Includes app areas lacking API contract backing. |

### AGENT_RESEARCHER_SPEC.md

| Section | Verdict | Notes |
|---|---|---|
| 1-5 Legal/process/field model | Flag | High value, but needs claim-level source precision. |
| 6 Architecture review | Pass | Useful and specific to Architect draft. |
| 7 Gap analysis | Pass | Actionable gap framing. |
| 8 Recommendations | Flag | Needs explicit "must now" vs "future" slicing. |
| 9 Proposed model | Flag | Candidate design, but must be reconciled with Architect ownership. |
| 10 Sources | Flag | Needs direct source linkage to high-risk claims. |

## Required Actions Before Phase 2

### Must resolve (blocking)

1. **Canonical Filing schema decision**
   - Owner: Architect + Researcher
   - Output: Updated Architect Filing model, API schemas, migration plan, and event payloads.
   - Acceptance: No remaining conflict with Researcher "mandatory VAT fields" set.

2. **UI/API parity resolution**
   - Owner: Architect + Designer
   - Output: Endpoint matrix mapping each designed screen/action to defined API contract entries.
   - Acceptance: Every page action in Designer spec has an Architect endpoint and role rule.

3. **Assessment side-effect contract**
   - Owner: Architect + Designer
   - Output: Explicit rule for filing status transitions on assessment creation/update.
   - Acceptance: One shared state-transition table used by both specs.

4. **Legal claim traceability**
   - Owner: Researcher
   - Output: Add source anchors (law section/site page + effective date) for each behavior-driving claim.
   - Acceptance: Deadlines, penalties, correction windows, and thresholds each have explicit references.

5. **Decision defense package**
   - Owner: Architect + Designer + Researcher
   - Output: Short justification appendix per agent for challenged decisions.
   - Acceptance: Each challenged decision includes selected option, rejected options, tradeoffs, risk impact, and why the final choice is preferred.

6. **SKAT VAT UX replication brief**
   - Owner: Researcher (input to Architect + Designer)
   - Output: A source-backed brief describing current SKAT VAT filing flow/style in TastSelv Erhverv:
     - Navigation flow and step sequence
     - Filing field groups and required-field behavior
     - Validation/help interactions
     - Draft/save/confirm/receipt/correction states
     - Terminology and label conventions
   - Acceptance: Architect and Designer each reference this brief in their revised specs and explain any intentional deviations.

### Re-review checklist

1. No "Reject" verdicts remain in Section Verdicts tables.
2. All blockers in this document moved to closed with evidence lines.
3. Updated Architect and Designer specs are mutually testable without new decisions.
4. Each challenged decision includes explicit alternatives considered and rationale for rejection.
5. No unresolved ownership ambiguity remains for API auth or workflow side effects.

## Coordination Attachments

The following targeted review documents are issued together with this gate:

- `AGENT_REVIEW_ARCHITECT.md`
- `AGENT_REVIEW_DESIGNER.md`
- `AGENT_REVIEW_RESEARCHER.md`
