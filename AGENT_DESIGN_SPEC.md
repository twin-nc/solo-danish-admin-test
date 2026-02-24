# AGENT_DESIGN_SPEC.md — Danish Tax Administration Platform

## Design Approach Note

This specification is based on thorough knowledge of the skat.dk and Danish government (borger.dk / digst.dk) design system, the Det Fælles Designsystem (DDS), and SKAT's established visual identity — navy blue primary palette, clean sans-serif typography (Source Sans Pro / system sans), strict grid layouts, and authoritative government iconography. All design tokens are cross-referenced against the publicly documented Danish government design guidelines.

---

## 1. Design Principles

### 1.1 Core Principles

**Authoritative and Trustworthy**
Every visual decision must reinforce the weight and legitimacy of a government tax authority. The interface communicates competence through consistent structure, restrained use of colour, and clear typographic hierarchy. Nothing decorative that does not serve a function.

**Clarity Over Cleverness**
Tax administration involves complex data — filings, assessments, legal statuses, multi-step workflows. The UI must eliminate ambiguity at every point. Labels are explicit, statuses are visually distinct, and actions have unambiguous consequence indicators.

**Accessible by Default (WCAG 2.1 AA)**
All colour combinations meet a minimum 4.5:1 contrast ratio for normal text and 3:1 for large text and UI components. Focus states are clearly visible. All interactive elements are keyboard navigable. No information is conveyed by colour alone — always paired with an icon or text label. Minimum touch target size 44x44px.

**Danish Government Aesthetic**
The visual language mirrors skat.dk: structured header with the SKAT wordmark, a dark navy top bar, clean white content areas, muted grey sidebars, and the characteristic Danish government blue (`#004B87` family) used for primary actions and active navigation states.

**Desktop-First, Responsive to Tablet**
The primary users (tax officers, administrators) work on desktop workstations. The layout is optimised for 1280px and wider. Tablet support (768–1024px) is provided through sidebar collapse and responsive grid adjustments. Mobile is out of scope for the admin platform but graceful degradation is expected.

**Data Density with Breathing Room**
Officers work with large datasets. Tables must be dense enough to show meaningful data per screen but table rows use sufficient vertical padding (12px top/bottom) so that scanning is not fatiguing. White space is structural.

**Progressive Disclosure**
Complex entities (Party, Filing, Assessment) expose summary information first. Detail panels, modals, and expanded sections reveal depth on demand.

---

## 2. Design Tokens

### 2.1 Colour Palette

#### Primary — SKAT Navy Blue

```css
--color-primary-900: #002B52;
--color-primary-800: #003D6E;
--color-primary-700: #004B87;   /* core brand blue — primary buttons, links */
--color-primary-600: #0059A0;
--color-primary-500: #1A6FB5;
--color-primary-400: #4A90C8;
--color-primary-300: #7BB3D8;
--color-primary-200: #B3D4EC;
--color-primary-100: #D9EAF5;
--color-primary-50:  #EEF6FB;
```

#### Secondary — Warm Grey

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
/* Success */
--color-success-700: #1B6B32;  --color-success-500: #2EA052;
--color-success-200: #A8DCBA;  --color-success-50:  #EDF8F1;

/* Warning */
--color-warning-700: #7A4B00;  --color-warning-500: #C27A00;
--color-warning-200: #F5CF80;  --color-warning-50:  #FDF6E3;

/* Error */
--color-error-700: #8B1A1A;    --color-error-500: #D03030;
--color-error-200: #F0A8A8;    --color-error-50:  #FDF0F0;

/* Info */
--color-info-700: #005F6E;     --color-info-500: #0096AA;
--color-info-200: #80D5E0;     --color-info-50:  #E5F8FA;
```

### 2.2 Typography

```css
--font-family-base: 'Source Sans Pro', 'Helvetica Neue', Arial, sans-serif;
--font-family-mono: 'Source Code Pro', 'Courier New', Courier, monospace;

