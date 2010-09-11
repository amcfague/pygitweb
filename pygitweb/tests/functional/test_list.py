from pygitweb.tests import *

class TestListController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='list', action='index'))
        # Test response...
