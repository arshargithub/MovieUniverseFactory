"""Opt-in, versioned metadata import; never reads credentials or retains messages."""
from __future__ import annotations

import json
from pathlib import Path

from .experiment_ledger import timestamp, union
from .telemetry import digest

CATEGORIES = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
              'output_tokens', 'reasoning_output_tokens', 'total_tokens')
DEFINITIONS = {
    'input_tokens': 'Reported input total; cached input is a subset.',
    'cached_input_tokens': 'Subset of input; do not add to total.',
    'cache_write_input_tokens': 'Retained as reported; not added to total.',
    'output_tokens': 'Reported output total; reasoning output is a subset.',
    'reasoning_output_tokens': 'Subset of output; do not add to total.',
    'total_tokens': 'Reported total; input plus output, without subset double counting.',
}


def token_values(values):
    result = {}
    for key in CATEGORIES:
        value = values.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f'invalid token count: {key}')
        result[key] = value
    return result


def import_rollout(path: Path, *, task_id: str, start: str, end: str,
                   installed_version: str, max_bytes=4_000_000) -> dict:
    """Only codex-cli 0.153.4 token_usage_record metadata, explicitly scoped.

    Bounded tail import deliberately reports PARTIAL. Inherited records with other
    thread IDs are excluded; response IDs deduplicate retries. No response_item,
    message text, prompt, arguments, reasoning or account credentials are retained.
    """
    source = 'codex-rollout-token-usage/v0.153.4'
    if installed_version != '0.153.4':
        return {'status': 'UNKNOWN', 'reason': 'unsupported installed format', 'records': []}
    low, high = timestamp(start), timestamp(end)
    if low > high:
        raise ValueError('invalid usage window')
    records, contexts, seen = [], {}, set()
    path = Path(path)
    if not path.is_file():
        return {'status': 'UNKNOWN', 'reason': 'task-local usage file unavailable', 'records': []}
    with path.open('rb') as stream:
        size = path.stat().st_size
        offset = max(0, size-max_bytes)
        if offset:
            stream.seek(offset)
            stream.readline()
        for line in stream:
            try:
                raw = json.loads(line)
                utc = raw.get('timestamp')
                when = timestamp(utc) if utc else None
            except (ValueError, TypeError, AttributeError, UnicodeDecodeError):
                continue
            data = raw.get('payload') or {}
            if when is None or not isinstance(data, dict):
                continue
            if raw.get('type') == 'turn_context' and low <= when <= high:
                contexts[data.get('turn_id')] = {
                    'model': data.get('model'), 'effort': data.get('effort'),
                    'attribution': 'runtime_turn_context', 'utc': utc,
                }
            if raw.get('type') != 'token_usage_record' or data.get('thread_id') != task_id:
                continue
            if when is None or not low <= when <= high:
                continue
            if not data.get('response_id') or data.get('inherited'):
                continue
            identity = (task_id, data['response_id'])
            values = token_values(data.get('usage') or {})
            # Keep duplicates for the reconciler to detect conflicting records.
            record = {
                'record_id': digest(identity), 'source': source, 'utc': utc,
                'task_id': task_id, 'turn_id': data.get('turn_id'),
                'response_id': data['response_id'], 'stream_id': task_id,
                'mode': 'incremental', 'tokens': values,
                'model': contexts.get(data.get('turn_id'), {}).get('model'),
                'effort': contexts.get(data.get('turn_id'), {}).get('effort'),
                'setting_attribution': 'runtime_turn_context' if data.get('turn_id') in contexts else 'UNKNOWN',
            }
            if digest(record) not in seen:
                records.append(record)
                seen.add(digest(record))
    return {'status': 'PARTIAL' if records else 'UNKNOWN', 'source': source,
            'reason': 'Optional local-log parsing; tail/scope completeness not independently established.',
            'window_start': start, 'window_end': end, 'task_id': task_id,
            'bounded_bytes': max_bytes, 'tail_truncated': bool(offset),
            'token_definitions': DEFINITIONS, 'model_observations': list(contexts.values()),
            'records': records}


