# Agent Architect Specification — Danish Tax Administration Platform

**Status:** Authoritative source of truth for all Coder agents
**Date:** 2026-02-23
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
│   │   ├── Badge.tsx                 # Status badge (DRAFT, SUBMITTED, etc.)
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

### 2.2 New Database Table: `users`

**`app/models/user.py`**
```python
import uuid

from sqlalchemy import Boolean, String
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
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "TAXPAYER"
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

---

## 3. Tax Filing Module

### 3.1 Overview

The Filing module follows the **identical** structural pattern as the Registration module.

| Registration (existing) | Filing (new) |
|---|---|
| `app/models/party.py` | `app/models/filing.py` |
| `app/schemas/party.py` | `app/schemas/filing.py` |
| `app/repositories/party.py` | `app/repositories/filing.py` |
| `app/services/party.py` | `app/services/filing.py` |
| `app/events/party_events.py` | `app/events/filing_events.py` |
| `app/events/handlers/party_handlers.py` | `app/events/handlers/filing_handlers.py` |
| `app/routers/parties.py` | `app/routers/filings.py` |

### 3.2 Domain Model

**`app/models/filing.py`**
```python
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid


class Filing(Base, TimestampMixin):
    __tablename__ = "filings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parties.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    filing_period: Mapped[str] = mapped_column(String(20), nullable=False)
    filing_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    line_items: Mapped[list["FilingLineItem"]] = relationship(
        back_populates="filing", cascade="all, delete-orphan"
    )


class FilingLineItem(Base, TimestampMixin):
    __tablename__ = "filing_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    filing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filings.id", ondelete="CASCADE"), nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    filing: Mapped["Filing"] = relationship(back_populates="line_items")
```

**Valid field values:**

| Field | Valid Values |
|---|---|
| `filing_type` | `VAT`, `INCOME_TAX` |
| `status` | `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `ACCEPTED`, `REJECTED` |
| `filing_period` | `YYYY-QN` for quarterly (e.g. `2024-Q1`), `YYYY-MM` for monthly |

### 3.3 Pydantic Schemas

**`app/schemas/filing.py`**
```python
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FilingLineItemCreate(BaseModel):
    description: str = Field(..., examples=["Revenue from restaurant sales"])
    amount: Decimal = Field(..., examples=[Decimal("15000.00")])


class FilingLineItemRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    description: str
    amount: Decimal
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_map(cls, obj) -> "FilingLineItemRead":
        return cls(id=obj.id, description=obj.description, amount=obj.amount,
                   created_at=obj.created_at, updated_at=obj.updated_at)


class FilingCreate(BaseModel):
    party_id: uuid.UUID
    filing_period: str = Field(..., examples=["2024-Q1"])
    filing_type: str = Field(..., examples=["VAT"])
    total_amount: Decimal = Field(default=Decimal("0.00"))
    line_items: list[FilingLineItemCreate] = []


class FilingRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    party_id: uuid.UUID
    filing_period: str
    filing_type: str
    status: str
    total_amount: Decimal
    submitted_at: datetime | None
    line_items: list[FilingLineItemRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "FilingRead":
        return cls(
            id=obj.id, party_id=obj.party_id, filing_period=obj.filing_period,
            filing_type=obj.filing_type, status=obj.status, total_amount=obj.total_amount,
            submitted_at=obj.submitted_at,
            line_items=[FilingLineItemRead.from_orm_map(li) for li in obj.line_items],
            created_at=obj.created_at, updated_at=obj.updated_at,
        )
```

### 3.4 Repository

**`app/repositories/filing.py`**
```python
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.filing import Filing, FilingLineItem
from app.schemas.filing import FilingCreate


class FilingRepository:

    def create_filing(self, payload: FilingCreate, db: Session) -> Filing:
        filing = Filing(
            party_id=payload.party_id, filing_period=payload.filing_period,
            filing_type=payload.filing_type, total_amount=payload.total_amount,
            status="DRAFT",
        )
        db.add(filing)
        db.flush()
        for item in payload.line_items:
            db.add(FilingLineItem(filing_id=filing.id, description=item.description, amount=item.amount))
        db.commit()
        return self.get_filing_by_id(filing.id, db)  # type: ignore[return-value]

    def get_filing_by_id(self, filing_id: uuid.UUID, db: Session) -> Filing | None:
        return (
            db.query(Filing).options(selectinload(Filing.line_items))
            .filter(Filing.id == filing_id).first()
        )

    def list_filings_by_party(self, party_id: uuid.UUID, db: Session) -> list[Filing]:
        return (
            db.query(Filing).options(selectinload(Filing.line_items))
            .filter(Filing.party_id == party_id)
            .order_by(Filing.created_at.desc()).all()
        )

    def submit_filing(self, filing_id: uuid.UUID, db: Session) -> Filing | None:
        filing = db.query(Filing).filter(Filing.id == filing_id).first()
        if filing is None:
            return None
        filing.status = "SUBMITTED"
        filing.submitted_at = datetime.now(timezone.utc)
        db.commit()
        return self.get_filing_by_id(filing_id, db)
```

