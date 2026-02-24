# Danish Tax Administration Platform — Researcher Agent Report

**Document:** AGENT_RESEARCHER_SPEC.md
**Date:** 2026-02-24
**Author:** Researcher Agent
**Status:** Phase 1 deliverable — input to all Coder agents

---

## Executive Summary

This report provides a comprehensive research foundation for building a Danish Tax Administration Platform that authentically models Danish VAT (moms) administration. It covers the legal framework of Danish VAT law (momslov), Danish business registration procedures (CVR/SE numbers, Erhvervsstyrelsen), SKAT's digital systems including TastSelv Erhverv, the end-to-end procedural flow from business formation to VAT payment, and the specific data fields required in a Danish momsangivelse (VAT return).

Following the research, a gap analysis of `AGENT_ARCHITECT_SPEC.md` identifies significant structural deficiencies: the Filing module's data model does not capture any of the mandatory Rubrik A–E fields from a real momsangivelse; the Party/Registration module lacks CVR number, SE number, and VAT registration date fields; filing period validation does not enforce Danish deadline rules; and the generic `filing_type = "VAT"` terminology does not map to Danish tax concepts such as momsangivelse, aconto, or afregningsperiode.

The recommendations section provides specific, actionable changes to data models, API contracts, and business logic, prioritised by impact.

---

## 1. Danish VAT (Moms) Legal Framework

### 1.1 Statutory Basis

Danish VAT is governed by **Momsloven** (Lovbekendtgørelse nr. 1021 af 26. september 2019, as amended). The administering authority is **Skattestyrelsen** (commonly referred to as SKAT, a part of the umbrella organisation Skatteforvaltningen). The law implements EU Council Directive 2006/112/EC on the common system of VAT.

### 1.2 VAT Rates

| Category | Rate | Danish Term | Examples |
|---|---|---|---|
| Standard rate | **25%** | Normalsatsen | Most goods and services |
| Zero-rated | **0%** | Nulsats | Newspapers (dagblade), EU exports |
| Exempt (no VAT charged, no input VAT recovery) | **0%** | Momsfritaget | Medical services, insurance, financial services, passenger transport, education |

Denmark has no reduced rate unlike many EU member states. The only practical distinction is 25% versus 0%/exempt. The system does not need a multi-rate VAT calculation engine for domestic sales, but must handle zero-rated exports and EU intra-community supplies.

### 1.3 VAT Registration Threshold

- **Threshold:** DKK 50,000 annual turnover (omsætning) from taxable supplies
- Any business whose taxable turnover exceeds or is expected to exceed DKK 50,000 in a 12-month period **must** register for VAT before commencing taxable activity (Momsloven § 47)
- Voluntary registration is possible for businesses below the threshold (e.g. to recover input VAT on startup costs)
- Non-resident businesses supplying digital services to Danish consumers must register (no threshold for B2C digital services under the EU OSS regime)

### 1.4 Filing Periods (Afregningsperiode)

SKAT assigns a filing frequency based on the previous year's VAT-liable turnover:

| Period | Danish Term | Turnover Trigger | Filing Period |
|---|---|---|---|
| Monthly | Månedlig | Turnover > DKK 50 million | Calendar month |
| Quarterly | Kvartalsvis | Turnover DKK 5–50 million | Calendar quarter (Q1=Jan–Mar, Q2=Apr–Jun, Q3=Jul–Sep, Q4=Oct–Dec) |
| Semi-annual | Halvårlig | Turnover < DKK 5 million | H1=Jan–Jun, H2=Jul–Dec |

New registrants are typically assigned quarterly or semi-annual depending on projected turnover.

### 1.5 Filing Deadlines (Angivelsesfrist)

| Period type | Period end | Deadline |
|---|---|---|
| Monthly | End of month M | 25th of month M+1 |
| Quarterly | End of quarter (Mar/Jun/Sep/Dec) | 10th of the second month after quarter end (e.g. Q1 = 10 May) |
| Semi-annual H1 | 30 June | 1 September |
| Semi-annual H2 | 31 December | 1 March (following year) |

