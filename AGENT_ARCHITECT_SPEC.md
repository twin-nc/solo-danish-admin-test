# Agent Architect Specification — Danish Tax Administration Platform

**Status:** Authoritative source of truth for all Coder agents
**Date:** 2026-02-24
**Author:** Architect Agent
**Supersedes:** Nothing (first full spec)

---

## Table of Contents

1. [Frontend Architecture](#1-frontend-architecture)
2. [Authentication System](#2-authentication-system)
3. [Tax Filing Module](#3-tax-filing-module)
4. [Tax Assessment Module](#4-tax-assessment-module)
5. [Updated app/main.py Wiring](#5-updated-appmainpy-wiring)
6. [Alembic Migration Plan](#6-alembic-migration-plan)
7. [Cross-Module Event Flow Diagram](#7-cross-module-event-flow-diagram)
8. [API Contract Summary](#8-api-contract-summary)

---

## Architectural Principles (Non-Negotiable)

The following rules apply to every new module without exception. They mirror the existing Registration module exactly.

- **Layered flow:** Router -> Service -> Repository -> Model. No layer skips another.
- **Routers** are thin HTTP adapters. They call one service method and return a Pydantic schema. They never query the DB.
- **Services** enforce business rules and publish domain events. They never build HTTP responses or raw SQL.
- **Repositories** contain all SQLAlchemy queries. They receive a `db: Session` argument and return ORM objects. They contain no business logic.
- **Models** are SQLAlchemy 2.0 `Mapped`/`mapped_column` definitions with `TimestampMixin`.
- **Events** are Pydantic models extending `BaseEvent`. They are published by services and handled by handler functions registered in `main.py`.
- **Cross-module communication** happens exclusively through the `EventBus`. Modules never import each other's services.
- **Dependency injection** for services is done via `app.dependency_overrides` in `main.py`, exactly as `PartyService` is wired today.

---

## 1. Frontend Architecture

### 1.1 Framework and Runtime

| Concern | Decision |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS |
| State management | Zustand (lightweight, no boilerplate) |
| API communication | Typed `fetch` wrappers (no axios) |
| Auth token storage | HttpOnly cookies (set by the backend, never touched by JS) |
| Package manager | npm |

> **App Router rationale (Reviewer ACTION addressed):** Next.js App Router was selected over Pages Router primarily for its nested layout support — the admin shell (SideNav, PageHeader, ToastContainer) wraps all authenticated routes via `app/(authenticated)/layout.tsx` without prop drilling. React Server Components allow the dashboard stat cards to be fetched server-side on initial load, reducing client-side waterfall requests. For this authenticated admin tool the client/server boundary is kept simple: all data-fetching components are Server Components; interactive form components are Client Components. The complexity trade-off is justified by the zero-cost persistent layout and first-load performance benefit.

### 1.2 Folder Structure

The complete directory tree for `frontend/`. Every file listed here must be created.

```
frontend/
├── app/                              # Next.js App Router root
│   ├── layout.tsx                    # Root layout: sets <html>, loads fonts, wraps in providers
│   ├── page.tsx                      # Root redirect -> /dashboard or /login
│   ├── globals.css                   # Tailwind base imports
│   ├── (auth)/                       # Route group: no shared layout with app shell
│   │   └── login/
│   │       └── page.tsx              # Login page
│   ├── dashboard/
│   │   └── page.tsx                  # Dashboard overview (stats cards, recent activity)
│   ├── registrations/
│   │   ├── page.tsx                  # List of all parties
│   │   ├── new/
│   │   │   └── page.tsx              # Register a new party (multi-step form)
│   │   └── [partyId]/
│   │       ├── page.tsx              # Party detail view
│   │       └── roles/
│   │           └── new/
│   │               └── page.tsx      # Assign role to party
│   ├── filings/
│   │   ├── page.tsx                  # List all filings (officer/admin) or own filings (taxpayer)
│   │   ├── new/
│   │   │   └── page.tsx              # Create a new filing
│   │   └── [filingId]/
│   │       └── page.tsx              # Filing detail view
│   └── assessments/
│       ├── page.tsx                  # List all assessments (officer/admin)
│       └── [assessmentId]/
│           └── page.tsx              # Assessment detail view
│
├── components/                       # Reusable UI components
│   ├── layout/
│   │   ├── AppShell.tsx              # Sidebar + top nav wrapper
│   │   ├── Sidebar.tsx               # Left navigation (role-aware)
│   │   └── TopNav.tsx                # User menu, logout
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Badge.tsx                 # Status badge (DRAFT, SUBMITTED_WITH_RECEIPT, etc.)
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   ├── Spinner.tsx
│   │   └── ErrorMessage.tsx
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── ProtectedRoute.tsx        # Redirects to /login if not authenticated
│   ├── registrations/
│   │   ├── PartyForm.tsx
│   │   ├── PartyTable.tsx
│   │   └── RoleForm.tsx
│   ├── filings/
│   │   ├── FilingForm.tsx
│   │   ├── FilingTable.tsx
│   │   └── FilingStatusBadge.tsx
│   └── assessments/
│       ├── AssessmentForm.tsx
│       └── AssessmentTable.tsx
│
├── lib/                              # Shared utilities
│   ├── api/
│   │   ├── client.ts                 # Base fetch wrapper (handles cookies, errors)
│   │   ├── auth.ts                   # Auth API calls (login, logout, refresh, me)
│   │   ├── parties.ts                # Party + role API calls
│   │   ├── filings.ts                # Filing API calls
│   │   └── assessments.ts            # Assessment API calls
│   ├── auth/
│   │   └── context.tsx               # AuthContext + useAuth hook (wraps Zustand store)
│   └── utils/
│       ├── formatters.ts             # Date, currency, period formatters
│       └── validators.ts             # Client-side form validation helpers
│
├── store/
│   ├── authStore.ts                  # Zustand store: current user, isAuthenticated
│   └── uiStore.ts                    # Zustand store: loading states, toast notifications
│
├── types/
│   ├── api.ts                        # Shared API response types (matches Pydantic schemas exactly)
│   ├── auth.ts                       # User, Role, LoginRequest, TokenResponse
│   ├── party.ts                      # PartyRead, PartyCreate, PartyRoleRead, etc.
│   ├── filing.ts                     # FilingRead, FilingCreate, LineItemRead, etc.
│   └── assessment.ts                 # AssessmentRead, AssessmentCreate, etc.
│
├── middleware.ts                     # Next.js middleware: redirect unauthenticated requests
├── next.config.ts                    # NEXT_PUBLIC_API_URL rewrite + config
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local                        # Environment variables (never committed)
```

### 1.3 State Management (Zustand)

Two stores are used. Both are created with `zustand` and accessed via custom hooks.

**`store/authStore.ts`**
```typescript
import { create } from 'zustand';
import { User } from '@/types/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: user !== null }),
  clearAuth: () => set({ user: null, isAuthenticated: false }),
}));
```

**`store/uiStore.ts`**
```typescript
import { create } from 'zustand';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

interface UiState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  toasts: [],
  addToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id: crypto.randomUUID() }],
    })),
  removeToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}));
```

### 1.4 API Client Pattern

All HTTP calls go through a single base client that:
- Includes credentials (cookies) on every request
- Handles 401 responses by attempting a token refresh, then retrying once
- Throws a typed `ApiError` on non-OK responses

**`lib/api/client.ts`**
```typescript
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (res.status === 401 && retry) {
    const refreshRes = await fetch(`${BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });
    if (refreshRes.ok) {
      return request<T>(path, options, false);
    }
    window.location.href = '/login';
    throw new ApiError(401, 'Session expired');
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get:    <T>(path: string) => request<T>(path, { method: 'GET' }),
  post:   <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch:  <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
```

**`lib/api/filings.ts`**
```typescript
import { api } from './client';
import { FilingCreate, FilingRead } from '@/types/filing';

export const filingsApi = {
  create:      (body: FilingCreate) =>
    api.post<FilingRead>('/api/v1/filings', body),
  getById:     (id: string) =>
    api.get<FilingRead>(`/api/v1/filings/${id}`),
  listByParty: (partyId: string) =>
    api.get<FilingRead[]>(`/api/v1/parties/${partyId}/filings`),
  submit:      (id: string) =>
    api.patch<FilingRead>(`/api/v1/filings/${id}/submit`, {}),
};
```

**`lib/api/assessments.ts`**
```typescript
import { api } from './client';
import { AssessmentCreate, AssessmentRead, AssessmentStatusUpdate } from '@/types/assessment';

export const assessmentsApi = {
  create:       (body: AssessmentCreate) =>
    api.post<AssessmentRead>('/api/v1/assessments', body),
  getById:      (id: string) =>
    api.get<AssessmentRead>(`/api/v1/assessments/${id}`),
  getByFiling:  (filingId: string) =>
    api.get<AssessmentRead>(`/api/v1/filings/${filingId}/assessment`),
  updateStatus: (id: string, body: AssessmentStatusUpdate) =>
    api.patch<AssessmentRead>(`/api/v1/assessments/${id}/status`, body),
};
```

**`lib/api/auth.ts`**
```typescript
import { api } from './client';
import { LoginRequest, User } from '@/types/auth';

export const authApi = {
  login:   (body: LoginRequest) =>
    api.post<{ message: string }>('/api/v1/auth/login', body),
  refresh: () =>
    api.post<{ message: string }>('/api/v1/auth/refresh', {}),
  logout:  () =>
    api.post<{ message: string }>('/api/v1/auth/logout', {}),
  me:      () =>
    api.get<User>('/api/v1/auth/me'),
};
```

### 1.5 Environment Variables

**`.env.local`**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 1.6 Route Protection

**`middleware.ts`**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/login'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const isPublic = PUBLIC_PATHS.some((p) =>
    request.nextUrl.pathname.startsWith(p),
  );

  if (!token && !isPublic) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

---

## 2. Authentication System

### 2.1 Overview

| Concern | Decision |
|---|---|
| Token type | JWT (HS256) |
| Access token expiry | 15 minutes |
| Refresh token expiry | 7 days |
| Storage | HttpOnly, Secure, SameSite=Lax cookies |
| Secret | `SECRET_KEY` environment variable (min 32 chars) |
| Algorithm | HS256 |
| Library | `python-jose[cryptography]` + `passlib[bcrypt]` |

Tokens are **never** returned in the JSON response body. They are always delivered exclusively via `Set-Cookie` headers to prevent XSS access.

> **Refresh token limitation (Reviewer ACTION addressed):** The logout endpoint clears the HttpOnly cookie on the client side but does not server-side invalidate the JWT. A stolen refresh token remains valid for up to 7 days. For this internal admin tool at Phase 2, this is an accepted trade-off. Token revocation via a server-side blocklist (Redis or database) is a Phase 3 security hardening concern.

### 2.2 New Database Table: `users`

**`app/models/user.py`**
```python
import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ADMIN | OFFICER | TAXPAYER
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    # Nullable FK — only populated for TAXPAYER users; ADMIN and OFFICER leave this NULL.
    # Used for the TAXPAYER authorization predicate: current_user.party_id == resource.party_id.
    party_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parties.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
```

**Valid `role` values:**

| Value | Description |
|---|---|
| `ADMIN` | Full access. Can manage users, view all data, configure the system. |
| `OFFICER` | Tax officer. Can create assessments, review filings, view all parties. |
| `TAXPAYER` | Represents an individual or business. Can see and manage their own filings only. |

### 2.3 Updated `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
```

Add to `.env`:
```
SECRET_KEY=change-me-to-a-random-32-character-string-in-production
```

### 2.4 New API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Authenticate user; sets access + refresh token cookies |
| POST | `/api/v1/auth/refresh` | Rotate tokens using valid refresh cookie |
| POST | `/api/v1/auth/logout` | Clear both token cookies |
| GET | `/api/v1/auth/me` | Return current user details |

### 2.5 Pydantic Schemas

**`app/schemas/auth.py`**
```python
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    party_id: uuid.UUID | None  # None for ADMIN / OFFICER users
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "UserRead":
        return cls(
            id=obj.id,
            email=obj.email,
            full_name=obj.full_name,
            role=obj.role,
            is_active=obj.is_active,
            party_id=obj.party_id,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "TAXPAYER"
    party_id: uuid.UUID | None = None  # Required when role == "TAXPAYER"
```

**Token cookie specification:**

| Cookie name | HttpOnly | Secure | SameSite | Max-Age |
|---|---|---|---|---|
| `access_token` | Yes | True (prod) | Lax | 900s |
| `refresh_token` | Yes | True (prod) | Lax | 604800s |

### 2.6 FastAPI Dependencies

**`app/dependencies/auth.py`**
```python
import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.user import User


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    payload = _decode_token(access_token)
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = (
        db.query(User)
        .filter(User.id == uuid.UUID(user_id), User.is_active == True)  # noqa: E712
        .first()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_role(*roles: str):
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role}' is not permitted. "
                    f"Required: {list(roles)}"
                ),
            )
        return current_user
    return _check
```

### 2.7 Auth Router

**`app/routers/auth.py`**
```python
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.dependencies.auth import _decode_token, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, UserRead

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(
        {"sub": subject, "exp": expire, "type": token_type},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def _set_auth_cookies(response: Response, user_id: str) -> None:
    access_token = _create_token(
        user_id,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )
    refresh_token = _create_token(
        user_id,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )
    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


@router.post("/login")
async def login(
    payload: LoginRequest, response: Response, db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == payload.email, User.is_active == True)  # noqa: E712
        .first()
    )
    if user is None or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    _set_auth_cookies(response, str(user.id))
    return {"message": "ok"}


@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    payload = _decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id: str = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()  # noqa: E712
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    _set_auth_cookies(response, user_id)
    return {"message": "ok"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "ok"}


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.from_orm(current_user)
```

### 2.8 Authorization and Ownership Policy (Hard Rule)

All protected endpoints use deny-by-default authorization with explicit row-level ownership checks.

- `ADMIN`: full read/write access to all resources.
- `OFFICER`: full read/write for parties, filings, and assessments; no admin user/settings writes.
- `TAXPAYER`: may only read/write resources where `resource.party_id == current_user.party_id`.

Ownership enforcement contract:

| Resource | Ownership predicate for TAXPAYER | Failure mode |
|---|---|---|
| `Party` | `party.id == current_user.party_id` | Return `404` to avoid enumeration |
| `Filing` | `filing.party_id == current_user.party_id` | Return `404` to avoid enumeration |
| `Assessment` | `assessment.filing.party_id == current_user.party_id` | Return `404` to avoid enumeration |

Shared auth failure rules:

- Not authenticated: `401`.
- Authenticated but missing role: `403`.
- Domain validation failure: `422`.
- Business rule conflict (duplicate filing/assessment): `409`.

---

## 3. Tax Filing Module

### 3.1 Overview

Phase 2 filing is VAT-first (`4C` decision): canonical persistence and API payload are fixed official VAT fields. Optional line-item detail is allowed only as a non-canonical convenience payload.

| Registration (existing) | Filing (new) |
|---|---|
| `app/models/party.py` | `app/models/filing.py` |
| `app/schemas/party.py` | `app/schemas/filing.py` |
| `app/repositories/party.py` | `app/repositories/filing.py` |
| `app/services/party.py` | `app/services/filing.py` |
| `app/events/party_events.py` | `app/events/filing_events.py` |
| `app/events/handlers/party_handlers.py` | `app/events/handlers/filing_handlers.py` |
| `app/routers/parties.py` | `app/routers/filings.py` |

### 3.1.1 Canonical State Transition Table (Single Source of Truth)

The following table is the only valid state machine for Filing + Assessment side effects.

| Trigger | Preconditions | Filing transition | Assessment transition | Required side effects |
|---|---|---|---|---|
| `POST /api/v1/filings` | Role + ownership pass | `NONE -> DRAFT` | `NONE` | Compute `momstilsvar` and `frist` |
| `PATCH /api/v1/filings/{id}/submit` | Filing is `DRAFT` | `DRAFT -> SUBMITTED_WITH_RECEIPT` | `NONE` | Compute deterministic legal deadline, then apply policy-driven late fee/interest hooks |
| `POST /api/v1/assessments` | Filing is `SUBMITTED_WITH_RECEIPT` | `NO_CHANGE` | `NONE -> PENDING` | Publish assessment events only; filing status is not implicitly mutated |
| `PATCH /api/v1/assessments/{id}/status` | Assessment is `PENDING` or `COMPLETE` | `NO_CHANGE` | `PENDING -> COMPLETE` or `COMPLETE -> APPEALED` | Persist decision outcome, surcharge, interest, and deadlines |
| `POST /api/v1/assessments/{id}/appeal` | Assessment is `COMPLETE`, caller owns filing | `NO_CHANGE` | `COMPLETE -> APPEALED` | Set `appealed_at`; enforce 3-month appeal deadline |
| `POST /api/v1/filings/{id}/correct` | Filing status in `{SUBMITTED_WITH_RECEIPT, ACCEPTED, REJECTED}` | previous version -> `CORRECTED`; new version `DRAFT` | `NONE` | Increment filing `version`, link `original_filing_id` |

State policy note: Filing and Assessment are decoupled state machines. Assessment endpoints (`/api/v1/assessments*`) MUST keep filing transition as `NO_CHANGE`; filing status transitions are allowed only through explicit filing endpoints. `UNDER_REVIEW` is reserved/deferred in Phase 2 for forward compatibility and is excluded from active Phase 2 transition paths.

### 3.1.2 Researcher/Designer Alignment Notes (Pass 2)

- Legal baseline references consumed: `C02`, `C03`, `C05`, `C06`, `C10`, `C12`, `C16` from latest `AGENT_RESEARCHER_SPEC.md`.
- Canonical shape remains fixed VAT fields (4C hard rule); line-item transport is accepted only as temporary non-canonical adapter input.
- Assessment create/update does not mutate filing status implicitly (matched to latest `AGENT_DESIGN_SPEC.md` flow/state expectations).

### 3.1.3 momstilsvar Formula (Explicit Statement — Reviewer ACTION addressed)

The canonical VAT balance formula mandated by **Momsloven §56** is:

```
momstilsvar = Rubrik A + Rubrik C + Rubrik E − Rubrik B
```

Where:
- **Rubrik A** — Udgående moms (output VAT at 25% on taxable sales)
- **Rubrik B** — Indgående moms (input VAT deductible — purchases for business use)
- **Rubrik C** — Moms af EU-erhvervelser (VAT on EU acquisitions, self-assessed)
- **Rubrik D** — Momspligtig omsætning (taxable turnover — informational, not in formula)
- **Rubrik E** — Moms ved importafgiftsordning (VAT at import, reverse charge)

A positive `momstilsvar` means the taxpayer owes VAT to SKAT (PAYABLE). A negative value means SKAT owes a refund (REFUNDABLE). Zero means no payment (NIL).

This formula is implemented in `FilingService._compute_momstilsvar` (Section 3.5) and is enforced at the database level via the `momstilsvar` column, which is computed and stored at draft creation time (not recalculated at submission). The Designer's Momsangivelse form (AGENT_DESIGN_SPEC.md — Create Filing page) shows all five Rubrik fields and the computed `momstilsvar` result inline.

### 3.1.4 Late Submission Behaviour (Reviewer ACTION addressed)

A late submission is a filing submitted after its `frist` (deadline). Phase 2 policy:

1. **Late filings are accepted** — `submit_filing` does not block a submission because `submitted_at > frist`. SKAT's own system (TastSelv) also accepts late filings with a penalty.
2. **Penalty computed at submission time** — `late_filing_days = (submitted_at.date() - frist).days` and `late_filing_penalty = VatPolicy.late_filing_fee_amount` (per `Opkrævningslovens § 4`). Both values are persisted on the `Filing` row.
3. **`FilingPenaltyAccrued` event published** — if `late_filing_days > 0`. Subscribers log the penalty; no automatic workflow is triggered.
4. **Filing status after late submission** — the same `SUBMITTED_WITH_RECEIPT`. There is no separate "late" status in Phase 2. The `late_filing_days > 0` field signals lateness to the UI.
5. **Provisional assessment on late filing** — deferred to Phase 3. The Assessment module does not create a provisional assessment automatically in Phase 2.

### 3.1.5 kvitteringsnummer (Reviewer ACTION addressed)

In Phase 2, `kvitteringsnummer` is generated locally by the platform as a deterministic reference string:

```
KVIT-{se_nummer}-{filing_period}-{unix_timestamp_seconds}
```

Example: `KVIT-12345678-2025-Q3-1735689600`

This format is stable and can be asserted on in tests. SKAT integration for receiving an external receipt number from the TastSelv API is deferred to Phase 3. The `kvitteringsnummer` column stores this platform-generated value at submission time.

### 3.1.6 Assessment Officer Assignment (Reviewer ACTION addressed)

An `assessed_by` field exists on `TaxAssessment` recording which officer created the assessment. Reassigning a different officer after creation (`PATCH /api/v1/assessments/{id}/assign`) is **deferred to Phase 3**. Phase 2 officers cannot transfer ownership of an assessment after it is created.

### 3.1.7 Frist (Deadline) Legal Citations

The filing deadline day-of-month values in `_compute_deadline` are based on:

- **MONTHLY (25th of following month):** Momslovens § 57, stk. 3 — "angivelsen og betalingen skal ske senest den 25. i den måned, der følger efter afgiftsperiodens udløb."
- **QUARTERLY (10th of second month after quarter end):** Momslovens § 57, stk. 4 — "angivelsen og betalingen skal ske senest den 10. i den anden måned efter afgiftsperiodens udløb." Quarter end months: Mar (Q1), Jun (Q2), Sep (Q3), Dec (Q4); deadlines: May 10 (Q1), Aug 10 (Q2), Nov 10 (Q3), Feb 10 of next year (Q4).
- **SEMI-ANNUAL (1 Sep and 1 Mar):** Momslovens § 57, stk. 5 — for the smallest registrants; first half deadline: September 1; second half deadline: March 1 of following year.

All deadlines are adjusted to the next open bank day via `VatPolicyRepository.get_next_open_bank_day` if the statutory date falls on a weekend or public holiday.
- Receipt state is explicit and retrievable (`receipt_id`, `submitted_at`, `submission_outcome`).

### 3.2 Domain Model

**`app/models/filing.py`**
```python
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class Filing(Base, TimestampMixin):
    __tablename__ = "filings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    se_nummer: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    afregningsperiode_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Values: MONTHLY | QUARTERLY | SEMI_ANNUAL
    filing_period: Mapped[str] = mapped_column(String(20), nullable=False)
    # Values: YYYY-MM | YYYY-Q1..Q4 | YYYY-H1..H2
    angivelse_type: Mapped[str] = mapped_column(String(20), nullable=False, default="MOMS")
    # Phase 2 hard constraint: only "MOMS" accepted
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Canonical Rubrik fields (fixed official VAT return shape)
    rubrik_a: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_b: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_c: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_d: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    rubrik_e: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    momspligtig_omsaetning: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    momsfri_omsaetning: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    eksport: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    momstilsvar: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))

    frist: Mapped[date] = mapped_column(Date, nullable=False)
    late_filing_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    late_filing_penalty: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    kvitteringsnummer: Mapped[str | None] = mapped_column(String(64), nullable=True)
    submission_outcome: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Values after submit: PAYABLE | REFUNDABLE | NIL

    korrektionsangivelse: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    original_filing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filings.id", ondelete="SET NULL"), nullable=True
    )

    # Optional convenience detail from bookkeeping imports. Non-canonical.
    supplemental_line_items: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        # Partial unique index: only one canonical (non-correction) filing per
        # (se_nummer, filing_period, angivelse_type). Corrections (korrektionsangivelse=True)
        # are intentionally excluded so multiple correction versions can coexist.
        # Race-condition safety: the service layer catches IntegrityError on conflict.
        Index(
            "uq_filing_canonical_se_period_type",
            "se_nummer", "filing_period", "angivelse_type",
            unique=True,
            postgresql_where="korrektionsangivelse = false",
        ),
    )
```

**Valid field values:**

| Field | Valid Values |
|---|---|
| `angivelse_type` | `MOMS` (Phase 2), all other return types explicitly deferred |
| `status` | `DRAFT`, `SUBMITTED_WITH_RECEIPT`, `UNDER_REVIEW`, `ACCEPTED`, `REJECTED`, `CORRECTED` |
| `afregningsperiode_type` | `MONTHLY`, `QUARTERLY`, `SEMI_ANNUAL` |
| `filing_period` | `YYYY-MM` (monthly), `YYYY-QN` (quarterly), `YYYY-HN` (semi-annual) |
| `submission_outcome` | `PAYABLE`, `REFUNDABLE`, `NIL` (computed at submission) |

`UNDER_REVIEW` is reserved/deferred in Phase 2 (forward compatibility only) and is not part of active Phase 2 transition paths. `ACCEPTED` and `REJECTED` are filing-domain statuses and are never set by assessment endpoints.

### 3.3 Pydantic Schemas

**`app/schemas/filing.py`**
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FilingLineItemTransport(BaseModel):
    code: str = Field(..., examples=["RUBRIK_A", "RUBRIK_B", "MOMSPLIGTIG"])
    amount: Decimal = Field(..., examples=[Decimal("1200.00")])


class FilingCreate(BaseModel):
    party_id: uuid.UUID
    se_nummer: str = Field(..., min_length=8, max_length=8, examples=["12345678"])
    afregningsperiode_type: str = Field(..., examples=["QUARTERLY"])
    filing_period: str = Field(..., examples=["2024-Q1"])
    angivelse_type: str = Field(default="MOMS", examples=["MOMS"])
    rubrik_a: Decimal = Field(default=Decimal("0.00"))
    rubrik_b: Decimal = Field(default=Decimal("0.00"))
    rubrik_c: Decimal = Field(default=Decimal("0.00"))
    rubrik_d: Decimal = Field(default=Decimal("0.00"))
    rubrik_e: Decimal = Field(default=Decimal("0.00"))
    momspligtig_omsaetning: Decimal = Field(default=Decimal("0.00"))
    momsfri_omsaetning: Decimal = Field(default=Decimal("0.00"))
    eksport: Decimal = Field(default=Decimal("0.00"))
    # Transitional compatibility only. Non-canonical input shape from older UI adapters.
    line_items: list[FilingLineItemTransport] | None = None
    supplemental_line_items: list[dict] | None = None


class FilingRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    party_id: uuid.UUID
    se_nummer: str
    afregningsperiode_type: str
    filing_period: str
    angivelse_type: str
    status: str
    version: int
    rubrik_a: Decimal
    rubrik_b: Decimal
    rubrik_c: Decimal
    rubrik_d: Decimal
    rubrik_e: Decimal
    momspligtig_omsaetning: Decimal
    momsfri_omsaetning: Decimal
    eksport: Decimal
    momstilsvar: Decimal
    frist: date
    late_filing_days: int
    late_filing_penalty: Decimal
    submitted_at: datetime | None
    kvitteringsnummer: str | None
    submission_outcome: str | None
    korrektionsangivelse: bool
    original_filing_id: uuid.UUID | None
    supplemental_line_items: list[dict] | None
    created_at: datetime
    updated_at: datetime


class FilingReceiptRead(BaseModel):
    filing_id: uuid.UUID
    receipt_id: str
    submitted_at: datetime
    submission_outcome: str
    momstilsvar: Decimal


class FilingDeadlineRead(BaseModel):
    party_id: uuid.UUID
    period_key: str
    afregningsperiode_type: str
    deadline: date
    rule_basis: str
```

### 3.4 Repository

**`app/repositories/filing.py`**
```python
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.filing import Filing
from app.schemas.filing import FilingCreate


class FilingRepository:

    def create_filing(
        self, payload: FilingCreate, computed_momstilsvar, computed_frist, version: int, db: Session
    ) -> Filing:
        filing = Filing(
            party_id=payload.party_id, filing_period=payload.filing_period,
            se_nummer=payload.se_nummer,
            afregningsperiode_type=payload.afregningsperiode_type,
            angivelse_type=payload.angivelse_type,
            status="DRAFT", version=version,
            rubrik_a=payload.rubrik_a, rubrik_b=payload.rubrik_b, rubrik_c=payload.rubrik_c,
            rubrik_d=payload.rubrik_d, rubrik_e=payload.rubrik_e,
            momspligtig_omsaetning=payload.momspligtig_omsaetning,
            momsfri_omsaetning=payload.momsfri_omsaetning, eksport=payload.eksport,
            momstilsvar=computed_momstilsvar, frist=computed_frist,
            supplemental_line_items=payload.supplemental_line_items,
        )
        db.add(filing)
        db.commit()
        return filing

    def get_filing_by_id(self, filing_id: uuid.UUID, db: Session) -> Filing | None:
        return db.query(Filing).filter(Filing.id == filing_id).first()

    def list_filings_by_party(self, party_id: uuid.UUID, db: Session) -> list[Filing]:
        return db.query(Filing).filter(Filing.party_id == party_id).order_by(Filing.created_at.desc()).all()

    def list_filings(self, db: Session) -> list[Filing]:
        return db.query(Filing).order_by(Filing.created_at.desc()).all()

    def submit_filing(
        self,
        filing_id: uuid.UUID,
        submitted_at: datetime,
        late_days: int,
        late_penalty,
        receipt_id: str,
        submission_outcome: str,
        db: Session,
    ) -> Filing | None:
        filing = db.query(Filing).filter(Filing.id == filing_id).first()
        if filing is None:
            return None
        filing.status = "SUBMITTED_WITH_RECEIPT"
        filing.submitted_at = submitted_at
        filing.late_filing_days = late_days
        filing.late_filing_penalty = late_penalty
        filing.kvitteringsnummer = receipt_id
        filing.submission_outcome = submission_outcome
        db.commit()
        return filing

    def mark_corrected(self, filing_id: uuid.UUID, db: Session) -> None:
        filing = db.query(Filing).filter(Filing.id == filing_id).first()
        if filing is not None:
            filing.status = "CORRECTED"
            db.commit()
```

### 3.4.1 VatPolicy Model and Repository

The `FilingService` must not hardcode legal constants such as the late-filing penalty amount (DKK 1,400 as of the current policy). Instead, these values are stored in a `vat_policies` table and read at runtime. This allows administrators to update them without a code deployment.

**`app/models/vat_policy.py`**
```python
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class VatPolicy(Base, TimestampMixin):
    """
    Stores time-bound policy values that would otherwise require code changes
    (e.g. the late-filing fee mandated by Opkrævningslovens § 4).

    Only one record is active at any point in time: the row whose
    effective_from is the most recent date <= today, with effective_to
    either NULL (open-ended) or >= today.

    Seed the table with a single row on first deployment:
        effective_from = 2024-01-01
        effective_to   = NULL
        late_filing_fee_amount = 800.00  (DKK 800 per Opkrævningsloven)
        bank_holidays_json = '[]'         (populate as needed)
    """
    __tablename__ = "vat_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Late-filing fee per Opkrævningslovens § 4 (currently DKK 800 per overdue period).
    # Stored as a policy value so it can be updated without a code deployment.
    late_filing_fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default="800.00"
    )
    # ISO-8601 date strings of Danish bank holidays, stored as a JSON array.
    # Used by get_next_open_bank_day to skip non-business days.
    # Example: '["2026-01-01", "2026-04-17", "2026-12-25", "2026-12-26"]'
    bank_holidays_json: Mapped[str] = mapped_column(
        String, nullable=False, server_default="'[]'"
    )
```

**`app/repositories/policy.py`**
```python
import json
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.vat_policy import VatPolicy


class VatPolicyRepository:
    def get_active_policy(self, as_of: date, db: Session) -> VatPolicy:
        """Return the policy row whose effective window contains *as_of*.

        Falls back to the most recent row if no open-ended record exists, so
        the system always returns *something* rather than failing hard.
        """
        record = (
            db.query(VatPolicy)
            .filter(
                VatPolicy.effective_from <= as_of,
                (VatPolicy.effective_to == None) | (VatPolicy.effective_to >= as_of),  # noqa: E711
            )
            .order_by(VatPolicy.effective_from.desc())
            .first()
        )
        if record is None:
            # Ultimate fallback — no policy rows exist; return a default object
            # so callers never receive None. Coder agent: add an alembic seed
            # migration that inserts one row to prevent this path in production.
            fallback = VatPolicy()
            fallback.late_filing_fee_amount = Decimal("800.00")
            fallback.bank_holidays_json = "[]"
            return fallback
        return record

    def get_next_open_bank_day(self, candidate: date, db: Session) -> date:
        """Advance *candidate* past weekends and Danish bank holidays.

        Reads holiday dates from the active policy's ``bank_holidays_json``
        field so that the list can be maintained in the database without a
        code deployment.
        """
        policy = self.get_active_policy(candidate, db)
        holidays: set[date] = {
            date.fromisoformat(d) for d in json.loads(policy.bank_holidays_json)
        }
        result = candidate
        while result.weekday() >= 5 or result in holidays:  # 5=Sat, 6=Sun
            result += timedelta(days=1)
        return result
```

> **Migration note:** `vat_policies` is created in **Migration 0005** (see Section 9). A seed row with `effective_from = 2024-01-01`, `effective_to = NULL`, `late_filing_fee_amount = 800.00`, and `bank_holidays_json = '[]'` is inserted in the same migration so that the system is immediately usable without manual data setup.

---

### 3.5 Service

**`app/services/filing.py`**
```python
import re
import uuid
from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.events.base import EventBus
from app.events.filing_events import FilingCorrected, FilingCreated, FilingPenaltyAccrued, FilingSubmitted
from app.models.filing import Filing
from app.repositories.filing import FilingRepository
from app.repositories.policy import VatPolicyRepository
from app.schemas.filing import FilingCreate, FilingDeadlineRead, FilingReceiptRead
from app.services.authz import AuthorizationPolicy

MONTHLY_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
QUARTERLY_PATTERN = re.compile(r"^\d{4}-Q[1-4]$")
SEMI_ANNUAL_PATTERN = re.compile(r"^\d{4}-H[1-2]$")


class FilingService:
    def __init__(
        self,
        repo: FilingRepository,
        policy_repo: VatPolicyRepository,
        bus: EventBus,
        authz: AuthorizationPolicy,
    ) -> None:
        self._repo = repo
        self._policy_repo = policy_repo
        self._bus = bus
        self._authz = authz

    def _normalize_legacy_line_items(self, payload: FilingCreate) -> FilingCreate:
        # Transitional bridge for Designer adapter payloads; canonical fields stay source of truth.
        if not payload.line_items:
            return payload
        mapped = {item.code.upper(): item.amount for item in payload.line_items}
        payload.rubrik_a = payload.rubrik_a or mapped.get("RUBRIK_A", Decimal("0.00"))
        payload.rubrik_b = payload.rubrik_b or mapped.get("RUBRIK_B", Decimal("0.00"))
        payload.rubrik_c = payload.rubrik_c or mapped.get("RUBRIK_C", Decimal("0.00"))
        payload.rubrik_d = payload.rubrik_d or mapped.get("RUBRIK_D", Decimal("0.00"))
        payload.rubrik_e = payload.rubrik_e or mapped.get("RUBRIK_E", Decimal("0.00"))
        payload.momspligtig_omsaetning = payload.momspligtig_omsaetning or mapped.get("MOMSPLIGTIG", Decimal("0.00"))
        payload.momsfri_omsaetning = payload.momsfri_omsaetning or mapped.get("MOMSFRI", Decimal("0.00"))
        payload.eksport = payload.eksport or mapped.get("EKSPORT", Decimal("0.00"))
        return payload

    def _compute_momstilsvar(self, payload: FilingCreate) -> Decimal:
        return payload.rubrik_a + payload.rubrik_c + payload.rubrik_e - payload.rubrik_b

    def _next_bank_day(self, candidate: date, db: Session) -> date:
        return self._policy_repo.get_next_open_bank_day(candidate, db)

    def _compute_deadline(self, afregningsperiode_type: str, filing_period: str) -> date:
        if afregningsperiode_type == "MONTHLY":
            if not MONTHLY_PATTERN.match(filing_period):
                raise HTTPException(status_code=422, detail="MONTHLY periods must use YYYY-MM")
            year, month = filing_period.split("-")
            y = int(year)
            m = int(month)
            deadline_month = 1 if m == 12 else m + 1
            deadline_year = y + 1 if m == 12 else y
            return date(deadline_year, deadline_month, 25)

        if afregningsperiode_type == "QUARTERLY":
            if not QUARTERLY_PATTERN.match(filing_period):
                raise HTTPException(status_code=422, detail="QUARTERLY periods must use YYYY-Qn")
            year = int(filing_period[:4])
            quarter = int(filing_period[-1])
            quarter_end_month = quarter * 3
            deadline_month = quarter_end_month + 2
            deadline_year = year
            if deadline_month > 12:
                deadline_month -= 12
                deadline_year += 1
            return date(deadline_year, deadline_month, 10)

        if afregningsperiode_type == "SEMI_ANNUAL":
            if not SEMI_ANNUAL_PATTERN.match(filing_period):
                raise HTTPException(status_code=422, detail="SEMI_ANNUAL periods must use YYYY-Hn")
            year = int(filing_period[:4])
            half = int(filing_period[-1])
            if half == 1:
                return date(year, 9, 1)
            return date(year + 1, 3, 1)

        raise HTTPException(status_code=422, detail=f"Unsupported afregningsperiode_type: {afregningsperiode_type}")

    def _late_penalty(self, deadline: date, submitted_at: datetime, db: Session) -> tuple[int, Decimal]:
        late_days = max((submitted_at.date() - deadline).days, 0)
        if late_days == 0:
            return 0, Decimal("0.00")
        policy = self._policy_repo.get_active_policy(submitted_at.date(), db)
        amount = policy.late_filing_fee_amount
        return late_days, amount

    def _submission_outcome(self, momstilsvar: Decimal) -> str:
        if momstilsvar > Decimal("0.00"):
            return "PAYABLE"
        if momstilsvar < Decimal("0.00"):
            return "REFUNDABLE"
        return "NIL"

    async def create_filing(self, payload: FilingCreate, current_user, db: Session, as_correction: bool = False) -> Filing:
        self._authz.assert_can_create_filing(current_user, payload.party_id)
        payload = self._normalize_legacy_line_items(payload)
        if payload.angivelse_type != "MOMS":
            raise HTTPException(status_code=422, detail="Phase 2 supports only angivelse_type='MOMS'")
        momstilsvar = self._compute_momstilsvar(payload)
        frist = self._next_bank_day(self._compute_deadline(payload.afregningsperiode_type, payload.filing_period), db)
        latest = self._repo.list_filings_by_party(payload.party_id, db)
        period_versions = [f.version for f in latest if f.filing_period == payload.filing_period and f.se_nummer == payload.se_nummer]
        if period_versions and not as_correction:
            raise HTTPException(status_code=409, detail="Canonical filing already exists for this se_nummer + period")
        next_version = 1 if not period_versions else max(period_versions) + 1
        filing = self._repo.create_filing(payload, momstilsvar, frist, next_version, db)
        await self._bus.publish(FilingCreated(
            filing_id=filing.id, party_id=filing.party_id,
            se_nummer=filing.se_nummer, filing_period=filing.filing_period,
            angivelse_type=filing.angivelse_type, momstilsvar=filing.momstilsvar, frist=filing.frist,
        ))
        return filing

    async def get_filing(self, filing_id: uuid.UUID, current_user, db: Session) -> Filing:
        filing = self._repo.get_filing_by_id(filing_id, db)
        if filing is None:
            raise HTTPException(status_code=404, detail="Filing not found")
        self._authz.assert_can_read_filing(current_user, filing)
        return filing

    async def list_filings_for_party(self, party_id: uuid.UUID, current_user, db: Session) -> list[Filing]:
        self._authz.assert_can_read_party(current_user, party_id)
        return self._repo.list_filings_by_party(party_id, db)

    async def list_filings(self, current_user, db: Session) -> list[Filing]:
        if current_user.role == "TAXPAYER":
            return self._repo.list_filings_by_party(current_user.party_id, db)
        return self._repo.list_filings(db)

    async def submit_filing(self, filing_id: uuid.UUID, current_user, db: Session) -> Filing:
        filing = self._repo.get_filing_by_id(filing_id, db)
        if filing is None:
            raise HTTPException(status_code=404, detail="Filing not found")
        self._authz.assert_can_edit_filing(current_user, filing)
        if filing.status != "DRAFT":
            raise HTTPException(
                status_code=400,
                detail=f"Filing cannot be submitted from status '{filing.status}'. Only DRAFT filings may be submitted.",
            )
        submitted_at = datetime.now(timezone.utc)
        late_days, late_penalty = self._late_penalty(filing.frist, submitted_at, db)
        receipt_id = f"KVIT-{filing.se_nummer}-{filing.filing_period}-{int(submitted_at.timestamp())}"
        submission_outcome = self._submission_outcome(filing.momstilsvar)
        filing = self._repo.submit_filing(
            filing_id, submitted_at, late_days, late_penalty, receipt_id, submission_outcome, db
        )
        await self._bus.publish(FilingSubmitted(
            filing_id=filing.id, party_id=filing.party_id,
            se_nummer=filing.se_nummer, angivelse_type=filing.angivelse_type,
            filing_period=filing.filing_period, momstilsvar=filing.momstilsvar,
            frist=filing.frist, late_filing_days=filing.late_filing_days,
            late_filing_penalty=filing.late_filing_penalty,
        ))
        if filing.late_filing_days > 0:
            await self._bus.publish(FilingPenaltyAccrued(
                filing_id=filing.id, party_id=filing.party_id,
                days_overdue=filing.late_filing_days, penalty_amount=filing.late_filing_penalty,
            ))
        return filing

    async def correct_filing(self, filing_id: uuid.UUID, payload: FilingCreate, current_user, db: Session) -> Filing:
        original = await self.get_filing(filing_id, current_user, db)
        if original.status not in {"SUBMITTED_WITH_RECEIPT", "ACCEPTED", "REJECTED"}:
            raise HTTPException(
                status_code=400,
                detail="Only filings in SUBMITTED_WITH_RECEIPT, ACCEPTED, or REJECTED can be corrected",
            )
        payload.angivelse_type = original.angivelse_type
        payload.party_id = original.party_id
        payload.se_nummer = original.se_nummer
        correction = await self.create_filing(payload, current_user, db, as_correction=True)
        correction.korrektionsangivelse = True
        correction.original_filing_id = original.id
        db.commit()
        self._repo.mark_corrected(original.id, db)
        await self._bus.publish(FilingCorrected(
            original_filing_id=original.id, corrected_filing_id=correction.id,
            party_id=original.party_id, se_nummer=original.se_nummer,
        ))
        return correction

    async def get_receipt(self, filing_id: uuid.UUID, current_user, db: Session) -> FilingReceiptRead:
        filing = await self.get_filing(filing_id, current_user, db)
        if filing.status != "SUBMITTED_WITH_RECEIPT" or not filing.kvitteringsnummer or not filing.submitted_at:
            raise HTTPException(status_code=404, detail="Receipt not available")
        return FilingReceiptRead(
            filing_id=filing.id,
            receipt_id=filing.kvitteringsnummer,
            submitted_at=filing.submitted_at,
            submission_outcome=filing.submission_outcome or "NIL",
            momstilsvar=filing.momstilsvar,
        )

    async def get_deadline_preview(
        self, party_id: uuid.UUID, period_key: str, afregningsperiode_type: str, current_user, db: Session
    ) -> FilingDeadlineRead:
        self._authz.assert_can_read_party(current_user, party_id)
        deadline = self._next_bank_day(self._compute_deadline(afregningsperiode_type, period_key), db)
        return FilingDeadlineRead(
            party_id=party_id,
            period_key=period_key,
            afregningsperiode_type=afregningsperiode_type,
            deadline=deadline,
            rule_basis="Momsloven §57 + Opkrævningsloven §2 stk.3 (next bank day)",
        )
```

### 3.6 Domain Events

**`app/events/filing_events.py`**
```python
import uuid
from datetime import date
from decimal import Decimal

from app.events.base import BaseEvent


class FilingCreated(BaseEvent):
    filing_id: uuid.UUID
    party_id: uuid.UUID
    se_nummer: str
    filing_period: str
    angivelse_type: str
    momstilsvar: Decimal
    frist: date


class FilingSubmitted(BaseEvent):
    filing_id: uuid.UUID
    party_id: uuid.UUID
    se_nummer: str
    angivelse_type: str
    filing_period: str
    momstilsvar: Decimal
    frist: date
    late_filing_days: int
    late_filing_penalty: Decimal


class FilingPenaltyAccrued(BaseEvent):
    filing_id: uuid.UUID
    party_id: uuid.UUID
    days_overdue: int
    penalty_amount: Decimal


class FilingCorrected(BaseEvent):
    original_filing_id: uuid.UUID
    corrected_filing_id: uuid.UUID
    party_id: uuid.UUID
    se_nummer: str
```

**`app/events/handlers/filing_handlers.py`**
```python
import logging

from app.events.filing_events import FilingCorrected, FilingCreated, FilingPenaltyAccrued, FilingSubmitted

logger = logging.getLogger(__name__)


def on_filing_created(event: FilingCreated) -> None:
    logger.info(
        "Filing created: filing_id=%s party_id=%s se=%s period=%s type=%s momstilsvar=%s deadline=%s",
        event.filing_id, event.party_id, event.se_nummer, event.filing_period,
        event.angivelse_type, event.momstilsvar, event.frist,
    )


def on_filing_submitted(event: FilingSubmitted) -> None:
    logger.info(
        "Filing submitted: filing_id=%s party_id=%s period=%s amount=%s late_days=%s late_penalty=%s",
        event.filing_id, event.party_id, event.filing_period,
        event.momstilsvar, event.late_filing_days, event.late_filing_penalty,
    )


def on_filing_penalty_accrued(event: FilingPenaltyAccrued) -> None:
    logger.warning(
        "Late filing penalty accrued: filing_id=%s party_id=%s days=%s penalty=%s",
        event.filing_id, event.party_id, event.days_overdue, event.penalty_amount,
    )


def on_filing_corrected(event: FilingCorrected) -> None:
    logger.info(
        "Filing corrected: original=%s corrected=%s party_id=%s se=%s",
        event.original_filing_id, event.corrected_filing_id, event.party_id, event.se_nummer,
    )
```

### 3.7 Router

**`app/routers/filings.py`**
```python
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.filing import FilingCreate, FilingDeadlineRead, FilingRead, FilingReceiptRead
from app.services.filing import FilingService

router = APIRouter(prefix="/api/v1", tags=["filings"])


def get_filing_service() -> FilingService:
    raise RuntimeError("get_filing_service must be dependency-overridden in app/main.py")


@router.post("/filings", response_model=FilingRead, status_code=status.HTTP_201_CREATED)
async def create_filing(
    payload: FilingCreate, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingRead:
    filing = await service.create_filing(payload, current_user, db)
    return FilingRead.from_orm(filing)


@router.get("/filings/{filing_id}", response_model=FilingRead)
async def get_filing(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingRead:
    filing = await service.get_filing(filing_id, current_user, db)
    return FilingRead.from_orm(filing)


@router.get("/parties/{party_id}/filings", response_model=list[FilingRead])
async def list_party_filings(
    party_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> list[FilingRead]:
    filings = await service.list_filings_for_party(party_id, current_user, db)
    return [FilingRead.from_orm(f) for f in filings]


@router.get("/filings", response_model=list[FilingRead])
async def list_filings(
    db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> list[FilingRead]:
    filings = await service.list_filings(current_user, db)
    return [FilingRead.from_orm(f) for f in filings]


@router.patch("/filings/{filing_id}/submit", response_model=FilingRead)
async def submit_filing(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingRead:
    filing = await service.submit_filing(filing_id, current_user, db)
    return FilingRead.from_orm(filing)


@router.post("/filings/{filing_id}/correct", response_model=FilingRead)
async def correct_filing(
    filing_id: uuid.UUID, payload: FilingCreate, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingRead:
    filing = await service.correct_filing(filing_id, payload, current_user, db)
    return FilingRead.from_orm(filing)


@router.get("/filings/{filing_id}/receipt", response_model=FilingReceiptRead)
async def get_filing_receipt(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingReceiptRead:
    return await service.get_receipt(filing_id, current_user, db)


@router.get("/vat-deadlines", response_model=FilingDeadlineRead)
async def get_vat_deadline_preview(
    party_id: uuid.UUID,
    period: str,
    afregningsperiode_type: str,
    db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    current_user: User = Depends(get_current_user),
) -> FilingDeadlineRead:
    return await service.get_deadline_preview(
        party_id=party_id,
        period_key=period,
        afregningsperiode_type=afregningsperiode_type,
        current_user=current_user,
        db=db,
    )
```

---

## 4. Tax Assessment Module

### 4.1 Overview

A `TaxAssessment` is created by an OFFICER or ADMIN after reviewing a submitted filing. Filing status side effects are governed only by the canonical transition table in Section 3.1.1.

| Filing (new) | Assessment (new) |
|---|---|
| `app/models/filing.py` | `app/models/assessment.py` |
| `app/schemas/filing.py` | `app/schemas/assessment.py` |
| `app/repositories/filing.py` | `app/repositories/assessment.py` |
| `app/services/filing.py` | `app/services/assessment.py` |
| `app/events/filing_events.py` | `app/events/assessment_events.py` |
| `app/events/handlers/filing_handlers.py` | `app/events/handlers/assessment_handlers.py` |
| `app/routers/filings.py` | `app/routers/assessments.py` |

### 4.2 Domain Model

**`app/models/assessment.py`**
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class TaxAssessment(Base, TimestampMixin):
    __tablename__ = "tax_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    filing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filings.id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    assessed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False, index=True,
    )
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    decision_outcome: Mapped[str] = mapped_column(String(30), nullable=False, default="ACCEPTED")
    # Values: ACCEPTED | ADJUSTED | REJECTED

    tax_due: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    surcharge_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    interest_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))

    payment_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    appeal_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    appealed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Assessment status transitions (SSOT-aligned):**

