import speedtest
import asyncio
from config import Config

class SpeedTest:
    def __init__(self):
        self.st = speedtest.Speedtest()

    async def run(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run_sync)

    def _run_sync(self):
        try:
            self.st.get_best_server()
            download = self.st.download() / 1024 / 1024
            upload = self.st.upload() / 1024 / 1024
            return {
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": self.st.results.ping
            }
        except Exception as e:
            return {"error": str(e)}

speed_test = SpeedTest()