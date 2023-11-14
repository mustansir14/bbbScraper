from selenium.webdriver.chrome.options import Options


class DriverOptions:
    def create(self, proxy: str | None = None):
        options = Options()
        options.headless = False
        options.add_argument("window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument("--mute-audio")
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--single-process'); # one process to take less memory
        options.add_argument('--renderer-process-limit=1')  # do not allow take more resources
        options.add_argument('--disable-crash-reporter')  # disable crash reporter process
        options.add_argument('--no-zygote')  # disable zygote process
        options.add_argument('--disable-crashpad')
        options.add_argument('--grabber-bbb-mustansir')
        # options.add_argument("--auto-open-devtools-for-tabs")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")

        if proxy:
            options.add_argument("--proxy-server=%s" % "socks5://" + proxy)

        return options;
