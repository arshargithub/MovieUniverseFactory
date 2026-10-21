"""Narrow native dispatch bridge: inspect only until authoring handlers qualify.

Durable pre-dispatch reservation, source/plan/dependency admission, immutable
output bindings, explicit internal step review. No shell/code-string interface.
An in-process capability is accidental-bypass protection, not an OS sandbox.
"""
from contextlib import closing
from pathlib import Path
import json
import re
from . import production_knowledge as pk
from . import review_control as rc
from .production_workflow import require, nonempty, rows, bindings

_ACTIVE = {}
BLENDER_BIN = '/Applications/Blender.app/Contents/MacOS/Blender'


def engine_digest():
    folder = Path(__file__).parent / 'adapters/blender'
    return pk.digest({str(p.relative_to(folder)): pk.file_hash(p) for p in sorted(folder.glob('*.py'))})


def check_capability(capability, job):
    entry = _ACTIVE.get(id(capability))
    require(entry is not None and entry['capability'] is capability, 'ROUTE_FIRST_NATIVE_ADMISSION_REQUIRED')
    require(not entry['used'] and entry['digest'] == pk.digest(job), 'NATIVE_CAPABILITY_REPLAY_OR_SUBSTITUTION')
    entry['controller']._fresh(entry['state'])
    current = entry['controller'].state(entry['state']['task'])
    require(current['stage'] == 'EXECUTING' and all(current[k] == entry['state'][k]
            for k in ('cycle', 'fingerprint')), 'NATIVE_ADMISSION_CHANGED')
    require(entry['engine'] == engine_digest(), 'NATIVE_HANDLER_CHANGED')
    entry['used'] = True


