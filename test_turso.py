
import os
import asyncio
import libsql_client
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = os.getenv("TURSO_DATABASE_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    client = libsql_client.create_client(url=url, auth_token=token)
    try:
        print("TURSO_DATABASE_URL:", os.getenv("TURSO_DATABASE_URL"))
        print("TURSO_AUTH_TOKEN:", os.getenv("TURSO_AUTH_TOKEN"))
        result = await client.execute("SELECT 1;")
        print(result.rows)
    finally:
        await client.close()

asyncio.run(test())