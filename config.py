import os

# Get the absolute path of the directory containing this file.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base application configuration settings.

    It's recommended to set sensitive values using environment variables,
    especially for production deployments.
    """
    # A secret key is required for session management and CSRF protection.
    # WARNING: The default key is for development only and is insecure.
    #          You MUST set a proper SECRET_KEY environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-secret-key-for-development-only'

    # Database configuration.
    # The default URI is for a local MySQL database.
    # IMPORTANT: Update 'root' and 'drivemate' with your actual
    #            database username and name if they are different.
    # The `?charset=utf8mb4` is added to ensure compatibility with older
    # MySQL versions that do not support the default 'utf8mb4_0900_ai_ci' collation.
    # For production, it is highly recommended to set the DATABASE_URL
    # environment variable instead of hardcoding credentials.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://root@localhost/drivemate?charset=utf8mb4'

    # This disables a feature of Flask-SQLAlchemy that signals the application
    # every time a change is about to be made in the database. It's a good
    # practice to disable it to save resources unless you need it.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Explicitly set the session collation to a widely compatible one.
    # This is a more robust fix for the 'Unknown collation: utf8mb4_0900_ai_ci'
    # error when connecting to older MySQL servers from a newer client.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'collation': 'utf8mb4_general_ci'}
    }

    # Flask-Mail configuration
    # For production, it is highly recommended to set these as environment variables.
    MAIL_SERVER = 'smtp.hostinger.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = True  # Hostinger uses SSL on port 465

    # WARNING: Do NOT hardcode credentials. Set these as environment variables.
    # On Windows (cmd.exe): set MAIL_USERNAME=your-email@bataitech.com
    # On Linux/macOS: export MAIL_USERNAME="your-email@bataitech.com"
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Master encryption key for file encryption
    # WARNING: This key MUST be kept secret and ideally loaded from a secure environment variable
    #          or a Key Management Service (KMS) in production.
    # The default key provided is for development purposes only.
    # You can generate a new key by running: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    _MASTER_KEY_STR = os.environ.get('MASTER_ENCRYPTION_KEY') or 'zexP8T389Hh2hP3G-2y5d2V3fplk_yI3gTqfJc_U-wY='
    MASTER_ENCRYPTION_KEY = _MASTER_KEY_STR.encode('utf-8')

    # Razorpay configuration
    # WARNING: Do NOT hardcode credentials. Set these as environment variables.
    # You can get these from your Razorpay dashboard.
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
