from urllib.request import Request, urlopen
from time import strftime

from services import API_KEYS, HTTP_TOO_MANY_REQUESTS, HTTP_BAD_REQUEST


class Service:

    def __init__(self, use_production=False, logging=True):
        self.env = "production" if use_production else "sandbox"
        self.log = logging

    def log_message(self, message, level="INFO"):
        if self.log:
            print("{}\t|\t{}\t|{}".format(strftime('%Y-%m-%d %H:%M:%S'), level, message))

    def log_warning(self, message):
        linebreak = "-"*len(message)+"\n"
        self.log_message("{0}{1}\n{0}".format(linebreak, message), level="WARN")

    def get_api_key(self, platform="alma", api="bibs"):
        return API_KEYS[platform][api][self.env]

    def make_request(self, apiPath, queryParams=None, method=lambda: 'GET', requestBody=None, headers=None):

        # build URL we'll be requesting to (note: we expect the apiPath to start with '/')
        api_key = self.get_api_key()
        url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1{api_path}?apiKey={api_key}'.format(
            api_path=apiPath, api_key=api_key
        )
        if queryParams:
            for key, value in queryParams.items():
                url += '&{}={}'.format(key, value)

        # build request
        data = requestBody if requestBody else {}
        headers = headers if headers else {}
        request = Request(url, data=data, headers=headers)
        request.get_method = method

        # send and store request
        self.log_message("making an alma request to '" + request.full_url + "'")
        response = urlopen(request)
        response_body = response.read().decode(response.headers.get_content_charset())

        if response.status == HTTP_TOO_MANY_REQUESTS:
            self.log_warning("WARNING! Received a 'Too Many Requests' response from alma! Please WAIT before retrying")
            exit(1)
        elif response.status == HTTP_BAD_REQUEST:
            self.log_warning("WARNING! Bad Request")
            self.log_message(request)
        else:
            self.log_message("response code: " + str(response.status))

        return response_body
