import logging
import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv


class ConfigBase(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.logger = logging.getLogger(f"{cls.__module__}.{cls.__qualname__}")
        cls.logger.info(f"{cls.__qualname__} subclass initialized.")

    def __init__(self):
        load_dotenv()
        self.logger.debug(f"{self.__class__.__qualname__} Config instance created")

    @property
    @abstractmethod
    def SQLALCHEMY_DATABASE_URI(self) -> str: ...

    @property
    @abstractmethod
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool: ...

    @property
    @abstractmethod
    def SECRET_KEY(self) -> str: ...


class AppTestingConfig(ConfigBase):
    def __init__(self, testing: bool = True):
        if not testing:
            raise ValueError("AppTestingConfig must be initialized with testing=True")
        super().__init__()
        self.logger.debug("AppTestingConfig initialized.")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

        if not TEST_DATABASE_URL:
            self.logger.error("TEST_DATABASE_URL environment variable not set.")
            raise ValueError("TEST_DATABASE_URL environment variable not set.")

        if "test" not in TEST_DATABASE_URL:
            self.logger.error(
                "TEST_DATABASE_URL does not appear to be a test database."
            )
            raise ValueError("TEST_DATABASE_URL does not appear to be a test database.")

        self.logger.debug("Using Test DATABASE_URL")
        return TEST_DATABASE_URL

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        return False

    @property
    def SECRET_KEY(self) -> str:
        SECRET_KEY = os.getenv("TEST_SECRET_KEY")
        if not SECRET_KEY:
            self.logger.error("TEST_SECRET_KEY environment variable not set.")
            raise ValueError("TEST_SECRET_KEY environment variable not set.")
        return SECRET_KEY


class ProductionConfig(ConfigBase):
    def __init__(self, testing: bool = True):
        if testing:
            self.logger.error(
                "ProductionConfig cannot be initialized with testing=True"
            )
            raise ValueError("ProductionConfig must be initialized with testing=False")

        super().__init__()
        self.logger.debug("ProductionConfig initialized.")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        DATABASE_URL = os.getenv("DATABASE_URL")

        if not DATABASE_URL:
            self.logger.error("DATABASE_URL environment variable not set.")
            raise ValueError("DATABASE_URL environment variable not set.")

        if "test" in DATABASE_URL.lower():
            self.logger.error(
                "test cannot appear in database URL for production database."
            )
            raise ValueError(
                "test cannot appear in database URL for production database."
            )

        self.logger.debug("Using Production DATABASE_URL")
        return DATABASE_URL

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        return False

    @property
    def SECRET_KEY(self) -> str:
        SECRET_KEY = os.getenv("SECRET_KEY")
        if not SECRET_KEY:
            self.logger.error("SECRET_KEY environment variable not set.")
            raise ValueError("SECRET_KEY environment variable not set.")
        return SECRET_KEY
