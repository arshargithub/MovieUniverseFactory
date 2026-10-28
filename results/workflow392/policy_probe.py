"""Offline executable decision-table illustration. NOT a production controller.

Inputs below are authored scenarios. This exercises proposed policy logic, not
artistic perception, historical prevention or a live migration. No native,
provider, controller/database mutation or model dispatch is available here.
"""
import json
from pathlib import Path

POLICY = dict(version='392-PROPOSED', first_visual_slots=2,
              family_slots=6, stagnation_visual_attempts=3,
              families_per_capability=2, engineering_slots=12,
              qualified_capability_slots=12, foundational_capability_slots=24)

VALID_BASE = dict(contract_complete=True, lineage_complete=True,
                  scope_authorized=True, sources_current=True,
                  rights_and_model_authorized=True, mandatory_context_complete=True,
                  proof_kinds_match=True, prerequisites_met=True,
                  evidence_coverage_complete=True, authority_remaining=6,
                  image_evidence=True)


def decide(s):
    if not set(VALID_BASE) <= s.keys():
        return 'BLOCK_CONTRACT'
    if not s.get('contract_complete', True):
        return 'BLOCK_CONTRACT'
    if not s.get('lineage_complete', True):
        return 'BLOCK_ACCOUNTING'
    if not s.get('scope_authorized', True):
        return 'BLOCK_AUTHORITY'
    if s.get('unapproved_contract_change'):
        return 'BLOCK_SCOPE_CHANGE'
    if not s.get('sources_current', True):
        return 'BLOCK_STALE_PROOF'
    if not s.get('rights_and_model_authorized', True):
        return 'BLOCK_RIGHTS_OR_MODEL'
    if s.get('paid_operation') and not s.get('cost_reserved'):
        return 'BLOCK_RESOURCE_RESERVATION'
    if not s.get('mandatory_context_complete', True):
        return 'BLOCK_CONTEXT'
    if s.get('external_block'):
        return 'BLOCK_EXTERNAL'
    exception = s.get('exception_approved', False)
    if s.get('root_retired') and not exception:
        return 'RETIRED_FOR_PRODUCTION'
    if exception:
        if s.get('operation') not in {'native_transport', 'apply_existing_graft', 'key_pose_render', 'motion_preview', 'review'}:
            return 'BLOCK_EXCEPTION_SCOPE'
        if s.get('new_anatomy_variant'):
            return 'BLOCK_EXCEPTION_SCOPE'
        if s.get('requests_technical_repair') and s.get('technical_repairs_used', 0) >= 1:
            return 'STOP_TERMINAL_PROBE'
    if s.get('art_disposition') and not s.get('image_evidence', False):
        return 'BLOCK_DISPOSITION_KIND'
    if not s.get('proof_kinds_match', True):
        return 'BLOCK_PROOF_KIND'
    if not s.get('prerequisites_met', True):
        return 'BLOCK_DEPENDENCY_ORDER'
    if not s.get('evidence_coverage_complete', True):
        return 'BLOCK_EVIDENCE_COVERAGE'
    # A valid existing result can finish at the ceiling; caps govern further work.
    if s.get('all_required_agent_criteria_pass') and not s.get('critical_regression'):
        return 'COMPLETE' if s.get('director_accepted') else 'READY_FOR_DIRECTOR_AV'
    if exception:
        if s.get('exception_used', 0) >= 2 or s.get('valid_native_anatomy_failed'):
            return 'STOP_TERMINAL_PROBE'
        if s.get('authority_remaining', 1) <= 0:
            return 'BLOCK_ALLOWANCE'
        return 'CONTINUE_TERMINAL_PROBE'
    if s.get('authority_remaining', 1) <= 0:
        return 'BLOCK_ALLOWANCE'
    cap = POLICY['foundational_capability_slots'] if s.get('needs_engineering') else POLICY['qualified_capability_slots']
    if s.get('goal_slots_used', 0) >= cap or s.get('failed_families', 0) >= POLICY['families_per_capability']:
        return 'RETIRE_CAPABILITY_FOR_ENVELOPE'
    if s.get('critical_regression'):
        return 'HOLD_REPAIR_REGRESSION'
    if s.get('engineering_lane'):
        if s.get('engineering_slots_used', 0) >= POLICY['engineering_slots']:
            return 'STOP_ENGINEERING_UNQUALIFIED'
        if s.get('same_error_after_repair_count', 0) >= 2:
            return 'HOLD_ENGINEERING_REASSESSMENT'
        return 'CONTINUE_BOUNDED_ENGINEERING'
    if s.get('family_falsified'):
        return 'RETIRE_FAMILY'
    if s.get('family_slots_used', 0) >= POLICY['family_slots']:
        return 'RETIRE_FAMILY'
    if s.get('stagnant_visual_attempts', 0) >= POLICY['stagnation_visual_attempts']:
        return 'RETIRE_FAMILY'
    if s.get('qualified_path') and not s.get('first_visual_exists') and s.get('family_slots_used', 0) >= POLICY['first_visual_slots']:
        return 'STOP_QUALIFICATION_NOT_DEMONSTRATED'
    return 'CONTINUE_AUTHORIZED_WORK'