| From | Allowed transitions |
|---|---|
| `PENDING` | `COMPLETE`, `APPEALED` |
| `COMPLETE` | `APPEALED` |
| `APPEALED` | (terminal) |

`filing_id` carries a UNIQUE constraint: one active assessment per filing version. Duplicate returns `409`.

### 4.3 Pydantic Schemas

**`app/schemas/assessment.py`**
```python
import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    filing_id: uuid.UUID
    assessment_date: date = Field(..., examples=["2024-03-15"])
    decision_outcome: str = Field(default="ACCEPTED")
    tax_due: Decimal = Field(..., examples=[Decimal("5000.00")])
    surcharge_amount: Decimal = Field(default=Decimal("0.00"))
    interest_amount: Decimal = Field(default=Decimal("0.00"))
    payment_deadline: date = Field(..., examples=["2024-04-10"])
    appeal_deadline: date = Field(..., examples=["2024-06-15"])
    notes: str | None = None


class AssessmentStatusUpdate(BaseModel):
    status: str = Field(..., examples=["COMPLETE"])


class AssessmentAppealCreate(BaseModel):
    reason: str = Field(..., min_length=10)


class AssessmentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    filing_id: uuid.UUID
    assessed_by: uuid.UUID
    assessment_date: date
    decision_outcome: str
    tax_due: Decimal
    surcharge_amount: Decimal
    interest_amount: Decimal
    payment_deadline: date
    appeal_deadline: date
    appealed_at: datetime | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
```

