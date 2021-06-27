from configparser import ConfigParser


async def get_login_data():
    mail = config_parser.get("login", "mail")
    password = config_parser.get("login", "password")
    if mail == "" or password == "":
        raise Exception("You have to set login data in a config file")
    else:
        return mail, password


async def get_database_config():
    host = config_parser.get("database", "host")
    user = config_parser.get("database", "user")
    password = config_parser.get("database", "password")
    database_name = config_parser.get("database", "database_name")
    port = config_parser.get("database", "port")
    if host == "" or user == "" or database_name == "" and port == "":
        raise Exception("You have to set database data in a config file")
    else:
        return host, user, password, database_name, port


async def get_smpt_config():
    hostname = config_parser.get("smpt", "hostname")
    mail = config_parser.get("smpt", "mail")
    password = config_parser.get("smpt", "password")
    if hostname == "" or mail == "" or password == "":
        raise Exception("You have to set SMPT data in a config file")
    else:
        return hostname, mail, password


config_parser = ConfigParser()
config_parser.read("config.cfg", "UTF-8")

django_password = config_parser.get("django_password", "django_password")
if django_password == "":
    raise Exception("You have to configure your django_password in a config file")