--font-size-xs:   0.75rem;    /* 12px */
--font-size-sm:   0.875rem;   /* 14px */
--font-size-base: 1rem;       /* 16px */
--font-size-md:   1.125rem;   /* 18px */
--font-size-lg:   1.25rem;    /* 20px */
--font-size-xl:   1.5rem;     /* 24px */
--font-size-2xl:  2rem;       /* 32px */

--font-weight-regular:  400;
--font-weight-medium:   500;
--font-weight-semibold: 600;
--font-weight-bold:     700;
```

### 2.3 Spacing Scale

```css
--space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
--space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px;
```

### 2.4 Border Radius & Shadows

```css
--radius-sm: 4px; --radius-md: 6px; --radius-lg: 12px; --radius-full: 9999px;

--shadow-sm: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
--shadow-md: 0 4px 6px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.06);
--shadow-lg: 0 10px 24px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.06);
```

### 2.5 Tailwind Config Extension

```js
// tailwind.config.js — theme.extend
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#002B52', 800: '#003D6E', 700: '#004B87', 600: '#0059A0',
          500: '#1A6FB5', 400: '#4A90C8', 300: '#7BB3D8', 200: '#B3D4EC',
          100: '#D9EAF5', 50: '#EEF6FB',
        },
        secondary: {
          900: '#1A1A1A', 800: '#2E2E2E', 700: '#4A4A4A', 600: '#6B6B6B',
          500: '#8C8C8C', 400: '#ADADAD', 300: '#C8C8C8', 200: '#E0E0E0',
          100: '#F0F0F0', 50: '#F8F8F8',
        },
        page: '#F4F5F7',
        border: '#DDE1E7',
        success: { 700: '#1B6B32', 500: '#2EA052', 200: '#A8DCBA', 50: '#EDF8F1' },
        warning: { 700: '#7A4B00', 500: '#C27A00', 200: '#F5CF80', 50: '#FDF6E3' },
        error:   { 700: '#8B1A1A', 500: '#D03030', 200: '#F0A8A8', 50: '#FDF0F0' },
        info:    { 700: '#005F6E', 500: '#0096AA', 200: '#80D5E0', 50: '#E5F8FA' },
      },
      fontFamily: {
        sans: ['Source Sans Pro', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['Source Code Pro', 'Courier New', 'Courier', 'monospace'],
      },
      borderRadius: { sm: '4px', md: '6px', lg: '12px', full: '9999px' },
      boxShadow: {
        sm: '0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06)',
        md: '0 4px 6px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.06)',
        lg: '0 10px 24px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.06)',
      },
    },
  },
}
```

---

## 3. Component Library

### 3.1 Button

**Variants:** `primary` | `secondary` | `ghost` | `danger`
**Sizes:** `sm` (32px h) | `md` (40px h) | `lg` (48px h)
**States:** default | hover | focus | disabled | loading

| Variant | Background | Text | Hover bg |
|---------|-----------|------|---------|
| primary | `primary-700` | white | `primary-600` |
| secondary | white | `primary-700` | `primary-50` |
| ghost | transparent | `primary-700` | `primary-50` |
| danger | `error-500` | white | `error-600` |

Focus: 2px offset ring in `primary-200`. Disabled: `secondary-300` bg, `secondary-500` text.
Loading: spinner replaces label, button stays same width.

**Usage:** One primary button per view area. Form submits use `lg`. Table row actions use ghost `sm`. Destructive confirmations use `danger`.

---

### 3.2 Badge / StatusChip

Pill shape (`radius-full`), 1px border, `font-size-xs`, `font-weight-semibold`. Optional coloured dot prefix.

| Status | Background | Text | Border |
|--------|-----------|------|--------|
| `DRAFT` / `KLADDE` | `secondary-100` | `secondary-700` | `secondary-300` |
| `SUBMITTED` / `INDBERETTET` | `info-50` | `info-700` | `info-200` |
| `UNDER_REVIEW` / `UNDER_BEHANDLING` | `warning-50` | `warning-700` | `warning-200` |
| `ACCEPTED` / `GODKENDT` | `success-50` | `success-700` | `success-200` |
| `REJECTED` / `AFVIST` | `error-50` | `error-700` | `error-200` |
| `PENDING` / `AFVENTENDE` | `warning-50` | `warning-700` | `warning-200` |
| `COMPLETE` / `AFSLUTTET` | `success-50` | `success-700` | `success-200` |
| `APPEALED` / `ANKET` | `primary-100` | `primary-800` | `primary-300` |
| `IN_BUSINESS` / `AKTIV` | `success-50` | `success-700` | `success-200` |

---

### 3.3 DataTable

Full-width, `shadow-sm`, `radius-md`, white background.

- **Header:** `secondary-50` bg, `font-weight-semibold`, `font-size-sm`. Sortable columns show `ChevronUpDownIcon`; active sort shows directional chevron in `primary-700`.
- **Rows:** 52px height, `font-size-sm`. Alternating `secondary-50` zebra stripe. Hover: `primary-100`.
- **Actions column:** 120px, ghost `sm` buttons ("Vis", "Rediger").
- **Empty state:** Centred `InboxIcon` (64px, `secondary-300`) + "Ingen resultater" heading.
- **Loading:** 5 skeleton rows, `animate-pulse`.
- **Pagination:** Below table. "Viser X–Y af Z" left. Prev/next + page numbers right. Active page: `primary-700` bg.

---

### 3.4 FormField

Wraps label + input/select/textarea + helper/error text.

- Input: 40px height, white bg, 1.5px `secondary-400` border, `radius-sm`.
- Focus: `primary-700` border, `0 0 0 3px primary-200` shadow.
- Error: `error-500` border, error message in `error-600` `font-size-xs` with `ExclamationCircleIcon`.
- Label: `font-size-sm`, `font-weight-medium`, 4px margin-bottom. Required asterisk in `error-500`.

---

### 3.5 Card

White bg, `radius-md`.
- `default` variant: 1px `border-color` border.
- `elevated` variant: `shadow-md`, no border.
- Header: `secondary-50` bg, `border-b`, padding 12px 16px.
- Footer: `secondary-50` bg, `border-t`, padding 12px 16px.

---

### 3.6 PageHeader

Full-width bar on `page-bg`. Padding 24px 32px.
- Breadcrumb row: `font-size-sm`, `secondary-600`, `ChevronRightIcon` separators. Current page non-linked `secondary-900`.
- Title: `font-size-2xl`, `font-weight-bold`, 6px below breadcrumb.
- Subtitle: `font-size-base`, `secondary-600`.
- Actions slot: right-aligned, flex row, 8px gap.
- StatusChip: inline with title, 8px right.

---

### 3.7 SideNav

- Width: 256px expanded, 64px collapsed (icon-only).
- Background: `primary-800` (#003D6E).
- Top logo area: 64px height, white SKAT wordmark.
- Nav items: 44px height, `radius-md`, white icons + text. Active: `primary-700` bg + 3px `primary-300` left border.
- Group labels: `font-size-xs`, `primary-400`, uppercase.
- Bottom user strip: `primary-900` bg. Avatar initial, name, role badge, logout button.

---

### 3.8 StatCard

White bg, `shadow-sm`, `radius-md`, 1px `border-color`. Padding 20px 24px.
- Icon box: 48x48px, `iconColor-50` bg, 24px icon in `iconColor-700`.
- Label: `font-size-sm`, `secondary-600`.
- Value: `font-size-2xl`, `font-weight-bold`.
- Trend: `font-size-xs`, `ArrowTrendingUpIcon`/`ArrowTrendingDownIcon`, success-600/error-600.

---

### 3.9 Modal / Dialog

- Backdrop: `rgba(0,0,0,0.45)`.
- Container: white, `radius-lg`, `shadow-lg`. Sizes: sm=480px, md=600px, lg=800px.
- Header: `secondary-50` bg, `border-b`, `XMarkIcon` close button.
- Footer: `secondary-50` bg, `border-t`, right-aligned buttons.
- Animation: fade backdrop (150ms), slide modal from below (200ms ease-out).

---

### 3.10 Toast / Notification

Fixed bottom-right, 360px wide, `radius-md`, `shadow-lg`.
4px thick left border in variant colour. Icon strip on left.
Auto-dismiss progress bar at bottom. Slide-in from right (250ms).

| Variant | Icon | Left border |
|---------|------|------------|
| success | `CheckCircleIcon` | `success-500` |
| error | `ExclamationCircleIcon` | `error-500` |
| warning | `ExclamationTriangleIcon` | `warning-500` |
| info | `InformationCircleIcon` | `info-500` |

---

## 4. Page Layouts and Wireframes

### 4a. Login Page

```
+----------------------------------------------------------+
|                  [primary-800 background]                 |
|                                                          |
|          +----------------------------------+            |
|          |  [SKAT crown logo 48px]          |            |
|          |  Skatteforvaltningens Platform   |            |
|          |  --------------------------------|            |
|          |                                  |            |
|          |  E-mail adresse                  |            |
|          |  [________________________]      |            |
|          |                                  |            |
|          |  Adgangskode              [eye]  |            |
|          |  [________________________]      |            |
|          |                                  |            |
|          |  [       Log ind          ]      |            |
|          |                                  |            |
|          |  Glemt adgangskode?              |            |
|          +----------------------------------+            |
|              Version 1.0 — SKAT Internt                  |
+----------------------------------------------------------+
```

- Full-screen `primary-800` background.
- Login card: white, `radius-lg`, `shadow-lg`, 420px wide, 40px padding, centred.
- Error state: full-width `error-50` alert above Log ind button.

---

### 4b. Dashboard

```
+--------+-----------------------------------------------+
|        | [PageHeader: Dashboard]                       |
| SIDE   +-----------------------------------------------+
| NAV    | [StatCard: Parter] [StatCard: Indberetninger] |
| 256px  | [StatCard: Vurderinger] [StatCard: Afviste]   |
|        +-----------------------------------------------+
|        | [Card: Seneste Registreringer]                |
|        |   DataTable (5 rows): Navn|TIN|Status|Dato    |
|        +-----------------------------------------------+
|        | [Card: Seneste Indberetninger]                |
|        |   DataTable (5 rows): Part|Periode|Status|Dato|
|        +-----------------------------------------------+
|        | [Card: Hurtige Handlinger]                    |
|        |  [Registrer Ny Part][Ny Indberetn.][Vurder.]  |
+--------+-----------------------------------------------+
```

---

### 4c. Parties List

```
+--------+-----------------------------------------------+
| SIDE   | [PageHeader: Parter] [Btn: Registrer Part]    |
| NAV    +-----------------------------------------------+
|        | [Search: "Søg på navn, TIN..."]               |
|        | [Status v] [Sektor v] [Nulstil]               |
|        +-----------------------------------------------+
|        | [DataTable: Navn|TIN|Status|Sektor|Dato|Vis]  |
|        | [Pagination]                                  |
+--------+-----------------------------------------------+
```

---

### 4d. Party Detail

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Acme ApS] [IN_BUSINESS] [Tildel]   |
| NAV    | Breadcrumb: Parter > Acme ApS                    |
|        +--------------------------------------------------+
|        | [Card elevated: Partioplysninger — ID/type/dates]|
|        +--------------------------------------------------+
|        | [2-col grid]                                     |
|        | [Card: Identifikatorer] [Card: Klassifikationer] |
|        | [Card: Kontakter]       [Card: Navne]            |
|        +--------------------------------------------------+
|        | [Card: Roller — DataTable]                       |
+--------+--------------------------------------------------+
```