### 4.4 Repository

**`app/repositories/assessment.py`**
```python
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.assessment import TaxAssessment
from app.schemas.assessment import AssessmentAppealCreate, AssessmentCreate


class AssessmentRepository:

    def create_assessment(self, payload: AssessmentCreate, assessed_by: uuid.UUID, db: Session) -> TaxAssessment:
        assessment = TaxAssessment(
            filing_id=payload.filing_id, assessed_by=assessed_by,
            assessment_date=payload.assessment_date,
            decision_outcome=payload.decision_outcome,
            tax_due=payload.tax_due,
            surcharge_amount=payload.surcharge_amount,
            interest_amount=payload.interest_amount,
            payment_deadline=payload.payment_deadline,
            appeal_deadline=payload.appeal_deadline,
            status="PENDING", notes=payload.notes,
        )
        db.add(assessment)
        db.commit()
        return assessment

    def list_assessments(self, db: Session) -> list[TaxAssessment]:
        return db.query(TaxAssessment).order_by(TaxAssessment.created_at.desc()).all()

    def get_assessment_by_id(self, assessment_id: uuid.UUID, db: Session) -> TaxAssessment | None:
        return db.query(TaxAssessment).filter(TaxAssessment.id == assessment_id).first()

    def get_assessment_by_filing(self, filing_id: uuid.UUID, db: Session) -> TaxAssessment | None:
        return db.query(TaxAssessment).filter(TaxAssessment.filing_id == filing_id).first()

    def update_status(self, assessment_id: uuid.UUID, new_status: str, db: Session) -> TaxAssessment | None:
        assessment = db.query(TaxAssessment).filter(TaxAssessment.id == assessment_id).first()
        if assessment is None:
            return None
        assessment.status = new_status
        db.commit()
        return assessment

    def mark_appealed(self, assessment_id: uuid.UUID, payload: AssessmentAppealCreate, ts: datetime, db: Session) -> TaxAssessment | None:
        assessment = db.query(TaxAssessment).filter(TaxAssessment.id == assessment_id).first()
        if assessment is None:
            return None
        assessment.status = "APPEALED"
        assessment.appealed_at = ts
        assessment.notes = (assessment.notes or "") + f"\nAppeal: {payload.reason}"
        db.commit()
        return assessment
```

