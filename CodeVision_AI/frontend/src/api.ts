import type {Project, Health, AskResult, Resolution} from './types'
async function req<T>(url:string, init?:RequestInit):Promise<T>{
  let resp:Response
  try { resp=await fetch(url,init) } catch { throw Error('Backend unreachable. Start FastAPI on port 8000, then refresh.') }
  const body=await resp.json().catch(()=>({detail:'Unexpected server response.'}))
  if(!resp.ok) throw Error(typeof body.detail==='string'?body.detail:`HTTP ${resp.status}`)
  return body as T
}
const json=(value:unknown):RequestInit=>({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(value)})
export const api={
  health:()=>req<Health>('/api/health'),
  projects:()=>req<{id:string;title:string;origin:string;created_at:string}[]>('/api/projects'),
  project:(id:string)=>req<Project>(`/api/projects/${id}`),
  demo:()=>req<Project>('/api/demo',{method:'POST'}),
  importGithub:(url:string)=>req<Project>('/api/import/github',json({url})),
  importZip:(file:File)=>{const form=new FormData();form.append('file',file);return req<Project>('/api/import/zip',{method:'POST',body:form})},
  ask:(id:string,question:string,useMemory:boolean)=>req<AskResult>(`/api/projects/${id}/ask`,json({question,use_memory:useMemory})),
  remember:(id:string,record:{issue:string;root_cause:string;fix:string;failed_attempts:string})=>req<{stored_in_hindsight:boolean;bank_id:string}>(`/api/projects/${id}/resolutions`,json(record)),
  rememberDemo:(id:string)=>req<{stored_in_hindsight:boolean;bank_id:string}>(`/api/projects/${id}/demo/remember`,{method:'POST'}),
  resolutions:(id:string)=>req<Resolution[]>(`/api/projects/${id}/resolutions`),
  reflect:(id:string,question:string)=>req<{answer:string;provider:string}>(`/api/projects/${id}/reflect`,json({question}))
}
