class InjectedBrowserExtension(object):
    """ Offers methods to inject an extended browser into the Splinter browser
    class hierarchy. All methods not related to spawning/cloning a new browser
    instance are provided by :class:`ExtendedBrowser`.

    """

    @classmethod
    def spawn(cls, browser_factory, *args, **kwargs):
        """ Takes a Splinter browser factory together with the arguments
        meant for the factory and returns a new browser with the current class
        injected into the class hierarchy.

        """

        browser = browser_factory(*args, **kwargs)

        class LeechedExtendedBrowser(cls, browser.__class__):
            pass

        browser.spawn_parameters = browser_factory, args, kwargs
        browser.__class__ = LeechedExtendedBrowser
        return browser

    def clone(self):
        """ Returns an independent instance of the current browser (all state
        is reset on the new instance).

        """

        browser_factory, args, kwargs = self.spawn_parameters
        browser = self.__class__.spawn(browser_factory, *args, **kwargs)

        for key, value in self.clone_parameters.items():
            setattr(browser, key, value)

        return browser

    @property
    def clone_parameters(self):
        """ Returns a dictionary of values that need to be applied to the new
        browser instance after it is cloned.

        """
        return {}


class ExtendedBrowser(InjectedBrowserExtension):
    """ Extends Splinter's browser with OneGov specific methods.

    """

    # Prefix appended to urls without http prefix.
    baseurl = None

    @property
    def clone_parameters(self):
        return {
            'baseurl': self.baseurl
        }

    def visit(self, url):
        """ Overrides the default visit method to provied baseurl support. """
        if self.baseurl and not url.startswith('http'):
            url = self.baseurl.rstrip('/') + url

        return super().visit(url)

    def login(self, username, password, to=None):
        """ Login a user through the usualy /auth/login path. """

        url = '/auth/login' + (to and ('/?to=' + to) or '')

        self.visit(url)
        self.fill('username', username)
        self.fill('password', password)
        self.find_by_css('form input[type="submit"]').first.click()

    def login_admin(self, to=None):
        self.login('admin@example.org', 'hunter2', to)

    def login_editor(self, to=None):
        self.login('editor@example.org', 'hunter2', to)

    def logout(self):
        self.get('/auth/logout')