### 3.5 Service

**`app/services/filing.py`**
```python
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.events.base import EventBus
from app.events.filing_events import FilingCreated, FilingSubmitted
from app.models.filing import Filing
from app.repositories.filing import FilingRepository
from app.schemas.filing import FilingCreate


class FilingService:
    def __init__(self, repo: FilingRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def create_filing(self, payload: FilingCreate, db: Session) -> Filing:
        filing = self._repo.create_filing(payload, db)
        await self._bus.publish(FilingCreated(
            filing_id=filing.id, party_id=filing.party_id,
            filing_type=filing.filing_type, filing_period=filing.filing_period,
        ))
        return filing

    async def get_filing(self, filing_id: uuid.UUID, db: Session) -> Filing:
        filing = self._repo.get_filing_by_id(filing_id, db)
        if filing is None:
            raise HTTPException(status_code=404, detail="Filing not found")
        return filing

    async def list_filings_for_party(self, party_id: uuid.UUID, db: Session) -> list[Filing]:
        return self._repo.list_filings_by_party(party_id, db)

    async def submit_filing(self, filing_id: uuid.UUID, db: Session) -> Filing:
        filing = self._repo.get_filing_by_id(filing_id, db)
        if filing is None:
            raise HTTPException(status_code=404, detail="Filing not found")
        if filing.status != "DRAFT":
            raise HTTPException(
                status_code=400,
                detail=f"Filing cannot be submitted from status '{filing.status}'. Only DRAFT filings may be submitted.",
            )
        filing = self._repo.submit_filing(filing_id, db)
        await self._bus.publish(FilingSubmitted(
            filing_id=filing.id, party_id=filing.party_id,
            filing_type=filing.filing_type, filing_period=filing.filing_period,
            total_amount=filing.total_amount,
        ))
        return filing
```

### 3.6 Domain Events

**`app/events/filing_events.py`**
```python
import uuid
from decimal import Decimal

from app.events.base import BaseEvent


class FilingCreated(BaseEvent):
    filing_id: uuid.UUID
    party_id: uuid.UUID
    filing_type: str
    filing_period: str


class FilingSubmitted(BaseEvent):
    filing_id: uuid.UUID
    party_id: uuid.UUID
    filing_type: str
    filing_period: str
    total_amount: Decimal
```

**`app/events/handlers/filing_handlers.py`**
```python
import logging

from app.events.filing_events import FilingCreated, FilingSubmitted

logger = logging.getLogger(__name__)


def on_filing_created(event: FilingCreated) -> None:
    logger.info(
        "Filing created — filing_id=%s party_id=%s type=%s period=%s",
        event.filing_id, event.party_id, event.filing_type, event.filing_period,
    )


def on_filing_submitted(event: FilingSubmitted) -> None:
    logger.info(
        "Filing submitted — filing_id=%s party_id=%s type=%s period=%s amount=%s",
        event.filing_id, event.party_id, event.filing_type,
        event.filing_period, event.total_amount,
    )
```

### 3.7 Router

