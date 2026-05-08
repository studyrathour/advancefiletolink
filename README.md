# File2Link Bot Advanced ⚡

A high-speed Telegram file-to-link converter with advanced features and admin panel.

## Features

- ⚡ **Fast Streaming** - Raw API streaming with 1MB chunks
- 📤 **Auto File Upload** - Files processed automatically
- 📢 **Channel Posting** - Process files from channels
- 🔒 **User Management** - Ban/unban, authorize users
- 📊 **Monitoring** - Ping, speedtest, stats
- 🎛️ **Admin Panel** - Web dashboard for file management
- 🚀 **Multi-Instance** - Multiple bot tokens support

## Tech Stack

- Pyrogram 2.0.106
- FastAPI 0.109.0
- MongoDB (Motor)
- Uvicorn

## Quick Deploy

### Render (Free)

1. Fork this repository
2. Create a Web Service on Render
3. Add environment variables:
   - `API_ID`, `API_HASH`, `BOT_TOKEN`
   - `BIN_CHANNEL`, `OWNER_ID`
   - `DATABASE_URL`
4. Deploy!

### Environment Variables

```
API_ID=12345678
API_HASH=your_hash
BOT_TOKEN=your_token
BIN_CHANNEL=-1001234567890
OWNER_ID=123456789
DATABASE_URL=mongodb+srv://...
PORT=8080
```

### Admin Panel (Optional)
```
ADMIN_ENABLED=True
ADMIN_EMAIL=admin@email.com
ADMIN_PASSWORD=your_password
SESSION_SECRET=secret_key
```

## Bot Commands

- `/start` - Start bot
- `/help` - Help
- `/link` - Generate link (reply to file)
- `/ping` - Check latency
- `/stats` - View statistics

### Admin Only
- `/ban`, `/unban` - Ban/unban users
- `/broadcast` - Broadcast message
- `/speedtest` - Run speed test

## Documentation

See [memory.md](./memory.md) for complete documentation.

## Credits

Based on:
- [File-to-stream](https://github.com/GrabCoolGadgets/File-to-stream) - Speed
- [FileToLink2](https://github.com/studyrathour/FileToLink2) - Features

## License

MIT