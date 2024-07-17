import pickle
import unittest
from app.jobs.subscribe import SubscribeJob
from app import models


class UserDaoTestCase(unittest.TestCase):

    def test_write(self):
        user1 = models.User(
            id=1,
            username='admin',
            password='123',
            admin=True,
            disabled=False,
        )
        user2 = models.User(
            id=2,
            username='admin2',
            password='1232',
            admin=True,
            disabled=False,
        )
        file_path = '/Users/yellowstrong/Downloads/__rss_cache__'
        with open(file_path, 'wb') as f:
            pickle.dump([user1, user2], f)

    def test_load_rss(self):
        file_path = '/Users/yellowstrong/Downloads/__rss_cache__'
        with open(file_path, 'rb') as f:
            catch = pickle.load(f)
            return catch

    def test_refresh(self):
        SubscribeJob().refresh()


if __name__ == "__main__":
    unittest.main()