**`app/routers/filings.py`**
```python
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.filing import FilingCreate, FilingRead
from app.services.filing import FilingService

router = APIRouter(prefix="/api/v1", tags=["filings"])


def get_filing_service() -> FilingService:
    raise NotImplementedError


@router.post("/filings", response_model=FilingRead, status_code=status.HTTP_201_CREATED)
async def create_filing(
    payload: FilingCreate, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    _: User = Depends(require_role("TAXPAYER", "OFFICER", "ADMIN")),
) -> FilingRead:
    filing = await service.create_filing(payload, db)
    return FilingRead.from_orm(filing)


@router.get("/filings/{filing_id}", response_model=FilingRead)
async def get_filing(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    _: User = Depends(get_current_user),
) -> FilingRead:
    filing = await service.get_filing(filing_id, db)
    return FilingRead.from_orm(filing)


@router.get("/parties/{party_id}/filings", response_model=list[FilingRead])
async def list_party_filings(
    party_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    _: User = Depends(get_current_user),
) -> list[FilingRead]:
    filings = await service.list_filings_for_party(party_id, db)
    return [FilingRead.from_orm(f) for f in filings]


@router.patch("/filings/{filing_id}/submit", response_model=FilingRead)
async def submit_filing(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: FilingService = Depends(get_filing_service),
    _: User = Depends(require_role("TAXPAYER", "OFFICER", "ADMIN")),
) -> FilingRead:
    filing = await service.submit_filing(filing_id, db)
    return FilingRead.from_orm(filing)
```

---

## 4. Tax Assessment Module

### 4.1 Overview

A `TaxAssessment` is created by an OFFICER or ADMIN after reviewing a submitted filing. Subscribes to `FilingSubmitted`.

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
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
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
    assessment_date: Mapped[str] = mapped_column(String(20), nullable=False)
    tax_due: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    penalties: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Status transitions:**

| From | Allowed transitions |
|---|---|
| `PENDING` | `COMPLETE`, `APPEALED` |
| `COMPLETE` | `APPEALED` |
| `APPEALED` | (terminal) |

`filing_id` carries a UNIQUE constraint — one assessment per filing only. Duplicate returns HTTP 409.

### 4.3 Pydantic Schemas

**`app/schemas/assessment.py`**
```python
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    filing_id: uuid.UUID
    assessment_date: str = Field(..., examples=["2024-03-15"])
    tax_due: Decimal = Field(..., examples=[Decimal("5000.00")])
    penalties: Decimal = Field(default=Decimal("0.00"))
    notes: str | None = None


class AssessmentStatusUpdate(BaseModel):
    status: str = Field(..., examples=["COMPLETE"])


class AssessmentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    filing_id: uuid.UUID
    assessed_by: uuid.UUID
    assessment_date: str
    tax_due: Decimal
    penalties: Decimal
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj) -> "AssessmentRead":
        return cls(
            id=obj.id, filing_id=obj.filing_id, assessed_by=obj.assessed_by,
            assessment_date=obj.assessment_date, tax_due=obj.tax_due,
            penalties=obj.penalties, status=obj.status, notes=obj.notes,
            created_at=obj.created_at, updated_at=obj.updated_at,
        )
```

### 4.4 Repository

**`app/repositories/assessment.py`**
```python
import uuid

from sqlalchemy.orm import Session

from app.models.assessment import TaxAssessment
from app.schemas.assessment import AssessmentCreate


class AssessmentRepository:

    def create_assessment(self, payload: AssessmentCreate, assessed_by: uuid.UUID, db: Session) -> TaxAssessment:
        assessment = TaxAssessment(
            filing_id=payload.filing_id, assessed_by=assessed_by,
            assessment_date=payload.assessment_date, tax_due=payload.tax_due,
            penalties=payload.penalties, status="PENDING", notes=payload.notes,
        )
        db.add(assessment)
        db.commit()
        return self.get_assessment_by_id(assessment.id, db)  # type: ignore[return-value]

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
        return self.get_assessment_by_id(assessment_id, db)
```

### 4.5 Service

