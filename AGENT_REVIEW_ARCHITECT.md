# AGENT_REVIEW_ARCHITECT.md - Targeted Review for Architect Agent

## Purpose

This document isolates Architect-owned issues from Reviewer findings so updates can be made with minimal ambiguity.

## Findings (ordered by severity)

### Blockers

1. **Filing model conflicts with Danish VAT domain constraints**
   - Current model uses `FilingLineItem` and generic `filing_type`: `AGENT_ARCHITECT_SPEC.md:706`, `:716`, `:733`
   - This conflicts with Researcher mandatory Rubrik-field recommendation: `AGENT_RESEARCHER_SPEC.md:315`, `:317`, `:391`

2. **API contract does not cover all designed app areas**
   - Contract summary lacks admin-specific API coverage despite designed admin pages: `AGENT_ARCHITECT_SPEC.md:1668-1688` vs `AGENT_DESIGN_SPEC.md:530-531`

3. **Assessment/filing side effects must match fixed policy**
   - Product owner decision: assessment actions must not implicitly mutate filing state.
   - Architect contract must enforce decoupled state machines.

### High

1. **Assessment date type is string**
   - `assessment_date: Mapped[str]`: `AGENT_ARCHITECT_SPEC.md:1063`
   - Requires explicit rationale or change to proper date type.

2. **Authorization model lacks ownership policy**
   - Many read endpoints allow `Any` role: `AGENT_ARCHITECT_SPEC.md:1676-1688`
   - No explicit policy for "taxpayer can only read own resources."

### Medium

1. **Terminology divergence risk**
   - Uses `VAT`/`INCOME_TAX`: `AGENT_ARCHITECT_SPEC.md:733`, `:1765`
   - Researcher recommends Danish-aligned naming: `AGENT_RESEARCHER_SPEC.md:376-377`

## Architect Questions (must answer in spec update)

1. Is Filing in Phase 2 strictly VAT-first, or multi-tax from day one?
2. What is the canonical Filing payload shape for VAT (fixed fields vs line-items), and why?
3. Do we support `/admin/users` and `/admin/settings` in this phase? If yes, which endpoints are required?
4. What are explicit row-level access rules per role for parties, filings, and assessments?

## Decision Challenges (justify or revise)

1. **Why is a multi-tax Filing abstraction (`VAT`, `INCOME_TAX`) appropriate now?**  
   If this is future-proofing, justify why the extra complexity does not increase phase risk.
2. **Why should VAT filing use generic line items instead of fixed Rubrik fields?**  
   If retained, explain how legal reporting fields are guaranteed without ambiguity.
3. **Why should `assessment_date` remain string-based?**  
   Provide concrete operational benefits over typed date handling, or change it.
4. **Why are `Any` role reads safe on sensitive resources?**  
   Provide a threat model and mitigation strategy, not only role labels.

## Suggested Alternatives to Evaluate

1. VAT-first canonical model in Phase 2, with explicit extension hooks for non-VAT return types later.
2. Dual representation approach: fixed Rubrik fields persisted, optional computed display rows in UI only.
3. Typed date/time fields everywhere with serialization handled at schema boundary.
4. Explicit policy table: endpoint -> role -> ownership predicate -> failure mode.

## Required Architect Changes

1. Apply product-owner decision `4C` as a hard constraint:
   - Canonical VAT filing persistence and API contract must be fixed official fields.
   - Any line-item support in Phase 2 must be non-canonical and must not replace required VAT fields.
2. Publish a reconciled Filing model section aligned with Researcher must-have legal fields or document a justified alternative and scope deferral.
3. Update API contract summary with a complete page-to-endpoint mapping (including admin scope decisions).
4. Add explicit role + ownership rules to each endpoint.
5. Resolve assessment date typing and state-transition rules, enforcing:
   - no implicit filing mutation from assessment endpoints.
   - filing transitions only via filing endpoints.
6. Update event payload definitions if Filing schema changes.
7. Consume the Researcher "SKAT VAT Filing UX Benchmark" and reflect it in:
   - Filing endpoint flow
   - Submission/correction states
   - Required-field and validation behavior exposed by API
   Include explicit notes for any intentional deviation from SKAT flow.

## Acceptance Criteria

1. No unresolved contradiction with `AGENT_RESEARCHER_SPEC.md` on VAT filing minimum fields.
2. Every action in `AGENT_DESIGN_SPEC.md` has a corresponding endpoint and auth rule.
3. State transitions are defined once and reused across filing/assessment sections.
4. Reviewer can trace all changes directly in updated section text with no extra assumptions.
5. Each challenged decision includes final choice, alternatives considered, and rejection rationale.
6. Updated filing workflow contract is demonstrably compatible with the SKAT benchmark or has documented, justified deviations.
