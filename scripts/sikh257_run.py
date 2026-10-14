"""Fresh knowledge admission, allowlisted environment and recorded local worker."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from movie_factory import production_knowledge as pk
from movie_factory.sikh257_contract import ROOT, SOURCES, HERO_SOURCES, validate, digest, LAYOUT_CACHE

def main():
    if len(sys.argv) not in (3,4) or (len(sys.argv)==4 and sys.argv[3]!='--prepare'):raise ValueError('operation attempt [--prepare] required')
    job={'operation':sys.argv[1],'attempt':int(sys.argv[2])}
    out=validate(job)
    bound=['docs/planning/SERIES_01_SIKH_SEQUENCE.md','docs/planning/SERIES_01_SIKH_REFERENCE_INTAKE_256.json',
           'docs/planning/SERIES_01_SIKH_FAMILY_OPTIONS.md','docs/knowledge/CURRENT_PRODUCTION_STATE.md',
           'scripts/sikh257_native.py','src/movie_factory/sikh257_contract.py','src/movie_factory/sikh257_geometry.py','scripts/sikh257_run.py',*SOURCES]
    if job['operation'].startswith('layout'):bound.extend(['scripts/sikh257_layout.py',LAYOUT_CACHE])
    if job['operation']=='hero':bound.extend(['scripts/sikh261_character.py','docs/planning/SERIES_01_SIKH_BASELINE_V01.md','docs/planning/SERIES_01_SIKH_EXECUTION_257.md','.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',*HERO_SOURCES])
    task={'id':f'sikh257-{job["operation"]}-{job["attempt"]:02d}', 'operation':'modeling' if job['operation']=='inspect' else 'motion',
          'entities':['sikh_camera','renderer'],'query':'connected turban face cover uncovering motorcycle supported greeting leader rear Punjab night',
          'intent':'Authorized local source inspection and early complete-sequence construction; no production acceptance, paid generation or release.',
          'phase':'execution','inputs':{p:digest(ROOT/p) for p in bound},'open_decisions':[],
          'execution_authority':{'source':bound[0],'scope':'Director257 continuation, Sikh-only rough sequence with one-cloth turban/cover'},
          'max_context_characters':32000}
    packet=pk.task_packet(ROOT,task)
    proof=ROOT/'.runtime/knowledge-pilot213'/task['id'];proof.parent.mkdir(parents=True,exist_ok=True)
    proof.with_suffix('.json').write_text(json.dumps(packet,indent=2)+'\n')
    proof.with_suffix('.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if len(sys.argv)==4:
        print(proof.with_suffix('.md'));return
    jobs=ROOT/'.runtime/art-direction/series01-sikh257/jobs';jobs.mkdir(parents=True,exist_ok=True)
    jp=jobs/(task['id']+'.json')
    if jp.exists():raise ValueError('Existing job')
    jp.write_text(json.dumps(job))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    scratch=jobs/(task['id']+'-sandbox');scratch.mkdir()
    env.update(BLENDER_USER_CONFIG=str(scratch/'config'),BLENDER_USER_SCRIPTS=str(scratch/'scripts'),BLENDER_USER_DATAFILES=str(scratch/'data'))
    start=time.time()
    with jp.with_suffix('.log').open('w') as log:
        process=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh257_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    jp.with_suffix('.receipt.json').write_text(json.dumps({'returncode':process.returncode,'process_seconds':time.time()-start,'packet_digest':packet['packet_digest'],'source_inputs':task['inputs'],'output':str(out.relative_to(ROOT))},indent=2)+'\n')
    if process.returncode or not (out/'completed.json').exists():raise RuntimeError('Native job failed: '+str(jp.with_suffix('.log')))
    print(out)

if __name__=='__main__':main()