**`app/services/assessment.py`**
```python
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.events.assessment_events import AssessmentCompleted, AssessmentCreated
from app.events.base import EventBus
from app.models.assessment import TaxAssessment
from app.repositories.assessment import AssessmentRepository
from app.schemas.assessment import AssessmentCreate

VALID_STATUS_TRANSITIONS: dict[str, set[str]] = {
    "PENDING":  {"COMPLETE", "APPEALED"},
    "COMPLETE": {"APPEALED"},
    "APPEALED": set(),
}


class AssessmentService:
    def __init__(self, repo: AssessmentRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def create_assessment(self, payload: AssessmentCreate, assessed_by: uuid.UUID, db: Session) -> TaxAssessment:
        existing = self._repo.get_assessment_by_filing(payload.filing_id, db)
        if existing is not None:
            raise HTTPException(status_code=409, detail=f"Assessment already exists for filing {payload.filing_id}")
        assessment = self._repo.create_assessment(payload, assessed_by, db)
        await self._bus.publish(AssessmentCreated(
            assessment_id=assessment.id, filing_id=assessment.filing_id, assessed_by=assessment.assessed_by,
        ))
        return assessment

    async def get_assessment(self, assessment_id: uuid.UUID, db: Session) -> TaxAssessment:
        assessment = self._repo.get_assessment_by_id(assessment_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return assessment

    async def get_assessment_for_filing(self, filing_id: uuid.UUID, db: Session) -> TaxAssessment:
        assessment = self._repo.get_assessment_by_filing(filing_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail=f"No assessment found for filing {filing_id}")
        return assessment

    async def update_status(self, assessment_id: uuid.UUID, new_status: str, db: Session) -> TaxAssessment:
        assessment = self._repo.get_assessment_by_id(assessment_id, db)
        if assessment is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        allowed = VALID_STATUS_TRANSITIONS.get(assessment.status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{assessment.status}' to '{new_status}'. Allowed: {sorted(allowed) if allowed else 'none'}",
            )
        assessment = self._repo.update_status(assessment_id, new_status, db)
        if new_status == "COMPLETE":
            await self._bus.publish(AssessmentCompleted(
                assessment_id=assessment.id, filing_id=assessment.filing_id,
                tax_due=assessment.tax_due, penalties=assessment.penalties,
            ))
        return assessment
```

### 4.6 Domain Events

**`app/events/assessment_events.py`**
```python
import uuid
from decimal import Decimal

from app.events.base import BaseEvent


class AssessmentCreated(BaseEvent):
    assessment_id: uuid.UUID
    filing_id: uuid.UUID
    assessed_by: uuid.UUID


class AssessmentCompleted(BaseEvent):
    assessment_id: uuid.UUID
    filing_id: uuid.UUID
    tax_due: Decimal
    penalties: Decimal
```

**`app/events/handlers/assessment_handlers.py`**
```python
import logging

from app.events.assessment_events import AssessmentCompleted, AssessmentCreated
from app.events.filing_events import FilingSubmitted

logger = logging.getLogger(__name__)


def on_filing_submitted_notify_assessment(event: FilingSubmitted) -> None:
    logger.info(
        "Filing awaiting assessment — filing_id=%s party_id=%s type=%s period=%s amount=%s",
        event.filing_id, event.party_id, event.filing_type, event.filing_period, event.total_amount,
    )


def on_assessment_created(event: AssessmentCreated) -> None:
    logger.info(
        "Assessment created — assessment_id=%s filing_id=%s assessed_by=%s",
        event.assessment_id, event.filing_id, event.assessed_by,
    )


def on_assessment_completed(event: AssessmentCompleted) -> None:
    logger.info(
        "Assessment completed — assessment_id=%s filing_id=%s tax_due=%s penalties=%s",
        event.assessment_id, event.filing_id, event.tax_due, event.penalties,
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
from app.schemas.assessment import AssessmentCreate, AssessmentRead, AssessmentStatusUpdate
from app.services.assessment import AssessmentService

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])
filing_assessment_router = APIRouter(prefix="/api/v1/filings", tags=["assessments"])


def get_assessment_service() -> AssessmentService:
    raise NotImplementedError


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    payload: AssessmentCreate, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    current_user: User = Depends(require_role("OFFICER", "ADMIN")),
) -> AssessmentRead:
    assessment = await service.create_assessment(payload, current_user.id, db)
    return AssessmentRead.from_orm(assessment)


@router.get("/{assessment_id}", response_model=AssessmentRead)
async def get_assessment(
    assessment_id: uuid.UUID, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    _: User = Depends(get_current_user),
) -> AssessmentRead:
    assessment = await service.get_assessment(assessment_id, db)
    return AssessmentRead.from_orm(assessment)


@router.patch("/{assessment_id}/status", response_model=AssessmentRead)
async def update_assessment_status(
    assessment_id: uuid.UUID, payload: AssessmentStatusUpdate,
    db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    _: User = Depends(require_role("OFFICER", "ADMIN")),
) -> AssessmentRead:
    assessment = await service.update_status(assessment_id, payload.status, db)
    return AssessmentRead.from_orm(assessment)


@filing_assessment_router.get("/{filing_id}/assessment", response_model=AssessmentRead)
async def get_filing_assessment(
    filing_id: uuid.UUID, db: Session = Depends(get_db),
    service: AssessmentService = Depends(get_assessment_service),
    _: User = Depends(get_current_user),
) -> AssessmentRead:
    assessment = await service.get_assessment_for_filing(filing_id, db)
    return AssessmentRead.from_orm(assessment)
```

