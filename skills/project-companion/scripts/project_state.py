#!/usr/bin/env python3
"""Validate and transform project snapshots. No network, storage, or notifications.

JSON request on stdin; JSON result on stdout. Exit 0 for success, 2 for a
validation/conflict error. Updated snapshots are proposals until saved externally.
"""
import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ITEM_STATES = {'planned', 'ready', 'in progress', 'blocked', 'done', 'dropped'}
PROJECT_STATES = {'draft', 'active', 'paused', 'complete', 'abandoned'}
LEVELS = {'milestone': None, 'task': 'milestone', 'action': 'task'}


class Invalid(ValueError):
    def __init__(self, message, code='invalid_input'):
        super().__init__(message)
        self.code = code


def require(condition, message, code='invalid_input'):
    if not condition:
        raise Invalid(message, code)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(nonempty(v) for v in value)


def validate(snapshot):
    require(isinstance(snapshot, dict), 'Snapshot must be an object.')
    require(type(snapshot.get('schema_version')) is int and snapshot['schema_version'] == 1,
            'Supported schema_version is 1.')
    project = snapshot.get('project')
    require(isinstance(project, dict), 'Project must be an object.')
    require(nonempty(project.get('id')) and nonempty(project.get('title')),
            'Project requires identity and title.')
    require(isinstance(project.get('state'), str) and project['state'] in PROJECT_STATES,
            'Unknown project state.')
    spec = project.get('spec')
    require(isinstance(spec, dict) and nonempty(spec.get('goal')), 'Spec requires a goal.')
    require(strings(spec.get('success_criteria')) and bool(spec['success_criteria']),
            'Spec requires success criteria.')
    reminder = project.get('reminder')
    require(isinstance(reminder, dict) and type(reminder.get('enabled')) is bool,
            'Reminder requires an enabled boolean.')
    require(reminder.get('mode') in ('review', 'monitor'), 'Unknown reminder mode.')
    timezone = reminder.get('timezone')
    if timezone is not None:
        require(nonempty(timezone), 'Timezone must be an IANA name.')
        try:
            ZoneInfo(timezone)
        except (ValueError, ZoneInfoNotFoundError):
            raise Invalid('Timezone is not an available IANA timezone.') from None
    if reminder['enabled']:
        require(timezone is not None and nonempty(reminder.get('schedule_id')),
                'Enabled reminders require timezone and confirmed schedule identity.')
    require(reminder.get('schedule_id') is None or nonempty(reminder['schedule_id']),
            'Schedule identity must be a string or null.')
    items = snapshot.get('items')
    require(isinstance(items, list), 'Items must be a list.')
    by_id = {}
    for item in items:
        require(isinstance(item, dict) and nonempty(item.get('id')), 'Item requires an identity.')
        require(item['id'] not in by_id, 'Duplicate item identity.')
        by_id[item['id']] = item
        require(item.get('project_id') == project['id'], 'Item belongs to another project.')
        require(nonempty(item.get('title')), 'Item requires a title.')
        require(isinstance(item.get('level'), str) and item['level'] in LEVELS, 'Unknown item level.')
        require(isinstance(item.get('state'), str) and item['state'] in ITEM_STATES, 'Unknown item state.')
        require(strings(item.get('criteria')) and bool(item['criteria']), 'Item requires criteria.')
        require(strings(item.get('met_criteria', [])), 'Met criteria must be a string list.')
        require(set(item.get('met_criteria', [])) <= set(item['criteria']), 'Unknown met criterion.')
        require(strings(item.get('dependencies', [])), 'Dependencies must be identities.')
        require(strings(item.get('evidence', [])), 'Evidence must be a string list.')
        require('note' not in item or isinstance(item['note'], str), 'Progress note must be text.')
        minutes = item.get('minutes')
        require(minutes is None or (type(minutes) in (int, float) and 0 < minutes < float('inf')),
                'Minutes must be a positive finite estimate or null.')
    focus = project.get('focus')
    require(focus is None or (nonempty(focus) and focus in by_id and by_id[focus]['level'] == 'milestone'),
            'Focus must reference a milestone in this project.')
    for item in items:
        parent = item.get('parent')
        expected_level = LEVELS[item['level']]
        if expected_level is None:
            require(parent is None, 'Milestone parent must be null.')
        else:
            require(nonempty(parent) and parent in by_id, 'Parent is missing.')
            require(by_id[parent]['level'] == expected_level, 'Invalid parent level or parent cycle.')
        for dependency in item.get('dependencies', []):
            require(dependency in by_id, 'Dependency is missing.')
    # Iterative DFS avoids recursion failures with large projects.
    colors = {}
    for identity in by_id:
        stack = [(identity, False)]
        while stack:
            current, leaving = stack.pop()
            if leaving:
                colors[current] = 2
                continue
            require(colors.get(current) != 1, 'Dependency cycle.')
            if colors.get(current) == 2:
                continue
            colors[current] = 1
            stack.append((current, True))
            stack.extend((d, False) for d in by_id[current].get('dependencies', []))
    for name in ('history', 'occurrences'):
        require(isinstance(snapshot.get(name), list) and
                all(isinstance(v, dict) for v in snapshot[name]), f'{name} must be a list of objects.')
    operation_ids = [h['id'] for h in snapshot['history'] if 'id' in h]
    require(all(nonempty(v) for v in operation_ids) and len(operation_ids) == len(set(operation_ids)),
            'Duplicate or invalid operation identity.')
    occurrence_keys = []
    for record in snapshot['occurrences']:
        require(nonempty(record.get('key')) and record.get('state') in ('reserved', 'delivered', 'unknown'),
                'Invalid occurrence record.')
        occurrence_keys.append(record['key'])
    require(len(occurrence_keys) == len(set(occurrence_keys)), 'Duplicate occurrence identity.')
    return by_id