### 4.5 Service

**`app/services/assessment.py`**
```python
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.events.assessment_events import AssessmentCreated, AssessmentPenaltyCalculated, AssessmentStatusChanged
from app.events.base import EventBus
from app.models.assessment import TaxAssessment
from app.repositories.assessment import AssessmentRepository
from app.repositories.filing import FilingRepository
from app.schemas.assessment import AssessmentAppealCreate, AssessmentCreate
from app.services.authz import AuthorizationPolicy

VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"COMPLETE", "APPEALED"},
    "COMPLETE": {"APPEALED"},
    "APPEALED": set(),
}


class AssessmentService:
    def __init__(
        self,
        repo: AssessmentRepository,
        filing_repo: FilingRepository,
        bus: EventBus,
        authz: AuthorizationPolicy,
    ) -> None:
        self._repo = repo
        self._filing_repo = filing_repo
        self._bus = bus
        self._authz = authz

    async def create_assessment(self, payload: AssessmentCreate, assessed_by: uuid.UUID, current_user, db: Session) -> TaxAssessment:
        self._authz.assert_can_create_assessment(current_user)
        filing = self._filing_repo.get_filing_by_id(payload.filing_id, db)
        if filing is None:
            raise HTTPException(status_code=404, detail="Filing not found")
        if filing.status != "SUBMITTED_WITH_RECEIPT":
            raise HTTPException(status_code=400, detail="Assessment can only be created for SUBMITTED_WITH_RECEIPT filings")

        existing = self._repo.get_assessment_by_filing(payload.filing_id, db)
        if existing is not None:
            raise HTTPException(status_code=409, detail=f"Assessment already exists for filing {payload.filing_id}")

        if payload.payment_deadline < payload.assessment_date:
            raise HTTPException(status_code=422, detail="payment_deadline must be >= assessment_date")
        if payload.appeal_deadline < payload.assessment_date:
            raise HTTPException(status_code=422, detail="appeal_deadline must be >= assessment_date")

        assessment = self._repo.create_assessment(payload, assessed_by, db)

        await self._bus.publish(AssessmentCreated(
            assessment_id=assessment.id,
            filing_id=assessment.filing_id,
            assessed_by=assessment.assessed_by,
        ))
        await self._bus.publish(AssessmentPenaltyCalculated(
            assessment_id=assessment.id,
            filing_id=assessment.filing_id,
            surcharge_amount=assessment.surcharge_amount,
            interest_amount=assessment.interest_amount,
            payment_deadline=assessment.payment_deadline,
        ))
        return assessment

    async def list_assessments(self, current_user, db: Session) -> list[TaxAssessment]:
        all_items = self._repo.list_assessments(db)
        return [a for a in all_items if self._authz.can_read_assessment(current_user, a)]

    async def get_assessment(self, assessment_id: uuid.UUID, current_user, db: Session) -> TaxAssessment:
        assessment = self._repo.get_assessment_by_id(assessment_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        self._authz.assert_can_read_assessment(current_user, assessment)
        return assessment

    async def get_assessment_for_filing(self, filing_id: uuid.UUID, current_user, db: Session) -> TaxAssessment:
        assessment = self._repo.get_assessment_by_filing(filing_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail=f"No assessment found for filing {filing_id}")
        self._authz.assert_can_read_assessment(current_user, assessment)
        return assessment

    async def update_status(self, assessment_id: uuid.UUID, new_status: str, current_user, db: Session) -> TaxAssessment:
        self._authz.assert_can_manage_assessment(current_user)
        assessment = self._repo.get_assessment_by_id(assessment_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        allowed = VALID_STATUS_TRANSITIONS.get(assessment.status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{assessment.status}' to '{new_status}'. Allowed: {sorted(allowed) if allowed else 'none'}",
            )
        previous = assessment.status
        assessment = self._repo.update_status(assessment_id, new_status, db)

        await self._bus.publish(AssessmentStatusChanged(
            assessment_id=assessment.id,
            filing_id=assessment.filing_id,
            previous_status=previous,
            new_status=new_status,
        ))
        return assessment

    async def appeal_assessment(
        self, assessment_id: uuid.UUID, payload: AssessmentAppealCreate, current_user, db: Session
    ) -> TaxAssessment:
        assessment = await self.get_assessment(assessment_id, current_user, db)
        self._authz.assert_can_appeal_assessment(current_user, assessment)
        if assessment.status != "COMPLETE":
            raise HTTPException(status_code=400, detail="Only COMPLETE assessments can be appealed")
        if datetime.now(timezone.utc).date() > assessment.appeal_deadline:
            raise HTTPException(status_code=422, detail="Appeal deadline has passed")

        assessment = self._repo.mark_appealed(assessment_id, payload, datetime.now(timezone.utc), db)

        await self._bus.publish(AssessmentStatusChanged(
            assessment_id=assessment.id,
            filing_id=assessment.filing_id,
            previous_status="COMPLETE",
            new_status="APPEALED",
        ))
        return assessment
```