If the deadline falls on a weekend or public holiday, it extends to the next working day.

### 1.6 Penalties for Late or Incorrect Filing

| Violation | Penalty |
|---|---|
| Late filing (for aflevering af momsangivelse) | DKK 65 per day, maximum DKK 1,000 per return (dagbod) |
| Late payment of VAT due | Interest: SKAT's official interest rate + 0.7% per month on outstanding balance, compounded monthly |
| Voluntary correction within 3 years | No penalty if proactive disclosure |
| Negligent incorrect return (uagtsomt fejl) | Tillæg (surcharge) of up to 10% of unpaid VAT |
| Intentional fraud (forsæt) | Criminal prosecution; fines up to 3x the unpaid tax |

### 1.7 Correction of Filed Returns

Businesses may correct a submitted momsangivelse within **3 years** of the filing deadline (Skatteforvaltningsloven § 31). SKAT may reassess within **3 years** for normal errors and **10 years** in cases of fraud.

---

## 2. Danish Business Registration

### 2.1 CVR Number (Det Centrale Virksomhedsregister)

The **CVR number** is the central business registration number in Denmark.

- **Format:** 8 digits (e.g. `12345678`)
- **Issuing authority:** Erhvervsstyrelsen (Danish Business Authority), operating cvr.dk
- **Modulus check:** CVR numbers pass a modulus-11 check digit (weights: 2,7,6,5,4,3,2,1)
- **Public registry:** All CVR numbers and company data are publicly accessible at `virk.dk`
- **Linkage to SKAT:** Skattestyrelsen uses CVR as the primary business tax identifier

### 2.2 SE Number (SE-nummer)

The **SE number** is a separate 8-digit number issued by Skattestyrelsen for tax and VAT purposes.

- A business can have **one CVR** but **multiple SE numbers** if it operates different activities with separate VAT accounts
- For most SMEs, the SE number is identical to the CVR number
- The SE number is the identifier on a **momsangivelse** and on bank payment references (FI-kode)
- Large groups may have a single CVR with multiple SE numbers for different subsidiaries

**Key distinction:**
- `CVR` = business identity (from Erhvervsstyrelsen)
- `SE` = tax account identity (from Skattestyrelsen), tied to a specific VAT obligation

### 2.3 Business Entity Types

| Danish Name | Abbreviation | English Equivalent |
|---|---|---|
| Aktieselskab | A/S | Public limited company |
| Anpartsselskab | ApS | Private limited company |
| Enkeltmandsvirksomhed | ENK | Sole trader |
| Interessentskab | I/S | General partnership |
| Kommanditselskab | K/S | Limited partnership |
| Filial af udenlandsk selskab | FILIAL | Branch of foreign company |

### 2.4 Registration Process

1. **Erhvervsstyrelsen registration (via virk.dk):**
   - Submit stiftelsesdokument (articles of association)
   - Pay registration fee (DKK ~670 for ApS online)
   - CVR number assigned within 1–5 business days

2. **SKAT VAT registration (via virk.dk → TastSelv Erhverv):**
   - Complete "Registrering af virksomhed" (Form 40.112 or digital equivalent)
   - Declare: expected turnover, activity type (DB07/NACE code), start date
   - SKAT assigns SE number and afregningsperiode (filing frequency)
   - SKAT sends velkomstbrev confirming SE number and first filing deadline

3. **Ongoing obligations:**
   - File momsangivelse each period via TastSelv Erhverv
   - Pay VAT due by deadline (bank transfer with FI-kode referencing SE number)
   - Notify SKAT within 8 days of changes to turnover, activity, or cessation

### 2.5 Industry Classification

Businesses must declare their primary activity using **DB07** (Dansk Branchekode 2007), Denmark's implementation of EU NACE Rev. 2. SKAT uses this to risk-profile businesses for audit and apply sector-specific VAT rules.

---

## 3. SKAT Digital Systems

### 3.1 TastSelv Erhverv

