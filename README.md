# AI Test Case Generation Agent

An AI-powered platform that converts API requirements and feature specifications into structured QA test cases automatically.

The goal is simple:

Instead of manually writing validation tests, boundary checks, negative scenarios, and business-flow cases, engineers can paste requirements and instantly generate test coverage.

Built for the Agentic AI Hackathon.

---

## Why we built this

Writing test cases is repetitive.

A developer or QA engineer usually receives requirements like:

```text
Signup API

Fields:
email
password
phone

Rules:
Email valid
Password minimum 8 characters
Phone exactly 10 digits

Signup succeeds only when all fields are valid
```

From that, someone has to manually think about:

- Valid scenarios
- Invalid inputs
- Boundary values
- Missing fields
- Edge cases
- Success flows

That takes time.

It is also easy to miss important validations.

This project automates that process.

---

## What it does

Paste requirements.

The system analyzes them and generates:

- Functional test cases
- Boundary validations
- Negative scenarios
- Edge cases
- Business-flow validations

It also estimates coverage and exports results in structured JSON.

---

## Example

Input:

```text
Loan API

Rules:

loanAmount >= 5000

loanAmount <= 500000

PAN required

employmentType optional

Loan approved only when validations pass
```

Generated output:

### Boundary

```json
{
 "loanAmount":4999
}
```

Expected:

```
Validation fails because loanAmount is below minimum.
```

---

### Boundary

```json
{
 "loanAmount":5000
}
```

Expected:

```
Validation succeeds.
```

---

### Negative

```json
{
 "PAN":""
}
```

Expected:

```
Validation fails because PAN is required.
```

---

### Business Flow

```json
{
 "loanAmount":100000,
 "PAN":"ABCDE1234F"
}
```

Expected:

```
Loan approved.
```

---

## How it works

```text
Requirements Input
        ↓
Constraint Parser
        ↓
Rule Engine
        ↓
Coverage Engine
        ↓
Test Case Generator
        ↓
Export JSON
```

### Constraint Parser

Extracts:

- Required fields
- Optional fields
- Validation constraints
- Numeric boundaries
- Exact length rules
- Business conditions

### Rule Engine

Creates:

- Boundary tests
- Negative tests
- Functional tests
- Success paths
- Combined invalid scenarios

### Coverage Engine

Calculates:

- Coverage percentage
- Parsed constraints
- Generated categories
- Validation completeness

---

## Features

- Constraint extraction
- Boundary generation
- Negative test generation
- Business-flow validation
- Coverage estimation
- JSON export
- Example templates
- Responsive UI
- Dark SaaS interface
- Mobile support

---

## Tech Stack

Frontend:

- Next.js
- TypeScript
- React

Backend:

- Python
- Constraint parser
- Rule engine
- Coverage engine

Deployment:

Frontend:

- Vercel

Backend:

- Render

---

## Running locally

Clone repository:

```bash
git clone <repo-url>

cd ai-test-generator
```

Frontend:

```bash
cd frontend

npm install

npm run dev
```

Backend:

```bash
cd backend

pip install -r requirements.txt

python main.py
```

Frontend:

```
https://ai-test-generator-orcin.vercel.app
```

Backend:

```
https://ai-test-generator-fc41.onrender.com
```

---

## Example scenarios to try

### Signup API

```text
email
password
phone

Email valid

Password minimum 8

Phone exactly 10 digits
```

### Checkout API

```text
cartTotal > 0

paymentMethod required

coupon optional

Checkout succeeds only when payment succeeds
```

### Payment API

```text
amount > 0

currency required

maximum amount 50000
```

---

## Future improvements

- Swagger/OpenAPI import
- Playwright test export
- CI/CD integrations
- Persistent history
- Multi-language support
- PDF report generation

---

## License

MIT

---

Built to reduce repetitive QA effort and improve software validation workflows.
