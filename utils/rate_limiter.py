import time
from collections import defaultdict
from config import Config
import database as db

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)
        self.queue = []
        self.queue_size = 0

    async def check_rate_limit(self, user_id: int) -> bool:
        if not Config.RATE_LIMIT_ENABLED:
            return True

        if user_id == Config.OWNER_ID:
            return True

        if await db.is_authorized(user_id):
            return True

        if self.queue_size >= Config.MAX_QUEUE_SIZE:
            return False

        now = time.time()
        window = Config.RATE_LIMIT_PERIOD_MINUTES * 60

        user_requests = self.user_requests[user_id]
        user_requests = [t for t in user_requests if now - t < window]
        self.user_requests[user_id] = user_requests

        if len(user_requests) >= Config.MAX_FILES_PER_PERIOD:
            return False

        user_requests.append(now)
        self.queue_size += 1
        return True

    async def release_slot(self, user_id: int):
        self.queue_size = max(0, self.queue_size - 1)

rate_limiter = RateLimiter()