**TastSelv Erhverv** is SKAT's online self-service portal for businesses. Primary channel for:

- Filing momsangivelser (VAT returns)
- Filing lønsumsafgift (payroll tax returns)
- Filing A-skat and AM-bidrag
- Viewing account balances and payment history
- Receiving SKAT communications (digital post via e-Boks)
- Changing registration details
- Applying for refunds

**Authentication:** MitID Erhverv (successor to NemID Erhverv from 2022). Delegation via "fuldmagt" allows accountants/employees to access on behalf of the company.

### 3.2 Digital VAT Return Submission

When filing a momsangivelse via TastSelv Erhverv, the following fields are entered:

| Rubrik | Field Name (DK) | Field Name (EN) |
|---|---|---|
| A | Salgsmoms (udgående moms) | Output VAT on domestic sales |
| B | Købsmoms (indgående moms) | Input VAT on domestic purchases |
| C | EU-varekøb (erhvervelsesmoms) | VAT on EU goods acquisitions |
| D | EU-varesalg (listesystem) | EU intra-community goods/services sales (zero-rated) |
| E | Importmoms | Import VAT (from customs declarations) |

Additional fields:
- **Omsætning:** Total sales value for the period
- **Momspligtig omsætning:** Taxable turnover (sales subject to VAT at 25%)
- **Momsfri omsætning:** VAT-exempt sales
- **Eksport:** Value of zero-rated exports outside the EU

**Calculated field (derived, not entered):**
- `Momstilsvar` = Rubrik A + Rubrik C + Rubrik E − Rubrik B
  - Positive: business owes SKAT
  - Negative: SKAT owes business a refund (tilbagebetaling)

### 3.3 E-indberetning API

Large businesses and accountancy firms use SKAT's **E-indberetning API** (or Skattedata API) to submit returns programmatically. Requires an OCES certificate (virksomhedscertifikat). Data format is XML-based, mapping to the same Rubrik fields.

---

## 4. End-to-End Procedural Flow

```
STEP 1: Business Formation
  └─ Founders file at Erhvervsstyrelsen (via virk.dk)
  └─ CVR number assigned (8-digit)

STEP 2: VAT Registration with SKAT
  └─ Login to TastSelv Erhverv with MitID Erhverv
  └─ Complete registration: activity (DB07 code), expected turnover, start date
  └─ SKAT assigns SE number (usually = CVR for single-entity businesses)
  └─ SKAT assigns afregningsperiode (monthly / quarterly / semi-annual)
  └─ SKAT sends velkomstbrev confirming SE number and first filing deadline

STEP 3: Ongoing Business Operations (per period)
  └─ Business issues VAT invoices to customers (must include SE/CVR number)
  └─ Bookkeeping system accumulates:
      ├─ Salgsmoms (Rubrik A): VAT charged on sales
      ├─ Købsmoms (Rubrik B): VAT paid on purchases (deductible)
      ├─ EU-varekøb (Rubrik C): acquisition VAT on EU goods
      ├─ EU-varesalg (Rubrik D): value of intra-community supplies
      └─ Importmoms (Rubrik E): VAT from customs on imports

STEP 4: Momsangivelse Preparation
  └─ Aggregate all Rubrik A–E figures
  └─ Calculate Momstilsvar = A + C + E − B
  └─ Prepare Listesystem data if EU supplies (Rubrik D > 0)

STEP 5: Digital Submission via TastSelv Erhverv
  └─ Navigate to "Moms" → "Ny momsangivelse"
  └─ Select SE number and filing period
  └─ Enter Rubrik A, B, C, D, E values
  └─ Review calculated Momstilsvar
  └─ Submit (kvittere)
  └─ Receive kvitteringsnummer (confirmation number) and PDF kvittering

STEP 6: Payment or Refund
  └─ If Momstilsvar > 0 (VAT due):
      └─ Pay via bank transfer (FI-kode 73) by filing deadline
      └─ Payment reference: SE number + period code
  └─ If Momstilsvar < 0 (refund due):
      └─ SKAT transfers refund to NemKonto within ~5 business days

STEP 7: SKAT Review and Assessment
  └─ SKAT risk-profiles submitted returns (automated + officer review)
  └─ If discrepancy detected:
      ├─ SKAT contacts business (digital post to e-Boks)
      ├─ Business provides documentation (bilag)
      └─ SKAT issues "Agterskrivelse" (proposed assessment) before final decision
  └─ If accepted: no further action
  └─ If assessment raised: "Afgørelse" (formal decision) issued
      ├─ Business may appeal (klage) to Skatteankestyrelsen within 3 months
      └─ Further appeal to Landsskatteretten or courts

STEP 8: Audit and Enforcement
  └─ SKAT may conduct momseftersyn (VAT audit) — on-site or desk review
  └─ 3-year ordinary reassessment window (Skatteforvaltningsloven § 31)
  └─ 10-year window for intentional errors (§ 32)
```

