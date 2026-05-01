import unittest

from todo_agent import Database


class DbTests(unittest.TestCase):
    def test_add_and_list(self):
        db = Database()
        db.add("first")
        db.add("second")
        self.assertEqual(len(db.list()), 2)

    def test_complete_then_filter(self):
        db = Database()
        t = db.add("todo")
        self.assertTrue(db.complete(t.id))
        self.assertEqual(len(db.list(include_done=False)), 0)
        self.assertEqual(len(db.list(include_done=True)), 1)

    def test_delete(self):
        db = Database()
        t = db.add("todo")
        self.assertTrue(db.delete(t.id))
        self.assertEqual(len(db.list()), 0)

    def test_missing_complete(self):
        self.assertFalse(Database().complete(999))


if __name__ == "__main__":
    unittest.main()