def ancestors(item, by_id):
    result = []
    while item.get('parent'):
        item = by_id[item['parent']]
        result.append(item)
    return result


def available(snapshot, by_id):
    if snapshot['project']['state'] != 'active':
        return []
    result = []
    for item in snapshot['items']:
        if item['level'] != 'action' or item['state'] not in ('ready', 'in progress'):
            continue
        lineage = [item, *ancestors(item, by_id)]
        if any(p['state'] in ('blocked', 'done', 'dropped') for p in lineage[1:]):
            continue
        if any(by_id[d]['state'] != 'done' for p in lineage for d in p.get('dependencies', [])):
            continue
        result.append(item)
    return result


def choose(snapshot, by_id, budget=None):
    require(budget is None or (type(budget) in (int, float) and 0 < budget < float('inf')),
            'Time budget must be positive and finite.')
    ready = available(snapshot, by_id)
    candidates = [i for i in ready if budget is None or
                  (i.get('minutes') is not None and i['minutes'] <= budget)]
    focus = snapshot['project'].get('focus')
    candidates.sort(key=lambda i: (focus not in [p['id'] for p in ancestors(i, by_id)],
                                   i['state'] != 'in progress', i.get('minutes') or float('inf')))
    return {'ok': True, 'action': candidates[0] if candidates else None,
            'needs_decomposition': bool(ready) and not bool(candidates),
            'reason': 'Advances a ready outcome within the budget.' if candidates else
                      'Reduce a ready action or estimate it.' if ready else
                      'No ready action; review blockers, project state, or unfinished criteria.'}