---

### 4e. Register Party

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Registrer Ny Part]                  |
| NAV    | Breadcrumb: Parter > Registrer                   |
|        +--------------------------------------------------+
|        | [Card: 1. Grundoplysninger]                      |
|        |   [Partitype select — read-only]                 |
|        | [Card: 2. Identifikator]                         |
|        |   [Identifikatortype] [Identifikatorværdi]       |
|        | [Card: 3. Klassifikationer]                      |
|        |   [Virksomhedsstørrelse] [Erhvervssektor]        |
|        | [Card: 4. Tilstand]                              |
|        |   [Tilstand select]                              |
|        | [Card: 5. Kontakt]                               |
|        |   [E-mailadresse]                                |
|        | [Card: 6. Navne]                                 |
|        |   [Juridisk navn] [Alias (optional)]             |
|        |   [+ Tilføj endnu et navn]                       |
|        +--------------------------------------------------+
|        | [sticky footer: Annuller | Registrer Part]       |
+--------+--------------------------------------------------+
```

---

### 4f. Filings List

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Indberetninger] [Ny Indberetning]   |
| NAV    +--------------------------------------------------+
|        | [Search: part/TIN] [Status v] [Periode v]        |
|        | [Dato fra] [Dato til] [Nulstil]                  |
|        +--------------------------------------------------+
|        | [DataTable: Part|Periode|Type|Beløb|Status|Dato] |
|        | [Pagination]                                     |
+--------+--------------------------------------------------+
```

