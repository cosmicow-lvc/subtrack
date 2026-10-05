import os


os.environ["POSTGRES_USER"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["POSTGRES_DB"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-bytes"
os.environ["CORS_ORIGINS"] = '["http://localhost"]'