def reconcile(records: list[dict], *, task_ids: list[str], start: str, end: str,
              complete_capture=False, inherited_response_ids=(), windows=None) -> dict:
    """Sum increments or differences, never cumulative snapshots themselves.

    A cumulative stream needs a snapshot exactly at the attribution boundary or
    an explicit boundary_baseline. Unexplained reset becomes a new uncounted
    baseline with partial coverage. Changing model does not reset counters.
    """
    low, high = timestamp(start), timestamp(end)
    if low > high:
        raise ValueError('invalid attribution window')
    scopes = union([(timestamp(a), timestamp(b)) for a, b in windows]) if windows is not None else [(low, high)]
    seen, streams, captured, issues = {}, {}, set(), []
    totals = {k: None for k in CATEGORIES}
    category_observations = {k: 0 for k in CATEGORIES}
    task_sources = {}
    blocks = []
    for record in sorted(records, key=lambda r: timestamp(r['utc'])):
        if record.get('task_id') not in task_ids:
            continue
        if record.get('inherited') or record.get('response_id') in inherited_response_ids:
            continue
        when = timestamp(record['utc'])
        if when < low or when > high:
            continue
        scope = next(((a, b) for a, b in scopes if a <= when <= b), None)
        if scope is None:
            continue
        identity = (record.get('task_id'), record.get('response_id') or record.get('record_id'))
        fingerprint = digest(record)
        if not record.get('record_id'):
            issues.append('missing_usage_identity')
            continue
        if identity in seen:
            if seen[identity] != fingerprint:
                issues.append('conflicting_duplicate_usage')
            continue
        seen[identity] = fingerprint
        existing_source = task_sources.setdefault(record['task_id'], record.get('source'))
        if record.get('source') != existing_source:
            issues.append('overlapping_usage_sources_require_reconciliation')
            continue
        values = token_values(record.get('tokens') or {})
        mode = record.get('mode')
        stream_key = (record['task_id'], record.get('source'), record.get('stream_id'), scope)
        prior = streams.get(stream_key)
        if prior and prior['mode'] != mode:
            issues.append('mixed_counter_modes')
            continue
        streams[stream_key] = {'mode': mode, 'tokens': values, 'epoch': record.get('counter_epoch')}
        if mode == 'cumulative':
            if prior is None or record.get('boundary_baseline'):
                if when != scope[0] and not record.get('boundary_baseline'):
                    issues.append('missing_boundary_baseline')
                continue
            reset = record.get('counter_epoch') != prior['epoch'] or any(
                values[k] is not None and prior['tokens'][k] is not None
                and values[k] < prior['tokens'][k] for k in CATEGORIES)
            if reset:
                issues.append('counter_reset_gap')
                continue
            delta = {k: values[k]-prior['tokens'][k]
                     if values[k] is not None and prior['tokens'][k] is not None else None
                     for k in CATEGORIES}
        elif mode == 'incremental':
            # Half-open attribution window prevents adjacent episodes counting a boundary twice.
            if when == scope[0]:
                continue
            delta = values
        else:
            issues.append('unsupported_usage_source_or_mode')
            continue
        captured.add(record['task_id'])
        if any(delta[k] is None for k in ('input_tokens', 'output_tokens', 'total_tokens')):
            issues.append('missing_token_fields')
        if delta['total_tokens'] is not None and delta['input_tokens'] is not None and delta['output_tokens'] is not None:
            if delta['total_tokens'] != delta['input_tokens'] + delta['output_tokens']:
                issues.append('inconsistent_total')
        for subset, parent in [('cached_input_tokens', 'input_tokens'), ('reasoning_output_tokens', 'output_tokens')]:
            if delta[subset] is not None and delta[parent] is not None and delta[subset] > delta[parent]:
                issues.append('inconsistent_subset')
        for key, value in delta.items():
            if value is not None:
                totals[key] = (totals[key] or 0) + value
                category_observations[key] += 1
        blocks.append({'record_id': record['record_id'], 'task_id': record['task_id'],
                       'turn_id': record.get('turn_id'), 'utc': record['utc'],
                       'model': record.get('model'), 'effort': record.get('effort'),
                       'setting_attribution': record.get('setting_attribution', 'UNKNOWN'), 'tokens': delta})
    missing = sorted(set(task_ids)-captured)
    if missing:
        issues.append('missing_linked_tasks')
    if not complete_capture:
        issues.append('capture_completeness_not_established')
    return {'status': 'UNKNOWN' if not blocks else 'PARTIAL' if issues else 'OBSERVED_SCOPE',
            'observed_tokens': totals,
            'category_coverage': {k: {'observed_blocks': n, 'total_blocks': len(blocks)}
                                  for k, n in category_observations.items()},
            'exact_attributable_tokens': {k: totals[k] if category_observations[k] == len(blocks) else None
                                          for k in CATEGORIES} if not issues and blocks else None,
            'expected_tasks': task_ids, 'captured_tasks': sorted(captured), 'missing_tasks': missing,
            'window_start': start, 'window_end': end, 'uncertainties': sorted(set(issues)),
            'blocks': blocks, 'token_definitions': DEFINITIONS,
            'actual_engineering_charge_usd': None,
            'subscription': {'treatment': 'shared fixed overhead', 'allocation_usd': None},
            'api_equivalent_estimate_usd': None,
            'account_allowance': {'scope': 'account-wide; not experiment token attribution', 'observations': []}}
