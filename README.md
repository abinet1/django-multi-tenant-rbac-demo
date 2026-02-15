# Django Multi-Tenant SaaS Backend Demo (DRF + JWT)

## The Video demo is in **Video Demo** folder and Postman collection **Django Multi-Tenant Backend.postman_collection.json**

**A complete implementation of the Demo Task** using Django and Django REST Framework.

This project is **backend-only** (no frontend, no email sending). All flows (invitations, password reset, product sharing) return tokens directly in JSON responses for demo purposes.


The implementation strictly follows the provided specification, including:
- Multi-app structure
- Role-based access control (RBAC)
- Multi-tenant scoping
- Correct model relations & constraints
- Basic security hardening (JWT, throttling, safe responses)

## Project Overview

This is a multi-tenant platform where:
- A **Tenant** represents an organization
- Each Tenant has multiple **Companies**
- Users have roles: **Admin**, **Manager**, **Staff**, **Customer**
- **Staff** create **Products** that can be shared via unguessable `share_token`
- **Customers** claim products via a public endpoint and get read-only access

The system starts with a **platform Superadmin** (created via `createsuperuser`) who bootstraps the first tenant.

## Key Features Implemented

- **Multi-Tenant Isolation** – All querysets filtered by `request.user.tenant`
- **Role-Based Access Control** – Custom permission classes matching the spec exactly
- **Invitation Flow** (API-only):
  - Bootstrap Admin (Superadmin → first Tenant Admin)
  - Manager invitation (Admin only)
  - Single-use, expiring, unguessable tokens
- **Direct Staff Creation** (Admin/Manager only, no invitation)
- **Product Sharing & Customer Claim** (public endpoint creates/logs in Customer)
- **JWT Authentication** with access + refresh tokens
- **Security**:
  - Throttling on login & password reset
  - Safe responses (no email existence leakage)
  - Strong password validation
  - Deny-by-default permissions
  - UUID primary keys (no ID guessing)
- **Multi-App Architecture** (required):
  - `accounts` – Custom User, auth, RBAC helpers
  - `tenants` – Tenant & Company models
  - `invitations` – Invitation model & accept flow
  - `products` – Product model & public claim
  - `core` – Shared utils (permissions, mixins, throttles)

All **21 required endpoints** are implemented with correct permissions and scoping.

## Tech Stack

- **Python** 3.10+
- **Django** 5.0.7
- **Django REST Framework** 3.15.2
- **djangorestframework-simplejwt** 5.3.1
- **UUID** for primary keys
- **SQLite** (development) – easily switch to PostgreSQL

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/django-multi-tenant-demo.git
cd django-multi-tenant-demo

# Create and activate virtual environment
python -m venv env
source env/bin/activate    # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create platform superadmin
python manage.py createsuperuser   # Use email as username

# Run development server
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

## Quick Start Demo Flow

1. Login as **Superadmin**
2. Create **Bootstrap Admin invitation**
3. Accept invitation → creates first Tenant + Admin
4. Login as **Admin**
5. Create Company → Create Staff
6. Login as **Staff** → Create Product (gets `share_token`)
7. Use `share_token` in public claim endpoint → creates Customer
8. Login as **Customer** → sees only their products
9. Login as **Admin** → views customers & their products

## API Endpoints (All 21 Implemented)

### Auth (`/api/auth/`)
- `POST /login/` → JWT tokens
- `POST /token/refresh/` → New access token
- `POST /password-reset/request/` → Safe reset token (no leakage)
- `POST /password-reset/confirm/` → Update password

### Invitations (`/api/invitations/`)
- `POST /bootstrap-admin/` (Superadmin only)
- `POST /` (Admin only – Manager invitation)
- `POST /accept/` (public)

### Tenant & Companies (`/api/`)
- `GET/PATCH /tenant/me/` (Admin/Manager; name read-only)
- `GET/POST/PATCH /companies/` & `/companies/{id}/` (Admin/Manager)

### Staff (`/api/`)
- `POST/GET /staff/` (Admin/Manager only)

### Products (`/api/`)
- `POST/PATCH/GET /products/` & `/products/{id}/` (role-scoped)

### Public (`/api/public/`)
- `POST /products/claim/` (no auth – creates Customer)

### Admin Views (`/api/admin/`)
- `GET /customers/` (Admin only)
- `GET /customers/{id}/products/` (Admin only)

Full details in the attached Postman collection.

## Permission Matrix (Exact Match)

| Action                                      | Superadmin | Admin | Manager | Staff          | Customer      |
|---------------------------------------------|------------|-------|---------|----------------|---------------|
| Bootstrap Admin invitation                  | Yes        | No    | No      | No             | No            |
| Invite Manager                              | No         | Yes   | No      | No             | No            |
| View/Edit Tenant (name read-only)           | No         | Yes   | View    | No             | No            |
| Manage Companies                            | No         | Yes   | Yes     | No             | No            |
| Create/List Staff                           | No         | Yes   | Yes     | No             | No            |
| Create/Update Products                      | No         | No    | No      | Yes (own company) | No         |
| List/View Products                          | No         | All   | All     | Own company    | Own only      |
| Claim Product (public)                      | Yes        | Yes   | Yes     | Yes            | Yes           |
| View Customers & Their Products             | No         | Yes   | No      | No             | No            |

## Security Implementation

- **Tenant Scoping**: `TenantScopedMixin` filters all querysets
- **Object-Level Permissions**: Staff & Customer can only access their own data
- **Throttling**: Applied to login & password reset
- **Safe Responses**: Password reset never leaks email existence
- **Token Security**: All tokens (invitation, share_token, reset) use `secrets.token_urlsafe(48)`
- **Password Validation**: Django's strong validators enforced
- **Deny-by-Default**: Global `IsAuthenticated` + role-specific permissions

## Testing with Postman

- Import the provided **Collection** and **Environment** JSON files
- Collection organized by user role for clear demonstration
- Includes **auto-save test scripts** for tokens, IDs, and share_token
- Use **Collection Runner** for fully automated end-to-end flow

## Demo Video

A 5–10 minute screen recording demonstrates:
- Full bootstrapping flow
- User creation (Superadmin → Admin → Manager → Staff → Customer)
- Product creation & sharing
- Customer claim
- Admin views
- Permission enforcement (forbidden attempts)
- Tenant isolation

(Link provided in submission)

## Compliance with Specification

This implementation **fully meets** all requirements from the task document:
- Multi-app structure
- Exact model schema & constraints
- All 21 endpoints with correct permissions
- Tenant name read-only
- No invitation for Staff
- Public claim creates/logs in Customer
- Security hardening (throttling, safe responses, etc.)

```