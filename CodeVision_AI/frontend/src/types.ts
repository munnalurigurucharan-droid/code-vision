export type FileNode = {
  path: string; language: string; lines: number; imports: string[];
  symbols: {name:string;kind:string;line:number;doc?:string}[];
  calls: [string,number][]; warnings:string[]; entrypoint:boolean; preview:string
}
export type Project = {
  id:string; title:string; origin:string;
  stats:{files:number;lines:number;dependencies:number;warnings:number};
  frameworks:string[]; languages:Record<string,number>; entrypoints:string[];
  files:FileNode[]; edges:{source:string;target:string}[]; mermaid:string;
  flow:{step:number;title:string;description:string}[]; limitations:string[]
}
export type Health = {status:string;hindsight_configured:boolean;hindsight_verified:boolean;groq_configured:boolean;mode:string}
export type AskResult = {answer:string;provider:string;memory_status:string;memories:{id:string;text:string}[];memory_error:string|null;bank_id:string;disclaimer:string}
export type Resolution = {issue:string;root_cause:string;fix:string;attempts:string;created_at:string}
