# NetSage AI — AI-Assisted Network Troubleshooting Platform

<div align="center">

**Networking + AI + Explainability + Human Oversight**

An intelligent troubleshooting assistant for Cisco Packet Tracer / Cisco-style lab networks that diagnoses network issues using AI, validates with deterministic rules, and requires human review before accepting any fix.

</div>

---

## Problem Statement

Junior network engineers often know individual commands but struggle to connect a symptom to the real root cause. When a PC gets an IP address but cannot reach a server, is the problem VLAN, routing, DHCP, DNS, ACL, or NAT?

NetSage AI bridges this gap by:
- Analyzing symptoms, topology notes, and `show` command outputs
- Providing AI-powered diagnosis with confidence levels
- Running deterministic rule-based checks independently
- **Always requiring human review** before any fix is accepted

## Architecture

```
NetSage AI/
├── backend/                    # Python FastAPI backend
│   ├── main.py                # Application entry point
│   ├── database.py            # SQLite database layer
│   ├── models.py              # Pydantic data models
│   ├── seed.py                # Database seeder (35 cases)
│   └── routers/               # API route handlers
│       ├── cases.py           # CRUD for cases
│       ├── diagnosis.py       # AI diagnosis & rule checker
│       ├── reviews.py         # Human review workflow
│       └── dashboard.py       # Dashboard stats & analytics
├── ai/                        # AI diagnosis engine
│   ├── diagnosis/
│   │   ├── engine.py          # Provider abstraction layer
│   │   ├── mock_provider.py   # Demo mode (no API key needed)
│   │   └── openai_provider.py # OpenAI-compatible API
│   └── schemas/
│       └── diagnosis_schema.py # JSON validation
├── rule_checker/              # Deterministic Python checks
│   ├── ip_checks.py           # Duplicate IP detection
│   ├── subnet_checks.py       # Wrong subnet masks
│   ├── gateway_checks.py      # Gateway mismatch
│   ├── interface_checks.py    # Interface down detection
│   ├── vlan_checks.py         # Missing VLAN detection
│   ├── routing_checks.py      # Missing route detection
│   └── main.py                # Check orchestrator
├── frontend/                  # Professional SPA frontend
│   ├── index.html             # Main application shell
│   ├── css/styles.css         # Dark theme design system
│   └── js/                    # Application JavaScript
├── dataset/
│   └── cases.csv              # 35 realistic troubleshooting cases
├── docs/
│   └── diagnose_prompt.md     # AI prompt library
├── tests/                     # Test suite
├── run.py                     # Single-command launcher
└── README.md
```

## Features

### Dashboard
- Total cases, analyzed, accepted, edited, rejected counts
- AI-human agreement rate
- Cases by issue type, severity, and OSI layer
- Interactive charts (Chart.js)
- Recent cases table

### Case Management
- Create, view, edit, and delete troubleshooting cases
- Filter by status, issue type, and severity
- 35 pre-loaded realistic Cisco lab scenarios

### AI Diagnosis Engine
- Structured JSON diagnosis output
- Root cause, confidence, OSI layer, evidence
- Next command recommendation
- Step-by-step fix instructions
- Alternative causes when confidence is low
- Provider abstraction (OpenAI API or mock demo)

### Rule-Based Python Checker
- Duplicate IP detection
- Wrong subnet masks
- Gateway mismatch
- Interface down (admin/operational)
- Missing VLAN
- Missing routes / routing loops
- OSPF/EIGRP configuration issues

### Human Review Workflow
- Accept, Edit, or Reject every AI diagnosis
- Reviewer notes and edited diagnosis storage
- Complete audit trail
- Case status tracking

### Responsible AI
- 5 documented cases where AI was corrected
- AI vs human correction comparison
- Lessons learned from each correction
- Agreement rate calculation

### Demo Mode
- Guided step-by-step walkthrough
- Uses CASE-001 (Wrong VLAN Assignment)
- Complete workflow from symptom to resolution

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python FastAPI |
| Frontend | HTML5 / CSS3 / JavaScript (SPA) |
| Database | SQLite (PostgreSQL-ready) |
| AI | OpenAI-compatible API + Mock Provider |
| Charts | Chart.js |
| Styling | Custom CSS (dark NOC theme) |
| Fonts | Inter, JetBrains Mono |

## Installation

### Prerequisites
- Python 3.10+ (tested with Python 3.14)

### Setup

```bash
# Clone or navigate to the project directory
cd "NetSage AI"

# Install Python dependencies
pip install -r backend/requirements.txt

# (Optional) Set up OpenAI API key for real AI diagnosis
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Environment Variables

```env
# OpenAI API Key (leave empty for demo mode)
OPENAI_API_KEY=

