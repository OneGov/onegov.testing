from onegov.testing.capturelog import CaptureLogPlugin
from pytest_splinter.plugin import Browser
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def pytest_configure(config):
    """Activate log capturing if appropriate."""

    config.pluginmanager.register(CaptureLogPlugin(config), '_capturelog')


def pytest_cmdline_main(config):
    if config.option.splinter_webdriver in (None, 'chrome'):
        # automatically setup chrome if requested
        config.option.splinter_webdriver = 'chrome'
        config.option.splinter_webdriver_executable\
            = ChromeDriverManager().install()

        # currently leads to an exception if used
        config.option.splinter_window_size = None

        # doesn't yet produce anything in headless mode
        config.option.splinter_make_screenshot_on_failure = False


def DefaultBrowser(*args, **kwargs):

    # force chrome into headless mode
    if args and args[0] == 'chrome':
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        kwargs['options'] = options

    return Browser(*args, **kwargs)


def pytest_fixture_setup(fixturedef, request):

    # override the default pytest-splinter browser class
    if fixturedef.argname == 'splinter_browser_class':
        if fixturedef.func.__module__ == 'pytest_splinter.plugin':
            fixturedef.func = lambda *args, **kwargs: DefaultBrowser
