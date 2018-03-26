import json
import os
import requests


def request_and_scrape(url,
                       filter_str,
                       host,
                       log_file='app.log',
                       host_uri='http://localhost:8000',
                       extract_by_str=True):
    """ Take in URL, grab the relevant log line,
        return dict for comparison """

    log_path = ""
    # In prod testing, will need to point to unique log path
    if os.path.exists("/etc/ansible/facts.d/active_gunicorn_svc.fact"):
        log_path = "-alpha"

    JSON_LOG_FILE = "/var/www/django{}/logs/{}".format(log_path, log_file)
    # Generate log event via http requests
    host.run("curl --user-agent testinfra {}".format(host_uri) + url)
    # Pick out the last log line from django logs
    # This is obviously only reliable test on a test instance with no
    # other incoming traffic.
    grab_log = host.check_output("grep {0} {1} | tail -n 1".format(
                                 filter_str,
                                 JSON_LOG_FILE
                                 ))

    # Process JSON
    if extract_by_str:
        raw_json = json.loads(grab_log)[filter_str]
        # The current json structure uses the time as the key
        # its a pretty dumb design.
        return raw_json[raw_json.keys()[0]]
    else:
        return json.loads(grab_log)

def test_json_log_exception(host):
    """
    Ensure json logging is working for exception
    """

    url = u"/page-doesnt-exist/"

    request = {
                u"data": {},
                u"meta": {
                    u"content_length": u'',
                    u"content_type": u'text/plain',
                    u"http_host": u"localhost:8000",
                    u"http_user_agent": u"testinfra",
                    u"path_info": url,
                    u"remote_addr": u"127.0.0.1",
                    u"remote_host": u"",
                    u"tz": u"UTC",
                },
                u"method": u"GET",
                u"path": url,
                u"scheme": u"http",
                u"user": u"AnonymousUser"
               }

    error_line = request_and_scrape(url, 'ERROR', host)
    assert 'exception' in error_line
    assert error_line['request'] == request


def test_json_log_200(host):
    """
    Ensure json logging is working for requests
    """

    should_return = {u"request":
                        {u"data": {},
                             u"meta": {
                                        u"content_length": u'',
                                        u"content_type": u'text/plain',
                                        u"http_host": u"localhost:8000",
                                        u"http_user_agent": u"testinfra",
                                        u"path_info": u"/",
                                        u"remote_addr": u"127.0.0.1",
                                        u"remote_host": u"",
                                        u"tz": u"UTC"},
                             u"method": u"GET",
                             u"path": u"/",
                             u"scheme": u"http",
                             u"user": u"AnonymousUser"},
                        u"response": {
                            u"charset": u"utf-8",
                            u"headers": {
                                u"Content-Type": u"text/html; charset=utf-8"
                                },
                            u"reason": u"OK",
                            u"status": 200}}

    assert request_and_scrape('/', 'INFO', host) == should_return


def test_django_security_logs(host):
    """
    Ensure other logging names are firing (outside of requests/exceptions)
    """

    should_return =  {
            u"levelname": u"ERROR",
            u"name": u"django.security.DisallowedHost",
            u"module": u"exception",
            u"message": u"Invalid HTTP_HOST header: '0.0.0.0:8000'. You may need to add '0.0.0.0' to ALLOWED_HOSTS.",
            u"request": "<WSGIRequest: GET '/'>",
            u"status_code": 400}

    response = request_and_scrape('/',
                                  'ALLOWED_HOSTS',
                                  host,
                                  'django-other.log',
                                  'http://0.0.0.0:8000',
                                  extract_by_str=False)

    # Remove time field which obviously will always change
    response.pop('asctime', None)
    assert response == should_return
