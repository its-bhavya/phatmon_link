# Phantom Link BBS

A modern reimagining of the 1980s Bulletin Board System (BBS) that combines retro terminal aesthetics with real-time chat capabilities.

## Project Structure

```
phantom-link/
├── backend/                    # Python FastAPI backend
│   ├── auth/                   # Authentication module
│   ├── commands/               # Command handler module
│   ├── rooms/                  # Room management module
│   ├── websocket/              # WebSocket manager module
│   └── tests/                  # Backend tests
├── frontend/                   # Frontend HTML/CSS/JS
│   ├── css/                    # Stylesheets (CRT effects, terminal styling)
│   ├── js/                     # JavaScript modules
│   └── assets/                 # Static assets (fonts, sounds)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Setup

### 1. Create Python Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
copy .env.example .env
```

## Development

(To be added in later tasks)

## Testing

(To be added in later tasks)

## License

(To be determined)
