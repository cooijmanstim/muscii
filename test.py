import unittest2

import music as mu

class TestTie(unittest2.TestCase):
    def test_tie(self):
        self.assertEqual(mu.tie(mu.Rest(duration=2), mu.Rest(duration=3)),
                         mu.Rest(duration=5))
        self.assertEqual(mu.tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=0, duration=3)),
                         mu.Note(pitch=0, duration=5))
        self.assertEqual(mu.tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=3)),
                         mu.Tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=3)))
        self.assertEqual(mu.tie(mu.Tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=3)),
                                   mu.Note(pitch=1, duration=2)),
                         mu.Tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=5)))
        self.assertEqual(mu.tie(mu.Note(pitch=1, duration=2),
                                   mu.Tie(mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=3))),
                         mu.Tie(mu.Note(pitch=1, duration=2), mu.Note(pitch=0, duration=2), mu.Note(pitch=1, duration=3)))
        with self.assertRaises(mu.InvalidTieError):
            mu.tie(mu.Rest(duration=1), mu.Note(pitch=0, duration=2))

if __name__ == "__main__":
    unittest2.main()
