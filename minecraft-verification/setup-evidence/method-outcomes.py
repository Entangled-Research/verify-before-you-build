"""Summarize declared method reuse from evidence; do not infer undeclared copying."""
import argparse,json,collections
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);a=p.parse_args()
for run in a.runs:
    events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
    rows=collections.defaultdict(collections.Counter);attempt=None
    for e in events:
        typ=e['event']
        if typ=='dependency_started':
            attempt=e['id'];rows[attempt]['production starts']+=1
            if e['status']!='verified':rows[attempt]['without receipt']+=1
        elif typ=='dependency_blocked':rows[e['id']]['blocked']+=1
        elif typ=='verification_started':rows[e['id']]['tests']+=1
        elif typ=='receipt':rows[e['id']]['test '+e['status']]+=1
        elif typ=='method_revised':
            key='changed steps' if e['before']['steps']!=e['after']['steps'] else 'unchanged resubmissions'
            rows[e['after']['id']][key]+=1
        elif typ=='tool_error' and e['tool']['tool']=='use_method':rows[e['tool']['id']]['production errors']+=1
        elif typ=='tool_result':attempt=None
        elif typ=='action' and attempt and e['role']=='production':rows[attempt]['production primitives']+=1
    print(run.name)
    for name,counts in rows.items():print(name,dict(counts))
