import os

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("S3_ACCESS_KEY_ID", "test-key")
os.environ.setdefault("S3_SECRET_ACCESS_KEY", "test-secret")
os.environ.setdefault("S3_BUCKET", "aikon-test")
