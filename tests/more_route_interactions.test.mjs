import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function control(dataset={}) {
  const listeners={};
  const attrs={};
  const classes=new Set();
  return {
    dataset, attrs, classes, hidden:false, textContent:"",
    setAttribute(name,value){attrs[name]=value;},
    addEventListener(name,fn){listeners[name]=fn;},
    click(){assert.equal(typeof listeners.click,"function");listeners.click();},
    classList:{toggle(name,active){if(active)classes.add(name);else classes.delete(name);}}
  };
}
test('More Route graph and detail views follow one decision selection',()=>{
  const ids=Array.from({length:7},(_,i)=>"D"+(i+1));
  const choices=ids.map(id=>control({mrChoice:id}));
  const nodes=ids.map(id=>control({mrNode:id}));
  const panels=ids.map(id=>control({mrPanel:id}));
  const edgeNames=["D1:D2","D2:D3","D3:D4","D1:D5","D4:D5","D2:D6","D5:D6","D6:D7"];
  const edges=edgeNames.map(id=>control({mrEdge:id}));
  const all=control();
  const status=control();
  const collections={
    "[data-mr-choice]":choices,
    "[data-mr-panel]":panels,
    "[data-mr-node]":nodes,
    "[data-mr-edge]":edges
  };
  const document={
    querySelectorAll(selector){return collections[selector]||[];},
    querySelector(selector){return selector==="[data-mr-show-all]"?all:null;},
    getElementById(id){return id==="mr-selection-status"?status:null;}
  };
  const source=fs.readFileSync(new URL('../site/more-route/more-route.js',import.meta.url),'utf8');
  vm.runInNewContext(source,{document});
  assert.equal(choices[0].attrs['aria-pressed'],'true');
  assert.equal(nodes[0].attrs['aria-pressed'],'true');
  assert.equal(panels.filter(p=>!p.hidden).length,1);
  assert.equal(edges.filter(x=>x.classes.has('mr-relevant')).length,2);
  nodes[5].click();
  assert.equal(choices[5].attrs['aria-pressed'],'true');
  assert.equal(nodes[5].attrs['aria-pressed'],'true');
  assert.deepEqual(panels.filter(p=>!p.hidden).map(p=>p.dataset.mrPanel),['D6']);
  assert.deepEqual(edges.filter(x=>x.classes.has('mr-relevant')).map(x=>x.dataset.mrEdge),['D2:D6','D5:D6','D6:D7']);
  choices[3].click();
  assert.equal(panels[3].hidden,false);
  assert.equal(nodes[3].attrs['aria-pressed'],'true');
  all.click();
  assert.equal(panels.every(p=>!p.hidden),true);
  assert.equal(edges.every(e=>!e.classes.has('mr-relevant')),true);
  assert.equal(all.attrs['aria-pressed'],'true');
});
