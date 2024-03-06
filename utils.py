from urllib.parse import urlparse
import random
import string

import pymysql
import config


db_config = {
    "host": config.host,
    "user": config.user,
    "password": config.passwrd,
    "db": config.db
}


def get_db_connection():
    """Create and return a new database connection."""
    return pymysql.connect(**db_config)


def list_data(shorty_url):
    """
    Takes short_url for input.
    Returns counter , browser , platform ticks. 
    """
    with get_db_connection() as conn, conn.cursor() as cursor:

        su = [shorty_url]
        info_sql = "SELECT URL , S_URL ,TAG FROM WEB_URL WHERE S_URL= %s; "
        counter_sql = "SELECT COUNTER FROM WEB_URL WHERE S_URL= %s; "
        browser_sql = "SELECT CHROME , FIREFOX , SAFARI, OTHER_BROWSER FROM WEB_URL WHERE S_URL =%s;"
        platform_sql = "SELECT ANDROID , IOS , WINDOWS, LINUX , MAC , OTHER_PLATFORM FROM WEB_URL WHERE S_URL = %s;"

        cursor.execute(info_sql, su)
        info_fetch = cursor.fetchone()
        cursor.execute(counter_sql, su)
        counter_fetch = cursor.fetchone()
        cursor.execute(browser_sql, su)
        browser_fetch = cursor.fetchone()
        cursor.execute(platform_sql, su)
        platform_fetch = cursor.fetchone()

    return info_fetch, counter_fetch, browser_fetch, platform_fetch


def random_token(size=6):
    """
    Generates a random string of 6 chars , use size argument 
    to change the size of token.
    Returns a valid token of desired size , 
    *default is 6 chars
    """
    BASE_LIST = string.digits + string.letters

    token = ''.join((random.choice(BASE_LIST)) for char in range(size))
    return token


def url_check(url):
    """
    Expects a string as argument.
    Retruns True , if URL is valid else False.
    For detailed docs look into urlparse.
    """
    min_attr = ('scheme', 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True
        else:
            return False
    except:
        return False
