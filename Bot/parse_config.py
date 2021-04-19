from configparser import ConfigParser


async def get_login_data():
    mail = config_parser.get("login", "mail")
    password = config_parser.get("login", "password")
    try:
        assert mail != "" and password != ""
    except AssertionError:
        raise Exception("You have to set login data in a config file")
    return mail, password


async def get_database_config():
    host = config_parser.get("database", "host")
    user = config_parser.get("database", "user")
    password = config_parser.get("database", "password")
    database_name = config_parser.get("database", "database_name")
    port = config_parser.get("database", "port")
    try:
        assert host != "" and user != "" and database_name != "" and port != ""
    except AssertionError:
        raise Exception("You have to set database data in a config file")
    return host, user, password, database_name, port


async def get_smpt_config():
    hostname = config_parser.get("smpt", "hostname")
    mail = config_parser.get("smpt", "mail")
    password = config_parser.get("smpt", "password")
    try:
        assert hostname != "" and mail != "" and password != ""
    except AssertionError:
        raise Exception("You have to set SMPT data in a config file")
    return hostname, mail, password


config_parser = ConfigParser()
config_parser.read("config.cfg", "UTF-8")
