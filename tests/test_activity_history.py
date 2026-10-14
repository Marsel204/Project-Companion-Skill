import unittest
import test_project_state as base


class ActivityHistoryTests(unittest.TestCase):
    call = base.StateTests.call
    apply = base.StateTests.apply

    def test_completion_records_previous_and_new_state(self):
        r = self.apply(type='complete', item_id='a1')
        record = r['snapshot']['history'][-1]
        self.assertIn('before', record)
        self.assertEqual(record['before']['state'], 'ready')
        self.assertEqual(record['after']['state'], 'done')

    def test_scope_history_retains_original_goal(self):
        r = self.apply(type='revise_spec', accepted=True,
                       changes={'goal': 'Narrower topic'}, reason='Supervisor feedback')
        record = r['snapshot']['history'][-1]
        self.assertIn('before', record)
        self.assertEqual(record['before']['goal'], 'Choose a feasible question')
        self.assertEqual(record['after']['goal'], 'Narrower topic')


if __name__ == '__main__':
    unittest.main()