CASES = [
    ('missing required attribute', {'__omit__': ['lineage_complete']}, 'BLOCK_CONTRACT'),
    ('missing contract', {'contract_complete': False}, 'BLOCK_CONTRACT'),
    ('renaming loses history', {'lineage_complete': False}, 'BLOCK_ACCOUNTING'),
    ('new name cannot evade parent118', {'needs_engineering': True, 'goal_slots_used': 118}, 'RETIRE_CAPABILITY_FOR_ENVELOPE'),
    ('244fit before target form', {'prerequisites_met': False}, 'BLOCK_DEPENDENCY_ORDER'),
    ('249dense build before pose proof', {'prerequisites_met': False}, 'BLOCK_DEPENDENCY_ORDER'),
    ('218image-free art label', {'art_disposition': True, 'image_evidence': False}, 'BLOCK_DISPOSITION_KIND'),
    ('rest metric passed as visual proof', {'proof_kinds_match': False}, 'BLOCK_PROOF_KIND'),
    ('new topology reuses old proof', {'sources_current': False}, 'BLOCK_STALE_PROOF'),
    ('missing reverse view', {'evidence_coverage_complete': False}, 'BLOCK_EVIDENCE_COVERAGE'),
    ('small score improvements no closure', {'stagnant_visual_attempts': 3}, 'RETIRE_FAMILY'),
    ('family ceiling with partial progress', {'family_slots_used': 6}, 'RETIRE_FAMILY'),
    ('valid result at family ceiling', {'family_slots_used': 6, 'authority_remaining': 0, 'all_required_agent_criteria_pass': True}, 'READY_FOR_DIRECTOR_AV'),
    ('three good cells permit remaining work', {'family_slots_used': 4, 'first_visual_exists': True, 'qualified_path': True, 'stagnant_visual_attempts': 0}, 'CONTINUE_AUTHORIZED_WORK'),
    ('first visual absent qualified path', {'qualified_path': True, 'family_slots_used': 2, 'first_visual_exists': False}, 'STOP_QUALIFICATION_NOT_DEMONSTRATED'),
    ('known prep66bringup sensitivity', {'engineering_lane': True, 'engineering_slots_used': 9, 'needs_engineering': True, 'goal_slots_used': 9}, 'CONTINUE_BOUNDED_ENGINEERING'),
    ('bringup is not infinite', {'engineering_lane': True, 'engineering_slots_used': 12, 'needs_engineering': True, 'goal_slots_used': 12}, 'STOP_ENGINEERING_UNQUALIFIED'),
    ('repeat technical purported repair', {'engineering_lane': True, 'same_error_after_repair_count': 2}, 'HOLD_ENGINEERING_REASSESSMENT'),
    ('regression cannot average away', {'critical_regression': True}, 'HOLD_REPAIR_REGRESSION'),
    ('two failed families stop goal', {'failed_families': 2}, 'RETIRE_CAPABILITY_FOR_ENVELOPE'),
    ('more cycles do not unretire', {'root_retired': True, 'authority_remaining': 100}, 'RETIRED_FOR_PRODUCTION'),
    ('Astra cannot unretire', {'root_retired': True, 'rights_and_model_authorized': True}, 'RETIRED_FOR_PRODUCTION'),
    ('specific approved terminal probe', {'root_retired': True, 'exception_approved': True, 'operation': 'apply_existing_graft', 'exception_used': 0, 'authority_remaining': 2}, 'CONTINUE_TERMINAL_PROBE'),
    ('terminal probe forbids sculpt loop', {'root_retired': True, 'exception_approved': True, 'operation': 'apply_existing_graft', 'new_anatomy_variant': True}, 'BLOCK_EXCEPTION_SCOPE'),
    ('terminal valid anatomy failure', {'root_retired': True, 'exception_approved': True, 'operation': 'review', 'valid_native_anatomy_failed': True}, 'STOP_TERMINAL_PROBE'),
    ('terminal no extension', {'root_retired': True, 'exception_approved': True, 'operation': 'review', 'exception_used': 2}, 'STOP_TERMINAL_PROBE'),
    ('terminal no extra repair', {'root_retired': True, 'exception_approved': True, 'operation': 'native_transport', 'requests_technical_repair': True, 'technical_repairs_used': 1}, 'STOP_TERMINAL_PROBE'),
    ('unapproved quality reduction', {'unapproved_contract_change': True}, 'BLOCK_SCOPE_CHANGE'),
    ('mandatory rule lost during compaction', {'mandatory_context_complete': False}, 'BLOCK_CONTEXT'),
    ('unreserved paid operation', {'paid_operation': True, 'cost_reserved': False}, 'BLOCK_RESOURCE_RESERVATION'),
    ('external outage not anatomy failure', {'external_block': True}, 'BLOCK_EXTERNAL'),
    ('positive internal proof still needs DirectorAV', {'all_required_agent_criteria_pass': True}, 'READY_FOR_DIRECTOR_AV'),
    ('actual scoped Director acceptance', {'all_required_agent_criteria_pass': True, 'director_accepted': True}, 'COMPLETE'),
    # Retained negative control: mechanical validation cannot see a dishonest
    # positive artistic assertion. Human review/calibration is still necessary.
    ('SEMANTIC_LIMIT_bad_image_falsely_asserted_pass', {'all_required_agent_criteria_pass': True, 'image_evidence': True}, 'READY_FOR_DIRECTOR_AV'),
]


def main():
    rows = []
    for name, overrides, expected in CASES:
        state = dict(VALID_BASE, **{k:v for k,v in overrides.items() if k != '__omit__'})
        for key in overrides.get('__omit__', []):
            state.pop(key)
        actual = decide(state)
        assert actual == expected, (name, expected, actual)
        rows.append(dict(case=name, inputs=state, expected=expected, actual=actual))
    output = dict(policy=POLICY, valid_base_fixture=VALID_BASE, cases=rows, assertion_matches=len(rows),
                  deployment='NONE', scope='Authored offline decision-table checks only.',
                  limits=['Not production implementation or Director policy adoption.',
                          'Not blind historical prediction or perceptual qualification.',
                          'Known false artistic PASS remains able to reach human review.',
                          'Does not qualify admin projection equivalence or safe migration.'])
    Path(__file__).with_name('POLICY_PROBE_RESULTS.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(dict(cases=len(rows), assertion_matches=len(rows), production_deployed=False, retained_semantic_limit=True)))


if __name__ == '__main__':
    main()
