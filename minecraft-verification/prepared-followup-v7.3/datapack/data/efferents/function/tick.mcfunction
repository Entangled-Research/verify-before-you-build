execute unless entity @a[name=ProfessorPickaxe] run scoreboard players set ProfessorPickaxe ev_phase 0
execute if score ProfessorPickaxe ev_phase matches 0 run scoreboard players enable ProfessorPickaxe ev_prod
execute if score ProfessorPickaxe ev_phase matches 0 if score ProfessorPickaxe ev_prod matches 1 run function efferents:production
scoreboard players enable InspectorIngot ev_case
execute if score InspectorIngot ev_case matches 1 run function efferents:test_1
execute if score InspectorIngot ev_case matches 2 run function efferents:test_2
execute if score InspectorIngot ev_case matches 3 run function efferents:test_3
execute if score InspectorIngot ev_case matches 4 run function efferents:test_4
execute if score InspectorIngot ev_case matches 5 run function efferents:test_5
execute if score InspectorIngot ev_case matches 6 run function efferents:test_6
execute if score InspectorIngot ev_case matches 7 run function efferents:test_7
execute if score InspectorIngot ev_case matches 8 run function efferents:test_8
execute if score InspectorIngot ev_case matches 9 run function efferents:test_9
execute if score InspectorIngot ev_case matches 10 run function efferents:test_10
execute if score InspectorIngot ev_case matches 11 run function efferents:test_11
execute if score InspectorIngot ev_case matches 12 run function efferents:test_12