---

## 5. VAT Return Field Specification

All mandatory and optional fields in a Danish momsangivelse:

| Field ID | Danish Name | English Name | Data Type | Notes |
|---|---|---|---|---|
| `rubrik_a` | Salgsmoms (udgående moms) | Output VAT | Decimal (18,2) | VAT charged on domestic sales at 25%. Always non-negative. |
| `rubrik_b` | Købsmoms (indgående moms) | Input VAT | Decimal (18,2) | Deductible VAT on business purchases. Always non-negative. |
| `rubrik_c` | Moms af EU-varekøb | EU acquisition VAT | Decimal (18,2) | Self-assessed VAT on goods bought from EU VAT-registered suppliers. |
| `rubrik_d` | EU-varesalg og ydelser | EU intra-community sales value | Decimal (18,2) | Value (excl. VAT) of goods/services to VAT-registered EU customers. Zero-rated. Triggers Listesystem filing. |
| `rubrik_e` | Importmoms | Import VAT | Decimal (18,2) | VAT on goods imported from outside the EU. |
| `momspligtig_omsaetning` | Momspligtig omsætning | Taxable turnover | Decimal (18,2) | Total value (excl. VAT) of sales subject to Danish VAT. |
| `momsfri_omsaetning` | Momsfri omsætning | VAT-exempt turnover | Decimal (18,2) | Sales where no VAT is charged and no input VAT is recoverable. |
| `eksport` | Eksport (nulsats) | Zero-rated exports | Decimal (18,2) | Value of goods exported outside the EU (zero-rated under Momsloven § 34). |
| `momstilsvar` | Momstilsvar | Net VAT payable/(refundable) | Decimal (18,2) | **Calculated:** A + C + E − B. Positive = payable; negative = refundable. |
| `afregningsperiode` | Afregningsperiode | Filing period | String | Format: YYYY-MM (monthly), YYYY-QN (quarterly), YYYY-HN (semi-annual). |
| `se_nummer` | SE-nummer | SE number | String(8) | 8-digit SKAT-assigned tax account number. |
| `frist` | Angivelsesfrist | Filing deadline | Date | Computed deadline; used for late-filing penalty calculation. |
| `korrektionsangivelse` | Er dette en korrektionsangivelse? | Is this a correction return? | Boolean | True if amending a previously filed return. |
| `original_angivelse_id` | Oprindelig angivelses-ID | Original filing reference | UUID | Reference to the original filing if this is a correction. |
| `kvitteringsnummer` | Kvitteringsnummer | Confirmation number | String | Assigned by SKAT on successful submission. |

---

## 6. Architecture Review

Reviewed `AGENT_ARCHITECT_SPEC.md` (dated 2026-02-23) against research findings.

---

## 7. Gap Analysis

### 7.1 Filing Module — Critical Missing Fields

**Location:** `AGENT_ARCHITECT_SPEC.md` Section 3.2 (`app/models/filing.py`) and Section 3.3 (`app/schemas/filing.py`)