# Optional: Custom OpenAI-compatible base URL
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Model selection
OPENAI_MODEL=gpt-4o-mini
```

**No API key required for demo mode.** The application uses a case-aware mock provider that generates realistic diagnoses clearly labeled as "[DEMO MODE]".

## Running the Application

### Start the Server

```bash
python run.py
```

The server starts at **http://localhost:8000**

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Run the Python Rule Checker (Standalone)

```bash
python rule_checker/main.py
```

### Run Tests

```bash
# All tests (set encoding for Windows)
set PYTHONIOENCODING=utf-8
python tests/test_rule_checker.py
python tests/test_ai_schema.py
python tests/test_reviews.py
python tests/test_agreement.py
```

## Dataset Format

The `dataset/cases.csv` contains 35 realistic troubleshooting cases with columns:

| Column | Description |
|--------|-------------|
| case_id | Unique case identifier |
| title | Descriptive case title |
| symptom | Observed problem description |
| topology_notes | Network topology information |
| show_outputs | Cisco `show` command output |
| expected_fault | Known root cause |
| osi_layer | Affected OSI layer(s) |
| concept | Issue category (VLAN, DHCP, etc.) |
| severity | Low / Medium / High / Critical |

### Issue Categories Covered
- VLAN (7 cases) — wrong assignment, trunk, native mismatch, VTP, STP, port security, EtherChannel
- Gateway (6 cases) — wrong gateway, interface down, duplex, subnet mismatch, duplicate IP, clock rate
- DHCP (4 cases) — pool misconfiguration, excluded addresses, relay, snooping
- DNS (2 cases) — missing DNS config, unreachable server
- Routing (7 cases) — static route, OSPF, EIGRP, HSRP, wildcard mask, routing loop, subinterface
- ACL (2 cases) — HTTP blocking, implicit deny
- NAT (3 cases) — inside/outside, pool exhaustion, static mapping
- Wireless (4 cases) — SSID disabled, guest isolation, security mismatch, channel overlap

## AI Prompt Architecture

The prompt library (`docs/diagnose_prompt.md`) defines:

1. **System Role** — NetSage AI as a Cisco troubleshooting expert
2. **Core Principles** — Evidence-based reasoning, no hallucination
3. **Required JSON Schema** — Structured output format
4. **Insufficient Evidence Protocol** — How to handle missing data
5. **3 Worked Examples** — High confidence, medium confidence, and insufficient evidence

The AI must:
- Only reference evidence from provided `show` command output
- Never invent or fabricate evidence
- Give calibrated confidence scores
- Recommend the next diagnostic command
- Never suggest automatic command execution

## Human Review Workflow

```
AI Diagnosis Generated
        ↓
Human Reviewer Sees Diagnosis
        ↓
    ┌───────┬────────┬───────┐
    │Accept │ Edit   │Reject │
    └───┬───┘────┬───┘───┬───┘
        │        │       │
        ▼        ▼       ▼
    Resolved  Resolved  Rejected
    (as-is)   (modified) (re-analyze)
```

Every review records:
- Case ID, AI diagnosis, reviewer decision
- Edited diagnosis (if modified)
- Reviewer notes, timestamp

**The AI never automatically applies fixes.** All recommendations require human approval.

## Responsible AI Approach

NetSage AI embeds responsible AI principles:

1. **Human Oversight** — Every AI diagnosis must be reviewed
2. **Transparency** — AI confidence and evidence are always visible
3. **Correction Logging** — Cases where AI was wrong are documented
4. **Dual Validation** — Deterministic rule checker runs independently of AI
5. **No Auto-Execution** — Configuration commands are only recommended, never applied
6. **Agreement Tracking** — AI-human alignment is continuously measured

### Agreement Rate Formula

```
AI-Human Agreement Rate = Accepted Cases / Reviewed Cases × 100
```

## Demo Instructions

1. Start the application: `python run.py`
2. Open http://localhost:8000 in your browser
3. Click **Demo Mode** in the sidebar
4. Follow the 8-step guided walkthrough:
   - Identify the problem (CASE-001: Wrong VLAN Assignment)
   - Examine symptoms and evidence
   - Run the deterministic rule checker
   - Run AI diagnosis
   - Review AI evidence
   - Submit human review (Accept/Edit/Reject)
   - View fix recommendations
   - Complete with full audit trail

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/cases | List all cases |
| GET | /api/cases/{id} | Get single case |
| POST | /api/cases | Create new case |
| PUT | /api/cases/{id} | Update case |
| DELETE | /api/cases/{id} | Delete case |
| POST | /api/diagnosis/{id}/ai | Run AI diagnosis |
| POST | /api/diagnosis/{id}/rule-check | Run rule checker |
| GET | /api/diagnosis/{id} | Get latest diagnosis |
| POST | /api/reviews/{id} | Submit review |
| GET | /api/reviews/{id} | Get reviews for case |
| GET | /api/dashboard/stats | Dashboard statistics |
| GET | /api/dashboard/analytics | Analytics data |
| GET | /api/dashboard/responsible-ai | Responsible AI log |
| GET | /health | Health check |

## Team Members

- Abhishek kumar Das Pattanayak (2306172)
- Abhipray Pradhan (2306004)
- surya prakash (2306236)


## License

This project is built for educational and demonstration purposes.