---

## 5. Updated app/main.py Wiring

```python
import logging

from fastapi import FastAPI

from app.events.assessment_events import AssessmentCompleted, AssessmentCreated
from app.events.bus import InMemoryEventBus
from app.events.filing_events import FilingCreated, FilingSubmitted
from app.events.handlers.assessment_handlers import (
    on_assessment_completed, on_assessment_created,
    on_filing_submitted_notify_assessment,
)
from app.events.handlers.filing_handlers import on_filing_created, on_filing_submitted
from app.events.handlers.party_handlers import on_party_registered, on_party_role_assigned
from app.events.party_events import PartyRegistered, PartyRoleAssigned
from app.repositories.assessment import AssessmentRepository
from app.repositories.filing import FilingRepository
from app.repositories.party import PartyRepository
from app.routers import parties, roles
from app.routers import auth as auth_module
from app.routers.assessments import (
    filing_assessment_router, get_assessment_service,
    router as assessments_router,
)
from app.routers.filings import get_filing_service, router as filings_router
from app.routers.parties import get_party_service
from app.services.assessment import AssessmentService
from app.services.filing import FilingService
from app.services.party import PartyService

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Danish Tax Administration Platform",
    version="2.0.0",
    description="Registration, Filing, and Assessment modules.",
)

# ── Event Bus ─────────────────────────────────────────────────────────────────
bus = InMemoryEventBus()

bus.subscribe(PartyRegistered, on_party_registered)
bus.subscribe(PartyRoleAssigned, on_party_role_assigned)
bus.subscribe(FilingCreated, on_filing_created)
bus.subscribe(FilingSubmitted, on_filing_submitted)
bus.subscribe(FilingSubmitted, on_filing_submitted_notify_assessment)
bus.subscribe(AssessmentCreated, on_assessment_created)
bus.subscribe(AssessmentCompleted, on_assessment_completed)

# ── Services ──────────────────────────────────────────────────────────────────
party_service    = PartyService(repo=PartyRepository(), bus=bus)
filing_service   = FilingService(repo=FilingRepository(), bus=bus)
assessment_service = AssessmentService(repo=AssessmentRepository(), bus=bus)

# ── Dependency Overrides ──────────────────────────────────────────────────────
app.dependency_overrides[get_party_service]      = lambda: party_service
app.dependency_overrides[get_filing_service]     = lambda: filing_service
app.dependency_overrides[get_assessment_service] = lambda: assessment_service

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_module.router)
app.include_router(parties.router)
app.include_router(roles.router)
app.include_router(filings_router)
app.include_router(assessments_router)
app.include_router(filing_assessment_router)


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
0003_add_filings_tables
     |
     v
0004_add_tax_assessments_table
```

### Migration 0002 — `users`

**`alembic/versions/0002_add_users_table.py`**
```python
"""add users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-23
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
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
```

### Migration 0003 — `filings` and `filing_line_items`

**`alembic/versions/0003_add_filings_tables.py`**
```python
"""add filings and filing_line_items tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-02-23
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
        sa.Column("filing_period", sa.String(20), nullable=False),
        sa.Column("filing_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["party_id"], ["parties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_filings_party_id", "filings", ["party_id"])

    op.create_table(
        "filing_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["filing_id"], ["filings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("filing_line_items")
    op.drop_index("ix_filings_party_id", table_name="filings")
    op.drop_table("filings")
```

### Migration 0004 — `tax_assessments`

