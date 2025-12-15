from dotenv import load_dotenv
import os

load_dotenv()

#db
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

#channels
RELEASES_CHANNEL_ID = os.getenv("RELEASES_CHANNEL_ID")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")

#roles
NEW_RELEASES_ROLE_ID = os.getenv("NEW_RELEASES_ROLE_ID")

#routes
NOTIFY_API_ROUTE = os.getenv("NOTIFY_API_ROUTE")

#
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")