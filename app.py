import logging
import traceback
from logging.handlers import RotatingFileHandler
from time import strftime

from flask import Flask, request, redirect, render_template, make_response

from utils import get_db_connection, list_data, random_token, url_check


app = Flask(__name__)
app.config.from_object('config')


shorty_host = "http://localhost:8080/"


@app.route('/analytics/<short_url>')
def analytics(short_url):
    info_fetch, counter_fetch, browser_fetch, platform_fetch = list_data(
        short_url)
    return render_template("data.html", host=shorty_host, info=info_fetch, counter=counter_fetch,
                           browser=browser_fetch, platform=platform_fetch)


@app.route('/', methods=['GET', 'POST'])
def index():
    with get_db_connection() as conn, conn.cursor() as cursor:
        # Fetch all data to display on index
        cursor.execute("SELECT * FROM WEB_URL;")
        result_all_fetch = cursor.fetchall()

        if request.method == 'POST':
            og_url = request.form.get('url_input')
            custom_suff = request.form.get('url_custom', '')
            tag_url = request.form.get('url_tag', '')

            token_string = random_token() if not custom_suff else custom_suff

            if og_url and url_check(og_url):
                cursor.execute(
                    "SELECT S_URL FROM WEB_URL WHERE S_URL = %s FOR UPDATE", (token_string,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO WEB_URL(URL, S_URL, TAG) VALUES(%s, %s, %s)", (og_url, token_string, tag_url))
                    conn.commit()
                    return render_template('index.html', shorty_url=f"{shorty_host}{token_string}")
                else:
                    error = "The custom suffix already exists. Please use another suffix or leave it blank for a random one."
            else:
                error = "Invalid URL provided. Please enter a valid URL."

            return render_template('index.html', table=result_all_fetch, host=shorty_host, error=error)

        return render_template('index.html', table=result_all_fetch, host=shorty_host)


@app.route('/<short_url>')
def reroute(short_url):
    with get_db_connection() as conn, conn.cursor() as cursor:
        platform = request.user_agent.platform or 'other'
        browser = request.user_agent.browser or 'other'
        browser_dict = {'firefox': 0, 'chrome': 0, 'safari': 0, 'other': 0}
        platform_dict = {'windows': 0, 'iphone': 0,
                         'android': 0, 'linux': 0, 'macos': 0, 'other': 0}

        # Increment browser and platform counters
        browser_dict[browser] = browser_dict.get(browser, 0) + 1
        platform_dict[platform] = platform_dict.get(platform, 0) + 1

        cursor.execute(
            "SELECT URL FROM WEB_URL WHERE S_URL = %s;", (short_url,))
        try:
            new_url = cursor.fetchone()[0]
            update_counters(cursor, short_url, browser_dict, platform_dict)
            conn.commit()
            return redirect(new_url)
        except Exception:
            return render_template('404.html'), 404


def update_counters(cursor, short_url, browser_dict, platform_dict):
    """Update browser and platform counters in the database for the given short_url."""
    counter_sql = """UPDATE WEB_URL SET COUNTER = COUNTER + 1,
                     CHROME = CHROME + %s, FIREFOX = FIREFOX + %s, SAFARI = SAFARI + %s, OTHER_BROWSER = OTHER_BROWSER + %s,
                     ANDROID = ANDROID + %s, IOS = IOS + %s, WINDOWS = WINDOWS + %s, LINUX = LINUX + %s, MAC = MAC + %s, OTHER_PLATFORM = OTHER_PLATFORM + %s
                     WHERE S_URL = %s;"""
    cursor.execute(counter_sql, (browser_dict['chrome'], browser_dict['firefox'], browser_dict['safari'], browser_dict['other'],
                                 platform_dict['android'], platform_dict['iphone'], platform_dict[
                                     'windows'], platform_dict['linux'], platform_dict['macos'], platform_dict['other'],
                                 short_url))


@app.route('/search', methods=['GET', 'POST'])
def search():
    s_tag = request.form.get('search_url', '')
    if not s_tag:
        return render_template('index.html', error="Please enter a search term.")

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM WEB_URL WHERE TAG = %s", (s_tag,))
        search_tag_fetch = cursor.fetchall()
        return render_template('search.html', host=shorty_host, search_tag=s_tag, table=search_tag_fetch)


@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr,
                 request.method, request.scheme, request.full_path, response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp,
                 request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return make_response(e, 405)


def setup_logger():
    """Configure and return a logger instance."""
    handler = RotatingFileHandler('shorty.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger('tdm')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger


logger = setup_logger()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