The `Filing` model currently contains only:
```python
filing_period: str       # e.g. "2024-Q1"
filing_type: str         # "VAT" or "INCOME_TAX"
total_amount: Decimal    # single aggregate number
submitted_at: datetime
```

And `FilingLineItem` contains:
```python
description: str
amount: Decimal
```

**Gaps:**

| Gap | Impact | Danish Legal Basis |
|---|---|---|
| No `rubrik_a` (salgsmoms) field | Cannot represent a real momsangivelse | Momsloven § 56 |
| No `rubrik_b` (købsmoms) field | Cannot calculate momstilsvar | Momsloven § 37 |
| No `rubrik_c` (EU acquisition VAT) field | EU acquisitions unrepresented | Momsloven § 11 |
| No `rubrik_d` (EU intra-community sales) field | Cannot trigger Listesystem obligation | Momsloven § 34 |
| No `rubrik_e` (import VAT) field | Import obligations unrepresented | Momsloven § 12 |
| No `momspligtig_omsaetning` field | Cannot report total taxable turnover | SKAT form requirement |
| No `momsfri_omsaetning` field | Exempt sales not captured | Momsloven § 13 |
| No `eksport` field | Exports not separately tracked | Momsloven § 34 |
| No `momstilsvar` computed field | Core output of momsangivelse missing | Momsloven § 56 |
| No `frist` (filing deadline) field | Deadline enforcement impossible | Bekendtgørelse om moms §§ 74–77 |
| No `korrektionsangivelse` flag | Cannot model correction returns | Skatteforvaltningsloven § 31 |
| No `se_nummer` reference on filing | Filing not linked to SKAT tax account | Core identifier for momsangivelse |
| `FilingLineItem` is free-text description+amount | **Completely wrong abstraction** — a momsangivelse has fixed Rubrik fields, not arbitrary line items | Momsloven § 56 |

> **Severity:** The `FilingLineItem` abstraction is fundamentally wrong for VAT returns. A Danish momsangivelse is a fixed-field form. The line item model may suit income tax or other returns, but for `filing_type = "VAT"`, the model needs dedicated Rubrik fields instead.

### 7.2 Filing Module — Missing Business Rules

**Location:** `app/services/filing.py` (Section 3.5)

| Missing Rule | Description | Impact |
|---|---|---|
| No deadline calculation | `submit_filing()` does not compute or enforce angivelsesfrist | Late filings not flagged; penalties cannot be calculated |
| No SE number ownership check | Any TAXPAYER can file for any `party_id` | Security risk — businesses should only file for their own SE number |
| No afregningsperiode eligibility check | No validation that the filing period matches the party's assigned frequency | Monthly filer cannot submit quarterly and vice versa |
| No duplicate period check | Same SE number can submit two returns for the same period | One return per period per SE number is the rule |
| No momstilsvar calculation | Service does not compute Rubrik A + C + E − B | Most fundamental output of a VAT return is not computed |
| No correction return chain | No logic for `korrektionsangivelse` pointing to original return | Cannot model amended returns |

### 7.3 Party/Registration Module — Missing Danish Identifiers

**Location:** Existing `app/models/party.py` and `app/schemas/party.py`

| Gap | Description | Impact |
|---|---|---|
| No `cvr_nummer` dedicated field | Stored as generic `PartyIdentifier` with `identifierTypeCL = "TIN"` | CVR must be validated (8 digits, modulus-11), indexed, and uniquely constrained |
| No `se_nummer` field | Not present anywhere | Filings need to reference SE number, not party UUID |
| No `vat_registration_date` field | Date of VAT registration with SKAT not stored | Required for computing first filing period and deadline |
| No `afregningsperiode` (filing frequency) on party | MONTHLY/QUARTERLY/SEMI_ANNUAL not stored | Filing module cannot validate whether a filing period is valid for this party |
| No `db07_kode` (industry/branch code) field | DB07/NACE classification not stored | Required for audit risk profiling and sector-specific VAT rules |
| No `nemkonto` (bank account) field | NemKonto for VAT refunds not stored | Cannot process automated refunds |
| `party_type_code = "ORGADM1"` opaque code | No mapping to Danish entity types (ApS, A/S, ENK, etc.) | Meaningless to Danish users |
| `identifierTypeCL = "TIN"` generic label | Should use `"CVR"` and `"SE"` as distinct identifier types | Ambiguous; does not distinguish CVR from SE |
| `partyStateCL = "IN_BUSINESS"` generic state | Should include: `AKTIV`, `UNDER_TVANGSOPLOSNING`, `OPHOERT`, `KONKURS` | Does not align with CVR register status codes |

