目前仅限原版，de战锤还没试
创建arena存档以后不要一边开着这个测试存档一边又执行创建，会卡住。开其他存档没有影响
## 安装
1.整个项目拷贝到dominons6安装目录下

2.拷贝resources下地图和mod到
%APPDATA%\Dominions6\

项目中的pretender_placeholder.2h不要动

## 基本配置
所有配置都在arena_config.json里面。
必须要配的就是:

<span style="color:#EE0000">arena.save</span> 这个是要测试的存档名称，大部分报错都是这个没配好。

<span style="color:#EE0000">arena.own_nation</span> 是己方国家，这个是读存档的源点，配错了会报错。

<span style="color:#EE0000">player.start_province enemy.start_province</span>配置文件里面是写的陆上出生，海国要改一下，不然会报错

player.provinces  player.battle_report  player.extra_units 这几个是拷贝侦察报告，战报和自定义，具体见配置文件注释。不配不会报错但是就只有debug单位了

## 运行
在dom6arena目录下输入：
python -m dom6arena.arena_build "arena_config.json"

## 配置文件说明

注释写在配置文件里了

伪神单位模板:

{"id": 3368, "magic_paths": { "F": 4, "A": 4, "W": 2, "E": 2, "S": 4, "D": 2, "N": 3, "B": 2, "H": 0 }}

读战报模板，战报是根据省份id，攻击方id，防御方id，顺序来获取的，这是有时候刺杀、仪式战斗、撞车会有同个省n多战报。seq是从上往下数，默认0:

{"province": 207, "attacker": 127, "defender": 124, "copy": "attacker", "seq": 0}

配置地图上没有的单位，模板是这个说明见配置文件注释:

{"id": 1256, "count": 1, "magic_paths": { "F": 4, "A": 4, "W": 2, "E": 2, "S": 4, "D": 2, "N": 3, "B": 2, "H": 3 }},
{"id": 211,  "count": 50, "as_commander": false}
