"""Fixed offline head-only inspection; no arbitrary paths or provider code."""
import importlib.util
import json
from pathlib import Path
import sys

SPEC = importlib.util.spec_from_file_location('mesh_inspector280', Path(__file__).with_name('inspect_meshy278.py'))
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)
inspector.RAW = inspector.ROOT/'.runtime/assets/series01-sikh280-meshy/original.glb'
inspector.EXPECTED = '57f412eecfe01595b60d833e67f399c2c43a607a25f76b00817bba4468035f9a'
inspector.OUT = inspector.ROOT/'.runtime/art-direction/series01-sikh280/native-inspection01'
inspector.VIEW_YAW = 0.0
inspector.TASK = inspector.ROOT/'results/sikh280/task-native.json'
inspector.WORKER = Path(__file__).resolve()

if __name__ == '__main__':
    if '--' in sys.argv:
        args = sys.argv[sys.argv.index('--')+1:]
        if len(args) != 1:
            raise ValueError('One structured operation required')
        inspector.run(json.loads(args[0]))
    else:
        if len(sys.argv) != 2:
            raise ValueError('inspect or reopen required')
        inspector.launch({'operation': sys.argv[1]})