def apply(snapshot, by_id, operation):
    require(isinstance(operation, dict) and nonempty(operation.get('id')), 'Operation requires identity.')
    fingerprint = hashlib.sha256(json.dumps(operation, sort_keys=True, ensure_ascii=False,
                                            allow_nan=False).encode()).hexdigest()
    previous = next((h for h in snapshot['history'] if h.get('id') == operation['id']), None)
    if previous:
        require(previous.get('fingerprint') == fingerprint,
                'Operation identity was reused with a different payload.', 'operation_conflict')
        return {'ok': True, 'snapshot': snapshot, 'duplicate': True}
    op_type = operation.get('type')
    require(nonempty(op_type), 'Operation type must be a nonempty string.')
    identity = operation.get('item_id')
    item_ops = {'progress', 'complete', 'block', 'reopen', 'drop'}
    if op_type in item_ops:
        if identity is None and op_type == 'complete':
            candidates = available(snapshot, by_id)
            require(len(candidates) == 1, 'Which action is complete?', 'ambiguous_action')
            identity = candidates[0]['id']
        require(nonempty(identity) and identity in by_id, 'Item identity is missing.', 'missing_item')
        item = by_id[identity]
        before = copy.deepcopy(item)
        expected = operation.get('expected', {})
        require(isinstance(expected, dict), 'Expected fields must be an object.')
        require(all(item.get(k) == v for k, v in expected.items()),
                'A field changed since it was read.', 'field_conflict')
        if op_type == 'complete':
            met = operation.get('met_criteria', item.get('met_criteria', []))
            require(strings(met) and set(met) <= set(item['criteria']), 'Unknown met criteria.')
            if item['level'] != 'action':
                require(set(item['criteria']) <= set(met), 'Outcome criteria remain unmet.', 'criteria_unmet')
            item['met_criteria'] = list(item['criteria']) if item['level'] == 'action' else met
            item['state'] = 'done'
            item['completion_source'] = 'user report'
        else:
            item['state'] = {'progress': 'in progress', 'block': 'blocked',
                             'reopen': 'ready', 'drop': 'dropped'}[op_type]
            if op_type == 'reopen':
                item['met_criteria'] = []
        if 'note' in operation:
            require(isinstance(operation['note'], str), 'Progress note must be text.')
            item['note'] = operation['note']
        if 'evidence' in operation:
            require(strings(operation['evidence']), 'Evidence must be a string list.')
            item['evidence'] = list(dict.fromkeys(item.get('evidence', []) + operation['evidence']))
        after = copy.deepcopy(item)
    elif op_type == 'revise_spec':
        require(operation.get('accepted') is True, 'Material revision requires user acceptance.', 'acceptance_required')
        changes = operation.get('changes')
        require(isinstance(changes, dict) and bool(changes), 'Revision requires changed spec fields.')
        before = copy.deepcopy(snapshot['project']['spec'])
        snapshot['project']['spec'].update(changes)
        after = copy.deepcopy(snapshot['project']['spec'])
    elif op_type == 'set_project_state':
        state = operation.get('state')
        require(isinstance(state, str) and state in PROJECT_STATES, 'Unknown project state.')
        if state == 'complete':
            require(operation.get('confirmed') is True, 'Project completion requires confirmation.', 'acceptance_required')
            met = operation.get('met_success_criteria', [])
            require(strings(met) and set(snapshot['project']['spec']['success_criteria']) <= set(met),
                    'Project success criteria remain unmet.', 'criteria_unmet')
        before = {'state': snapshot['project']['state'],
                  'reminder': copy.deepcopy(snapshot['project']['reminder'])}
        snapshot['project']['state'] = state
        if state in ('paused', 'complete', 'abandoned'):
            reminder = snapshot['project']['reminder']
            reminder['enabled'] = False
            reminder['cancellation_pending'] = bool(reminder.get('schedule_id'))
        after = {'state': snapshot['project']['state'],
                 'reminder': copy.deepcopy(snapshot['project']['reminder'])}
    else:
        raise Invalid('Unknown operation type.')
    validate(snapshot)
    snapshot['history'].append({'id': operation['id'], 'fingerprint': fingerprint,
                                'operation': copy.deepcopy(operation), 'resolved_item_id': identity,
                                'timestamp': datetime.now(timezone.utc).isoformat(),
                                'before': before, 'after': after})
    return {'ok': True, 'snapshot': snapshot, 'duplicate': False}


