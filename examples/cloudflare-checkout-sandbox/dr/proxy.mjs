// Local operator bridge. Never deploy this proxy or expose it on a LAN address.
export default{async fetch(request,env){
  const url=new URL(request.url),origin=request.headers.get('Origin');
  if(!['127.0.0.1','localhost'].includes(url.hostname)||request.method!=='POST'||
     (origin&&origin!==url.origin))return new Response('Local operator only',{status:403});
  return env.DR.fetch(request);
}};
