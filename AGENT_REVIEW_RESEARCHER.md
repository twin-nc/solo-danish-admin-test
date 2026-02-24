# AGENT_REVIEW_RESEARCHER.md - Targeted Review for Researcher Agent

## Purpose

This document isolates Researcher-owned updates needed to make legal/domain guidance auditable and implementation-ready.

## New Directive From Product Owner

Research the **current SKAT VAT filing style** in TastSelv Erhverv and produce a replication brief for Architect and Designer.
Product-owner filing decision is `4C`:
- Phase 2 canonical model uses fixed official VAT fields.
- Optional line-item convenience detail can be considered later and must not replace official fields.

Minimum expected output (new section or companion file):

1. Current end-to-end filing journey as shown in official SKAT guidance.
2. Screen/step structure (what users see in sequence).
3. Field model and interaction style (fixed fields vs line-items, required marks, helpers, confirmations).
4. Validation and error behavior (where visible in official guidance).
5. Submission outcomes (receipt/confirmation and post-submission actions).
6. Clear notes on what is known from public sources vs what is not visible without login.

Use official primary sources only (e.g., skat.dk business pages, SKAT official guidance/video pages).
If direct interface details are partially inaccessible, mark uncertainty explicitly and avoid guesswork.

## Findings (ordered by severity)

### Blockers

1. **High-impact legal claims need claim-level traceability**
   - Deadlines, penalties, correction windows, and related rules are stated, but implementation-critical claims are not directly tied to specific source sections/effective dates in-line.
   - A source list exists: `AGENT_RESEARCHER_SPEC.md:493`, but not enough for deterministic implementation.

### High

1. **Need explicit "must now" vs "future" split**
   - Recommendations include both critical legal constraints and broader platform enhancements: `AGENT_RESEARCHER_SPEC.md:387-426`
   - Architect cannot implement safely without a strict MVP legal baseline.

2. **Some recommendations assume scope expansion decisions**
   - Example: terminology and multi-return types (`MOMS`, `SELSKABSSKAT`, `LONSUMSAFGIFT`) require product and architecture scope confirmation.

### Medium

1. **Cross-spec reconciliation notes should be stronger**
   - Gap analysis is strong, but include explicit "minimum change set to unblock phase" for Architect.

## Researcher Questions (must answer in spec update)

1. Which legal rules are mandatory for a VAT-first MVP, and which are best-practice enhancements?
2. For each behavior-driving rule, what exact legal/source reference and version date applies?
3. Which Danish terms must be persisted in database values vs only shown as UI labels?
4. Are any listed penalties/rates policy-variable and therefore should be configurable instead of hardcoded?

## Decision Challenges (justify or revise)

1. **Why should each recommended field/rule be implemented now vs deferred?**  
   Provide minimal legal sufficiency boundary for Phase 2.
2. **Why are the cited legal interpretations implementation-safe as written?**  
   For each critical claim, show specific legal reference and effective period.
3. **Why should terminology changes be applied at persistence level instead of presentation level?**  
   Explain migration and backward-compatibility impact.
4. **Why should penalties/interest be hardcoded if rates or policy can change?**  
   Recommend configurability boundaries where needed.

## Suggested Alternatives to Evaluate

1. Two-tier output:
   - `Legal minimum required now`
   - `Best-practice enhancements later`
2. Confidence grading on each claim (`high`, `medium`, `low`) with rationale.
3. Rule source map maintained as a machine-readable table that can drive tests/docs.
4. Policy configurability guidance: which values are constants, which should be configurable.

## Required Researcher Changes

1. Add an evidence appendix with claim IDs:
   - `Claim ID`
   - `Rule statement`
   - `Source URL/title`
   - `Legal section/article`
   - `Effective date`
   - `Confidence`
2. Add a strict MVP legal baseline table for Architect:
   - `Required now`
   - `Recommended now`
   - `Defer`
3. Provide a compact "Architect unblock package" listing only mandatory model fields, validations, and endpoint constraints for Phase 2.
4. Add a "SKAT VAT Filing UX Benchmark" section with citations and explicit design implications for:
   - `AGENT_ARCHITECT_SPEC.md`
   - `AGENT_DESIGN_SPEC.md`
5. Provide a replication policy note: replicate workflow and interaction patterns, but do not require copying SKAT protected assets/branding elements verbatim.

## Acceptance Criteria

1. Every blocking legal claim is independently verifiable from in-doc references.
2. Architect can implement VAT Filing MVP without making legal-policy guesses.
3. Recommendation priorities are unambiguous and phase-aligned.
4. No blocker in `AGENT_REVIEWER_SPEC.md` remains attributable to missing Researcher precision.
5. Each challenged decision includes selected approach and rejected alternatives with tradeoff rationale.
6. SKAT VAT UX benchmark is concrete enough that Designer can reproduce interaction patterns without inventing undocumented behavior.
