目前仅限原版，de战锤还没试。目前仅支撑Windows

创建arena存档以后不要一边开着这个测试存档一边又执行创建，会卡住。开其他存档没有影响。

如果战报双方都不是己方，只能拷贝一方，无法选择拷贝双方单位。

## 安装
1.把dom6arena_standalone目录拷贝到dominons6安装目录下

2.分别拷贝resources下的map和mod到 %APPDATA%\Dominions6\  对应map和mod

项目中的pretender_placeholder.2h不要动

3.[下载 Dom6Arena.exe](/dom6arena_standalone/dist/Dom6Arena.exe?raw=true)

放在dominonions6根目录双击运行


## 从配置文件启动


windows控制台进入到dom6arena_standalone目录中

启动gui：

python -m dom6arena.arena_gui

从配置文件启动

python -m dom6arena.arena_build "arena_config.json"

注意：复制省份的输入框可以输入多个省份id，要用英文逗号分开。如果省份有战斗，控制台会有互动，用户要根据提示选择。



## 参数说明

所有配置都在arena_config.json里面，界面配置好以后也是保存在配置文件中。


player.extra_units 这个是添加自定义单位，具体见配置文件注释。默认不用配。


<span style="color:#EE0000">arena.save</span> 这个是要测试的存档名称。


<span style="color:#EE0000">arena.own_nation</span> 是己方国家，这个是读存档的源点，配错了会报错。


<span style="color:#EE0000">player.start_province enemy.start_province</span>配置文件里面是写的陆上出生，测海国要改一下出生省份到水省，不然会报错。具体见配置文件注释。


player.provinces 这个是拷贝省份兵力，敌人就是从侦察报告，如果有战斗需要在控制台选，可以精确复制战斗一方的单位、装备、宝石、脚本；复制要选战前还是战后；可以复制双方单位用于复盘；控制台互动时如果选择跳过战报（如刺杀战败）则拷贝当前兵力或侦察报告。该参数不配不会报错但是就只有debug单位了


## 配置模板

伪神单位模板，有时候敌人的神无法从当前存档复制，为了测试要手动配一下:

{"id": 3368, "magic_paths": { "F": 4, "A": 4, "W": 2, "E": 2, "S": 4, "D": 2, "N": 3, "B": 2, "H": 0 }}


配置地图上没有的单位，模板是这个说明见配置文件注释:

{"id": 1256, "count": 1, "magic_paths": { "F": 4, "A": 4, "W": 2, "E": 2, "S": 4, "D": 2, "N": 3, "B": 2, "H": 3 }},
{"id": 211,  "count": 50, "as_commander": false}



## 注意事项

拷贝敌方侦察报告是不精确的，只有开荒阶段使用侦察报告测试才有价值。对付人类玩家尽可能的通过拷贝战报来测试。

不要等到首都被压几回合后才想到测试，敌人一出现就要测试，有可能的话每开一块地前都测一下。
