"""Synthetic human approvals for offline controls; never production authority."""
import copy
import json
from movie_factory import stage_routing as routing, production_knowledge as pk


def assignment(root, packet, *, max_calls=1, identity='fixture-astra', runner_database='routed.sqlite3'):
    def write(name, data):
        p = root / name
        p.write_text(json.dumps(data, indent=2) if isinstance(data, dict) else data)
        return {'path': name, 'sha256': pk.file_hash(p)}
    source = write(identity+'-human.txt', 'SYNTHETIC FIXTURE: approve this exact scoped diagnostic.')
    retro = write(identity+'-retro.json', {'finding': 'Method remains ambiguous after a discriminating control',
                                          'limits': 'Synthetic control; no production result'})
    record = dict(id=identity, trigger='unresolved_diagnosis', reason='Identify the unresolved cause',
                  evidence={retro['path']: retro['sha256']}, retrospective=retro,
                  assignment=dict(task=packet['task'], packet_digest=routing.scope_digest(packet), runner_database=runner_database, max_calls=max_calls,
                                  expected_output='A diagnosis and discriminating test', success_test='Control separates the two candidate causes'))
    record['director_approval'] = write(identity+'-approval.json', dict(decision='approve_astra_escalation',
        assignment=copy.deepcopy(record), source=source, director_reply='SYNTHETIC FIXTURE APPROVAL'))
    return record


def packet(actor='planner'):
    return dict(task='fixture', actor=actor, stage='BRIEFING', cycle=0, planning_step='GROUNDING',
                planning_input_digest='a'*64, authority={'path':'fixture-authority','sha256':'b'*64})
