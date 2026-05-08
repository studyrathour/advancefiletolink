import asyncio
import math
from typing import Optional, AsyncIterator
from pyrogram import raw
from pyrogram.types import Message
from config import Config


class ByteStreamer:
    def __init__(self, clients: list):
        self.clients = clients
        self.media_sessions = {}
        self.work_loads = {i: 0 for i in range(len(clients))}

    async def get_media_session(self, dc_id: int, client_index: int = None) -> Optional[raw.Client]:
        if client_index is None:
            client_index = await self._get_best_client()

        if client_index not in self.media_sessions:
            client = self.clients[client_index]
            self.media_sessions[client_index] = await client.media_session()

        return self.media_sessions[client_index]

    async def _get_best_client(self) -> int:
        min_workload = min(self.work_loads.items(), key=lambda x: x[1])
        return min_workload[0]

    def update_workload(self, client_index: int, delta: int):
        self.work_loads[client_index] = max(0, self.work_loads.get(client_index, 0) + delta)

    async def stream_file(
        self,
        file_id: str,
        offset: int = 0,
        first_part: bool = True,
        part_size: int = 1024 * 1024,
    ) -> AsyncIterator[bytes]:
        client_index = await self._get_best_client()
        client = self.clients[client_index]
        media_session = await self.get_media_session(client_index, client_index)

        self.update_workload(client_index, 1)

        try:
            file = client.resolve_peer(file_id)
            location = raw.types.InputDocumentFileLocation(
                id=file.id,
                access_hash=file.access_hash,
                file_reference=file.file_reference,
            )

            while True:
                chunk = await self._fetch_chunk(
                    media_session,
                    location,
                    offset,
                    part_size,
                    client.dc_id
                )
                if not chunk:
                    break

                if len(chunk) < part_size:
                    yield chunk
                    break

                yield chunk
                offset += len(chunk)
        finally:
            self.update_workload(client_index, -1)

    async def _fetch_chunk(
        self,
        media_session: raw.Client,
        location: raw.types.InputDocumentFileLocation,
        offset: int,
        part_size: int,
        dc_id: int
    ) -> Optional[bytes]:
        try:
            result = await media_session.invoke(
                raw.functions.upload.GetFile(
                    location=location,
                    offset=offset,
                    limit=part_size
                )
            )
            if isinstance(result, raw.types.upload.File):
                return result.bytes
            return None
        except Exception as e:
            print(f"Error fetching chunk: {e}")
            return None

    async def get_file_size(self, file_id: str, client_index: int = None) -> int:
        if client_index is None:
            client_index = await self._get_best_client()

        client = self.clients[client_index]
        media_session = await self.get_media_session(client_index, client_index)

        try:
            file = client.resolve_peer(file_id)
            location = raw.types.InputDocumentFileLocation(
                id=file.id,
                access_hash=file.access_hash,
                file_reference=file.file_reference,
            )

            result = await media_session.invoke(
                raw.functions.upload.GetFile(
                    location=location,
                    offset=0,
                    limit=1
                )
            )
            if hasattr(result, 'size'):
                return result.size
        except Exception as e:
            print(f"Error getting file size: {e}")

        return 0

    async def cross_dc_auth(self, dc_id: int, client_index: int = None):
        if client_index is None:
            client_index = await self._get_best_client()

        client = self.clients[client_index]

        if client.dc_id != dc_id:
            try:
                auth_key = await client.invoke(
                    raw.functions.auth.ExportAuthorization(dc_id=dc_id)
                )
                await client.invoke(
                    raw.functions.auth.ImportAuthorization(
                        id=auth_key.id,
                        bytes=auth_key.bytes
                    )
                )
            except Exception as e:
                print(f"Cross-DC auth error: {e}")


streamer = None

def init_streamer(clients: list):
    global streamer
    streamer = ByteStreamer(clients)
    return streamer