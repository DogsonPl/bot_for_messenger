from configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class LoginData:
    mail: str
    password: str


async def get_login_data() -> LoginData:
    mail = config_parser.get("login", "mail")
    password = config_parser.get("login", "password")
    if mail == "" or password == "":
        raise Exception("You have to set login data in a config file")
    else:
        return LoginData(mail, password)


@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database_name: str
    port: int


async def get_database_config() -> DatabaseConfig:
    host = config_parser.get("database", "host")
    user = config_parser.get("database", "user")
    password = config_parser.get("database", "password")
    database_name = config_parser.get("database", "database_name")
    port = config_parser.get("database", "port")
    if host == "" or user == "" or database_name == "" and port == "":
        raise Exception("You have to set database data in a config file")
    else:
        return DatabaseConfig(host, user, password, database_name, int(port))


@dataclass
class SmtpConfig:
    hostname: str
    mail: str
    password: str


async def get_smpt_config() -> SmtpConfig:
    hostname = config_parser.get("smpt", "hostname")
    mail = config_parser.get("smpt", "mail")
    password = config_parser.get("smpt", "password")
    if hostname == "" or mail == "" or password == "":
        raise Exception("You have to set SMPT data in a config file")
    else:
        return SmtpConfig(hostname, mail, password)


config_parser = ConfigParser()
config_parser.read("config.cfg", "UTF-8")

django_password = config_parser.get("django_password", "django_password")
if django_password == "":
    raise Exception("You have to configure your django_password in a config file")


weather_api_key = config_parser.get("weather", "key")
if weather_api_key == "":
    raise Exception("You have to configure your weather api key on https://openweathermap.org/api")