### 7.4 Assessment Module — Missing Danish Tax Concepts

**Location:** `AGENT_ARCHITECT_SPEC.md` Section 4.2 (`app/models/assessment.py`)

| Gap | Description | Impact |
|---|---|---|
| `assessment_date` stored as `String(20)` | Should be a proper `Date` column | String dates cannot be sorted or compared correctly |
| No `agterskrivelse_sent_at` field | Danish law requires SKAT to issue a proposed assessment before the final decision | Cannot model the mandatory "hearing" step in Danish administrative law |
| No `afgoerelse_type` (decision type) field | Assessment can be: accept, partial adjustment, full adjustment, cancellation | All decisions collapsed into generic status |
| No `klage_frist` (appeal deadline) field | Appeal must be filed within 3 months of the afgørelse | Cannot enforce or display appeal deadlines |
| No `interest_amount` (rentetillaeg) field | Interest on late payment is a distinct line from the penalty surcharge | Combined into `penalties` column — legally insufficient |
| Status `APPEALED` is terminal | In Danish procedure, an appeal can be upheld, partially allowed, or overturned | State machine is incomplete |

### 7.5 API Contract — Missing Endpoints

| Missing Endpoint | Description |
|---|---|
| `GET /api/v1/parties?cvr={cvr_number}` | Look up party by CVR number |
| `GET /api/v1/filings?se_nummer={se}` | Look up all filings for a given SE number |
| `POST /api/v1/filings/{id}/correct` | Submit a correction return (korrektionsangivelse) |
| `GET /api/v1/parties/{id}/afregningsperioder` | List all valid filing periods for a party (based on their frequency) |
| `GET /api/v1/deadlines?party_id={id}&period={period}` | Calculate the filing deadline for a given party and period |
| `POST /api/v1/assessments/{id}/agterskrivelse` | Mark that the proposed assessment notice has been sent |

### 7.6 Terminology Mismatches

| Current (Spec) | Correct Danish Terminology | Context |
|---|---|---|
| `filing_type = "VAT"` | `angivelse_type = "MOMS"` | Danish term for a VAT return is "momsangivelse" |
| `filing_type = "INCOME_TAX"` | `angivelse_type = "SELSKABSSKAT"` or `"SELVANGIVELSE"` | Income tax returns are separate in Danish tax law |
| `status = "DRAFT"` | `status = "KLADDE"` | Should use Danish terms or keep English consistently throughout |
| `penalties` on Assessment | `tillaeg` + `renter` (separate fields) | Surcharges (tillæg) and interest (renter) have different legal bases |
| `notes` on Assessment | `begrundelse` | "Begrundelse" (reasoning) is the legally required field per Forvaltningsloven § 22 |
| `assessed_by` | `sagsbehandler_id` | "Sagsbehandler" is the Danish term for the case officer |

---

## 8. Recommendations

### Priority: High (blocks correct legal compliance)

