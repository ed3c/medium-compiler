#!/usr/bin/env python3
"""SYNTHETIC TRANSPORT CONTROL ONLY. Never a model, writer, or human evidence."""
import json
import os
from pathlib import Path
import sys
import time
import uuid

if '--version' in sys.argv:
    print('codex-cli synthetic-transport-control');raise SystemExit()
if '--help' in sys.argv:
    print('--json --ephemeral --ignore-user-config --sandbox --output-last-message');raise SystemExit()
mode=Path('fixture-mode.txt').read_text().strip() if Path('fixture-mode.txt').exists() else 'good'
if mode=='timeout':
    print(json.dumps({'type':'thread.started','thread_id':'fixture-timeout'}),flush=True)
    time.sleep(10);raise SystemExit()
if mode=='mutate':
    Path('inputs/article.md').write_text('SYNTHETIC CORRUPTION\n')
final='SYNTHETIC CONTROL: guard refused; recording is not natural behavior.'
if mode=='empty-final':final=''
Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text(final)
events=[{'type':'thread.started','thread_id':'synthetic-'+str(uuid.uuid4())},{'type':'turn.started'},
 {'type':'item.started','item':{'id':'cmd','type':'command_execution','command':'fixture only','status':'in_progress'}},
 {'type':'item.completed','item':{'id':'cmd','type':'command_execution','command':'fixture only',
  'aggregated_output':'SYNTHETIC guard refusal; no natural writer. GH_TOKEN='+str('GH_TOKEN' in os.environ),
  'exit_code':2,'status':'completed'}},
 {'type':'item.completed','item':{'id':'msg','type':'agent_message','text':final}},
 {'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}]
if mode=='missing-exit':events[3]['item'].pop('exit_code')
if mode=='unknown':events[3]['item']['type']='unqualified_tool'
if mode=='truncated':events.pop()
for event in events:print(json.dumps(event),flush=True)
