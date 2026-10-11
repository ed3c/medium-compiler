import test from "node:test";
import assert from "node:assert/strict";
import {validPayment,decision,invariant,sameCharge} from "../site/reliability/logic.mjs";

test("original payment identity and cents must be explicit",()=>{
  assert.deepEqual(validPayment("cart-1",1250),{key:"cart-1",amount:1250,currency:"USD"});
  for(const value of ["", "bad key", "<script>","a".repeat(90)])
    assert.throws(()=>validPayment(value,1));
  for(const value of [-1,0,1.2,1000001,NaN,"42"])
    assert.throws(()=>validPayment("cart-1",value));
});
test("a lost response cannot invent PAID from no charge",()=>{
  const order={key:"cart-1",amount:1250,status:"PENDING"};
  assert.equal(decision(order,null),"PENDING");
  assert.equal(decision(order,{key:"cart-1",amount:1250,currency:"USD"}),"PAID");
  assert.throws(()=>decision(order,{key:"cart-1",amount:1400,currency:"USD"}));
});
test("recovered PAID state requires matching provider evidence",()=>{
  const order={key:"cart-1",amount:1250,status:"PAID"};
  assert.equal(invariant({orders:[order],charges:[]}).pass,false);
  assert.equal(invariant({orders:[order],charges:[{key:"cart-1",amount:1250,currency:"USD"}]}).pass,true);
  assert.equal(invariant({orders:[],charges:[{key:"x"},{key:"x"}]}).pass,false);
  assert.equal(sameCharge(order,{key:"cart-1",amount:1250,currency:"EUR"}),false);
});