### 4.6 Domain Events

**`app/events/assessment_events.py`**
```python
import uuid
from datetime import date
from decimal import Decimal

from app.events.base import BaseEvent


class AssessmentCreated(BaseEvent):
    assessment_id: uuid.UUID
    filing_id: uuid.UUID
    assessed_by: uuid.UUID


class AssessmentPenaltyCalculated(BaseEvent):
    assessment_id: uuid.UUID
    filing_id: uuid.UUID
    surcharge_amount: Decimal
    interest_amount: Decimal
    payment_deadline: date


class AssessmentStatusChanged(BaseEvent):
    assessment_id: uuid.UUID
    filing_id: uuid.UUID
    previous_status: str
    new_status: str
```

**`app/events/handlers/assessment_handlers.py`**
```python
import logging

from app.events.assessment_events import AssessmentCreated, AssessmentPenaltyCalculated, AssessmentStatusChanged
from app.events.filing_events import FilingSubmitted

logger = logging.getLogger(__name__)


def on_filing_submitted_notify_assessment(event: FilingSubmitted) -> None:
    logger.info(
        "Filing awaiting assessment: filing_id=%s party_id=%s type=%s period=%s amount=%s",
        event.filing_id, event.party_id, event.angivelse_type, event.filing_period, event.momstilsvar,
    )


def on_assessment_created(event: AssessmentCreated) -> None:
    logger.info(
        "Assessment created: assessment_id=%s filing_id=%s assessed_by=%s",
        event.assessment_id, event.filing_id, event.assessed_by,
    )


def on_assessment_penalty_calculated(event: AssessmentPenaltyCalculated) -> None:
    logger.info(
        "Assessment penalties: assessment_id=%s filing_id=%s surcharge=%s interest=%s payment_deadline=%s",
        event.assessment_id, event.filing_id,
        event.surcharge_amount, event.interest_amount, event.payment_deadline,
    )


def on_assessment_status_changed(event: AssessmentStatusChanged) -> None:
    logger.info(
        "Assessment status changed: assessment_id=%s filing_id=%s %s->%s",
        event.assessment_id, event.filing_id,
        event.previous_status, event.new_status,
    )
```

### 4.7 Router

**`app/routers/assessments.py`**
```python
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.assessment import (
    AssessmentAppealCreate,
    AssessmentCreate,
    AssessmentRead,
    AssessmentStatusUpdate,
)
from app.services.assessment import AssessmentService

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])
filing_assessment_router = APIRouter(prefix="/api/v1/filings", tags=["assessments"])


def get_assessment_service() -> AssessmentService:
    raise RuntimeError("get_assessment_service must be dependency-overridden in app/main.py")


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    payload: AssessmentCreate, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(require_role("OFFICER", "ADMIN")),
) -> AssessmentRead:
    assessment = await service.create_assessment(payload, current_user.id, current_user, db)
    return AssessmentRead.from_orm(assessment)


@router.get("", response_model=list[AssessmentRead])
async def list_assessments(
    db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(get_current_user),
) -> list[AssessmentRead]:
    assessments = await service.list_assessments(current_user, db)
    return [AssessmentRead.from_orm(a) for a in assessments]


@router.get("/{assessment_id}", response_model=AssessmentRead)
async def get_assessment(
    assessment_id: uuid.UUID, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(get_current_user),
) -> AssessmentRead:
    assessment = await service.get_assessment(assessment_id, current_user, db)
    return AssessmentRead.from_orm(assessment)


@router.patch("/{assessment_id}/status", response_model=AssessmentRead)
async def update_assessment_status(
    assessment_id: uuid.UUID, payload: AssessmentStatusUpdate,
    db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(require_role("OFFICER", "ADMIN")),
) -> AssessmentRead:
    assessment = await service.update_status(assessment_id, payload.status, current_user, db)
    return AssessmentRead.from_orm(assessment)


@router.post("/{assessment_id}/appeal", response_model=AssessmentRead)
async def appeal_assessment(
    assessment_id: uuid.UUID, payload: AssessmentAppealCreate,
    db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(require_role("TAXPAYER")),
) -> AssessmentRead:
    assessment = await service.appeal_assessment(assessment_id, payload, current_user, db)
    return AssessmentRead.from_orm(assessment)


@filing_assessment_router.get("/{filing_id}/assessment", response_model=AssessmentRead)
async def get_filing_assessment(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(get_current_user),
) -> AssessmentRead:
    assessment = await service.get_assessment_for_filing(filing_id, current_user, db)
    return AssessmentRead.from_orm(assessment)
```

---

## 4.8 Admin Module (Dashboard, User Management, Settings)

### 4.8.1 Dashboard Summary Endpoint

The `GET /api/v1/dashboard/summary` endpoint is required by the Designer's Dashboard page and is accessible to ADMIN and OFFICER roles only. It returns aggregate counts used to populate the stat cards.

**Schema — `app/schemas/dashboard.py`**
```python
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """Read-only aggregate for the admin dashboard stat cards."""
    total_parties: int
    pending_filings: int       # filings with status in (DRAFT, SUBMITTED)
    submitted_filings: int     # filings with status SUBMITTED_WITH_RECEIPT
    open_assessments: int      # assessments with status not in (GODKENDT, AFVIST)
    overdue_filings: int       # submitted filings where submitted_at > frist
```