---

### 4g. Filing Detail

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Moms Q1 2024 — Acme ApS] [SUBM.]   |
| NAV    | [Opret Vurdering btn — officer only]             |
|        +--------------------------------------------------+
|        | [Card elevated: Indberetningsoplysninger]         |
|        |   Part(link) | TIN | Periode | Indgivet | Type   |
|        +--------------------------------------------------+
|        | [Card: Momslinjer — DataTable + TOTAL row]       |
|        +--------------------------------------------------+
|        | [Card: Statustidslinje — step indicator]         |
|        +--------------------------------------------------+
|        | [Card: Sagsbehandlernoter — officer only]        |
+--------+--------------------------------------------------+
```

---

### 4h. Create Filing

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Ny Indberetning]                    |
| NAV    +--------------------------------------------------+
|        | [Card: 1. Partioplysninger]                      |
|        |   [Vælg part autocomplete] [Periode] [År]        |
|        | [Card: 2. Momslinjer]                            |
|        |   [inline table: Beskrivelse|Grundlag|Sats|Beløb]|
|        |   [+ Tilføj linje]                               |
|        |   Beregnet momstilsvar: DKK X,XXX               |
|        | [Card: 3. Erklæring]                             |
|        |   [☐ Jeg bekræfter at oplysningerne er korrekte] |
|        +--------------------------------------------------+
|        | [sticky: Annuller | Gem kladde | Indberet]       |
+--------+--------------------------------------------------+
```

