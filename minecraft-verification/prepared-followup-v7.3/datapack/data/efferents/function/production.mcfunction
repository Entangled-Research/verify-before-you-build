fill -8 98 -8 8 98 8 sandstone
fill -8 99 -8 8 99 8 sand
fill -8 100 -8 8 109 8 glass
fill -7 100 -7 7 108 7 air
fill -8 100 -8 -8 109 -8 sand
fill -8 100 8 -8 109 8 sand
fill 8 100 -8 8 109 -8 sand
fill 8 100 8 8 109 8 sand
setblock 1 100 0 crafting_table
setblock -1 100 0 furnace[facing=east]
setblock 0 100 2 chest[facing=north]
clear ProfessorPickaxe
gamemode survival ProfessorPickaxe
effect give ProfessorPickaxe minecraft:resistance 100000 4 true
tp ProfessorPickaxe 0.5 100 0.5
give ProfessorPickaxe minecraft:oak_log 32
give ProfessorPickaxe minecraft:raw_iron 48
give ProfessorPickaxe minecraft:cobblestone 64
give ProfessorPickaxe minecraft:redstone 32
give ProfessorPickaxe minecraft:string 16
give ProfessorPickaxe minecraft:sugar_cane 32
give ProfessorPickaxe minecraft:leather 12
give ProfessorPickaxe minecraft:diamond 2
give ProfessorPickaxe minecraft:obsidian 4
give ProfessorPickaxe minecraft:slime_ball 1
give ProfessorPickaxe minecraft:quartz 8
give ProfessorPickaxe minecraft:sand 8
give ProfessorPickaxe minecraft:coal 32
scoreboard players set ProfessorPickaxe ev_prod 0
scoreboard players set ProfessorPickaxe ev_phase 1
tellraw ProfessorPickaxe {"text":"EV_READY:production"}