**`alembic/versions/0004_add_tax_assessments_table.py`**
```python
"""add tax_assessments table

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-23
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
        sa.Column("assessment_date", sa.String(20), nullable=False),
        sa.Column("tax_due", sa.Numeric(18, 2), nullable=False),
        sa.Column("penalties", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0.00")),
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

### New Tables Summary

| Table | Primary Key | Foreign Keys | Notable Constraints |
|---|---|---|---|
| `users` | `id` UUID | — | `email` UNIQUE |
| `filings` | `id` UUID | `party_id` → `parties.id` CASCADE | index on `party_id` |
| `filing_line_items` | `id` UUID | `filing_id` → `filings.id` CASCADE | — |
| `tax_assessments` | `id` UUID | `filing_id` → `filings.id` CASCADE; `assessed_by` → `users.id` SET NULL | `filing_id` UNIQUE |

---

## 7. Cross-Module Event Flow Diagram

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         REGISTRATION MODULE                                  ║
║  POST /api/v1/parties                                                        ║
║    └─> PartyService.register_party()                                         ║
║          ├─> PartyRepository.create_party()      [DB: parties + children]   ║
║          └─> EventBus.publish(PartyRegistered)                               ║
║                └─> on_party_registered()         [logs]                     ║
║  POST /api/v1/parties/{id}/roles                                             ║
║    └─> PartyService.assign_role()                                            ║
║          ├─> PartyRepository.create_role()       [DB: party_roles]          ║
║          └─> EventBus.publish(PartyRoleAssigned)                             ║
║                └─> on_party_role_assigned()      [logs]                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║                           FILING MODULE                                      ║
║  POST /api/v1/filings                                                        ║
║    └─> FilingService.create_filing()                                         ║
║          ├─> FilingRepository.create_filing()    [DB: filings + line_items] ║
║          └─> EventBus.publish(FilingCreated)                                 ║
║                └─> on_filing_created()           [logs]                     ║
║  PATCH /api/v1/filings/{id}/submit                                           ║
║    └─> FilingService.submit_filing()                                         ║
║          ├─> FilingRepository.submit_filing()    [DB: status=SUBMITTED]     ║
║          └─> EventBus.publish(FilingSubmitted) ──────────────────────────┐  ║
║                └─> on_filing_submitted()         [Filing module logs]     │  ║
╚══════════════════════════════════════════════════════════════════════════════╝
                                                                           │
                    FilingSubmitted crosses module boundary                │
                    via EventBus — Assessment never imports FilingService  │
                                                                           v
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ASSESSMENT MODULE                                     ║
║  <── FilingSubmitted received                                                ║
║        └─> on_filing_submitted_notify_assessment() [logs; future: notify]  ║
║  POST /api/v1/assessments          (OFFICER or ADMIN only)                  ║
║    └─> AssessmentService.create_assessment()                                 ║
║          ├─> AssessmentRepository.create_assessment() [DB: tax_assessments] ║
║          └─> EventBus.publish(AssessmentCreated)                             ║
║                └─> on_assessment_created()       [logs]                     ║
║  PATCH /api/v1/assessments/{id}/status  (→ "COMPLETE")                      ║
║    └─> AssessmentService.update_status()                                     ║
║          ├─> AssessmentRepository.update_status() [DB: status=COMPLETE]     ║
║          └─> EventBus.publish(AssessmentCompleted)                           ║
║                └─> on_assessment_completed()     [logs]                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Event Ownership Table

| Event | Published by | Subscribed by |
|---|---|---|
| `PartyRegistered` | `PartyService` | `on_party_registered` (Registration) |
| `PartyRoleAssigned` | `PartyService` | `on_party_role_assigned` (Registration) |
| `FilingCreated` | `FilingService` | `on_filing_created` (Filing) |
| `FilingSubmitted` | `FilingService` | `on_filing_submitted` (Filing) + `on_filing_submitted_notify_assessment` (Assessment) |
| `AssessmentCreated` | `AssessmentService` | `on_assessment_created` (Assessment) |
| `AssessmentCompleted` | `AssessmentService` | `on_assessment_completed` (Assessment) |

---

## 8. API Contract Summary

| # | Method | Path | Auth | Roles | Request Schema | Response Schema | Code |
|---|---|---|---|---|---|---|---|
| 1 | GET | `/health` | No | — | — | `{"status":"ok"}` | 200 |
| 2 | POST | `/api/v1/auth/login` | No | — | `LoginRequest` | `{"message":"ok"}` + cookies | 200 |
| 3 | POST | `/api/v1/auth/refresh` | Cookie | — | — | `{"message":"ok"}` + cookies | 200 |
| 4 | POST | `/api/v1/auth/logout` | No | — | — | `{"message":"ok"}` | 200 |
| 5 | GET | `/api/v1/auth/me` | Yes | Any | — | `UserRead` | 200 |
| 6 | POST | `/api/v1/parties` | Yes | A,O,T | `PartyCreate` | `PartyRead` | 201 |
| 7 | GET | `/api/v1/parties/{id}` | Yes | Any | — | `PartyRead` | 200 |
| 8 | POST | `/api/v1/parties/{id}/roles` | Yes | A,O,T | `PartyRoleCreate` | `PartyRoleRead` | 201 |
| 9 | GET | `/api/v1/parties/{id}/roles` | Yes | Any | — | `list[PartyRoleRead]` | 200 |
| 10 | POST | `/api/v1/filings` | Yes | A,O,T | `FilingCreate` | `FilingRead` | 201 |
| 11 | GET | `/api/v1/filings/{id}` | Yes | Any | — | `FilingRead` | 200 |
| 12 | GET | `/api/v1/parties/{id}/filings` | Yes | Any | — | `list[FilingRead]` | 200 |
| 13 | PATCH | `/api/v1/filings/{id}/submit` | Yes | A,O,T | — | `FilingRead` | 200 |
| 14 | POST | `/api/v1/assessments` | Yes | A,O | `AssessmentCreate` | `AssessmentRead` | 201 |
| 15 | GET | `/api/v1/assessments/{id}` | Yes | Any | — | `AssessmentRead` | 200 |
| 16 | GET | `/api/v1/filings/{id}/assessment` | Yes | Any | — | `AssessmentRead` | 200 |
| 17 | PATCH | `/api/v1/assessments/{id}/status` | Yes | A,O | `AssessmentStatusUpdate` | `AssessmentRead` | 200 |

---

## Appendix A: Complete File Manifest

```
app/
├── config.py                   MODIFY (add SECRET_KEY + token settings)
├── main.py                     REPLACE (full replacement, Section 5)
├── dependencies/
│   ├── __init__.py             CREATE (empty)
│   └── auth.py                 CREATE
├── models/
│   ├── user.py                 CREATE
│   ├── filing.py               CREATE
│   └── assessment.py           CREATE
├── schemas/
│   ├── auth.py                 CREATE
│   ├── filing.py               CREATE
│   └── assessment.py           CREATE
├── repositories/
│   ├── filing.py               CREATE
│   └── assessment.py           CREATE
├── services/
│   ├── filing.py               CREATE
│   └── assessment.py           CREATE
├── events/
│   ├── filing_events.py        CREATE
│   ├── assessment_events.py    CREATE
│   └── handlers/
│       ├── filing_handlers.py      CREATE
│       └── assessment_handlers.py  CREATE
└── routers/
    ├── auth.py                 CREATE
    ├── filings.py              CREATE
    └── assessments.py          CREATE

