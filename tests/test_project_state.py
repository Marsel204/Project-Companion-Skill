import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/project-companion/scripts/project_state.py'


def project():
    return {
        'schema_version': 1,
        'project': {
            'id': 'p1', 'title': 'Thesis proposal', 'state': 'active', 'focus': 'm1',
            'spec': {'goal': 'Choose a feasible question',
                     'success_criteria': ['A scoped question'],
                     'hard_deadline': '2026-11-25', 'unknowns': ['Available data']},
            'reminder': {'enabled': False, 'mode': 'review', 'timezone': 'Asia/Jakarta',
                         'schedule_id': None, 'cancellation_pending': False},
        },
        'items': [
            {'id': 'm1', 'project_id': 'p1', 'parent': None, 'level': 'milestone',
             'title': 'Research direction', 'state': 'in progress',
             'criteria': ['Feasible question accepted'], 'met_criteria': [], 'dependencies': []},
            {'id': 't1', 'project_id': 'p1', 'parent': 'm1', 'level': 'task',
             'title': 'Candidate questions', 'state': 'in progress',
             'criteria': ['Three questions'], 'met_criteria': [], 'dependencies': []},
            {'id': 'a1', 'project_id': 'p1', 'parent': 't1', 'level': 'action',
             'title': 'Write candidate questions', 'state': 'ready',
             'criteria': ['Three questions written'], 'met_criteria': [],
             'minutes': 10, 'dependencies': []},
        ],
        'history': [], 'occurrences': [],
    }


