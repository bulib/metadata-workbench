from os.path import join, abspath, dirname, basename
from time import strftime
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from src.services.secrets import API_KEYS
except (ImportError, NameError):
    pass

CONTENT_TYPE_XML = {'Content-Type': 'application/xml'}
OUTPUT_DIRECTORY = abspath(join(dirname(__file__), "../../output"))

# helpful reused variables
HTTP_TOO_MANY_REQUESTS = 429
HTTP_BAD_REQUEST = 400


def construct_log_message(prefix, message, level="INFO"):
    """prepare a formatted log message with timestamp, originating method, and log level"""
    try:
        module = basename(prefix)
    except:
        module = prefix
    message = "{timestamp} | {module_name} [{level}] | {message}".format(
        timestamp=strftime('%Y-%m-%d %H:%M:%S'),
        module_name=module,
        level=level,
        message=message
    )
    if "warn" in level.lower() or "ERROR" in level.lower():
        message_length = len(message) if "\n" not in message else len(message.split("\n")[0])
        linebreak = "-" * message_length
        message = "{0}\n{1}\n{0}".format(linebreak, message)

    return message


class Service:

    def __init__(self, use_production=False, logging=True):
        self.env = "production" if use_production else "sandbox"
        self.log = logging
        self.api_key = ""
        self.base_url = ""

    def log_message(self, message, level="INFO"):
        if self.log:
            message_prefix = self.__class__.__name__
            print(construct_log_message(message_prefix, message, level=level))

    def log_warning(self, message):
        self.log_message(message, level="WARN")

    def make_request(self, apiPath="", queryParams=None, method='GET', requestBody=None, headers=None, return_whole_response=False):

        # build URL we'll be requesting to (note: we expect the apiPath to start with '/')
        url = '{base_url}{api_path}'.format(base_url=self.base_url, api_path=apiPath)
        if self.api_key:
            url += "?apikey={key}&".format(key=self.api_key)
        if queryParams:
            for key, value in queryParams.items():
                url += '{}={}&'.format(key, value)

        # build request
        data = requestBody if requestBody is not None else {}
        headers = headers if headers else {}
        request = Request(url, data=data, headers=headers)
        request.get_method = lambda: method

        # send and store request
        url_no_args = request.full_url.split("?")[0] or request.full_url
        self.log_message("making a '{}' request to '{}'.".format(method, url))
        try:
            response = urlopen(request)
            if return_whole_response:
                return response

            response_body = response.read().decode(response.headers.get_content_charset())

            if response.status == HTTP_TOO_MANY_REQUESTS:
                self.log_warning("WARNING! Received a 'Too Many Requests' response! Please WAIT before retrying")
                exit(1)
            elif response.status == HTTP_BAD_REQUEST:
                self.log_warning("WARNING! Bad Request")
                self.log_message(request)
            else:
                self.log_message("-> response code: " + str(response.status))

            return response if return_whole_response else response_body
        except HTTPError as httpError:
            self.log_warning("HTTPError received after making request: '{url}'!\n\tError {code} : {msg}".format(
                url=request.full_url, code=httpError.code, msg=httpError.msg)
            )
            # return httpError


def make_basic_request(url, debug=True):
    svc = Service(logging=debug)
    return svc.make_request(url)


def get_api_key(platform="alma", api="bibs", env="sandbox", notify_empty=True):
    try:
        return API_KEYS[platform][api][env]
    except NameError:
        if notify_empty:
            print(construct_log_message("services/__init__.py", "unable to acquire API", "WARN"))
        return ""