alembic/versions/
├── 0002_add_users_table.py             CREATE
├── 0003_add_filings_tables.py          CREATE
└── 0004_add_tax_assessments_table.py   CREATE
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
export type FilingType   = 'VAT' | 'INCOME_TAX';
export type FilingStatus = 'DRAFT' | 'SUBMITTED' | 'UNDER_REVIEW' | 'ACCEPTED' | 'REJECTED';

export interface FilingLineItemCreate { description: string; amount: string; }
export interface FilingLineItemRead extends FilingLineItemCreate {
  id: string; created_at: string; updated_at: string;
}
export interface FilingCreate {
  party_id: string; filing_period: string; filing_type: FilingType;
  total_amount: string; line_items: FilingLineItemCreate[];
}
export interface FilingRead {
  id: string; party_id: string; filing_period: string; filing_type: FilingType;
  status: FilingStatus; total_amount: string; submitted_at: string | null;
  line_items: FilingLineItemRead[]; created_at: string; updated_at: string;
}
```

**`types/assessment.ts`**
```typescript
export type AssessmentStatus = 'PENDING' | 'COMPLETE' | 'APPEALED';

export interface AssessmentCreate {
  filing_id: string; assessment_date: string; tax_due: string;
  penalties: string; notes?: string;
}
export interface AssessmentStatusUpdate { status: AssessmentStatus; }
export interface AssessmentRead {
  id: string; filing_id: string; assessed_by: string; assessment_date: string;
  tax_due: string; penalties: string; status: AssessmentStatus;
  notes: string | null; created_at: string; updated_at: string;
}
```

**`types/api.ts`**
```typescript
export interface ApiErrorDetail { detail: string | ValidationError[]; }
export interface ValidationError {
  type: string; loc: (string | number)[]; msg: string; input: unknown;
}
```