class StateTests(unittest.TestCase):
    def call(self, command, snapshot=None, **options):
        self.assertTrue(SCRIPT.is_file(),
                        'Required project-state behavior is not implemented: helper absent')
        request = {'snapshot': project() if snapshot is None else snapshot, **options}
        result = subprocess.run([sys.executable, str(SCRIPT), command],
                                input=json.dumps(request), text=True, capture_output=True)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f'Helper did not return JSON: {result.stdout!r}; {result.stderr}')
        self.assertEqual(result.returncode, 0 if value['ok'] else 2)
        return value

    def apply(self, snapshot=None, **operation):
        return self.call('apply', snapshot, operation={'id': 'op1', **operation})

    def item(self, snapshot, identity='a1'):
        return next(i for i in snapshot['items'] if i['id'] == identity)

    def scheduled(self, state='active', mode='review'):
        s = project()
        s['project']['state'] = state
        s['project']['reminder'].update(enabled=True, schedule_id='s1', mode=mode)
        return s

    def checkin(self, snapshot=None, **options):
        return self.call('checkin', self.scheduled() if snapshot is None else snapshot,
                         schedule_id='s1', occurrence='2026-10-21T12:00:00Z',
                         **options)

    def test_valid_project(self):
        self.assertTrue(self.call('validate')['ok'])

    def test_reject_duplicate_identity(self):
        s = project(); s['items'].append(copy.deepcopy(s['items'][-1]))
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_cross_project_link(self):
        s = project(); s['items'][-1]['project_id'] = 'p2'
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_parent_cycle(self):
        s = project(); s['items'][0]['parent'] = 'a1'
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_dependency_cycle(self):
        s = project(); s['items'][1]['dependencies'] = ['a1']
        s['items'][-1]['dependencies'] = ['t1']
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_unknown_dependency(self):
        s = project(); s['items'][-1]['dependencies'] = ['missing']
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_wrong_hierarchy(self):
        s = project(); s['items'][-1]['parent'] = 'm1'
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_bad_timezone(self):
        s = project(); s['project']['reminder']['timezone'] = 'Mars/Olympus'
        self.assertFalse(self.call('validate', s)['ok'])

    def test_reject_invalid_state(self):
        s = project(); s['items'][-1]['state'] = 'finished-ish'
        self.assertFalse(self.call('validate', s)['ok'])

    def test_next_action_fits_budget(self):
        r = self.call('next', budget=10)
        self.assertEqual(r['action']['id'], 'a1')

    def test_too_large_action_requests_decomposition(self):
        r = self.call('next', budget=5)
        self.assertIsNone(r['action']); self.assertTrue(r['needs_decomposition'])

    def test_unsatisfied_dependency_not_recommended(self):
        s = project(); s['items'][-1]['dependencies'] = ['t1']
        self.assertIsNone(self.call('next', s, budget=20)['action'])

    def test_ancestor_blocker_not_recommended(self):
        s = project(); s['items'][1]['state'] = 'blocked'
        self.assertIsNone(self.call('next', s, budget=20)['action'])

    def test_ancestor_dependency_not_ignored(self):
        s = project()
        s['items'].append({'id': 'm2', 'project_id': 'p1', 'parent': None,
                           'level': 'milestone', 'title': 'Data', 'state': 'planned',
                           'criteria': ['Data exists'], 'dependencies': []})
        s['items'][1]['dependencies'] = ['m2']
        self.assertIsNone(self.call('next', s, budget=20)['action'])

    def test_paused_project_has_no_recommendation(self):
        s = project(); s['project']['state'] = 'paused'
        self.assertIsNone(self.call('next', s, budget=20)['action'])

    def test_partial_progress_does_not_complete_parent(self):
        r = self.apply(type='progress', item_id='a1', note='Two of three questions')
        self.assertEqual(self.item(r['snapshot'])['state'], 'in progress')
        self.assertEqual(self.item(r['snapshot'], 'm1')['state'], 'in progress')
        self.assertEqual(self.item(r['snapshot'])['note'], 'Two of three questions')

    def test_clear_done_completes_only_action(self):
        r = self.apply(type='complete', item_id='a1')
        self.assertTrue(r['ok'])
        self.assertEqual(self.item(r['snapshot'])['state'], 'done')
        self.assertNotEqual(self.item(r['snapshot'], 'm1')['state'], 'done')

    def test_ambiguous_done_requires_question(self):
        s = project(); a = copy.deepcopy(s['items'][-1]); a['id'] = 'a2'; s['items'].append(a)
        r = self.apply(s, type='complete')
        self.assertFalse(r['ok']); self.assertEqual(r['error_code'], 'ambiguous_action')
        self.assertEqual(r['snapshot'], s)

    def test_duplicate_operation_is_idempotent(self):
        op = {'type': 'complete', 'item_id': 'a1'}
        first = self.apply(**op)
        second = self.apply(first['snapshot'], **op)
        self.assertTrue(second['duplicate'])
        self.assertEqual(first['snapshot'], second['snapshot'])
        self.assertEqual(len(second['snapshot']['history']), 1)

    def test_reused_operation_id_with_new_payload_rejected(self):
        first = self.apply(type='complete', item_id='a1')
        second = self.apply(first['snapshot'], type='reopen', item_id='a1')
        self.assertFalse(second['ok']); self.assertEqual(second['error_code'], 'operation_conflict')

    def test_parent_requires_outcome_criteria(self):
        r = self.apply(type='complete', item_id='m1')
        self.assertFalse(r['ok']); self.assertEqual(r['error_code'], 'criteria_unmet')

    def test_parent_can_complete_when_criteria_explicitly_met(self):
        r = self.apply(type='complete', item_id='m1',
                       met_criteria=['Feasible question accepted'])
        self.assertTrue(r['ok']); self.assertEqual(self.item(r['snapshot'], 'm1')['state'], 'done')

    def test_block_records_reason(self):
        r = self.apply(type='block', item_id='a1', note='Need data access')
        self.assertEqual(self.item(r['snapshot'])['state'], 'blocked')
        self.assertEqual(self.item(r['snapshot'])['note'], 'Need data access')

    def test_reopen_preserves_prior_report(self):
        r = self.apply(type='complete', item_id='a1', note='Three questions drafted')
        r = self.apply(r['snapshot'], id='op2', type='reopen', item_id='a1')
        self.assertEqual(self.item(r['snapshot'])['state'], 'ready')
        self.assertEqual(self.item(r['snapshot'])['note'], 'Three questions drafted')
        self.assertEqual(len(r['snapshot']['history']), 2)

    def test_scope_revision_requires_acceptance(self):
        s = project()
        r = self.apply(s, type='revise_spec', changes={'goal': 'Different thesis'})
        self.assertFalse(r['ok']); self.assertEqual(r['snapshot'], s)

    def test_accepted_revision_preserves_deadline_and_artifacts(self):
        s = project(); s['items'][-1]['evidence'] = ['https://example.org/draft']
        r = self.apply(s, type='revise_spec', accepted=True, reason='Supervisor feedback',
                       changes={'goal': 'Narrow question'})
        self.assertEqual(r['snapshot']['project']['spec']['hard_deadline'], '2026-11-25')
        self.assertEqual(self.item(r['snapshot'])['evidence'], ['https://example.org/draft'])
        self.assertEqual(r['snapshot']['project']['spec']['goal'], 'Narrow question')

    def test_same_field_conflict_rejected(self):
        s = project(); s['items'][-1]['state'] = 'blocked'
        r = self.apply(s, type='complete', item_id='a1', expected={'state': 'ready'})
        self.assertFalse(r['ok']); self.assertEqual(r['error_code'], 'field_conflict')
        self.assertEqual(r['snapshot'], s)

    def test_unrelated_edit_preserved(self):
        s = project(); s['items'][-1]['note'] = 'Manual Notion note'
        r = self.apply(s, type='complete', item_id='a1', expected={'state': 'ready'})
        self.assertTrue(r['ok']); self.assertEqual(self.item(r['snapshot'])['note'], 'Manual Notion note')

    def test_review_has_no_arbitrary_percentage(self):
        r = self.call('review')
        self.assertEqual(r['current_focus']['id'], 'm1')
        self.assertEqual(r['completed_outcomes'], [])
        self.assertNotIn('percentage', r); self.assertNotIn('percent', r)
        self.assertIn('Feasible question accepted', r['current_focus']['unmet_criteria'])

    def test_pause_retains_schedule_identity_and_marks_cancel_pending(self):
        r = self.apply(self.scheduled(), type='set_project_state', state='paused')
        reminder = r['snapshot']['project']['reminder']
        self.assertFalse(reminder['enabled']); self.assertEqual(reminder['schedule_id'], 's1')
        self.assertTrue(reminder['cancellation_pending'])

    def test_project_completion_requires_confirmed_success(self):
        r = self.apply(type='set_project_state', state='complete', confirmed=True)
        self.assertFalse(r['ok']); self.assertEqual(r['error_code'], 'criteria_unmet')

    def test_confirmed_project_completion_requests_schedule_shutdown(self):
        r = self.apply(self.scheduled(), type='set_project_state', state='complete',
                       confirmed=True, met_success_criteria=['A scoped question'])
        self.assertTrue(r['ok']); self.assertFalse(r['snapshot']['project']['reminder']['enabled'])
        self.assertTrue(r['snapshot']['project']['reminder']['cancellation_pending'])

    def test_checkin_reserves_one_occurrence_without_completing_work(self):
        r = self.checkin(phase='reserve')
        self.assertTrue(r['should_notify'])
        self.assertEqual(self.item(r['snapshot'])['state'], 'ready')
        self.assertEqual(r['snapshot']['occurrences'][0]['state'], 'reserved')

    def test_uncertain_delivery_requires_reconciliation_on_retry(self):
        first = self.checkin(phase='reserve')
        retry = self.checkin(first['snapshot'], phase='reserve')
        self.assertFalse(retry['should_notify']); self.assertTrue(retry['needs_reconciliation'])

    def test_acknowledged_delivery_not_repeated(self):
        r = self.checkin(phase='reserve')
        r = self.checkin(r['snapshot'], phase='delivered')
        r = self.checkin(r['snapshot'], phase='reserve')
        self.assertFalse(r['should_notify']); self.assertFalse(r['needs_reconciliation'])
        self.assertEqual(len(r['snapshot']['occurrences']), 1)

    def test_monitoring_quiet_without_meaningful_change(self):
        r = self.checkin(self.scheduled(mode='monitor'), phase='reserve', meaningful=False)
        self.assertFalse(r['should_notify']); self.assertEqual(r['snapshot']['occurrences'], [])

    def test_review_can_notify_without_a_change(self):
        self.assertTrue(self.checkin(phase='reserve', meaningful=False)['should_notify'])

    def test_paused_project_suppresses_checkin(self):
        r = self.checkin(self.scheduled(state='paused'), phase='reserve')
        self.assertFalse(r['should_notify'])

    def test_schedule_identity_mismatch_rejected(self):
        s = self.scheduled(); s['project']['reminder']['schedule_id'] = 'other'
        r = self.checkin(s, phase='reserve')
        self.assertFalse(r['ok'])

    def test_delivery_cannot_be_acknowledged_before_reservation(self):
        self.assertFalse(self.checkin(phase='delivered')['ok'])

    def test_dropped_item_excluded_but_not_deleted(self):
        r = self.apply(type='drop', item_id='a1', note='Changed scope')
        self.assertEqual(self.item(r['snapshot'])['state'], 'dropped')
        self.assertIsNone(self.call('next', r['snapshot'], budget=20)['action'])

    def test_invalid_budget_does_not_select_work(self):
        self.assertFalse(self.call('next', budget=-1)['ok'])

    def test_malformed_input_is_a_structured_error(self):
        r = self.call('validate', {'schema_version': 1, 'project': None})
        self.assertFalse(r['ok'])


if __name__ == '__main__':
    unittest.main()
