// Cloudflare Worker-level Access is the identity owner. No visitor API Key,
// custom JWT library, manual JWKS, or guessed session authorization.
export async function requireAccess(ctx){
  if(!ctx?.access)throw new Error("Cloudflare Access is not enabled for this Worker");
  const identity=await ctx.access.getIdentity();
  if(!identity?.email||typeof identity.email!=="string")throw new Error("Cloudflare Access identity is unavailable");
  return {userId:identity.id||identity.email,email:identity.email};
}
