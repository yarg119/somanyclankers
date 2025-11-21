write_file(file_path="lib/config.py", content="""
class Config:
    SECRET_KEY = 'your-256-bit-secret'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

# You can inherit this config for specific environments (e.g., development, production)
class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig(),
    'production': Config()
}
""")