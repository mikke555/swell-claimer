import curl_cffi


class HttpClient(curl_cffi.Session):
    def __init__(self, proxy: str = "", base_url: str = ""):
        super().__init__(impersonate="chrome131")
        self.base_url = base_url

        if proxy:
            self.proxies = {"https": proxy}

    def _request(self, method, endpoint, *args, **kwargs):
        if endpoint.startswith(("http://", "https://")):
            url = endpoint
        else:
            url = f"{self.base_url}{endpoint}"

        return self.request(method, url, *args, **kwargs)

    def get(self, endpoint, *args, **kwargs):
        return self._request("GET", endpoint, *args, **kwargs)

    def post(self, endpoint, *args, **kwargs):
        return self._request("POST", endpoint, *args, **kwargs)
