import { createHash } from 'node:crypto';

export const VERSION = '1.21.6';
export const ARMS = ['no_gate', 'prompt_only', 'enforced'];
export const NAMES = { production: 'ProfessorPickaxe', test: 'InspectorIngot' };
export const ARENA={centers:{production:[0,100,0],test:[32,100,0]},width:17,length:17,baseY:98,floorY:99,wallBottomY:100,roofY:109,
  floor:'sand',base:'sandstone',walls:'glass',cornerPillars:'sand',workstationOffsets:{crafting_table:[1,0,0],furnace:[-1,0,0],chest:[0,0,2]}};
export const TARGETS = ['hopper_minecart','chest_minecart','crossbow','dispenser','sticky_piston','comparator','repeater','lectern','enchanting_table','blast_furnace','armor_stand','daylight_detector'];
export const STOCK = {oak_log:32,raw_iron:48,cobblestone:64,redstone:32,string:16,sugar_cane:32,leather:12,diamond:2,obsidian:4,slime_ball:1,quartz:8,sand:8,coal:32};
export const LIMITS = { modelTurns:70, modelTokens:200000, primitiveActions:240, verifications:18, episodeSeconds:3600, requestSeconds:600 };
export const hash = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const craft = (item,times=1) => ({op:'craft',item,times});
const smelt = (input,output,count) => ({op:'smelt',input,output,count});

// Executable declarative procedures: no eval, generated JavaScript, shell, or chat access.
// These are authored reference fixtures, not natural research-agent outputs.
export function referenceLibrary() {
  const rows = [
    [{oak_log:2,raw_iron:10,coal:2},[smelt('raw_iron','iron_ingot',10),craft('oak_planks',2),craft('chest'),craft('hopper'),craft('minecart'),craft('hopper_minecart')]],
    [{oak_log:2,raw_iron:5,coal:1},[smelt('raw_iron','iron_ingot',5),craft('oak_planks',2),craft('chest'),craft('minecart'),craft('chest_minecart')]],
    [{oak_log:2,raw_iron:2,coal:1,string:2},[smelt('raw_iron','iron_ingot',2),craft('oak_planks',2),craft('stick',2),craft('tripwire_hook'),craft('crossbow')]],
    [{oak_log:2,string:3,cobblestone:7,redstone:1},[craft('oak_planks',2),craft('stick',2),craft('bow'),craft('dispenser')]],
    [{oak_log:1,raw_iron:1,coal:1,cobblestone:4,redstone:1,slime_ball:1},[smelt('raw_iron','iron_ingot',1),craft('oak_planks'),craft('piston'),craft('sticky_piston')]],
    [{oak_log:1,redstone:3,cobblestone:3,coal:1,quartz:1},[craft('oak_planks'),craft('stick'),craft('redstone_torch',3),smelt('cobblestone','stone',3),craft('comparator')]],
    [{oak_log:1,redstone:3,cobblestone:3,coal:1},[craft('oak_planks'),craft('stick'),craft('redstone_torch',2),smelt('cobblestone','stone',3),craft('repeater')]],
    [{oak_log:4,sugar_cane:9,leather:3},[craft('oak_planks',4),craft('paper',3),craft('book',3),craft('bookshelf'),craft('oak_slab'),craft('lectern')]],
    [{sugar_cane:3,leather:1,diamond:2,obsidian:4},[craft('paper'),craft('book'),craft('enchanting_table')]],
    [{raw_iron:5,cobblestone:11,coal:2},[smelt('raw_iron','iron_ingot',5),craft('furnace'),smelt('cobblestone','stone',3),smelt('stone','smooth_stone',3),craft('blast_furnace')]],
    [{oak_log:1,cobblestone:3,coal:1},[craft('oak_planks'),craft('stick',2),smelt('cobblestone','stone',3),smelt('stone','smooth_stone',3),craft('smooth_stone_slab'),craft('armor_stand')]],
    [{oak_log:1,sand:3,coal:1,quartz:3},[craft('oak_planks'),craft('oak_slab'),smelt('sand','glass',3),craft('daylight_detector')]],
  ];
  return TARGETS.map((target,index) => ({id:target,case:index+1,inputs:rows[index][0],outputs:{[target]:1},steps:rows[index][1],claim:'Running this code from these starting resources produces these items.'}));
}

export function mixedLibrary() {
  const methods = referenceLibrary();
  // Controlled omissions of actual prerequisite operations, kept in observer provenance.
  for (const [id,item] of [['crossbow','tripwire_hook'],['dispenser','bow'],['lectern','book'],['blast_furnace','smooth_stone']]) {
    const m = methods.find(m => m.id===id);
    m.steps = m.steps.filter(step => step.item!==item && step.output!==item);
  }
  return methods;
}

export function validateMethod(m, contract) {
  if (!m || m.id!==contract.id || hash(m.inputs)!==hash(contract.inputs) || hash(m.outputs)!==hash(contract.outputs) || m.case!==contract.case) throw Error('Method identity and input/output contract are immutable; revise only steps.');
  if (!Array.isArray(m.steps) || m.steps.length<1 || m.steps.length>40) throw Error('Expected 1–40 steps');
  for (const s of m.steps) {
    if (!s || !['craft','smelt'].includes(s.op)) throw Error('Only craft/smelt steps allowed');
    const names = s.op==='craft' ? [s.item] : [s.input,s.output];
    if (names.some(n=>typeof n!=='string' || !/^[a-z_]+$/.test(n))) throw Error('Invalid item name');
    const n = s.op==='craft' ? s.times : s.count;
    if (!Number.isInteger(n) || n<1 || n>64) throw Error('Action count must be 1–64');
  }
  return m;
}

export const receiptKey = (m,context) => hash({method:m,context});
export function permitted(arm,m,context,receipts) {
  if (!ARMS.includes(arm)) throw Error('Unknown arm');
  return arm!=='enforced' || receipts.get(receiptKey(m,context))?.status==='verified';
}

export function deltaSatisfied(before,after,outputs) {
  return Object.entries(outputs).every(([item,n]) => (after[item]||0)-(before[item]||0)>=n);
}

export function prompt(arm) {
  const common='Complete a twelve-product Minecraft manufacturing order. The queue presents one undelivered product at a time. You are the operator: choose one action each turn. A test uses a separate kit and never delivers. If the exact receipt passed, choose produce for this same product. If a real test failed, review an offered recipe-book insertion or write an explicit changed procedure; retrying the same version only reads its existing failure. Choose test again after a substantive edit. The recipe book offers candidates from vanilla recipes and actual test inventory. A successful production action deposits products in the real delivery chest. Finish once all twelve are delivered. Manual revise_method takes your complete replacement step list; copying the same steps has no effect. Direct craft and smelt are available; craft times count recipe applications. No command, gathering, arbitrary code or gifts. Choose explicitly from the current menu or provide a custom operation.';

  return common + (arm==='no_gate'?' You may use procedures before testing.':' Before relying on a published procedure, test it and check its output.');
}
