import copy
import json
import unittest
import test_project_state as base


class InputAndRecoveryTests(unittest.TestCase):
    call = base.StateTests.call
    apply = base.StateTests.apply
    item = base.StateTests.item
    scheduled = base.StateTests.scheduled
    checkin = base.StateTests.checkin

    def test_non_string_operation_type_returns_structured_error(self):
        r = self.apply(type=[])
        self.assertFalse(r['ok']); self.assertEqual(r['error_code'], 'invalid_input')

    def test_non_list_evidence_is_rejected_before_transformation(self):
        s = base.project(); s['items'][-1]['evidence'] = 'not a list'
        r = self.apply(s, type='progress', item_id='a1', evidence=['https://example.org/draft'])
        self.assertFalse(r['ok']); self.assertEqual(r['snapshot'], s)

    def test_dropped_ancestor_excludes_action(self):
        s = base.project(); s['items'][1]['state'] = 'dropped'
        self.assertIsNone(self.call('next', s, budget=20)['action'])

    def test_equivalent_occurrence_offsets_do_not_create_another_reservation(self):
        first = self.checkin(phase='reserve')
        second = self.call('checkin', first['snapshot'], schedule_id='s1',
                           occurrence='2026-10-21T19:00:00+07:00', phase='reserve')
        self.assertFalse(second['should_notify'])
        self.assertEqual(len(second['snapshot']['occurrences']), 1)

    def test_offset_missing_from_occurrence_is_rejected(self):
        r = self.call('checkin', self.scheduled(), schedule_id='s1',
                      occurrence='2026-10-21T12:00:00', phase='reserve')
        self.assertFalse(r['ok'])

    def test_disabled_reminders_suppress_checkin_with_existing_binding(self):
        s = self.scheduled(); s['project']['reminder']['enabled'] = False
        self.assertFalse(self.checkin(s, phase='reserve')['should_notify'])

    def test_input_snapshot_is_preserved_on_rejected_revision(self):
        s = base.project(); before = copy.deepcopy(s)
        r = self.apply(s, type='revise_spec', accepted=True, changes={'goal': None})
        self.assertFalse(r['ok']); self.assertEqual(r['snapshot'], before)

    def test_saved_json_roundtrip_restores_state_without_chat_context(self):
        updated = self.apply(type='progress', item_id='a1', note='Two questions drafted')['snapshot']
        restored = json.loads(json.dumps(updated))
        r = self.call('review', restored)
        self.assertEqual(r['current_focus']['id'], 'm1')
        self.assertEqual(self.item(restored)['note'], 'Two questions drafted')
        self.assertEqual(self.call('next', restored, budget=15)['action']['id'], 'a1')

    def test_unknown_estimate_does_not_claim_to_fit_budget(self):
        s = base.project(); s['items'][-1]['minutes'] = None
        r = self.call('next', s, budget=15)
        self.assertIsNone(r['action']); self.assertTrue(r['needs_decomposition'])

    def test_completed_ancestor_excludes_leftover_action(self):
        s = base.project(); s['items'][0]['state'] = 'done'
        self.assertIsNone(self.call('next', s, budget=20)['action'])


if __name__ == '__main__':
    unittest.main()
