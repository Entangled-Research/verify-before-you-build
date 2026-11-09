fill 24 98 -8 40 98 8 sandstone
fill 24 99 -8 40 99 8 sand
fill 24 100 -8 40 109 8 glass
fill 25 100 -7 39 108 7 air
fill 24 100 -8 24 109 -8 sand
fill 24 100 8 24 109 8 sand
fill 40 100 -8 40 109 -8 sand
fill 40 100 8 40 109 8 sand
setblock 33 100 0 crafting_table
setblock 31 100 0 furnace[facing=east]
setblock 32 100 2 chest[facing=north]
clear InspectorIngot
gamemode survival InspectorIngot
effect give InspectorIngot minecraft:resistance 100000 4 true
tp InspectorIngot 32.5 100 0.5
give InspectorIngot minecraft:oak_log 1
give InspectorIngot minecraft:cobblestone 3
give InspectorIngot minecraft:coal 1
scoreboard players set InspectorIngot ev_case 0
tellraw InspectorIngot {"text":"EV_READY:test_11"}