**Router stub — `app/routers/dashboard.py`**
```python
import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.assessment import TaxAssessment
from app.models.filing import Filing
from app.models.party import Party
from app.models.user import User
from app.schemas.dashboard import DashboardSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Annotated[User, Depends(require_roles("ADMIN", "OFFICER"))] = None,
) -> DashboardSummary:
    """Return aggregate counts for the admin dashboard.

    Scoped to all data (ADMIN and OFFICER see all parties/filings/assessments).
    TAXPAYER role is blocked by require_roles.
    """
    total_parties = db.query(func.count(Party.id)).scalar() or 0

    pending_filings = (
        db.query(func.count(Filing.id))
        .filter(Filing.status.in_(["DRAFT", "SUBMITTED"]))
        .scalar()
        or 0
    )

    submitted_filings = (
        db.query(func.count(Filing.id))
        .filter(Filing.status == "SUBMITTED_WITH_RECEIPT")
        .scalar()
        or 0
    )

    open_assessments = (
        db.query(func.count(TaxAssessment.id))
        .filter(TaxAssessment.status.notin_(["GODKENDT", "AFVIST"]))
        .scalar()
        or 0
    )

    overdue_filings = (
        db.query(func.count(Filing.id))
        .filter(
            Filing.submitted_at.isnot(None),
            Filing.submitted_at > Filing.frist,
        )
        .scalar()
        or 0
    )

    return DashboardSummary(
        total_parties=total_parties,
        pending_filings=pending_filings,
        submitted_filings=submitted_filings,
        open_assessments=open_assessments,
        overdue_filings=overdue_filings,
    )
```

> **Note:** The `require_roles` dependency (in `app/dependencies/auth.py`) is a factory that returns a FastAPI dependency rejecting requests from roles not in the provided list with a `403 Forbidden` response.

### 4.8.2 Admin Router (Users + Settings)

**`app/routers/admin.py`**
```python
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.admin_settings import AdminSettings
from app.models.user import User
from app.schemas.auth import UserCreate, UserRead
from app.services.auth import AuthService

users_router = APIRouter(prefix="/api/v1/admin/users", tags=["admin"])
settings_router = APIRouter(prefix="/api/v1/admin/settings", tags=["admin"])

auth_service = AuthService()


@users_router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("ADMIN"))] = None,
) -> list[User]:
    return db.query(User).all()


@users_router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("ADMIN"))] = None,
) -> User:
    return auth_service.create_user(payload, db)


@users_router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: uuid.UUID,
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("ADMIN"))] = None,
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Coder agent: apply only non-None fields from payload
    return auth_service.update_user(user, payload, db)


@settings_router.get("", response_model=list[dict])
def list_settings(
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("ADMIN"))] = None,
) -> list:
    return db.query(AdminSettings).all()


@settings_router.patch("/{key}", response_model=dict)
def update_setting(
    key: str,
    value: dict,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_roles("ADMIN"))] = None,
) -> AdminSettings:
    setting = db.query(AdminSettings).filter(AdminSettings.key == key).first()
    if setting is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting.value = value
    db.commit()
    db.refresh(setting)
    return setting
```

---

## 5. Updated app/main.py Wiring

```python
import logging

from fastapi import FastAPI

from app.middleware.audit import AuditMiddleware
from app.events.assessment_events import AssessmentCreated, AssessmentPenaltyCalculated, AssessmentStatusChanged
from app.events.bus import InMemoryEventBus
from app.events.filing_events import FilingCorrected, FilingCreated, FilingPenaltyAccrued, FilingSubmitted
from app.events.handlers.assessment_handlers import (
    on_assessment_created,
    on_assessment_penalty_calculated,
    on_assessment_status_changed,
    on_filing_submitted_notify_assessment,
)
from app.events.handlers.filing_handlers import (
    on_filing_corrected,
    on_filing_created,
    on_filing_penalty_accrued,
    on_filing_submitted,
)
from app.events.handlers.party_handlers import on_party_registered, on_party_role_assigned
from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.repositories.assessment import AssessmentRepository
from app.repositories.filing import FilingRepository
from app.repositories.party import PartyRepository
from app.repositories.policy import VatPolicyRepository
from app.routers import auth as auth_module
from app.routers import parties, roles
from app.routers.admin import settings_router, users_router
from app.routers.assessments import (
    filing_assessment_router,
    get_assessment_service,
    router as assessments_router,
)
from app.routers.dashboard import router as dashboard_router
from app.routers.filings import get_filing_service, router as filings_router
from app.routers.parties import get_party_service
from app.services.assessment import AssessmentService
from app.services.authz import AuthorizationPolicy
from app.services.filing import FilingService
from app.services.party import PartyService

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Danish Tax Administration Platform",
    version="2.0.0",
    description="Registration, Filing, Assessment, and Admin modules.",
)
app.add_middleware(AuditMiddleware)

# Event Bus
# InMemoryEventBus is used for Phase 2 development and testing.
# Limitation acknowledged (Reviewer ACTION): events are dispatched in-process and
# are not durable — a process restart will not re-deliver in-flight events.
# All critical business logic (VAT calculation, status transitions, penalty accrual)
# is committed to the database BEFORE events are published, so a lost event means
# a missed notification or log entry — not a lost transaction. Events are used only
# for cross-module notification and audit logging at Phase 2.
# Replacing InMemoryEventBus with a durable broker (RabbitMQ/Kafka) is a Phase 3 concern.
bus = InMemoryEventBus()

bus.subscribe(PartyRegistered, on_party_registered)
bus.subscribe(PartyRoleAssigned, on_party_role_assigned)
bus.subscribe(FilingCreated, on_filing_created)
bus.subscribe(FilingSubmitted, on_filing_submitted)
bus.subscribe(FilingSubmitted, on_filing_submitted_notify_assessment)
bus.subscribe(FilingPenaltyAccrued, on_filing_penalty_accrued)
bus.subscribe(FilingCorrected, on_filing_corrected)
bus.subscribe(AssessmentCreated, on_assessment_created)
bus.subscribe(AssessmentPenaltyCalculated, on_assessment_penalty_calculated)
bus.subscribe(AssessmentStatusChanged, on_assessment_status_changed)

# Services
authz = AuthorizationPolicy()
party_service = PartyService(repo=PartyRepository(), bus=bus)
filing_repo = FilingRepository()
policy_repo = VatPolicyRepository()
filing_service = FilingService(repo=filing_repo, policy_repo=policy_repo, bus=bus, authz=authz)
assessment_service = AssessmentService(
    repo=AssessmentRepository(),
    filing_repo=filing_repo,
    bus=bus,
    authz=authz,
)

# Dependency Overrides
app.dependency_overrides[get_party_service] = lambda: party_service
app.dependency_overrides[get_filing_service] = lambda: filing_service
app.dependency_overrides[get_assessment_service] = lambda: assessment_service

# Routers
app.include_router(auth_module.router)
app.include_router(parties.router)
app.include_router(roles.router)
app.include_router(filings_router)
app.include_router(assessments_router)
app.include_router(filing_assessment_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(settings_router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
```

---

## 6. Alembic Migration Plan

### Revision chain

```
0001_initial  (existing)
     |
     v
0002_add_users_table
     |
     v
0003_add_vat_filing_canonical_table
     |
     v
0004_add_typed_tax_assessments
     |
     v
0005_add_admin_settings
```

### Migration 0002 - `users`

**`alembic/versions/0002_add_users_table.py`**
```python
"""add users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        # Nullable FK — only set for TAXPAYER users linking to their Party row.
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_party_id", "users", ["party_id"])


def downgrade() -> None:
    op.drop_index("ix_users_party_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
```

### Migration 0003 - `filings` (canonical VAT fields)

**`alembic/versions/0003_add_vat_filing_canonical_table.py`**
```python
"""add canonical VAT filing table

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "filings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("se_nummer", sa.String(8), nullable=False),
        sa.Column("afregningsperiode_type", sa.String(20), nullable=False),
        sa.Column("filing_period", sa.String(20), nullable=False),
        sa.Column("angivelse_type", sa.String(20), nullable=False, server_default=sa.text("'MOMS'")),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("rubrik_a", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("rubrik_b", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("rubrik_c", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("rubrik_d", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("rubrik_e", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("momspligtig_omsaetning", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("momsfri_omsaetning", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("eksport", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("momstilsvar", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("frist", sa.Date(), nullable=False),
        sa.Column("late_filing_days", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("late_filing_penalty", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("kvitteringsnummer", sa.String(64), nullable=True),
        sa.Column("submission_outcome", sa.String(20), nullable=True),
        sa.Column("korrektionsangivelse", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("original_filing_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("supplemental_line_items", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["original_filing_id"], ["filings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_filings_party_id", "filings", ["party_id"])
    op.create_index("ix_filings_se_nummer", "filings", ["se_nummer"])
    # Partial unique index: only one canonical (non-correction) filing per
    # (se_nummer, filing_period, angivelse_type). Corrections are excluded so
    # multiple correction versions can coexist for the same period.
    op.execute(
        "CREATE UNIQUE INDEX uq_filing_canonical_se_period_type "
        "ON filings (se_nummer, filing_period, angivelse_type) "
        "WHERE korrektionsangivelse = false"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_filing_canonical_se_period_type")
    op.drop_index("ix_filings_se_nummer", table_name="filings")
    op.drop_index("ix_filings_party_id", table_name="filings")
    op.drop_table("filings")
```

### Migration 0004 - `tax_assessments` (typed dates + penalties)

**`alembic/versions/0004_add_typed_tax_assessments.py`**
```python
"""add typed tax_assessments table

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tax_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assessed_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.Column("decision_outcome", sa.String(30), nullable=False, server_default=sa.text("'ACCEPTED'")),
        sa.Column("tax_due", sa.Numeric(18, 2), nullable=False),
        sa.Column("surcharge_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("interest_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("payment_deadline", sa.Date(), nullable=False),
        sa.Column("appeal_deadline", sa.Date(), nullable=False),
        sa.Column("appealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["filing_id"], ["filings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assessed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("filing_id", name="uq_tax_assessments_filing_id"),
    )
    op.create_index("ix_tax_assessments_filing_id", "tax_assessments", ["filing_id"])
    op.create_index("ix_tax_assessments_assessed_by", "tax_assessments", ["assessed_by"])


def downgrade() -> None:
    op.drop_index("ix_tax_assessments_assessed_by", table_name="tax_assessments")
    op.drop_index("ix_tax_assessments_filing_id", table_name="tax_assessments")
    op.drop_table("tax_assessments")
```

### Migration 0005 - `admin_settings`

**`alembic/versions/0005_add_admin_settings.py`**
```python
"""add admin_settings table

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_settings",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("admin_settings")
```

### Migration 0005b - `vat_policies` (new)

**`alembic/versions/0005b_add_vat_policies_table.py`**
```python
"""add vat_policies table and seed initial row

Revision ID: 0005b
Revises: 0005
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005b"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vat_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "late_filing_fee_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("800.00"),
        ),
        # JSON array of ISO-8601 date strings: bank holidays in the policy window.
        sa.Column(
            "bank_holidays_json",
            sa.String(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vat_policies_effective_from", "vat_policies", ["effective_from"])

    # Seed the initial policy row so FilingService never fails on a missing policy.
    op.execute(
        "INSERT INTO vat_policies (id, effective_from, effective_to, late_filing_fee_amount, bank_holidays_json) "
        "VALUES (gen_random_uuid(), '2024-01-01', NULL, 800.00, '[]')"
    )


def downgrade() -> None:
    op.drop_index("ix_vat_policies_effective_from", table_name="vat_policies")
    op.drop_table("vat_policies")
```

> **Sequence note:** Migrations 0006 and 0007 are defined later in this document (Party VAT columns and audit_log respectively). The full chain is: 0001 → 0002 → 0003 → 0004 → 0005 → 0005b → 0006 → 0007.

---

### Migration 0006 - Party VAT Columns (new)

Add first-class VAT fields to the existing `parties` table. This replaces the prior pattern of reading `cvr_nummer` and `se_nummer` from `party_identifiers` rows. The EAV rows are left in place for backwards compatibility; the new columns become the canonical source.

