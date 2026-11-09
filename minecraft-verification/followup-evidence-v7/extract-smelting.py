"""Generate the local vanilla furnace map including nested item tag ingredients."""
import json, pathlib, zipfile, sys
jar=pathlib.Path.home()/'Library/Application Support/minecraft/versions/1.21.6/1.21.6.jar'
target=pathlib.Path(sys.argv[1])
with zipfile.ZipFile(jar) as z:
 def expand(ingredient,visited=()):
  if isinstance(ingredient,list):return [x for v in ingredient for x in expand(v,visited)]
  if ingredient.startswith('#minecraft:'):
   name=ingredient.removeprefix('#minecraft:')
   if name in visited:raise RuntimeError('cycle '+name)
   values=json.loads(z.read('data/minecraft/tags/item/'+name+'.json'))['values']
   return [x for v in values for x in expand(v,(*visited,name))]
  if not ingredient.startswith('minecraft:'):raise RuntimeError(ingredient)
  return [ingredient.split(':')[-1]]
 rs=set()
 for name in z.namelist():
  if not name.startswith('data/minecraft/recipe/') or not name.endswith('.json'):continue
  recipe=json.loads(z.read(name))
  if recipe.get('type')!='minecraft:smelting':continue
  for item in expand(recipe['ingredient']):
   rs.add((item,recipe['result']['id'].split(':')[-1]))
mapping=dict(sorted(rs))
for item,want in {'raw_iron':'iron_ingot','cobblestone':'stone','stone':'smooth_stone','sand':'glass','red_sand':'glass'}.items():
 assert mapping.get(item)==want,(item,mapping.get(item))
assert len(mapping)==len(rs),'ambiguous vanilla output for one input'
target.write_text('// Minecraft Java 1.21.6 furnace recipes from the installed jar, including expanded vanilla item tags.\nexport const smelting = new Map('+json.dumps(sorted(rs),indent=2)+');\n')
