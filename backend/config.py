import os

class Config:
    """配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 hours
    
    # 文件上传配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'photos')
    CONTRACTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'contracts')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000']
    CORS_ALLOW_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
    CORS_MAX_AGE = 3600

    # 邮件服务配置
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@qq.com'  # 系统邮箱
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-password'  # 邮箱授权码

    @staticmethod
    def init_app(app):
        # 创建上传目录
        os.makedirs(Config.PHOTOS_FOLDER, exist_ok=True)
        os.makedirs(Config.CONTRACTS_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root:123456@localhost/personnel_management'

class TestingConfig(Config):
    TESTING = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    DEBUG = False
    # 生产环境下使用更安全的配置
    JWT_COOKIE_SECURE = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:123456@localhost/personnel_management'
    # 生产环境下限制CORS来源
    CORS_ORIGINS = ['https://your-production-domain.com']

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