def review(snapshot, by_id):
    def outcome(item):
        return {**item, 'unmet_criteria': [c for c in item['criteria'] if c not in item.get('met_criteria', [])]}
    focus = snapshot['project'].get('focus')
    return {'ok': True, 'project_state': snapshot['project']['state'],
            'current_focus': outcome(by_id[focus]) if focus else None,
            'completed_outcomes': [outcome(i) for i in snapshot['items']
                                   if i['level'] == 'milestone' and i['state'] == 'done'],
            'blockers': [i for i in snapshot['items'] if i['state'] == 'blocked'],
            'counts': {'done_work_items': sum(i['state'] == 'done' for i in snapshot['items']),
                       'non_dropped_work_items': sum(i['state'] != 'dropped' for i in snapshot['items'])}}


def checkin(snapshot, request):
    reminder = snapshot['project']['reminder']
    require(nonempty(request.get('schedule_id')) and request['schedule_id'] == reminder.get('schedule_id'),
            'Schedule identity does not match the bound schedule.', 'schedule_conflict')
    occurrence = request.get('occurrence')
    require(nonempty(occurrence), 'Occurrence needs a stable timestamp identity.')
    try:
        parsed = datetime.fromisoformat(occurrence.replace('Z', '+00:00'))
    except ValueError:
        raise Invalid('Occurrence must be an ISO timestamp.') from None
    require(parsed.utcoffset() is not None, 'Occurrence timestamp must include an offset.')
    # Equivalent offset encodings name the same occurrence.
    canonical = parsed.astimezone(timezone.utc).isoformat()
    key = json.dumps([snapshot['project']['id'], request['schedule_id'], canonical], separators=(',', ':'))
    record = next((r for r in snapshot['occurrences'] if r['key'] == key), None)
    phase = request.get('phase', 'reserve')
    require(phase in ('reserve', 'delivered', 'unknown'), 'Unknown delivery phase.')
    result = {'ok': True, 'snapshot': snapshot, 'should_notify': False, 'needs_reconciliation': False}
    if phase == 'reserve':
        if record:
            result['needs_reconciliation'] = record['state'] != 'delivered'
        elif snapshot['project']['state'] == 'active' and reminder['enabled']:
            if reminder['mode'] == 'review' or request.get('meaningful') is True:
                snapshot['occurrences'].append({'key': key, 'state': 'reserved'})
                result['should_notify'] = True
    else:
        require(record is not None, 'No reservation exists for this occurrence.', 'missing_reservation')
        require(record['state'] != 'delivered' or phase == 'delivered',
                'Acknowledged delivery cannot become uncertain.', 'delivery_conflict')
        record['state'] = phase
        result['needs_reconciliation'] = phase == 'unknown'
    return result


def dispatch(command, request):
    original = request.get('snapshot') if isinstance(request, dict) else None
    try:
        require(isinstance(request, dict), 'Request must be an object.')
        snapshot = copy.deepcopy(original)
        by_id = validate(snapshot)
        if command == 'validate':
            return {'ok': True, 'errors': []}
        if command == 'next':
            return choose(snapshot, by_id, request.get('budget'))
        if command == 'apply':
            return apply(snapshot, by_id, request.get('operation'))
        if command == 'review':
            return review(snapshot, by_id)
        if command == 'checkin':
            return checkin(snapshot, request)
        raise Invalid('Unknown command.')
    except Invalid as error:
        return {'ok': False, 'error_code': error.code, 'error': str(error), 'snapshot': original}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'next', 'apply', 'review', 'checkin'))
    args = parser.parse_args()
    try:
        request = json.load(sys.stdin, parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
        result = dispatch(args.command, request)
    except (json.JSONDecodeError, ValueError):
        result = {'ok': False, 'error_code': 'invalid_json', 'error': 'Input must be valid finite JSON.'}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    sys.exit(main())