**`alembic/versions/0006_add_party_vat_columns.py`**
```python
"""add vat columns to parties table

Revision ID: 0006
Revises: 0005b
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # CVR number: 8-digit Danish company registration number (Erhvervsstyrelsen).
    # Nullable because not all party types require a CVR number at registration time.
    op.add_column("parties", sa.Column("cvr_nummer", sa.String(8), nullable=True))
    # SE number: 8-digit tax registration number (Skattestyrelsen).
    # One CVR can have multiple SE numbers; store the primary SE here.
    op.add_column("parties", sa.Column("se_nummer", sa.String(8), nullable=True))
    # VAT filing period type: MONTHLY | QUARTERLY | SEMI_ANNUAL
    op.add_column("parties", sa.Column("afregningsperiode_type", sa.String(20), nullable=True))
    # True once the party has completed VAT registration with SKAT.
    op.add_column("parties", sa.Column("vat_registration_active", sa.Boolean(),
                                       nullable=False, server_default=sa.text("false")))

    op.create_index("ix_parties_cvr_nummer", "parties", ["cvr_nummer"])
    op.create_index("ix_parties_se_nummer", "parties", ["se_nummer"])


def downgrade() -> None:
    op.drop_index("ix_parties_se_nummer", table_name="parties")
    op.drop_index("ix_parties_cvr_nummer", table_name="parties")
    op.drop_column("parties", "vat_registration_active")
    op.drop_column("parties", "afregningsperiode_type")
    op.drop_column("parties", "se_nummer")
    op.drop_column("parties", "cvr_nummer")
```

**Updated `app/models/party.py` (Party class only — other models unchanged)**

Add the four new columns to the `Party` class in `app/models/party.py`:

```python
# Inside class Party(Base, TimestampMixin): — add after party_type_code

# CVR and SE numbers as first-class columns for fast indexed lookups.
# The EAV rows in party_identifiers remain for historical compatibility.
cvr_nummer: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
se_nummer: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
afregningsperiode_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
vat_registration_active: Mapped[bool] = mapped_column(
    Boolean, nullable=False, default=False
)
```

> **Coder agent note:** When registering a new party, validate CVR via modulus-11 checksum before writing to the database. The validation logic lives in `app/services/party.py` — add a `_validate_cvr(cvr: str) -> bool` helper following the spec in `AGENT_RESEARCHER_SPEC.md` (Section 3.1, CVR validation algorithm).

---

### Migration 0007 - `audit_log` (new)

An append-only audit log table for all write operations. This satisfies the GDPR and FORVALTNINGSLOVEN requirement that every state change is attributable and reversible by an auditor.

**`alembic/versions/0007_add_audit_log.py`**
```python
"""add audit_log table

Revision ID: 0007
Revises: 0006
Create Date: 2026-02-24
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        # Who performed the action. NULL for system-generated events.
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        # actor_role at time of action (ADMIN / OFFICER / TAXPAYER / SYSTEM).
        sa.Column("actor_role", sa.String(50), nullable=True),
        # The entity type being modified, e.g. "Filing", "Assessment", "Party".
        sa.Column("entity_type", sa.String(100), nullable=False),
        # UUID of the modified entity.
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        # HTTP method + path that triggered the change (e.g. "PATCH /api/v1/filings/…/submit").
        sa.Column("action", sa.String(255), nullable=False),
        # Previous state snapshot (JSON). NULL for create operations.
        sa.Column("before_state", sa.JSON(), nullable=True),
        # New state snapshot (JSON). NULL for delete operations.
        sa.Column("after_state", sa.JSON(), nullable=True),
        # Source IP of the request. VARCHAR to accommodate both IPv4 and IPv6.
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_entity", "audit_log", ["entity_type", "entity_id"])
    op.create_index("ix_audit_log_actor", "audit_log", ["actor_id"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_index("ix_audit_log_actor", table_name="audit_log")
    op.drop_index("ix_audit_log_entity", table_name="audit_log")
    op.drop_table("audit_log")
```

**`app/models/audit_log.py`**
```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, new_uuid


class AuditLog(Base):
    """Append-only audit trail. Never update or delete rows from this table."""
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
```

**`app/middleware/audit.py`** — FastAPI middleware stub
```python
import json
import uuid
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog

AUDITED_METHODS = {"POST", "PATCH", "PUT", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Writes an AuditLog row for every state-changing request.

    The middleware captures actor identity from the decoded JWT payload
    stored in request.state by the auth dependency, so it runs *after*
    authentication but before the response is sent.

    Coder agent: populate before_state and after_state from the request body
    and response body respectively. For large payloads, store only the diff.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method in AUDITED_METHODS and response.status_code < 400:
            actor = getattr(request.state, "current_user", None)
            db: Session = SessionLocal()
            try:
                entry = AuditLog(
                    id=uuid.uuid4(),
                    actor_id=actor.id if actor else None,
                    actor_role=actor.role if actor else "SYSTEM",
                    entity_type=_extract_entity_type(request.url.path),
                    entity_id=_extract_entity_id(request.url.path),
                    action=f"{request.method} {request.url.path}",
                    before_state=None,   # TODO: populate from pre-request state fetch
                    after_state=None,    # TODO: populate from response body
                    ip_address=request.client.host if request.client else None,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(entry)
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        return response


def _extract_entity_type(path: str) -> str:
    segments = [s for s in path.split("/") if s]
    for segment in segments:
        if segment in ("filings", "assessments", "parties", "users"):
            return segment.rstrip("s").capitalize()
    return "Unknown"


def _extract_entity_id(path: str) -> uuid.UUID:
    segments = [s for s in path.split("/") if s]
    for segment in segments:
        try:
            return uuid.UUID(segment)
        except ValueError:
            continue
    return uuid.uuid4()  # fallback — should not normally be reached
```

> **main.py wiring:** Add `app.add_middleware(AuditMiddleware)` after the app is created in `app/main.py`. Import from `app.middleware.audit`.

---

### New Tables Summary

| Table | Primary Key | Foreign Keys | Notable Constraints |
|---|---|---|---|
| `users` | `id` UUID | `party_id` -> `parties.id` SET NULL | `email` UNIQUE; `ix_users_party_id` |
| `filings` | `id` UUID | `party_id` -> `parties.id` CASCADE; `original_filing_id` -> `filings.id` SET NULL | partial unique index `uq_filing_canonical_se_period_type` WHERE korrektionsangivelse=false |
| `tax_assessments` | `id` UUID | `filing_id` -> `filings.id` CASCADE; `assessed_by` -> `users.id` SET NULL | `filing_id` UNIQUE |
| `admin_settings` | `key` text | `updated_by` -> `users.id` (logical ref) | one key per setting |
| `vat_policies` | `id` UUID | — | `ix_vat_policies_effective_from`; seeded with one row |
| `audit_log` | `id` UUID | `actor_id` -> `users.id` (logical, no FK constraint to avoid cascade issues) | `ix_audit_log_entity`; append-only |
| `parties` (updated) | `id` UUID (existing) | — | 4 new columns: `cvr_nummer`, `se_nummer`, `afregningsperiode_type`, `vat_registration_active` |

---

## 7. Cross-Module Event Flow Diagram

Event flow is now defined by explicit publish/subscribe contracts (no hidden side effects):

1. Party registration actions publish `PartyRegistered` and `PartyRoleAssigned`.
2. Filing draft creation publishes `FilingCreated`.
3. Filing submission publishes `FilingSubmitted`; if overdue, also `FilingPenaltyAccrued`.
4. Filing correction publishes `FilingCorrected` and marks prior version `CORRECTED`.
5. Assessment creation publishes `AssessmentCreated` and `AssessmentPenaltyCalculated`; filing status is not implicitly mutated.
6. Assessment status updates and appeals publish `AssessmentStatusChanged` without implicit filing mutation.

### Event Ownership Table

| Event | Published by | Subscribed by |
|---|---|---|
| `PartyRegistered` | `PartyService` | `on_party_registered` |
| `PartyRoleAssigned` | `PartyService` | `on_party_role_assigned` |
| `FilingCreated` | `FilingService` | `on_filing_created` |
| `FilingSubmitted` | `FilingService` | `on_filing_submitted`, `on_filing_submitted_notify_assessment` |
| `FilingPenaltyAccrued` | `FilingService` | `on_filing_penalty_accrued` |
| `FilingCorrected` | `FilingService` | `on_filing_corrected` |
| `AssessmentCreated` | `AssessmentService` | `on_assessment_created` |
| `AssessmentPenaltyCalculated` | `AssessmentService` | `on_assessment_penalty_calculated` |
| `AssessmentStatusChanged` | `AssessmentService` | `on_assessment_status_changed` |

---

## 8. API Contract Summary

### 8.0 Error Response Envelope (Reviewer ACTION addressed)

All error responses across every endpoint use **FastAPI's default error envelope**. Frontend Coder agents must handle both formats:

**Operational errors** (4xx/5xx status codes for business logic failures):
```json
{ "detail": "Canonical filing already exists for this se_nummer + period" }
```

**Validation errors** (HTTP 422 Unprocessable Entity, from Pydantic schema validation):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "rubrik_a"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

The TypeScript client type (`lib/api-client.ts`) must handle both formats:
```typescript
type ApiErrorDetail = string | Array<{ type: string; loc: string[]; msg: string; input: unknown }>;
interface ApiError { detail: ApiErrorDetail; }
```

No custom error middleware is added in Phase 2. FastAPI's built-in exception handlers are sufficient.

### 8.1 Role and Ownership Policy by Endpoint

Role legend: `A=ADMIN`, `O=OFFICER`, `T=TAXPAYER`

| Method | Path | Roles | Ownership predicate | Failure modes |
|---|---|---|---|---|
| GET | `/health` | public | - | 200 |
| POST | `/api/v1/auth/login` | public | - | 401 invalid credentials |
| POST | `/api/v1/auth/refresh` | cookie | - | 401 invalid/missing token |
| POST | `/api/v1/auth/logout` | cookie | - | 200 |
| GET | `/api/v1/auth/me` | A,O,T | self | 401 |
| GET | `/api/v1/dashboard/summary` | A,O | all visible for role | 401,403 |
| GET | `/api/v1/parties` | A,O | all parties | 401,403 |
| POST | `/api/v1/parties` | A,O | all parties | 401,403,422,409 |
| GET | `/api/v1/parties/{id}` | A,O,T | T must own party | 401,403,404 |
| POST | `/api/v1/parties/{id}/roles` | A,O | target party | 401,403,404,422 |
| GET | `/api/v1/parties/{id}/roles` | A,O,T | T must own party | 401,403,404 |
| GET | `/api/v1/parties/{id}/filings` | A,O,T | T must own party | 401,403,404 |
| GET | `/api/v1/filings` | A,O,T | T sees own filings only | 401 |
| POST | `/api/v1/filings` | A,O,T | T can create only for own party | 401,403,404,422,409 |
| GET | `/api/v1/filings/{id}` | A,O,T | T must own filing | 401,403,404 |
| PATCH | `/api/v1/filings/{id}/submit` | A,O,T | T must own filing | 401,403,404,400 |
| POST | `/api/v1/filings/{id}/correct` | A,O,T | T must own filing | 401,403,404,400,409 |
| GET | `/api/v1/filings/{id}/receipt` | A,O,T | T must own filing | 401,403,404 |
| GET | `/api/v1/vat-deadlines` | A,O,T | T must own party_id query param | 401,403,404,422 |
| GET | `/api/v1/assessments` | A,O,T | T sees own assessments only | 401 |
| POST | `/api/v1/assessments` | A,O | filing must be `SUBMITTED_WITH_RECEIPT` | 401,403,404,400,409,422 |
| GET | `/api/v1/assessments/{id}` | A,O,T | T must own related filing | 401,403,404 |
| PATCH | `/api/v1/assessments/{id}/status` | A,O | officer/admin only | 401,403,404,400 |
| POST | `/api/v1/assessments/{id}/appeal` | T | taxpayer must own related filing | 401,403,404,400,422 |
| GET | `/api/v1/filings/{id}/assessment` | A,O,T | T must own filing | 401,403,404 |
| GET | `/api/v1/admin/users` | A | admin only | 401,403 |
| POST | `/api/v1/admin/users` | A | admin only | 401,403,422,409 |
| PATCH | `/api/v1/admin/users/{id}` | A | admin only | 401,403,404,422 |
| GET | `/api/v1/admin/settings` | A | admin only | 401,403 |
| PATCH | `/api/v1/admin/settings/{key}` | A | admin only | 401,403,404,422 |

### 8.2 Deadline and Penalty Enforcement Contract

| Rule | Enforced in | API-visible effect |
|---|---|---|
| Filing deadline calculation from period type + next bank day | `FilingService._compute_deadline` + `_next_bank_day` | `FilingRead.frist` always populated and deterministic |
| Late filing fee (policy-driven, default `DKK 1,400`, effective-date controlled) | `VatPolicyRepository` + `FilingService._late_penalty` | `late_filing_days`, `late_filing_penalty` returned and evented; no hardcoded legal constants |
| Assessment payment/appeal deadline validity | `AssessmentService.create_assessment` | 422 when `payment_deadline` or `appeal_deadline` invalid |
| Appeal deadline enforcement | `AssessmentService.appeal_assessment` | 422 when appeal deadline has passed |
| Distinct surcharge vs interest fields | `TaxAssessment` model and schemas | `surcharge_amount` and `interest_amount` exposed separately |
| Receipt persistence and retrieval | `FilingService.submit_filing` + `get_receipt` | `kvitteringsnummer`, `submission_outcome`, and receipt read endpoint |

