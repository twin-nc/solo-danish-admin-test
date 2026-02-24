# AGENT_REVIEW_DESIGNER.md - Targeted Review for Designer Agent

## Purpose

This document isolates Designer-owned corrections to ensure the UI/UX spec stays consistent with the architecture and legal model.

## Findings (ordered by severity)

### Blockers

1. **Filing UI assumes line-item model without resolved backend agreement**
   - UI and flow use line-items and "Momslinjer": `AGENT_DESIGN_SPEC.md:451`, `:469`, `:575`, `:589`
   - Reviewer gate requires canonical Filing model decision first.

2. **Navigation includes admin pages without confirmed API/feature scope**
   - `/admin/users`, `/admin/settings`: `AGENT_DESIGN_SPEC.md:530-531`, `:605`
   - Architect API contract currently does not define these flows/endpoints.

3. **Flow must align to fixed side-effect policy**
   - Product owner decision: assessment actions do not implicitly change filing state.
   - Designer flows must show filing changes only through filing endpoints.

### High

1. **Terminology consistency not finalized**
   - Status chips and flows use mostly English statuses (`SUBMITTED`, `ACCEPTED`): `AGENT_DESIGN_SPEC.md:206`, `:208`, `:581`
   - Researcher recommends Danish-aligned terms for legal context: `AGENT_RESEARCHER_SPEC.md:372-377`

2. **Registration labels still tied to current prototype codes**
   - `TIN`, `BUSINSSDM1`: `AGENT_DESIGN_SPEC.md:559`, `:563`
   - Researcher proposes CVR/SE and Danish role labels.

### Medium

1. **Design reference claims should include explicit evidence links**
   - Spec says it is cross-referenced with SKAT/DDS patterns but does not list concrete references.

## Designer Questions (must answer in spec update)

1. If Filing becomes Rubrik-field based, what exact UI structure replaces line-item entry?
2. Should admin pages remain in Phase 2 scope, or move to a later phase?
3. Do we standardize on Danish or English status labels in UI (or dual-label mapping)?
4. Which labels are fixed domain terms from law/process versus user-friendly display terms?

## Decision Challenges (justify or revise)

1. **Why is line-item entry the right UI for Danish VAT filing?**  
   If retained, demonstrate exact mapping to mandatory reporting fields and legal form semantics.
2. **Why are admin pages included now?**  
   Provide dependency and value argument, or explicitly defer with a UX placeholder strategy.
3. **Why does the flow imply filing mutation from assessment actions?**  
   Product policy is now fixed to no implicit mutation; narrative must match this.
4. **Why choose English status labels in key operator workflows?**  
   Justify language choice against legal/audit context and user expectations.

## Suggested Alternatives to Evaluate

1. Rubrik-first filing form with fixed fields and computed summary card (`momstilsvar`) rather than free line items.
2. Phase-gated nav: hide deferred admin routes behind feature flags and "Not in scope" stubs.
3. Dual-label strategy: canonical backend values + localized display labels.
4. Explicit screen contract table: each action includes endpoint, role, status preconditions, and expected failure states.

## Required Designer Changes

1. Apply product-owner decision `4C` as a hard constraint:
   - Phase 2 filing form must use fixed official VAT fields as the primary interaction.
   - Any line-item UI is optional later and must not replace official fields.
2. Add an explicit "Data Contract Alignment" table mapping each page component field to Architect schema fields.
3. Mark all screens/actions as `In Scope Phase 2` or `Deferred` based on resolved Architect contract.
4. Replace implied backend behavior statements with references to Architect-defined state rules.
   - Explicitly enforce no implicit filing mutation from assessment endpoints.
   - Treat `UNDER_REVIEW` as reserved/deferred in Phase 2 (label may exist, but no active transition usage).
5. Add a terminology map section (`domain value` -> `display label`) agreed with Architect/Researcher.
6. Consume the Researcher "SKAT VAT Filing UX Benchmark" and align filing UX patterns:
   - Step order
   - Field grouping and required markers
   - Validation/help cues
   - Confirmation/receipt/correction experience
   Document any intentional deviation and rationale.

## Acceptance Criteria

1. No designed action exists without a mapped API endpoint.
2. Filing page design matches the final canonical Filing schema exactly.
3. Status labels and workflow semantics are consistent with Architect and Researcher outputs.
4. No unresolved blocker from `AGENT_REVIEWER_SPEC.md` references the Designer spec.
5. Each challenged decision includes alternatives reviewed and a reasoned final selection.
6. Filing UX demonstrably mirrors SKAT interaction style at workflow level, with deviations explicitly justified.
