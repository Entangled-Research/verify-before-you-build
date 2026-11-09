import { receiptKey, TARGETS } from './protocol.mjs';
import { smelting } from './smelting.mjs';

function craftRecipes(bot, item) {
  const entry=bot.registry.itemsByName[item];
  if (!entry) return [];
  const table=bot.findBlock({matching:b=>b.name==='crafting_table',maxDistance:4});
  return bot.recipesAll(entry.id,null,table).map(recipe=>({
    yield:recipe.result.count,
    inputs:Object.fromEntries(recipe.delta.filter(x=>x.count<0).map(x=>[bot.registry.items[x.id].name,-x.count]))
  }));
}

// A recipe-book suggestion is a one-step edit of the supplied method. It is
// derived solely from the failed step, observed inventory and vanilla recipes.
// It never runs the edit or asserts that it will work.
export function suggestions(bot,method,receipt) {
  if (receipt?.status!=='failed' || !Number.isInteger(receipt.failedStep)) return [];
  const step=method.steps[receipt.failedStep], stock=receipt.after, found=new Map();
  if (step.op!=='craft') return [];
  for (const recipe of craftRecipes(bot,step.item)) {
    for (const [item,n] of Object.entries(recipe.inputs)) {
      const shortage=n-(stock[item]||0);
      if (shortage<=0 || found.has(item)) continue;
      for (const variant of craftRecipes(bot,item)) {
        const times=Math.ceil(shortage/variant.yield);
        if (Object.entries(variant.inputs).every(([i,count])=>(stock[i]||0)>=times*count)) {
          found.set(item,{op:'craft',item,times}); break;
        }
      }
      if (!found.has(item)) {
        for (const [input,output] of smelting) {
          if (output===item && (stock[input]||0)>=shortage) {
            found.set(item,{op:'smelt',input,output:item,count:shortage}); break;
          }
        }
      }
    }
  }
  return [...found.entries()].map(([item,step])=>({item,insertBefore:receipt.failedStep,step}));
}

export function compactReceipt(r) {
  return r ? {id:r.id,key:r.key,status:r.status,failure:r.failure,failedStep:r.failedStep,verifiedOutput:r.status==='verified'?r.outputs:undefined}:null;
}

export function taskView(methods,executor,bot,stock,last) {
  const pending=TARGETS.filter(id=>!(executor.delivered[id]>=1));
  const active=methods.find(m=>m.id===pending[0]);
  if (!active) return {complete:true};
  const key=receiptKey(active,executor.context),receipt=executor.receipts.get(key);
  const edits=suggestions(bot,active,receipt);
  const availableCommands=[{tool:'verify_method',id:active.id},{tool:'use_method',id:active.id},
    ...edits.map(e=>({tool:'insert_step',id:active.id,item:e.item}))];
  return {target:active.id,undelivered:pending,deliveryChest:executor.delivered,productionStock:stock,
    procedure:active,exactReceipt:compactReceipt(receipt),recipeBookEdits:edits,availableCommands,last};
}