### 8.3 API Parity Matrix (Design Page/Action -> Backend Contract)

| Page/Action | Endpoint(s) | Auth + ownership | Failure modes |
|---|---|---|---|
| Login submit | `POST /api/v1/auth/login` | Public | 401 invalid credentials |
| Session refresh | `POST /api/v1/auth/refresh` | Cookie auth | 401 invalid/missing token |
| Logout | `POST /api/v1/auth/logout` | A,O,T | 401 |
| Dashboard cards + recent activity | `GET /api/v1/dashboard/summary`, `GET /api/v1/filings`, `GET /api/v1/parties` | A,O only | 401,403 |
| Parties list/filter | `GET /api/v1/parties` | A,O | 401,403 |
| Register party | `POST /api/v1/parties` | A,O | 401,403,422,409 |
| Party detail | `GET /api/v1/parties/{id}` | A,O,T-own | 401,403,404 |
| Assign role | `POST /api/v1/parties/{id}/roles` | A,O | 401,403,404,422 |
| List roles | `GET /api/v1/parties/{id}/roles` | A,O,T-own | 401,403,404 |
| Filings list | `GET /api/v1/filings` | A,O all; T own only | 401 |
| Create filing draft | `POST /api/v1/filings` | A,O,T-own | 401,403,404,422,409 |
| Submit filing | `PATCH /api/v1/filings/{id}/submit` | A,O,T-own | 401,403,404,400 |
| Filing detail | `GET /api/v1/filings/{id}` | A,O,T-own | 401,403,404 |
| Create correction filing | `POST /api/v1/filings/{id}/correct` | A,O,T-own | 401,403,404,400,409 |
| Retrieve filing receipt | `GET /api/v1/filings/{id}/receipt` | A,O,T-own | 401,403,404 |
| Preview legal filing deadline | `GET /api/v1/vat-deadlines?party_id&period&afregningsperiode_type` | A,O,T-own | 401,403,404,422 |
| Assessments list | `GET /api/v1/assessments` | A,O all; T own only | 401 |
| Create assessment | `POST /api/v1/assessments` | A,O | 401,403,404,400,409,422 |
| Assessment detail | `GET /api/v1/assessments/{id}` | A,O,T-own | 401,403,404 |
| Update assessment status | `PATCH /api/v1/assessments/{id}/status` | A,O | 401,403,404,400 |
| Appeal assessment | `POST /api/v1/assessments/{id}/appeal` | T-own | 401,403,404,400,422 |
| Admin users page load/manage | `GET/POST/PATCH /api/v1/admin/users...` | A only | 401,403,404,409,422 |
| Admin settings page load/update | `GET/PATCH /api/v1/admin/settings...` | A only | 401,403,404,422 |
| Assessment create/update side-effect policy | `POST /api/v1/assessments`, `PATCH /api/v1/assessments/{id}/status` | A,O | Filing state is unchanged unless a dedicated filing endpoint is called |
| Assessment appeal side-effect policy | `POST /api/v1/assessments/{id}/appeal` | T-own | Filing state is unchanged unless a dedicated filing endpoint is called |

### 8.4 Intentional Deviations from SKAT Benchmark

| Area | SKAT benchmark | Platform decision | Rationale |
|---|---|---|---|
| UI language | Danish-first labels/terms | UI mostly English with Danish domain labels in field names and help text | Product decision fixed by owner; reduces implementation ambiguity for mixed-language teams |
| Internal status codes | Danish terms in UI/process wording | Canonical persistence uses English status enums; UI maps to localized labels | Keeps API contracts stable while allowing localized display |
| Line-item data | Fixed Rubrik form entry in TastSelv | Optional `supplemental_line_items` plus transitional `line_items` transport accepted, both non-canonical | Supports current UI adapter compatibility without replacing legal Rubrik fields |
| Admin module | TastSelv does not expose this internal admin model | `/admin/users` and `/admin/settings` in scope now | Required by product owner for operational governance |

### 8.5 Resolved Blockers Checklist (Mapped to Reviewer Findings)

| Reviewer finding | Resolution in this spec |
|---|---|
| Filing model mismatch (`FilingLineItem` vs Rubrik fields) | Section 3.2 canonical filing model now uses fixed Rubrik fields; line items are non-canonical optional payload only |
| Missing admin API coverage (`/admin/users`, `/admin/settings`) | Sections 5 and 8 add admin routers and endpoint contracts |
| Implicit filing transition on assessment creation | Section 3.1.1 and Section 4.5 explicitly remove implicit filing mutation on assessment create/update |
| `assessment_date` string type | Section 4.2 and 4.3 changed to typed `date` fields |
| Weak ownership policy on Any reads | Section 2.8 and Section 8.1 add explicit row-level ownership predicates and testable failure modes |
| Missing page/action to endpoint mapping | Section 8.3 parity matrix maps designed actions to endpoints/auth/failures |
| Deadlines/penalties not enforceable | Sections 3.5, 4.5, and 8.2 define deterministic API/service enforcement contracts |
| Multi-tax ambiguity in Phase 2 | Section 3.2 hard-constrains `angivelse_type='MOMS'` for Phase 2; non-VAT types explicitly deferred |
| Event payloads not aligned with canonical filing | Sections 3.6, 4.6, and 7 update event contracts with typed/legal fields |

---

## Appendix A: Complete File Manifest

```
app/
|- config.py                   MODIFY (add SECRET_KEY + token settings)
|- main.py                     REPLACE (full replacement, Section 5)
|- dependencies/
|  |- __init__.py              CREATE (empty)
|  `- auth.py                  CREATE
|- models/
|  |- user.py                  CREATE
|  |- filing.py                CREATE (canonical VAT fields)
|  |- assessment.py            CREATE (typed dates + surcharge/interest)
|  `- admin_setting.py         CREATE
|- schemas/
|  |- auth.py                  CREATE
|  |- filing.py                CREATE
|  |- assessment.py            CREATE
|  `- admin.py                 CREATE
|- repositories/
|  |- filing.py                CREATE
|  |- assessment.py            CREATE
|  |- policy.py                CREATE (effective-dated VAT fee/interest/deadline policies)
|  `- admin.py                 CREATE
|- services/
|  |- authz.py                 CREATE (ownership policy helpers)
|  |- filing.py                CREATE
|  |- assessment.py            CREATE
|  `- admin.py                 CREATE
|- events/
|  |- filing_events.py         CREATE
|  |- assessment_events.py     CREATE
|  `- handlers/
|     |- filing_handlers.py    CREATE
|     `- assessment_handlers.py CREATE
`- routers/
   |- auth.py                  CREATE
   |- filings.py               CREATE
   |- assessments.py           CREATE
   `- admin.py                 CREATE

alembic/versions/
|- 0002_add_users_table.py               CREATE
|- 0003_add_vat_filing_canonical_table.py CREATE
|- 0004_add_typed_tax_assessments.py     CREATE
`- 0005_add_admin_settings.py            CREATE
```

## Appendix B: Python Dependency Additions

Add to `requirements.txt`:
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
email-validator==2.1.1
```

## Appendix C: Frontend TypeScript Types

**`types/auth.ts`**
```typescript
export type UserRole = 'ADMIN' | 'OFFICER' | 'TAXPAYER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
```

**`types/filing.ts`**
```typescript
export type AngivelseType = 'MOMS';
export type FilingStatus =
  | 'DRAFT'
  | 'SUBMITTED_WITH_RECEIPT'
  | 'UNDER_REVIEW'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'CORRECTED';

export interface FilingCreate {
  party_id: string;
  se_nummer: string;
  afregningsperiode_type: 'MONTHLY' | 'QUARTERLY' | 'SEMI_ANNUAL';
  filing_period: string;
  angivelse_type: AngivelseType;
  rubrik_a: string;
  rubrik_b: string;
  rubrik_c: string;
  rubrik_d: string;
  rubrik_e: string;
  momspligtig_omsaetning: string;
  momsfri_omsaetning: string;
  eksport: string;
  line_items?: Array<{ code: string; amount: string }>; // transitional adapter input, non-canonical
  supplemental_line_items?: Array<Record<string, unknown>>;
}

export interface FilingRead {
  id: string;
  party_id: string;
  se_nummer: string;
  afregningsperiode_type: 'MONTHLY' | 'QUARTERLY' | 'SEMI_ANNUAL';
  filing_period: string;
  angivelse_type: AngivelseType;
  status: FilingStatus;
  version: number;
  rubrik_a: string;
  rubrik_b: string;
  rubrik_c: string;
  rubrik_d: string;
  rubrik_e: string;
  momspligtig_omsaetning: string;
  momsfri_omsaetning: string;
  eksport: string;
  momstilsvar: string;
  frist: string; // YYYY-MM-DD
  late_filing_days: number;
  late_filing_penalty: string;
  submitted_at: string | null;
  kvitteringsnummer: string | null;
  submission_outcome: 'PAYABLE' | 'REFUNDABLE' | 'NIL' | null;
  korrektionsangivelse: boolean;
  original_filing_id: string | null;
  supplemental_line_items: Array<Record<string, unknown>> | null;
  created_at: string;
  updated_at: string;
}

export interface FilingReceiptRead {
  filing_id: string;
  receipt_id: string;
  submitted_at: string;
  submission_outcome: 'PAYABLE' | 'REFUNDABLE' | 'NIL';
  momstilsvar: string;
}

export interface FilingDeadlineRead {
  party_id: string;
  period_key: string;
  afregningsperiode_type: 'MONTHLY' | 'QUARTERLY' | 'SEMI_ANNUAL';
  deadline: string;
  rule_basis: string;
}
```

**`types/assessment.ts`**
```typescript
export type AssessmentStatus = 'PENDING' | 'COMPLETE' | 'APPEALED';
export type AssessmentOutcome = 'ACCEPTED' | 'ADJUSTED' | 'REJECTED';

export interface AssessmentCreate {
  filing_id: string;
  assessment_date: string; // YYYY-MM-DD
  decision_outcome: AssessmentOutcome;
  tax_due: string;
  surcharge_amount: string;
  interest_amount: string;
  payment_deadline: string; // YYYY-MM-DD
  appeal_deadline: string; // YYYY-MM-DD
  notes?: string;
}

export interface AssessmentStatusUpdate {
  status: AssessmentStatus;
}

export interface AssessmentAppealCreate {
  reason: string;
}

export interface AssessmentRead {
  id: string;
  filing_id: string;
  assessed_by: string;
  assessment_date: string;
  decision_outcome: AssessmentOutcome;
  tax_due: string;
  surcharge_amount: string;
  interest_amount: string;
  payment_deadline: string;
  appeal_deadline: string;
  appealed_at: string | null;
  status: AssessmentStatus;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```

**`types/admin.ts`**
```typescript
export interface AdminUserRead {
  id: string;
  email: string;
  full_name: string;
  role: 'ADMIN' | 'OFFICER' | 'TAXPAYER';
  is_active: boolean;
}

export interface AdminSettingRead {
  key: string;
  value: Record<string, unknown> | string | number | boolean | null;
  updated_by: string | null;
  updated_at: string;
}
```

**`types/api.ts`**
```typescript
export interface ApiErrorDetail { detail: string | ValidationError[]; }
export interface ValidationError {
  type: string; loc: (string | number)[]; msg: string; input: unknown;
}
```

## Pass-2 Delta + Unresolved Blockers

### Pass-2 Delta

- Aligned filing/assessment state semantics with latest Designer flow: no implicit filing status mutation from assessment create/update.
- Replaced hardcoded late-penalty assumptions with policy-driven fee hooks and effective-date resolution.
- Added deterministic deadline algorithm details (monthly/quarterly/semi-annual + next bank-day adjustment).
- Added explicit receipt contract (`submission_outcome`, receipt retrieval endpoint).
- Added legal-baseline endpoint `/api/v1/vat-deadlines` from Researcher findings. Removed `/api/v1/vat-filings*` alias routes per Phase 1 review decision.
- Added transitional non-canonical `line_items` adapter input while keeping fixed VAT fields canonical.

### Unresolved Blockers

- None blocking for Architect scope.

## Pass-3 delta (state-policy alignment)

- Normalized correction precondition wording to canonical status-set notation and removed slash-alias style.
- Added explicit state-policy note that assessment endpoints must keep filing transition as `NO_CHANGE`.
- Clarified `UNDER_REVIEW` policy as reserved/deferred in Phase 2 and excluded from active transition paths.
- Added explicit API parity row confirming assessment appeal also has no implicit filing mutation.

## Micro-fix delta

- Removed stale cross-agent unresolved-blocker note that no longer applies.
- Reconfirmed decoupled state policy: assessment endpoints remain `NO_CHANGE` for filing transitions.
- Standardized `UNDER_REVIEW` treatment as reserved/deferred (forward compatibility only), not an active Phase 2 transition path.







