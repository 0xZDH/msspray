from selenium.common.exceptions import (  # type: ignore
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import (  # type: ignore
    Firefox,
    FirefoxProfile,
    DesiredCapabilities,
)
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.common.proxy import (  # type: ignore
    Proxy,
    ProxyType,
)
from selenium.webdriver.firefox.options import Options  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.support.ui import (  # type: ignore
    WebDriverWait,
    Select,
)


# fmt: off
# Mapping of XPATH elements (Default: Microsoft Login)
# NOTE: This can be adjusted according to the target
ELEMENTS = {
    "type":      "XPATH",
    "username":  '//*[@id="i0116"]',
    "password":  '//*[@id="i0118"]',
    "next":      '//*[@id="idSIButton9"]',
    "login":     '//*[@id="idSIButton9"]',
    "usererror": '//*[@id="usernameError"]',
    "passerror": '//*[@id="passwordError"]',
    "locked":    '//*[@id="idTD_Error"]',
    "work":      '//*[@id="aadTile"]',
}
# fmt: on


class FirefoxEngine:
    """Selenium Firefox Engine"""

    options = Options()
    profile = FirefoxProfile()

    # Supposed to help with memory issues
    profile.set_preference("permissions.default.image", 2)

    profile.set_preference("dom.ipc.plugins.enabled.libflashplayer.so", False)
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    profile.accept_untrusted_certs = True

    def __init__(
        self,
        wait: int = 3,
        proxy: str = None,
        headless: bool = True,
    ):
        """Initialize the Firefox Engine

        :param wait: seconds to wait for a page to load
        :param proxy: http/s proxy
        :param headless: if the engine should run as headless
        """
        self.proxy = None if not proxy else self._build_proxy(proxy)
        self.options.headless = headless
        self.driver = Firefox(
            options=self.options,
            firefox_profile=self.profile,
            desired_capabilities=self.proxy,
        )
        # NOTE: Not sure if these help or not with optimization
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1024, 768)
        self.wait = WebDriverWait(self.driver, wait)

    def _build_proxy(self, proxy):
        proxy = Proxy(
            {
                "proxyType": ProxyType.MANUAL,
                "httpProxy": proxy,
                "ftpProxy": proxy,
                "sslProxy": proxy,
                "noProxy": "",
            }
        )
        capabilities = DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(capabilities)
        return capabilities

    def quit(self):
        self.driver.quit()

    def close(self):
        self.driver.close()

    def refresh(self):
        self.driver.refresh()

    def back(self):
        self.driver.execute_script("window.history.go(-1)")

    def clear_cookies(self):
        self.driver.delete_all_cookies()

    def get(self, url):
        self.driver.get(url)

    def find_element(self, type_, value):
        try:
            return self.wait.until(
                lambda driver: driver.find_element(getattr(By, type_), value)
            )
        except TimeoutException:
            return None

    def populate_element(self, element, value):
        element.send_keys(value)

    def is_clickable(self, type_, value):
        return self.wait.until(EC.element_to_be_clickable((getattr(By, type_), value)))

    def click(self, button):
        button.click()

    def select_dropdown(self, element, value):
        select = Select(element)
        select.select_by_value(value)

    def submit(self, form):
        form.submit()

    def execute_script(self, code):
        self.driver.execute_script(code)

    def screenshot(self, filename):
        self.driver.get_screenshot_as_file(filename)


def reset_browser(
    browser: FirefoxEngine,
    wait: int = 3,
    proxy: str = None,
) -> FirefoxEngine:
    """Reset the browser context for performance

    :param browser: current FirefoxEngine object
    :param wait: seconds to wait for a page to load
    :param proxy: http/s proxy
    :returns: new FirefoxEngine object
    """
    browser.close()
    return FirefoxEngine(wait=wait, proxy=proxy)