| # | Recommendation | Affected File(s) | Action |
|---|---|---|---|
| H1 | Replace `FilingLineItem` with dedicated Rubrik fields on the `Filing` model | `app/models/filing.py`, `app/schemas/filing.py`, migration `0003` | Add `rubrik_a` through `rubrik_e`, `momspligtig_omsaetning`, `momsfri_omsaetning`, `eksport`, `momstilsvar` as `Numeric(18,2)` columns |
| H2 | Add `cvr_nummer` (String(8), unique) and `se_nummer` (String(8)) as first-class fields on `Party` | `app/models/party.py`, `app/schemas/party.py` | New columns with modulus-11 CVR validation in the service layer |
| H3 | Add `afregningsperiode_type` (MONTHLY/QUARTERLY/SEMI_ANNUAL) to `Party` | `app/models/party.py` | Service must validate that each `Filing.filing_period` matches the party's assigned frequency |
| H4 | Add `vat_registration_date` (Date, nullable) to `Party` | `app/models/party.py` | Needed to compute first filing period and deadline |
| H5 | Implement `momstilsvar` calculation in `FilingService`: `momstilsvar = rubrik_a + rubrik_c + rubrik_e - rubrik_b` | `app/services/filing.py` | Calculated and stored on the model; exposed in `FilingRead` schema |
| H6 | Implement filing deadline calculation: compute `angivelsesfrist` from `afregningsperiode_type` and period string | `app/services/filing.py`, `app/models/filing.py` | Add `frist` Date column; check on submit whether current timestamp exceeds deadline |
| H7 | Add uniqueness constraint: one momsangivelse per (se_nummer, filing_period, angivelse_type) | `app/models/filing.py` | `UniqueConstraint("se_nummer", "filing_period", "angivelse_type")`; return HTTP 409 on duplicate |

### Priority: Medium (significant improvements)

| # | Recommendation | Affected File(s) | Action |
|---|---|---|---|
| M1 | Add `korrektionsangivelse` (Boolean) and `original_filing_id` (UUID FK) to `Filing` | `app/models/filing.py`, `app/schemas/filing.py` | Enables correction return workflow; add `POST /api/v1/filings/{id}/correct` endpoint |
| M2 | Add `db07_kode` (String(6)) to `Party` model | `app/models/party.py` | Required for SKAT risk-profiling and sector-specific VAT rules |
| M3 | Change `assessment.assessment_date` from `String(20)` to `Date` column | `app/models/assessment.py`, migration `0004` | Fix type safety; enables date arithmetic for appeal deadlines |
| M4 | Add `agterskrivelse_sent_at` (DateTime) and `klage_frist` (Date) to `TaxAssessment` | `app/models/assessment.py` | Models the mandatory Danish administrative law hearing step |
| M5 | Separate `penalties` into `tillaeg` (Numeric 18,2) and `renter` (Numeric 18,2) on `TaxAssessment` | `app/models/assessment.py`, `app/schemas/assessment.py` | Surcharges and interest have different legal bases |
| M6 | Add `GET /api/v1/parties?cvr={cvr}` search endpoint | `app/routers/parties.py` | CVR lookup is the primary way Danish users identify businesses |
| M7 | Validate `filing_period` format in `FilingCreate` schema | `app/schemas/filing.py` | Accept `YYYY-MM`, `YYYY-Q[1-4]`, `YYYY-H[1-2]` only |
| M8 | Expand `Assessment.status` to include `AGTERSKRIVELSE_SENDT` state | `app/services/assessment.py` | `PENDING` → `AGTERSKRIVELSE_SENDT` → `COMPLETE` / `APPEALED` |

### Priority: Low (Danish convention alignment)

