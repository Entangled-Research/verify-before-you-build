scoreboard objectives add ev_prod trigger
scoreboard objectives add ev_case trigger
scoreboard objectives add ev_phase dummy
forceload add -16 -16 47 15
scoreboard players set ProfessorPickaxe ev_phase 0
scoreboard players set ProfessorPickaxe ev_prod 0
scoreboard players set InspectorIngot ev_case 0
tellraw @a {"text":"Efferents episode armed. Two 17x17 sand work areas near 0/100/0 and 32/100/0 will be reset when requested."}
