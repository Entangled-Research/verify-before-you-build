import os from 'node:os';
import path from 'node:path';
export const MLX={
  name:'mlx-community/Qwen3.5-9B-MLX-4bit',
  revision:'938d8919941c6e7efd3c7150eff7fe9d12afa631',
  base:'http://127.0.0.1:18601/v1',
  temperature:.2,maxTokens:1024,enableThinking:false,
  parser:'strict JSON object in assistant final content; no commands recovered from prose or reasoning'
};
export const modelPath=()=>path.join(os.homedir(),'.cache/huggingface/hub/models--mlx-community--Qwen3.5-9B-MLX-4bit/snapshots',MLX.revision);
const args={inspect:[],recipe:['item'],verify_method:['id'],use_method:['id'],revise_method:['id','steps'],craft:['item','times'],smelt:['input','output','count'],finish:[]};
export const interfacePrompt='\nReply with a single JSON object and no surrounding text. Use the tool field for the exact tool name. Include a short reason. Required additional keys by tool: '+JSON.stringify(args)+'. Choose the next action from the live observation. The raw tool response is the only source of truth about execution.';
export function decodeAction(content){
  const obj=JSON.parse(content);
  if(!obj||Array.isArray(obj)||typeof obj!=='object'||!Object.hasOwn(args,obj.tool)||typeof obj.reason!=='string')throw Error('Expected one JSON action with reason and a known tool.');
  const fields=args[obj.tool],allowed=['tool','reason',...fields];
  if(fields.some(k=>!Object.hasOwn(obj,k))||Object.keys(obj).some(k=>!allowed.includes(k)))throw Error('Wrong argument keys for '+obj.tool);
  for(const k of fields){
    if(k==='steps'){if(!Array.isArray(obj.steps))throw Error('Expected steps array');}
    else if(k==='times'||k==='count'){if(!Number.isInteger(obj[k])||obj[k]<1||obj[k]>64)throw Error('Invalid action count');}
    else if(typeof obj[k]!=='string'||!/^([a-z_]+)$/.test(obj[k]))throw Error('Invalid item or method name');
  }
  return obj;
}
export async function mlxChat(messages,seed,signal){
  const body={model:modelPath(),stream:false,messages,seed,temperature:MLX.temperature,max_tokens:MLX.maxTokens,chat_template_kwargs:{enable_thinking:MLX.enableThinking}};
  const response=await fetch(MLX.base+'/chat/completions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal});
  if(!response.ok)throw Error('Local MLX HTTP '+response.status+': '+(await response.text()).slice(0,300));
  const raw=await response.json(),msg=raw.choices?.[0]?.message;
  if(!msg||typeof msg.content!=='string'||!Number.isFinite(raw.usage?.prompt_tokens)||!Number.isFinite(raw.usage?.completion_tokens))throw Error('Local MLX response missing final content or token usage');
  return {raw,content:msg.content,promptTokens:raw.usage.prompt_tokens,generatedTokens:raw.usage.completion_tokens};
}