class Bridge:
    def __init__(self, controller):
        self.c = controller
        with closing(controller.connect()) as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS native_runs (
                    id TEXT PRIMARY KEY, task TEXT NOT NULL, cycle INTEGER NOT NULL,
                    fingerprint TEXT NOT NULL, step TEXT NOT NULL, record TEXT NOT NULL,
                    UNIQUE(task, cycle, fingerprint, step));
                CREATE TABLE IF NOT EXISTS native_reviews (
                    run TEXT PRIMARY KEY, record TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS native_runs_closed BEFORE UPDATE ON native_runs
                    WHEN json_extract(OLD.record, '$.status') != 'RESERVED'
                    BEGIN SELECT RAISE(ABORT, 'closed native run'); END;
                CREATE TRIGGER IF NOT EXISTS native_runs_no_delete BEFORE DELETE ON native_runs
                    BEGIN SELECT RAISE(ABORT, 'immutable native run'); END;
                CREATE TRIGGER IF NOT EXISTS native_reviews_no_update BEFORE UPDATE ON native_reviews
                    BEGIN SELECT RAISE(ABORT, 'immutable native review'); END;
                CREATE TRIGGER IF NOT EXISTS native_reviews_no_delete BEFORE DELETE ON native_reviews
                    BEGIN SELECT RAISE(ABORT, 'immutable native review'); END;
            ''')

    def runs(self, state):
        with closing(self.c.connect()) as con:
            return {r['step']: json.loads(r['record']) for r in con.execute(
                'SELECT step,record FROM native_runs WHERE task=? AND cycle=? AND fingerprint=?',
                (state['task'], state['cycle'], state['fingerprint']))}

    def review(self, run):
        with closing(self.c.connect()) as con:
            row = con.execute('SELECT record FROM native_reviews WHERE run=?', (run,)).fetchone()
        require(row is not None, 'STEP_REVIEW_NOT_RUN')
        return json.loads(row[0])

    def qualified(self, run):
        require(run['status'] == 'RETURNED', 'NATIVE_JOB_NOT_SUCCESSFUL')
        require(run['handler_digest'] == engine_digest(), 'NATIVE_HANDLER_CHANGED')
        bindings(self.c.root, run['artifacts'])
        verdict = self.review(run['id'])
        require(verdict['verdict'] == 'PASS' and not verdict['open_defects'], 'DEPENDENCY_REVIEW_FAILED')
        require(verdict['run_digest'] == pk.digest(run), 'STEP_REVIEW_STALE')
        bindings(self.c.root, verdict['evidence'])

    def dispatch(self, task, step, run_id, *, parent, blender_bin, timeout=300):
        """Registered read-only scene inspection, not arbitrary authoring."""
        from .task_router import DATABASE
        from .adapters.blender.runner import run_blender
        require(blender_bin == BLENDER_BIN, 'UNREGISTERED_NATIVE_EXECUTABLE')
        require(type(timeout) in {int, float} and 0 < timeout <= 600, 'NATIVE_TIMEOUT_BOUND')
        require(self.c.database == self.c.root / DATABASE, 'NATIVE_CANONICAL_CONTROLLER_REQUIRED')
        state = self.c.state(task)
        self.c._fresh(state)
        require(state['mode'] == 'local_native', 'OFFLINE_OR_FROZEN_CANNOT_LAUNCH_NATIVE')
        require(state['stage'] == 'EXECUTING', 'NATIVE_BEFORE_PLANNING_ADMISSION')
        require('native_inspect' in state['routing']['request']['operations'], 'UNROUTED_NATIVE_OPERATION')
        steps = rows(state['planning_artifacts']['STRATEGIZING']['steps'])
        require(step in steps, 'UNPLANNED_NATIVE_STEP')
        previous = self.runs(state)
        require(step not in previous, 'NATIVE_STEP_ALREADY_ATTEMPTED_REPLAN_REQUIRED')
        for dep in steps[step]['depends_on']:
            require(dep in previous, 'DEPENDENCY_NOT_RUN')
            self.qualified(previous[dep])
        rc.binding(self.c.root, parent)
        admitted = list(state['brief']['source_bindings'].values())
        for run in previous.values():
            admitted.extend(run.get('artifacts', {}).values())
        require(parent in admitted, 'UNBOUND_NATIVE_INPUT')
        require(Path(parent['path']).suffix == '.blend', 'INSPECT_REQUIRES_NATIVE')
        require(re.fullmatch(r'[a-zA-Z0-9_-]{1,96}', run_id) is not None, 'NATIVE_RUN_ID')
        output = rc.path(self.c.root, '.runtime/factory-native/' + run_id)
        require(not output.exists(), 'NATIVE_OUTPUT_EXISTS')
        job = {'mode': 'inspect', 'parent_native': str(rc.path(self.c.root, parent['path'])),
               'output_dir': str(output), 'seed': 332,
               'profile': {'name': 'inspect332', 'width': 64, 'height': 64,
                           'samples': 1, 'device': 'CPU', 'shots': []}}
        record = {'id': run_id, 'task': task, 'step': step, 'cycle': state['cycle'],
                  'fingerprint': state['fingerprint'], 'parent': parent,
                  'job_digest': pk.digest(job), 'handler_digest': engine_digest(), 'status': 'RESERVED'}
        # Reservation precedes any process or output directory. Crash between
        # these writes leaves a held lease, never an automatic retry permission.
        self.c.job(task, run_id, 'acquire', 'native-acquire:' + run_id)
        current = self.c.state(task)
        if any(current[k] != state[k] for k in ('cycle', 'fingerprint')):
            self.c.job(task, run_id, 'release', 'native-release:' + run_id)
            require(False, 'NATIVE_ADMISSION_CHANGED')
        with self.c.transaction() as con:
            con.execute('INSERT INTO native_runs VALUES(?,?,?,?,?,?)',
                        (run_id, task, state['cycle'], state['fingerprint'], step, json.dumps(record)))
        capability = object()
        _ACTIVE[id(capability)] = {'capability': capability, 'used': False, 'digest': pk.digest(job),
                                  'controller': self.c, 'state': state, 'engine': record['handler_digest']}
        try:
            result = run_blender(job, blender_bin=blender_bin, timeout=timeout, _admission=capability)
            require(result.get('ok') is True, 'NATIVE_WORKER_FAILED')
            require(engine_digest() == record['handler_digest'], 'NATIVE_HANDLER_CHANGED')
            self.c._fresh(state)
            rc.binding(self.c.root, parent)
            snapshot = output / 'snapshot.json'
            require(snapshot.is_file() and not snapshot.is_symlink(), 'NATIVE_OUTPUT_MISSING')
            # Parse before accepting it as structural evidence; content judgment
            # belongs to the separate step and final review, not successful exit.
            require(isinstance(json.loads(snapshot.read_text()), dict), 'NATIVE_OUTPUT_INVALID')
            record.update(status='RETURNED', artifacts={'snapshot': {
                'path': str(snapshot.relative_to(self.c.root)), 'sha256': pk.file_hash(snapshot)}})
        except Exception as e:
            record.update(status='FAILED', error=type(e).__name__ + ': ' + str(e))
        finally:
            _ACTIVE.pop(id(capability), None)
        # BaseException/process death intentionally retains RESERVED and lease.
        # Operator must establish process termination before recovery; no replay.
        with self.c.transaction() as con:
            con.execute('UPDATE native_runs SET record=? WHERE id=?', (json.dumps(record), run_id))
        self.c.job(task, run_id, 'release', 'native-release:' + run_id)
        return record

    def record_review(self, task, step, verdict):
        state = self.c.state(task)
        self.c._fresh(state)
        require(state['stage'] == 'EXECUTING', 'NATIVE_REVIEW_OUTSIDE_EXECUTION')
        run = self.runs(state)[step]
        require(run['status'] == 'RETURNED', 'NATIVE_JOB_NOT_SUCCESSFUL')
        require(run['handler_digest'] == engine_digest(), 'NATIVE_HANDLER_CHANGED')
        require(verdict.get('verdict') in {'PASS', 'FAIL', 'NOT_RUN'}, 'NATIVE_REVIEW_VERDICT')
        for key in ('observation', 'comparison'):
            require(nonempty(verdict.get(key)), 'NATIVE_REVIEW_OBSERVATION_REQUIRED')
        require(isinstance(verdict.get('open_defects'), list), 'NATIVE_DEFECTS_REQUIRED')
        require(verdict['run_digest'] == pk.digest(run), 'STEP_REVIEW_STALE')
        bindings(self.c.root, run['artifacts'])
        bindings(self.c.root, verdict['evidence'])
        require(all(b in verdict['evidence'].values() for b in run['artifacts'].values()), 'REVIEW_MUST_INSPECT_ACTUAL_OUTPUT')
        with self.c.transaction() as con:
            con.execute('INSERT INTO native_reviews VALUES(?,?)', (run['id'], json.dumps(verdict)))
        return verdict


def validate_candidate(controller, state, result):
    bridge = Bridge(controller)
    steps = rows(state['planning_artifacts']['STRATEGIZING']['steps'])
    runs = bridge.runs(state)
    require(set(runs) == set(steps), 'NATIVE_STEPS_INCOMPLETE')
    expected = {}
    for step, run in runs.items():
        bridge.qualified(run)
        expected.update({step + ':' + name: binding for name, binding in run['artifacts'].items()})
    require(result['candidate']['artifacts'] == expected, 'NATIVE_CANDIDATE_NOT_DISPATCH_OUTPUTS')
