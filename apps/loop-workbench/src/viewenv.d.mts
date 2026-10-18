export interface EpisodeScene {
  status: string;
  episode: null | {run_ref:string;episode_ref:string;task_ref:string;environment_ref:string;actor_ref:string};
  harness: null | {phase:string;baseline_ref:string|null;candidate_ref:string|null};
  actions:string[];observations:string[];
  verification:null|{status:string;verifier_ref:string|null};
  reward:null|{status:string;value:number|null;source_ref:string|null};
  termination:null|{status:string;reason_ref:string|null};message:string
}
export function reviewedEpisodePath(input: unknown, origin:string):string|null
export function projectViewEnv(record: unknown):EpisodeScene
export function inspectLayer(scene:EpisodeScene,layer:'actual'|'proposed'|'replay'):
  {layer:string;status:string;refs:string[]}

export function readReviewedEpisode(uri: string, origin: string,
  options?: {fetcher?:(url:string,init:RequestInit)=>Promise<Response>; signal?:AbortSignal;
    cryptoProvider?:Crypto}):Promise<unknown>
