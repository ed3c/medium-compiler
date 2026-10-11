// Cloudflare Access JWT verification. Do not accept client-supplied identity or static API keys.
// Requires an Access Application in front of the .workers.dev/custom domain.
function decodePart(value){
  if(!/^[A-Za-z0-9_-]+$/.test(value))throw new Error("Invalid JWT encoding");
  return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(value.replace(/-/g,"+").replace(/_/g,"/")),c=>c.charCodeAt(0))));
}
function bytes(value){return Uint8Array.from(atob(value.replace(/-/g,"+").replace(/_/g,"/")),c=>c.charCodeAt(0));}
export async function verifyAccess(request,env,now=Math.floor(Date.now()/1000)){
  const domain=env.ACCESS_TEAM_DOMAIN,aud=env.ACCESS_AUD;
  if(!domain||!aud||!(/^[A-Za-z0-9-]+\.cloudflareaccess\.com$/.test(domain)))throw new Error("Access is not configured");
  const token=request.headers.get("Cf-Access-Jwt-Assertion");
  if(!token)throw new Error("Cloudflare Access identity is required");
  const parts=token.split(".");
  if(parts.length!==3)throw new Error("Invalid Access JWT");
  const header=decodePart(parts[0]),payload=decodePart(parts[1]);
  if(header.alg!=="RS256"||!header.kid||!payload.sub)throw new Error("Invalid Access JWT header/subject");
  const audience=Array.isArray(payload.aud)?payload.aud:[payload.aud];
  if(payload.iss!=="https://"+domain||!audience.includes(aud)||
     !Number.isFinite(payload.exp)||payload.exp<=now||
     (payload.nbf!==undefined&&payload.nbf>now))throw new Error("Access JWT claims refused");
  const response=await fetch("https://"+domain+"/cdn-cgi/access/certs",{redirect:"error"});
  if(!response.ok)throw new Error("Access JWKS unavailable");
  const jwks=await response.json();
  const jwk=jwks.keys?.find(x=>x.kid===header.kid&&x.kty==="RSA"&&x.use!=="enc");
  if(!jwk)throw new Error("Access signing key unknown");
  const publicKey=await crypto.subtle.importKey("jwk",jwk,{name:"RSASSA-PKCS1-v1_5",hash:"SHA-256"},false,["verify"]);
  const ok=await crypto.subtle.verify("RSASSA-PKCS1-v1_5",publicKey,bytes(parts[2]),new TextEncoder().encode(parts[0]+"."+parts[1]));
  if(!ok)throw new Error("Invalid Access JWT signature");
  return {userId:payload.sub,email:payload.email||null};
}
