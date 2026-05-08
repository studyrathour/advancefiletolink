# File2Link Bot Advanced - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Environment Variables](#environment-variables)
6. [Deployment](#deployment)
7. [Bot Commands](#bot-commands)
8. [Workflow](#workflow)
9. [Git Repository](#git-repository)
10. [Changelog](#changelog)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Project Name:** File2Link Bot Advanced  
**Repository:** https://github.com/studyrathour/FiletoLink_bot_Advanced  
**Description:** A Telegram bot that converts files to direct download/stream links, merged from three sources for best speed + features + admin panel.  
**License:** MIT

---

## Features

### Core Features
- ⚡ **Fast Streaming** - Raw API streaming with 1MB chunks for maximum speed
- 📤 **Auto File Upload** - Files sent to bot are automatically processed
- 📢 **Channel Posting** - Process files from channels where bot is admin
- 🔗 **Multi-Instance Support** - Multiple bot tokens for load balancing

### User Management
- 🔒 **Ban/Unban Users** - Block users from using the bot
- 👥 **Authorization** - Authorize specific users permanently
- 📊 **User Tracking** - Track user activity in MongoDB

### Monitoring
- 📈 **Ping Command** - Check bot response time
- ⚡ **Speed Test** - Run network speed test
- 📊 **Stats Command** - View bot statistics and system info
- 🎛️ **Status Command** - View client workload status

### Admin Panel (Web Dashboard)
- 🔐 **Login System** - Session-based authentication
- 📁 **File Management** - Search, disable, delete files
- 📊 **Statistics** - Total files, downloads, storage info
- ⚙️ **Settings** - Password change, system info

### Additional Features
- 🚀 **Rate Limiting** - Prevent abuse
- 🔗 **Token System** - Token-based access control
- 📢 **Broadcast** - Send messages to all users
- 🔒 **Force Subscribe** - Require channel membership
- 📝 **Logging** - Log user activities

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Telegram Bot | Pyrogram 2.0.106 |
| Web Framework | FastAPI 0.109.0 |
| ASGI Server | Uvicorn 0.27.0 |
| Database | MongoDB (Motor async) |
| Templates | Jinja2 |
| Frontend | TailwindCSS (CDN) |
| Python | 3.14 |

---

## Project Structure

```
FiletoLink_bot_Advanced/
├── app.py                    # Main entry point (FastAPI + Pyrogram)
├── config.py                 # Configuration management
├── database.py               # MongoDB operations
├── streamer.py               # ByteStreamer for fast streaming
├── requirements.txt          # Python dependencies
├── render.yaml               # Render deployment config
├── config.env.example        # Environment template
├── .gitignore                # Git ignore rules
│
├── plugins/                  # Bot handlers
│   ├── __init__.py           # Plugin loader
│   ├── stream.py             # File processing (upload/stream)
│   ├── admin.py              # Admin commands (ban/unban/broadcast)
│   ├── common.py             # User commands (start/help/ping/stats)
│   └── callbacks.py          # Inline button handlers
│
├── utils/                    # Utility modules
│   ├── __init__.py           # Decorators
│   ├── rate_limiter.py       # Rate limiting
│   └── speedtest.py          # Speed test module
│
├── server/                   # Web server
│   ├── __init__.py
│   └── stream_routes.py      # Streaming endpoints + admin routes
│
├── templates/                # HTML templates
│   ├── show.html             # Download/stream page
│   └── admin/                # Admin panel
│       ├── login.html        # Admin login
│       ├── dashboard.html    # Dashboard with file management
│       └── settings.html     # Settings page
│
└── static/                   # Static files
    ├── css/admin.css
    └── js/admin.js
```

---

## Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID (from my.telegram.org) | `12345678` |
| `API_HASH` | Telegram API Hash | `abc123def456...` |
| `BOT_TOKEN` | Bot token from @BotFather | `123456789:ABCdefGHI...` |
| `BIN_CHANNEL` | Private channel for file storage | `-1001234567890` |
| `OWNER_ID` | Your Telegram user ID | `123456789` |
| `DATABASE_URL` | MongoDB connection string | `mongodb+srv://user:pass@host/db` |
| `PORT` | Web server port | `8080` |

### Optional Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_ENABLED` | `False` | Enable admin panel |
| `ADMIN_EMAIL` | `admin@example.com` | Admin login email |
| `ADMIN_PASSWORD` | `admin123` | Admin login password |
| `SESSION_SECRET` | `random-string` | Session secret key |
| `CHANNEL` | `False` | Enable channel message processing |
| `FORCE_CHANNEL_ID` | (none) | Required channel for users |
| `BANNED_CHANNELS` | (none) | Space-separated banned channels |
| `TOKEN_ENABLED` | `False` | Enable token-based access |
| `TOKEN_TTL_HOURS` | `24` | Token validity in hours |
| `RATE_LIMIT_ENABLED` | `False` | Enable rate limiting |
| `MAX_FILES_PER_PERIOD` | `2` | Max files per period |
| `RATE_LIMIT_PERIOD_MINUTES` | `1` | Rate limit period |
| `MAX_QUEUE_SIZE` | `100` | Max queued requests |
| `MULTI_TOKEN1` | (none) | Additional bot token |
| `MULTI_TOKEN2` | (none) | Additional bot token |
| `MULTI_TOKEN3` | (none) | Additional bot token |
| `LOG_CHANNEL` | (none) | Channel for activity logs |

---

## Deployment

### Deploy to Render (Free Tier)

1. **Push to GitHub** - Code is already pushed
2. **Create Web Service on Render:**
   - Connect to GitHub repository
   - Select the repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
3. **Add Environment Variables** in Render dashboard
4. **Deploy** - Wait for deployment to complete
5. **Test** - Send `/start` to your bot on Telegram

### Local Development

```bash
# Clone repository
git clone https://github.com/studyrathour/FiletoLink_bot_Advanced.git
cd FiletoLink_bot_Advanced

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create config.env
cp config.env.example config.env
# Edit config.env with your values

# Run the bot
python app.py
```

---

## Bot Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help message |
| `/link` | Generate link (reply to file) |
| `/ping` | Check bot latency |
| `/stats` | View bot statistics |
| `/dc` | Get data center info |
| `/about` | Bot information |

### Admin Commands (Owner Only)
| Command | Description |
|---------|-------------|
| `/ban <user_id> [reason]` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/authorize <user_id>` | Authorize a user |
| `/deauthorize <user_id>` | Remove user authorization |
| `/listauth` | List authorized users |
| `/users` | Total user count |
| `/broadcast` | Broadcast message (reply to message) |
| `/banned` | List banned users |
| `/speedtest` | Run speed test |
| `/status` | View client status |

---

## Workflow

### File Upload Flow
```
User sends file → Bot checks banned/auth →
Forwards to BIN_CHANNEL → Generates unique ID →
Saves to MongoDB → Returns download/stream links
```

### Streaming Flow
```
User visits URL → Server checks file exists →
Increments download count → Gets file from Telegram →
Streams via raw API (1MB chunks) → Returns to user
```

### Multi-Instance Flow
```
Request arrives → Server gets lowest workload client →
Client fetches file from BIN_CHANNEL →
ByteStreamer streams in 1MB chunks →
Returns to user
```

### Admin Panel Flow
```
User visits /admin → Login page →
Enter credentials → Session created →
Dashboard with file stats → Can disable/delete files
```

---

## Git Repository

**URL:** https://github.com/studyrathour/FiletoLink_bot_Advanced

### Git Commands Used
```bash
# Initialize
git init
git config user.name "Suraj Rathour"
git config user.email "surajrathour111@gmail.com"

# Add remote
git remote add origin https://github.com/studyrathour/FiletoLink_bot_Advanced.git

# Add and commit
git add .
git commit -m "Initial commit"

# Push
git branch -M main
git push -u origin main
```

---

## Changelog

### Commit History

| Commit | Description |
|--------|-------------|
| `67a3417` | Initial commit - Merged File-to-stream speed + FileToLink2 features + Admin panel |
| `f0bca01` | Fix: pyrogram version 2.0.106 |
| `020c9b6` | Add Procfile for Render |
| `f65161b` | Fix: Use uvicorn in Procfile |
| `1fdefe8` | Add render.yaml to fix deployment |
| `423eaf3` | Fix: Remove Procfile, use uvicorn in render.yaml |
| `6c7de26` | Fix: SyntaxError in async generator |
| `b5d52ae` | Fix: Route path error in app.py |
| `a146e96` | Fix: MULTI_TOKEN property to method |
| `84a57ab` | Add tgcrypto and debug logging |
| `40c9696` | Fix: session storage and route handling |
| `a321439` | Remove optional vars from config.env |

---

## Troubleshooting

### Common Issues

**1. Bot not replying**
- Check Render logs for startup errors
- Verify BOT_TOKEN is set correctly
- Ensure MongoDB connection works

**2. "Failed to start bot: unable to open database file"**
- Fixed by using `in_memory=True` and `/tmp/sessions`
- This is already in the latest code

**3. 404 on routes**
- Fixed route adding logic in app.py
- Ensure start command is correct

**4. TgCrypto warning**
- Not critical, bot will work
- Add `tgcrypto==1.2.5` to requirements for faster performance

**5. MongoDB connection error**
- Verify DATABASE_URL is correct
- Check MongoDB credentials

### Debug Mode

Check Render logs for:
- `BOT_TOKEN: xxx` - Should show token (masked)
- `MULTI_TOKEN: []` - Should show tokens or empty
- `Failed to start bot: <error>` - Shows the error

---

## Credits

### Original Repositories
1. **File-to-stream** (Speed optimized)
   - https://github.com/GrabCoolGadgets/File-to-stream

2. **FileToLink2** (Features)
   - https://github.com/studyrathour/FileToLink2

3. **telegram-file-to-link-bot** (Admin Panel)
   - https://github.com/studyrathour/telegram-file-to-link-bot

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues before creating new one