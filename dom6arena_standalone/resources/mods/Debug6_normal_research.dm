#modname "Debug Mod with Normal Research 1.2"
#description "This mod is intended for debugging the behaviour of Dominions 6. Unlike the other Debug mod it doesn't change the research level of anything. In addition, the mod introduces five new spells to help debug. The new spells are Super Wish, Super GoR, Super Divine Name, Contact Debug Sensei and Eyes of Debug. Non AI players also get a bunch of commanders with extremely high magic paths, including some mounted commanders for testing mounted interactions, and sites which give a large amount of gems, income, resources. Based on the Dominions 3 version by ryo_akashi.

Compatibility: Uses monster IDs 9001, 9002. This mod is only for debugging and testing purposes, but should be compatible with most other mods should you wish to use it to test them."
#version 1.2
#icon "Debug.tga"

--- version 1.2

--- debug specific spells only castable by debug sensei. Therefore not available to AI

--- Version 1.1

-- AI nations no longer get any of the debug mod income or commander benefits (but still benefit from every spell and item being researched)


---- van dude with extra stuff for mount testing

#newmonster 9002
#copystats 2342
#copyspr 2342
#clearmagic
#holy
#magicskill 0 9
#magicskill 1 9
#magicskill 2 9
#magicskill 3 9
#magicskill 4 9
#magicskill 5 9
#magicskill 6 9
#magicskill 7 9
#magicskill 8 9
#magicskill 9 9
#startage 100
#mapmove 25
#spy
#forgebonus 80
#stealthy 30
#supplybonus 999
#healer 999
#amphibian
#gcost 0
#nobadevents 100
#researchbonus 9999
#end


------
--New Monster
#newmonster 9001
#copystats 941
#copyspr 941
#hp 250
#name "Debug Sensei"
#descr "The Sensei is an almighty being, well versed in all magic. He warns you sternly to use him only for debugging the mysteries of Dominions."
#nametype 133
#clearmagic
#magicskill 0 9
#magicskill 1 9
#magicskill 2 9
#magicskill 3 9
#magicskill 4 9
#magicskill 5 9
#magicskill 6 9
#magicskill 7 9
#magicskill 8 9
#magicskill 9 9
#startage 100
#mapmove 25
#spy
#forgebonus 80
#stealthy 30
#supplybonus 999
#healer 999
#amphibian
#gcost 0
#nobadevents 100
#researchbonus 9999
#end

------
--New Spells
#newspell
#copyspell "Divine Name"
#name "Super Divine Name"
#descr "A cheaper Divine Name, costing one astral pearl."
#path 0 4
#school 0
#researchlevel 0
#pathlevel 0 1
#fatiguecost 0
#onlymnr 9001
#end

#newspell
#copyspell "Wish"
#name "Super Wish"
#descr "A cheaper Wish, costing one astral pearl."
#path 0 4
#school 0
#researchlevel 0
#pathlevel 0 1
#fatiguecost 0
#onlymnr 9001
#end

#newspell
#name "Contact Debug Sensei"
#descr "Contacts the Debug Sensei, an almighty being who is well versed in all magic."
#path 0 4
#school 0
#researchlevel 0
#pathlevel 0 1
#fatiguecost 0
#effect 10021
#damage 9001
#spec 8388608
#onlymnr 9001
#end

#newspell
#copyspell "The Eyes of God"
#name "The Eyes of Debug"
#descr "A cheaper The Eyes of God, costing nothing."
#path 0 4
#school 0
#researchlevel 0
#pathlevel 0 1
#fatiguecost 0
#onlymnr 9001
#end

#newsite
#name "OP Gem Site"
#path 1
#gems 0 100
#gems 1 100
#gems 2 100
#gems 3 100
#gems 4 100
#gems 5 100
#gems 6 100
#gems 7 100
#gems 8 100
#gold 10000
#res 10000
#rarity 5
#supply 10000
#end

#newevent
#rarity 5
#req_ai 0
#req_pregame
#req_indepok 1
#req_pop0ok
#msg "Debug Start Site [OP Gem Site]"
#notext
#nolog
#req_capital 1
#addsite -1
#nation -2
#com 9001
#com 9001
#com 9001
#com 9001
#com 9001
#com 9001
#com 9001
#com 9001
#com 9001
#end

#newevent
#rarity 5
#req_ai 0
#req_pregame
#req_indepok 1
#req_pop0ok
#msg "give mounted dudes"
#notext
#nolog
#req_capital 1
#addsite -1
#nation -2
#com 9002
#com 9002
#com 9002
#com 9002
#com 46
#com 46
#end

#newevent
#rarity 5
#req_ai 0
#req_indepok 1
#req_pop0ok
#nation -2
#msg "Give capitals candles."
#notext
#nolog
#req_capital 1
#incdom 10
#end



