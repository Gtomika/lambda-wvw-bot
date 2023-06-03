import pendulum
import unittest

from bot.commons import matchup_utils


class MatchupUtilsTest(unittest.TestCase):

    def test_detect_relink_date(self):
        # re-link is the last friday of any odd month
        example_relink_date = pendulum.datetime(year=2023, month=5, day=26)
        self.assertEqual(pendulum.FRIDAY, example_relink_date.day_of_week)
        self.assertTrue(matchup_utils.is_relink(example_relink_date))

    def test_detect_not_relink_date(self):
        # not relink because even month (but last friday)
        example_reset_but_not_relink_date_1 = pendulum.datetime(year=2023, month=4, day=28)
        self.assertEqual(pendulum.FRIDAY, example_reset_but_not_relink_date_1.day_of_week)
        self.assertFalse(matchup_utils.is_relink(example_reset_but_not_relink_date_1))

        # not relink because not friday
        example_reset_but_not_relink_date_2 = pendulum.datetime(year=2023, month=4, day=27)
        self.assertNotEqual(pendulum.FRIDAY, example_reset_but_not_relink_date_2.day_of_week)
        self.assertFalse(matchup_utils.is_relink(example_reset_but_not_relink_date_2))

        # not relink because odd month, friday, but not the last one
        example_reset_but_not_relink_date_3 = pendulum.datetime(year=2023, month=5, day=19)
        self.assertEqual(pendulum.FRIDAY, example_reset_but_not_relink_date_3.day_of_week)
        self.assertFalse(matchup_utils.is_relink(example_reset_but_not_relink_date_3))
