// Reusable pure business rules; no credentials, remote payments, or effects.
export const SCENARIOS = Object.freeze(["lost_reply","worker_crash","duplicate","reconcile","reset"]);
export function validPayment(key,amount){
  if(typeof key!=="string"||!/^[A-Za-z0-9_-]{1,80}$/.test(key)) throw new Error("Payment Key: 1-80 letters/digits/_/-");
  if(!Number.isSafeInteger(amount)||amount<1||amount>1000000) throw new Error("Amount must be 1..1000000 cents");
  return {key,amount,currency:"USD"};
}
export function sameCharge(order,charge){
  return !!charge&&charge.key===order.key&&charge.amount===order.amount&&charge.currency==="USD";
}
export function decision(order,charge){
  if(!order) throw new Error("Unknown order");
  if(order.status==="PAID") return "PAID";
  if(!charge) return "PENDING";
  if(!sameCharge(order,charge)) throw new Error("Payment identity conflict");
  return "PAID";
}
export function invariant(snapshot){
  const orders=snapshot.orders||[],charges=snapshot.charges||[];
  const keys=new Set();
  for(const c of charges){if(keys.has(c.key))return {pass:false,reason:"Duplicate Provider Charge"};keys.add(c.key);}
  for(const o of orders){if(o.status==="PAID"&&!charges.some(c=>sameCharge(o,c)))return {pass:false,reason:"PAID without matching Provider Charge"};}
  return {pass:true,reason:"No duplicate charge; every PAID order has a matching charge"};
}
