import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")

    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    MULTI_TOKEN_1 = os.getenv("MULTI_TOKEN_1", "")
    MULTI_TOKEN_2 = os.getenv("MULTI_TOKEN_2", "")
    MULTI_TOKEN_3 = os.getenv("MULTI_TOKEN_3", "")
    MULTI_TOKEN_4 = os.getenv("MULTI_TOKEN_4", "")
    MULTI_TOKEN_5 = os.getenv("MULTI_TOKEN_5", "")

    @property
    def MULTI_TOKEN(self):
        tokens = []
        for i in range(1, 50):
            token = os.getenv(f"MULTI_TOKEN_{i}", "")
            if token:
                tokens.append(token)
        return tokens

    BIN_CHANNEL = int(os.getenv("BIN_CHANNEL", 0))
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    OWNER_ID = int(os.getenv("OWNER_ID", 0))

    FQDN = os.getenv("FQDN", "")
    HAS_SSL = os.getenv("HAS_SSL", "True").lower() == "true"
    NO_PORT = os.getenv("NO_PORT", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 8080))
    BIND_ADDRESS = os.getenv("BIND_ADDRESS", "0.0.0.0")

    @property
    def BASE_URL(self):
        if self.FQDN:
            if self.NO_PORT or self.HAS_SSL:
                return f"https://{self.FQDN}"
            else:
                return f"http://{self.FQDN}:{self.PORT}"
        return f"http://localhost:{self.PORT}"

    FORCE_CHANNEL_ID = int(os.getenv("FORCE_CHANNEL_ID", 0)) if os.getenv("FORCE_CHANNEL_ID") else None

    CHANNEL = os.getenv("CHANNEL", "False").lower() == "true"

    BANNED_CHANNELS = set(int(x) for x in os.getenv("BANNED_CHANNELS", "").split() if x)

    MAX_BATCH_FILES = int(os.getenv("MAX_BATCH_FILES", 50))

    SET_COMMANDS = os.getenv("SET_COMMANDS", "True").lower() == "true"

    TOKEN_ENABLED = os.getenv("TOKEN_ENABLED", "False").lower() == "true"
    TOKEN_TTL_HOURS = int(os.getenv("TOKEN_TTL_HOURS", 24))

    SHORTEN_ENABLED = os.getenv("SHORTEN_ENABLED", "False").lower() == "true"
    SHORTEN_MEDIA_LINKS = os.getenv("SHORTEN_MEDIA_LINKS", "False").lower() == "true"
    URL_SHORTENER_API_KEY = os.getenv("URL_SHORTENER_API_KEY", "")
    URL_SHORTENER_SITE = os.getenv("URL_SHORTENER_SITE", "")

    GLOBAL_RATE_LIMIT = os.getenv("GLOBAL_RATE_LIMIT", "False").lower() == "true"
    MAX_GLOBAL_REQUESTS_PER_MINUTE = int(os.getenv("MAX_GLOBAL_REQUESTS_PER_MINUTE", 4))

    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"
    MAX_FILES_PER_PERIOD = int(os.getenv("MAX_FILES_PER_PERIOD", 2))
    RATE_LIMIT_PERIOD_MINUTES = int(os.getenv("RATE_LIMIT_PERIOD_MINUTES", 1))
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 100))

    UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/fyaz05/FileToLink")
    UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "main")

    NAME = os.getenv("NAME", "ThunderF2L")
    SLEEP_THRESHOLD = int(os.getenv("SLEEP_THRESHOLD", 600))
    WORKERS = int(os.getenv("WORKERS", 8))
    PING_INTERVAL = int(os.getenv("PING_INTERVAL", 840))

    ADMIN_ENABLED = os.getenv("ADMIN_ENABLED", "False").lower() == "true"
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    SESSION_SECRET = os.getenv("SESSION_SECRET", "your-secret-key-change-me")

    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0)) if os.getenv("LOG_CHANNEL") else None

    FINGERPRINT = os.getenv("FINGERPRINT", "")

    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 0)) * 1024 * 1024 if os.getenv("MAX_FILE_SIZE") else 0