| # | Recommendation | Affected File(s) | Action |
|---|---|---|---|
| L1 | Rename `filing_type` values from `"VAT"` / `"INCOME_TAX"` to `"MOMS"` / `"SELSKABSSKAT"` | `app/models/filing.py`, `types/filing.ts` | Aligns with SKAT terminology |
| L2 | Document valid `identifierTypeCL` values: `"CVR"`, `"SE"`, `"CPR"` | `app/schemas/party.py` | Replace generic `"TIN"` with Danish-correct identifier type codes |
| L3 | Document valid `partyStateCL` values: `"AKTIV"`, `"OPHOERT"`, `"UNDER_KONKURS"`, `"TVANGSOPLOEST"` | `app/schemas/party.py` | Aligns with CVR register status codes |
| L4 | Document valid `party_type_code` values: `"APS"`, `"AS"`, `"ENK"`, `"IS"`, `"KS"`, `"FILIAL"` | `app/schemas/party.py` | Replace opaque `"ORGADM1"` with Danish entity type codes |
| L5 | Document valid `party_role_type_code` values: `"MOMSREGISTRERET"`, `"ARBEJDSGIVER"`, `"IMPORTOER"` | `app/schemas/party_role.py` | Replace `"BUSINSSDM1"` with meaningful Danish tax role codes |
| L6 | Emit `ListesystemObligationRaised` event when `rubrik_d > 0` | `app/events/filing_events.py` | Future trigger for Listesystem filing requirement |
| L7 | Add `nemkonto` (String(18), nullable) to `Party` model | `app/models/party.py` | Required for processing VAT refunds (momstilsvar < 0) |
| L8 | Rename `notes` to `begrundelse` on `TaxAssessment` | `app/models/assessment.py` | "Begrundelse" is the legally required reasoning per Forvaltningsloven § 22 |
| L9 | Add Danish period display helper in `frontend/lib/utils/formatters.ts` | `frontend/lib/utils/formatters.ts` | `"2024-Q1"` → `"1. kvartal 2024"`, `"2024-H1"` → `"1. halvår 2024"` |
| L10 | Show `angivelsesfrist` in filings list with colour-coded deadline proximity | `frontend/components/filings/FilingTable.tsx` | Red = overdue, orange = within 7 days, green = on time |

---

## 9. Proposed Updated Filing Model

Recommended schema for `app/models/filing.py` to replace Section 3.2 of `AGENT_ARCHITECT_SPEC.md`:

```python
from sqlalchemy import Boolean, Date, UniqueConstraint

class Filing(Base, TimestampMixin):
    __tablename__ = "filings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    se_nummer: Mapped[str] = mapped_column(String(8), nullable=False, index=True)

    # Period identification
    afregningsperiode_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Values: "MONTHLY" | "QUARTERLY" | "SEMI_ANNUAL"
    filing_period: Mapped[str] = mapped_column(String(20), nullable=False)
    # Format: "YYYY-MM" | "YYYY-Q1..Q4" | "YYYY-H1..H2"
    frist: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Filing classification
    angivelse_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Values: "MOMS" | "SELSKABSSKAT" | "LONSUMSAFGIFT"
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="KLADDE")
    # Values: "KLADDE" | "INDBERETTET" | "UNDER_BEHANDLING" | "GODKENDT" | "AFVIST"

    # Core Rubrik fields (momsangivelse — Momsloven § 56)
    rubrik_a: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_b: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_c: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_d: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_e: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))

    # Summary fields
    momspligtig_omsaetning: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    momsfri_omsaetning: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    eksport: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    momstilsvar: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    # Computed: rubrik_a + rubrik_c + rubrik_e - rubrik_b

    # Submission tracking
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    kvitteringsnummer: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Correction return support
    korrektionsangivelse: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    original_filing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filings.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "se_nummer", "filing_period", "angivelse_type",
            name="uq_filing_se_nummer_period_type"
        ),
    )
```

---

## 10. Sources

- **Momsloven** (Lovbekendtgørelse nr. 1021 af 26. september 2019) — Danish VAT Act
- **Skatteforvaltningsloven** (LBK nr 635 af 13. juni 2012, as amended) — Danish Tax Administration Act
- **Forvaltningsloven** (LBK nr 433 af 22. april 2014) — Danish Public Administration Act
- **SKAT vejledning: Moms** — SKAT's official VAT guidance for businesses (skat.dk)
- **Erhvervsstyrelsen CVR-register** (cvr.dk) — Danish Business Authority company register
- **EU Council Directive 2006/112/EC** — EU VAT Directive implemented by Momsloven
- **DB07** (Dansk Branchekode 2007) — Danish implementation of NACE Rev. 2
- **AGENT_ARCHITECT_SPEC.md** (2026-02-23) — Platform architecture specification under review
