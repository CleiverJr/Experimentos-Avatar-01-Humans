import sys, os, json
sys.path.insert(0,'/home/claude/w/lab')
os.environ['DITTO_BF16']='1'
from ditto_lab import Renderer
jobs=json.load(open(sys.argv[1]))
R=Renderer(threads=2, bf16=True)
for j in jobs:
    R.render('/home/claude/w/lab/runs/avatar.pkl', j['npz'], j['out'], j.get('start',0), j.get('end'))
    print('done', j['out'], flush=True)
