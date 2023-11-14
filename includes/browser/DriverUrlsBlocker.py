class DriverUrlsBlocker:
    @staticmethod
    def set(driver):
        driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": [
            "analytics.google.com",
            "www.google-analytics.com",
            "stats.g.doubleclick.net",
            "js-agent.newrelic.com",
            "analytics.tiktok.com",
            "adservice.google.com",
            "ad.doubleclick.net",
            "googletagmanager.com",
            "livechatinc.com",
            "gstatic.com",
            "facebook.net",  # recaptcha
            "google.com",  # recaptcha
            "assets.adobedtm.com",
            "mouseflow.com",
            "hubspot.com",
            # "*.js",
            "*.png",
            "*.svg",
            "*.gif",
            "*.jpg",
            "*.jpeg",
            "*.bmp",
            "*.webp",
            "*.woff2",
            "*.woff",
        ]})

        driver.execute_cdp_cmd('Network.enable', {})