---

### 4i. Assessments List

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Vurderinger]                        |
| NAV    +--------------------------------------------------+
|        | [Search] [Status v] [Periode v] [Sagsbehandler v]|
|        +--------------------------------------------------+
|        | [DataTable: Part|Periode|Ref|Beløb|Status|Dato]  |
|        | [Pagination]                                     |
+--------+--------------------------------------------------+
```

---

### 4j. Assessment Detail

```
+--------+--------------------------------------------------+
| SIDE   | [PageHeader: Vurdering — Acme ApS Q1 2024]       |
| NAV    | [ACCEPTED status chip] [Anke btn — taxpayer]     |
|        +--------------------------------------------------+
|        | [Card elevated: Vurderingsoplysninger]            |
|        |   Part(link) | Indberetning(link) | Dato | Sagsb. |
|        +--------------------------------------------------+
|        | [Card: Vurderingsfelter — tax breakdown]         |
|        |   Skyldigt beløb: [DKK bold primary-700 xl]      |
|        +--------------------------------------------------+
|        | [Card: Sagsbehandlernoter]                       |
|        | [Card: Statustidslinje]                          |
|        | [Card: Ankeoplysninger — if APPEALED]            |
+--------+--------------------------------------------------+
```

---

## 5. Navigation Structure

### 5.1 Sidebar Items

| Label | Path | Heroicon | ADMIN | OFFICER | TAXPAYER |
|-------|------|----------|-------|---------|---------|
| Dashboard | `/dashboard` | `Squares2X2Icon` | ✓ | ✓ | — |
| Parter | `/parties` | `BuildingOffice2Icon` | ✓ | ✓ | — |
| Registrer Part | `/parties/new` | `PlusCircleIcon` | ✓ | ✓ | — |
| Indberetninger | `/filings` | `DocumentTextIcon` | ✓ | ✓ | ✓ |
| Ny Indberetning | `/filings/new` | `DocumentPlusIcon` | ✓ | ✓ | ✓ |
| Vurderinger | `/assessments` | `ClipboardDocumentCheckIcon` | ✓ | ✓ | ✓ |
| Brugere | `/admin/users` | `UsersIcon` | ✓ | — | — |
| Indstillinger | `/admin/settings` | `Cog6ToothIcon` | ✓ | — | — |

**Groups:** OVERBLIK · REGISTRERING · INDBERETNING · VURDERING · ADMINISTRATION

### 5.2 Breadcrumb Patterns

| Page | Breadcrumb |
|------|-----------|
| Dashboard | *(none)* |
| Parties List | Parter |
| Party Detail | Parter / [Navn] |
| Register Party | Parter / Registrer Ny Part |
| Filings List | Indberetninger |
| Filing Detail | Indberetninger / [Periode] [Part] |
| Create Filing | Indberetninger / Ny Indberetning |
| Assessments List | Vurderinger |
| Assessment Detail | Vurderinger / [Periode] [Part] |

---

## 6. User Flows

### 6.1 Officer Registers a New Business Party

```
/login → Log ind → /dashboard
→ Click "Registrer Ny Part"
→ /parties/new
→ Fill: TIN, størrelse (SMALL), sektor (PIZZERIA), email, juridisk navn
→ Click "Registrer Part" → POST /api/v1/parties
→ Success toast → Redirect /parties/{id}
→ Click "Tildel Rolle" → AssignRoleModal opens
→ Select role BUSINSSDM1, primary identifier, primary contact
→ Click "Tildel" → POST /api/v1/parties/{id}/roles
→ Success toast → Modal closes → Roller card refreshes
```

### 6.2 Taxpayer Submits a VAT Filing

```
/login → Log ind → /filings (taxpayer default)
→ Click "Ny Indberetning"
→ /filings/new (party pre-filled, read-only)
→ Select Periode: Q1, År: 2024
→ Add line items: Salgsmoms 100,000 DKK × 25% = 25,000
→ Add line: Købsmoms 40,000 DKK × 25% = 10,000
→ Summary shows: Momstilsvar DKK 15,000
→ Check declaration checkbox
→ Click "Indberet" → POST /api/v1/filings
→ Success toast → Redirect /filings/{id}
→ Status: SUBMITTED
```

### 6.3 Officer Creates an Assessment

```
/filings → Filter: Status = SUBMITTED
→ Click "Vis" on Acme ApS Q1 2024
→ /filings/{id} → Reviews line items
→ Click "Opret Vurdering"
→ /assessments/new?filing_id={id}
→ Fill: vurderet beløb, notes
→ Click "Opret Vurdering" → POST /api/v1/assessments
→ Success toast → /assessments/{id}
→ Filing status auto-transitions to ACCEPTED
```

### 6.4 Admin Reviews Dashboard

```
/login → /dashboard
→ Read stat cards: 247 parter, 89 indberetninger, 14 afventende, 3 afviste
→ Scan recent registrations table
→ Check recent filings table for stuck SUBMITTED rows
→ Click "Brugere" in sidebar → /admin/users
→ Navigate to /assessments, filter by sagsbehandler
```

---

## 7. Responsive Behaviour

| Breakpoint | Sidebar | Tables | StatCards | Forms |
|-----------|---------|--------|-----------|-------|
| Desktop >1024px | 256px expanded | Full columns | 4 columns | 2-column grid |
| Tablet 768–1024px | 64px icon-only (collapsible overlay) | Horizontal scroll, hide secondary columns | 2 columns | 1-column |
| Mobile <768px | Hidden, hamburger menu (full overlay) | Card-list view | 1 column | 1-column |

**Sidebar collapse:** On tablet, `translateX(-256px → 0)` 200ms on open. Backdrop overlay. Main content `margin-left: 64px` (icon sidebar fixed).

---

## 8. Frontend File Structure

```
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.ts
├── .env.local.example
├── public/
│   ├── skat-logo.svg
│   └── favicon.ico
│
├── app/
│   ├── layout.tsx                    # Root layout (fonts, providers)
│   ├── globals.css                   # Tailwind + CSS custom properties
│   ├── (auth)/
│   │   └── login/page.tsx
│   └── (app)/
│       ├── layout.tsx                # AppShell (SideNav + content)
│       ├── dashboard/page.tsx
│       ├── parties/
│       │   ├── page.tsx
│       │   ├── new/page.tsx
│       │   └── [id]/page.tsx
│       ├── filings/
│       │   ├── page.tsx
│       │   ├── new/page.tsx
│       │   └── [id]/page.tsx
│       ├── assessments/
│       │   ├── page.tsx
│       │   ├── new/page.tsx
│       │   └── [id]/page.tsx
│       └── admin/
│           ├── users/page.tsx
│           └── settings/page.tsx
│
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── Card.tsx
│   │   ├── FormField.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   ├── ToastContainer.tsx
│   │   ├── DataTable.tsx
│   │   ├── Pagination.tsx
│   │   ├── Spinner.tsx
│   │   ├── SkeletonRow.tsx
│   │   └── EmptyState.tsx
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── SideNav.tsx
│   │   ├── NavItem.tsx
│   │   ├── NavGroup.tsx
│   │   ├── PageHeader.tsx
│   │   ├── Breadcrumb.tsx
│   │   ├── TopBar.tsx
│   │   └── StickyFormFooter.tsx
│   ├── dashboard/
│   │   ├── StatCard.tsx
│   │   ├── RecentPartiesTable.tsx
│   │   └── RecentFilingsTable.tsx
│   ├── parties/
│   │   ├── PartyTable.tsx
│   │   ├── PartyFilterBar.tsx
│   │   ├── PartyInfoCard.tsx
│   │   ├── PartyIdentifiersCard.tsx
│   │   ├── PartyClassificationsCard.tsx
│   │   ├── PartyContactsCard.tsx
│   │   ├── PartyNamesCard.tsx
│   │   ├── PartyRolesCard.tsx
│   │   ├── AssignRoleModal.tsx
│   │   └── RegisterPartyForm.tsx
│   ├── filings/
│   │   ├── FilingTable.tsx
│   │   ├── FilingFilterBar.tsx
│   │   ├── FilingInfoCard.tsx
│   │   ├── FilingLineItemsTable.tsx
│   │   ├── FilingStatusTimeline.tsx
│   │   ├── FilingOfficerNotesCard.tsx
│   │   └── CreateFilingForm.tsx
│   ├── assessments/
│   │   ├── AssessmentTable.tsx
│   │   ├── AssessmentFilterBar.tsx
│   │   ├── AssessmentInfoCard.tsx
│   │   ├── AssessmentFieldsCard.tsx
│   │   ├── AssessmentStatusTimeline.tsx
│   │   ├── AssessmentOfficerNotesCard.tsx
│   │   ├── AssessmentAppealCard.tsx
│   │   ├── AppealModal.tsx
│   │   └── CreateAssessmentForm.tsx
│   └── auth/
│       └── LoginForm.tsx
│
├── lib/
│   ├── api/
│   │   ├── client.ts
│   │   ├── parties.ts
│   │   ├── filings.ts
│   │   ├── assessments.ts
│   │   └── auth.ts
│   ├── hooks/
│   │   ├── useParties.ts
│   │   ├── useParty.ts
│   │   ├── useFilings.ts
│   │   ├── useFiling.ts
│   │   ├── useAssessments.ts
│   │   ├── useAssessment.ts
│   │   ├── useAuth.ts
│   │   └── useToast.ts
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   └── ToastContext.tsx
│   └── utils/
│       ├── formatDate.ts
│       ├── formatCurrency.ts
│       ├── formatPeriod.ts
│       └── cn.ts
│
└── types/
    ├── party.ts
    ├── filing.ts
    ├── assessment.ts
    ├── auth.ts
    └── api.ts
```
