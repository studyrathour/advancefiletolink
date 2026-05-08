from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

client = AsyncIOMotorClient(Config.DATABASE_URL)
db = client.file2link

users_collection = db.users
banned_users_collection = db.banned_users
banned_channels_collection = db.banned_channels
authorized_users_collection = db.authorized_users
tokens_collection = db.tokens
files_collection = db.files
admins_collection = db.admins
workloads_collection = db.workloads
settings_collection = db.settings

async def init_db():
    await files_collection.create_index("file_id", unique=True)
    await files_collection.create_index("user_id")
    await tokens_collection.create_index("token", unique=True)
    await tokens_collection.create_index("expire_at")
    await users_collection.create_index("user_id", unique=True)

async def save_file(file_id, message_id, file_name, file_size, user_id, dc_id, file_type):
    await files_collection.update_one(
        {"file_id": file_id},
        {
            "$set": {
                "message_id": message_id,
                "file_name": file_name,
                "file_size": file_size,
                "user_id": user_id,
                "dc_id": dc_id,
                "file_type": file_type,
                "downloads": 0,
                "created_at": files_collection.database.client.server_info()
            }
        },
        upsert=True
    )

async def get_file(file_id):
    return await files_collection.find_one({"file_id": file_id})

async def increment_downloads(file_id):
    await files_collection.update_one(
        {"file_id": file_id},
        {"$inc": {"downloads": 1}}
    )

async def delete_file(file_id):
    await files_collection.delete_one({"file_id": file_id})

async def get_all_files(limit=50):
    return await files_collection.find().sort("downloads", -1).limit(limit).to_list(length=None)

async def search_files(query):
    return await files_collection.find({"file_name": {"$regex": query, "$options": "i"}}).to_list(length=None)

async def get_file_stats():
    total = await files_collection.count_documents({})
    downloads = await files_collection.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$downloads"}}}
    ]).to_list(length=None)
    total_downloads = downloads[0]["total"] if downloads else 0
    return {"total_files": total, "total_downloads": total_downloads}

async def save_user(user_id, name, username):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"name": name, "username": username}},
        upsert=True
    )

async def get_user(user_id):
    return await users_collection.find_one({"user_id": user_id})

async def get_all_users():
    return await users_collection.find().to_list(length=None)

async def get_user_count():
    return await users_collection.count_documents({})

async def is_banned_user(user_id):
    return await banned_users_collection.find_one({"user_id": user_id}) is not None

async def ban_user(user_id, reason=None):
    await banned_users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"reason": reason, "banned_at": files_collection.database.client.server_info()}},
        upsert=True
    )

async def unban_user(user_id):
    await banned_users_collection.delete_one({"user_id": user_id})

async def get_banned_users():
    return await banned_users_collection.find().to_list(length=None)

async def is_banned_channel(channel_id):
    return await banned_channels_collection.find_one({"channel_id": channel_id}) is not None

async def ban_channel(channel_id, reason=None):
    await banned_channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"reason": reason, "banned_at": files_collection.database.client.server_info()}},
        upsert=True
    )

async def unban_channel(channel_id):
    await banned_channels_collection.delete_one({"channel_id": channel_id})

async def is_authorized(user_id):
    return await authorized_users_collection.find_one({"user_id": user_id}) is not None

async def authorize_user(user_id):
    await authorized_users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"authorized_at": files_collection.database.client.server_info()}},
        upsert=True
    )

async def deauthorize_user(user_id):
    await authorized_users_collection.delete_one({"user_id": user_id})

async def get_authorized_users():
    return await authorized_users_collection.find().to_list(length=None)

async def save_token(token, user_id):
    from datetime import datetime, timedelta
    from config import Config
    expire_at = datetime.utcnow() + timedelta(hours=Config.TOKEN_TTL_HOURS)
    await tokens_collection.update_one(
        {"token": token},
        {"$set": {"user_id": user_id, "expire_at": expire_at}},
        upsert=True
    )

async def get_token(token):
    return await tokens_collection.find_one({"token": token})

async def delete_expired_tokens():
    from datetime import datetime
    await tokens_collection.delete_many({"expire_at": {"$lt": datetime.utcnow()}})

async def save_admin(email, password_hash):
    await admins_collection.update_one(
        {"email": email},
        {"$set": {"password_hash": password_hash}},
        upsert=True
    )

async def get_admin(email):
    return await admins_collection.find_one({"email": email})

async def get_admin_by_id(admin_id):
    return await admins_collection.find_one({"_id": admin_id})

async def update_workload(client_index, workload):
    await workloads_collection.update_one(
        {"client_index": client_index},
        {"$set": {"workload": workload, "updated_at": files_collection.database.client.server_info()}},
        upsert=True
    )

async def get_all_workloads():
    return await workloads_collection.find().to_list(length=None)

async def get_min_workload_client():
    workloads = await get_all_workloads()
    if not workloads:
        return 0
    return min(workloads, key=lambda x: x.get("workload", 0)).get("client_index", 0)

async def save_setting(key, value):
    await settings_collection.update_one(
        {"key": key},
        {"$set": {"value": value}},
        upsert=True
    )

async def get_setting(key):
    doc = await settings_collection.find_one({"key": key})
    return doc["value"] if doc else None