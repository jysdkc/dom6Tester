#modname "One Age 1.5"
#description "A simple mod which puts all vanilla nations into the Middle Age so they can play together. Each nation is identified as being from its original era and should have a recognisably distinct flag and appropriate fort technology.
Originally compiled by Zonk, then given vulgar nation tags by your homeboy jBrereton, updated for dom6 by Sombre

Compatibility: Should be compatible with all other mods, provided they do not interfere with the IDs of base game nations. Will not change the age of any mod nation."
#icon "./oneage.tga"

#version 1.5



--Changelog:

--version 1.5
-- LA Zemaitia added

--Version 1.4
-- EA Kailasa forts now early era
-- 

--Version 1.3
-- added LA Pyrene
-- fixed forts for some LA nations

--Version 1.2
-- fixed Andramania descriptions

--Version 1.1
-- added compatibility statement to description

--Version 1.00

-- started the process of reviewing and updating nation descriptions, especially the magic sections

-- nation numbers updated
-- added all new nations
-- ea and ma pyrene flags are distinct enough, checked

-- need to check all descriptions
-- all ea descriptions checked
-- all ma descriptions checked
-- all la descriptions checked


--On flags:
--flag border color can be altered with #secondarycolor to differentiate flags

--flag overlaps are:
-- EA Yomi, MA Shinuyama, and LA Jomon
-- EA Pelagia and MA Pelagia
-- EA Vanheim, MA Vanheim, and LA Midgard
-- EA Xibalba and LA Xibalba
-- EA Arcoscephale, MA Arcoscephale, LA Arcoscephale

--close flags are:
-- MA R'lyeh and LA R'lyeh
-- MA Jotunheim and LA Utgard
-- MA T'ien Ch'i and LA T'ien Ch'i

--this list may not be complete

--EA Yomi
#selectnation 23
#secondarycolor 1 0.5 0
#end

--MA Shinuyama
#selectnation 70
#secondarycolor 0 0 0.25
#end

--LA Jomon
#selectnation 110
--not changing its color
#end

--EA Pelagia
#selectnation 40
--not changing its color
#end

--MA Pelagia
#selectnation 86
#secondarycolor 0.75 0.5 0.25
#end

--EA Vanheim
#selectnation 20
#secondarycolor 0.3 0.75 0.75
#end

--MA Vanheim
#selectnation 78
#secondarycolor 0.8 0.8 0.8
#end

--LA Midgard
#selectnation 115
#secondarycolor 0.3 0.1 0
#end

--EA Xibalba
#selectnation 26
--not changing its color
#end

--LA Xibalba
#selectnation 112
#secondarycolor 0.8 0.5 0.5
#end

--EA Arcoscephale
#selectnation 5
--not changing its color
#end

--MA Arcoscephale
#selectnation 50
#secondarycolor 0.5 0.5 0.3
#end

--LA Arcoscephale
#selectnation 95
#secondarycolor 0.5 0.5 0.8
#end

#selectnation 5
#name "EA Arcoscephale" -- checked
#era 2
#brief "An ancient human kingdom led by Philosophers, Arcoscephale mainly uses heavy infantry, chariots and flying Icarids. The Philosophers are skilled researchers. Oreiads, roaming mountain spirits, and Mystics skilled in Astral and Elemental magic give Arcoscephale great magical versatility. The priestesses of Arcoscephale can heal wounded soldiers."
#descr "The kingdom of Arcoscephale is yet to be founded and in its place is a loose collection of city states. Bronze is more common than iron and hoplites have yet to see the light of day. Instead, myrmidons and chariots compose the core of the armies. In this time, slaves are commonly used and most free men have plenty of time to spend on fine arts and good living. Philosophers gather in the cities to discuss esoteric truths and engineers manufacture clever contraptions for civil or military use. At the heart of Arcoscephale lies Mount Cephalos, abode of the Awakening God. At the foot of the mountain is a great temple where sacred Pegasus Riders are trained. Icarids, men with mechanical wings, are also used in warfare. The philosophers are better at magical research in a slothful Dominion."
#summary "Race: Humans
Military: Heavy infantry, chariots, flying infantry, sacred Pegasus Riders, engineers
Magic: Nature, Astral, Elements. Philosopher researchers
Priests: Weak, healing. Sceptic preachers (reduces Dominion)
Dominion: Scry (accurate and automatic military reports inside dominion)"
#fortera 1
#end

#selectnation 8
#name "EA Ermor" -- checked
#era 2
#brief "Ermor is a human empire centered around a great city. The Empire has just recently converted to the New Faith and its magical skills are very versatile as mage-priests from the Old Faith still linger."
#descr "Ermor is an empire centered around a great city. For centuries it has grown and become more and more influential. Traders and travelers from near and far come to the city. By military campaigns, diplomacy and trade, Ermor has become a power to be reckoned with. By adopting local traditions and beliefs, the Ermorians posed little threat to neighbors and conquered peoples, but this has begun to change. A New God is arising. Old syncretistic faiths and spirit worship were banned by a Prophet dressed in white shrouds. The remnants of his body and shrouds are buried in the Holy City of Eldregate where the adherents of the New Faith are awaiting the arrival of the Reawakening God foreseen by the Prophet. The all-encompassing old state cult of the Numinas still survives, but the Pontifices and Flamen are slowly adopting the New Faith."
#summary "Race: Human.
Military: Human legionnaires and lizard auxiliaries.
Magic: Fire, Death, Astral, some Water, Earth, Air and Nature.
Priests: Powerful, can heal afflictions."
#end

#selectnation 13 -- checked
#name "EA Ulm"
#era 2
#brief "Ulm is a nation with a barbarian legacy. They are strong and proud and worship steel and spirits of the wild. The warriors of Ulm are stealthy and well versed in the ways of the wild. The warrior smiths are masters of magical forging."
#descr "Ulm is a land of cold mountains and dense forests. These wild lands were settled by proud and fierce barbarians in ages past. Their ancestry has made the inhabitants of the forests stronger and more resilient to the cold climate than ordinary men. Upon becoming men, youngsters are given a single knife and left in the forest at first snowfall. Those who survive the winter are allowed to return to their family.
The barbarians of Ulm live in small settlements ruled by chieftains and warrior smiths who search for the Enigma of Steel. Steel is a sacred metal and its maker is as well. Smithing has become the equivalent of making a sacrifice to the Lord and no other culture has developed such skill in forging magical items.
Horses are rare and those who use them in warfare are held in contempt. Sneak attacks, on the other hand, are common, and many warriors use stealth to engage opponents in hand-to-hand combat."
#summary "Race: Barbarians, partial cold resistance, prefers Cold scale +1.
Military: Strong medium infantry, stealthy infantry
Magic: Earth, Nature, Fire, Air, Water, some Death, superior magic item forging
Priests: Weak"
#fortera 1
#end

#selectnation 14
#name "EA Pyrène" --
#era 2
#brief "Pyrène is a cavern kingdom. It is mostly populated by Bekrydes, primitive humans, but they have allied themselves with giants of the wilderness above their caves. The mightiest of these giants are skilled in magic and have taught the Bekrydes how to farm and craft metal."
#descr "Pyrène is a realm of sprawling caverns beneath a densely forested mountain range. Here the Bekrydes, cave dwelling humans, have formed a kingdom. The Bekrydes live troglopastoral lives, herding Cave Cows and Blind Goats through their vast caverns in search of mushroom meadhows and muck fields filled with nutritious mineral. With the aid of ancient giants skilled in crafting and frarming the Bekrydes have spread to the mountains and forests surrounding their cavernous realm. The Bekrydes are primitive by most standards, but with the guidance of the Basajaunak and the Jentilak, they have lerned how the craft metal and now the Bekrydes field small groups of elite warriors with metal armaments.
In the mountains above the Pyrène caverns lies mount Anboto, where the Sorginak gathers. These servants of a primordial storm deity have been allies of the Jentilak since time immemorial. Now they aid the Bekryde kings as a favor to the Jentilak.
In the mounts also live the Tartalo, sheep herding cyclopses of limited mental faculties."
#summary "Race: Cave-dwelling humans and various giants.
Economics: Extra gold and resources in cave forts.
Military: Humans and giant infantry, boulder throwing giants.
Magic: Earth, Air, some Nature and Water.
Priests: Weak"
#fortera 1
#end

#selectnation 12
#name "EA Marverni" -- checked
#era 2
#brief "Marverni is a nation of tribal chiefdoms led by Druids, powerful readers of the stars and the Earth. Most warriors fight bare-chested, but noble warriors use chainmail armor."
#descr "Marverni is a nation of tribal chiefdoms guided by Druids and religious magistrates. The tribes have a long history of war and infighting, but recent developments have joined the tribes in pursuit of a single goal. The most prominent tribes are the Marverni, the Ambibates, the Eponi and the Carnutes. The Sequani, though a small tribe, are influential due to the large number of Druids among them. The smiths of the Marverni tribe are reputedly the inventors of chainmail and most nobles of the tribes use it. Lowborn warriors fight bare-chested. The Ambibates are known for their martial skills. The Eponi nobles fight on horseback and are the only cavalry available to the nation. The Carnute tribe guards the Sacred Forest of Carnutes where the Druids gather every year. The Carnute warriors are able to go berserk when wounded. Boars are a sacred symbol to the Marverni nation."
#summary "Race: Humans.
Military: Light and medium infantry, medium cavalry.
Magic: Earth, Astral, Nature, Water
Priests: Medium, can perform blood sacrifices"
#fortera 1
#end

#selectnation 9
#name "EA Sauromatia" -- checked
#era 2
#brief "Sauromatia is a tribal nation ruled by women. Swift raiders and lancers form the backbone of the armies. Amazon warriors and Androphags are the sacred elites of the Sauromatians. Witch Kings, masters of dark sorcery, rule the Androphag tribe. Hydras from the Pythian Marsh are tamed and used in warfare."
#descr "Sauromatia is a nation of nomadic warrior tribes ruled by women. Men and women fight side by side and all prominent tribes are ruled by warrior queens. This is a legacy of the Sauromatians merging with the Amazon tribes in times past. The Amazons leaders were not accepted, because they were not warriors, but they influenced the Sauromatians and women warriors gained power and prestige. Only the tribe of the Androphags has totally rejected the notion of female leadership. The Androphags are ruled by ancient Witch Kings who introduced cannibalism and man-flaying to the Sauromatians. The Androphags also use hydras from the Marshes of Pythia in warfare."
#summary "Military: Light and medium cavalry, serpent riders, lizard riders, hydras
Magic: Death, Nature, Blood, some Astral and Water
Priests: Weak, can perform blood sacrifices"
#fortera 1
#end

#selectnation 22
#name "EA T'ien Ch'i" -- checked
#era 2
#brief "T'ien Ch'i is an emerging empire. Masters of the Five Elements and Celestial Masters are versatile mages. The nobles partake personally in battles and their chariots form an important part of the army. Sacred Celestial Beings and the sacred Warriors of the Five Elements form the elite core of the armies."
#descr "The Celestial Empire has not yet been founded. The magic of The Way permeates the realm and reclusive mages conjure Celestial Beings to do their bidding. Nobles wage war upon each other for honor and glory. A few chosen warriors and mages dedicate their lives to training in the Way of the Five Elements. The deceased are worshipped and village priests conjure the dead to ask for guidance and aid. It is a time of legends."
#summary "Race: Humans
Military: Versatile and well-equipped with large shields and iron armaments. Noble chariots.
Magic: Water, Astral, Air, Fire, Nature, Glamour, Earth and some Death, Summon Celestial Beings
Priests: Average"
#fortera 1
#end

#selectnation 28
#name "EA Machaka" --
#era 2
#brief "A human kingdom ruled by a royal family of great men. Machaka uses many different animals for warfare and has light to medium infantry as well as archers. Priests and Witch doctors from various clans give Machaka a wide range of magical skills. Machakans dislike cold lands."
#descr "Machaka is an old sacral kingdom divided into totemic clans. The clans follow their totemic spirits and worship them as bringers of civilization and tell myths about their interactions with men. For centuries the Lion Clan has dominated the others and formed a unified kingdom under their wise rule. The Lion Clan is blessed by Lion and are superior to other men. The Great Men of Mababwe, called 'Colossi' by Arcoscephalean historians, have ruled the plains since Hyena was coerced to teach metalworking to men and Rhino was defeated by spears longer than his. From Great Mababwe, the semi-divine Colossi of the Lion Clan rule their lesser kin as sacred Kings and Queens. There are many totemic clans, but some have been more influential. Hyena, Rhino, Elephant and Spider all serve Lion with their totemic masters' skills and guidance. Recent contact with Berytos and other nations has seen the rise of ambition among the Colossi royalty and the Lion Kings are preparing for the Awakening of Lion. Machakans prefer hot lands."
#summary "Race: Humans and Colossi, prefers Heat scale +2
Military: Infantry, poison archers, spider riders, war lions, elephants
Magic: Fire, Earth, Death, Nature, Glamour
Priests: Average"
#fortera 1
#end

#selectnation 25
#name "EA Mictlan" -- checked
#era 2
#brief "Mictlan is an old kingdom ruled by priest-kings. Their God hungers and must be sated with blood sacrifice. Mictlan has powerful blood mages and priests, but its infantry uses archaic weapons."
#descr "Mictlan is an ancient tribal empire that has been isolated for centuries. The foul practices of the priest-kings of Mictlan have caused most neighbors to leave or face slavery or death by sacrifice. Since the dawn of the kingdom, blood has been spilled in the temples of the capital to feed the waning powers of the Hungry God. The armies are mainly composed of slaves from newly conquered lands. The mage-priests of Mictlan celebrate the two Faces and the two Dominions of the Hungry God, namely the Sun and the Moon, the Rain and the Forest. They are all skilled blood mages."
#summary "Race: Humans, prefers Heat scale +1
Military: Light infantry with slings and javelins, tribal kings can levy slaves, sacred Jaguar and Eagle Warriors
Magic: Blood, Fire, Astral, Nature, Water
Priests: Powerful, can perform blood sacrifices, Dominion does not spread unless blood is sacrificed"
#fortera 0
#end

#selectnation 16
#name "EA Abysia" -- checked
#era 2
#brief "Abysians are lava-born humanoids that radiate heat. Abysians mainly use heavy infantry. They have skilled Fire and Blood mages and their priests can perform blood sacrifices. Abysians dislike cold provinces."
#descr "Abysia is a hot wasteland, at the center of which lies a great volcano whose lava-lit caverns are inhabited by magma-born humanoids. Their flesh radiates heat and they are not harmed by flames. Abysians are stronger than humans and use very heavy armor and weaponry. Bows are not used, because they would burn to cinders in the glowing hands of the Abysians. The war machine of Abysia also includes Salamanders, lizardlike beings composed of the same hot lava-born flesh as the Abysians. The Anointed of Rhuax and the Anathemant Priests of the Flame Cult practice blood sacrifice to strengthen the power of the Awakening God. The Warlocks of the Smouldercone, a newly formed magical order, practice Blood magic and search for suitable blood slaves in conquered lands. Abysians prefer to live in extremely hot places. They do not farm or hunt for a living, so their income and supplies are not affected by the Growth or Death scale of a province. However, population will still die slowly in Abysia-controlled provinces with Death scales."
#summary "Race: Radiates heat, fire resistance, prefers Heat scale +3, wasteland survival. Death and Growth scales have half the standard effect on income and population growth and no effect on supplies. Extra gold and resources in cave forts.
Military: Very heavy infantry, no missile weapons, salamanders
Magic: Fire, Blood, Astral, some Earth
Priests: Powerful, can perform blood sacrifices"
#fortera 1
#end

#selectnation 24
#name "EA Caelum" -- checked
#era 2
#brief "Caelum is a union of three tribes of winged beings that live on high mountaintops. One tribe is fully immune to cold and another tribe is cold and lightning resistant. All mages of Caelum are skilled in Air magic and some also have some skill in Water and Death. All of Caelum dislikes warm lands."
#descr "Caelum is a magocracy of winged humanoids who inhabit the highest mountain peaks. They are the offspring of the Yazatas, semi-divine beings of an earlier age. Three tribes served the Yazatas in ancient times, the Kavi, the Airyas and the Mairyas. But some were led astray by the wicked Mainyus and Daevas. With the corruption of the purifying flame the Daevas as well as the Yazatas were banished from this world. With the disappearance of the Yazatas the three tribes were dispersed and fled their homelands. But when some Yazatas reemerged from hiding, the three tribes gathered and settled in the high mountain range where the last of the Eagle Kings resided. The former tribes are now known as the Tempest Clan of Spire Horn Mountain, the Raptor Clan of Raven's Vale and the Airyas of High Caelum. The Spire Horn Caelians are partially resistant to cold and lightning. The Raptorians are stronger and attuned to the Earth, but lack the elemental resistance characteristic of the other clans. The Airya once lived in the land of the White Forest where winter lasts for ten months. They still live in the coldest mountain peaks and are unaffected by low temperatures. Their priestesses try to purify the taint of the daevas and are keepers of the sacred flame of the White Forest. The Airya Seraphs craft magical ice that the many Caelians use instead of regular metal. The ice tempers with lower temperatures and the heavy ice armor is more durable in cold climates than in warmer ones. All weapons crafted from the ice are magical and capable of harming magical beings. The Caelians are skilled archers and prefer hit-and-run tactics, even though they do have some heavy troops, such as huge Mammoths."
#summary "Race: Flying, partially cold resistant, partially shock resistant, prefers Cold scale +2
Military: Flying units, skilled archers, mammoths
Magic: Air, some Water, Earth, Death and Fire
Priests: Average, Guardian Spirits."
#fortera 1
#end

#selectnation 27
#name "EA C'tis" --
#era 2
#brief "C'tis is an ancient kingdom of lizardmen. They do not use cavalry or archers, but use chariots and javelins instead. C'tis has powerful Death mages and powerful Lizard King priests. The lizards dislike cold provinces."
#descr "C'tis is a swampy river valley surrounded by sandy deserts. In the fertile valley a sacral kingdom of lizardlike humanoids has formed. The kingdom is ancient by human standards and its wisdom and magical knowledge are great. At the top of the society are the Lizard King and his Royal Heirs. The King is the highest priest of C'tis. Under the king are the High Priests with their sacred serpents and the enigmatic Sauromancers, great mages of death and rebirth. The lizards are herbivores, but have enslaved a race of carnivorous lizardmen who serve as soldiers and workers. The C'tissians are somewhat slow in movement, but have thick hides that protect them from cuts and bruises. Both lizard races are cold-blooded and become exhausted very quickly when fighting in cold provinces. They have partial resistance to poison. The inhabitants of C'tis prefer to live in warm provinces."
#summary "Race: Thick hides, cold-blooded, poison resistance, prefers Heat scale +2
Military: Chariots, infantry, slave warriors, sacred serpents
Magic: Death, Nature, some Water and Astral
Priests: Powerful"
#fortera 1
#end

#selectnation 7
#name "EA Pangaea" -- checked
#era 2
#brief "Pangaea is a woodland realm of wild halfmen. Pangaea has stealthy satyrs, flying harpies, strong centaurs, and raging minotaur warriors. The Panii are powerful mages of Nature and Earth and are able to lure women into the wild."
#descr "Pangaea is a woodland nation inhabited by wild beings connected with nature. Halfmen such as satyrs, centaurs and minotaurs serve the lords of the Sacred Groves deep in the forests. Expansion by the civilized nations has forced the beasts of Pangaea to arm themselves with man-made weapons. Minotaurs wield huge battleaxes and centaurs are trained to use spears and longbows. The magic of the Panii lures women into the forests where they turn wild and shed all their clothing. These women are called Maenads and are turned loose to fight humans with their bare hands and teeth."
#summary "Race: Forest beings, stealthy troops, troops will heal battle afflictions
Military: Satyr and minotaur infantry, centaur archers and warriors
Magic: Magical Tunes, Nature, Earth, Glamour, Blood, some Water. Can conjure Bramble Forts.
Priests: Average, can perform blood sacrifices"
#end

#selectnation 15
#name "EA Agartha" -- checked
#era 2
#brief "A cavern realm of Pale Ones and troglodytes. Pale Ones can grow to huge proportions. Oracles and Earth-Blood mage-kings rule the Pale Ones. All Pale Ones have perfect night vision."
#descr "In dark caverns under the Roots of the Earth a strange kind of one-eyed humanoids has evolved. Untouched by the sun, they have become known to humans as the Pale Ones. The Pale Ones are gifted with perfect darkvision and gills and inhabit underwater rivers and lakes as well as cavernous halls. Pale Ones never stop growing and ancient ones can grow to huge proportions. The wisest of the Ancient Ones are known as the Oracles, priest-mages of great power. The Oracles are gathered in a great, cavernous hall where they divine the fate of the Pale Ones."
#summary "Race: Pale Ones and troglodytes. Darkvision. Poor amphibians. Extra gold and resources in cave forts.
Military: Light infantry, medium infantry, Wet Ones, huge and sacred Ancient Ones.
Magic: Earth, Fire, Water, Death.
Priests: Powerful"
#fortera 1
#end

#selectnation 11
#name "EA Tir na n'Og" -- checked
#era 2
#brief "Tir na n'Og is a blessed isle ruled by a magical race known as Tuatha and their Sidhe descendants. Fir Bolg, lesser descendants of the Nemedians, compose much of the population. The Sidhe and Tuatha are able to weave illusions to hide their true appearance."
#descr "Tir na n'Og is a blessed isle surrounded by whispering mists. It is the home of the Tuatha, a highly magical race descended from the Nemedians who once warred with the Fomorians. The Tuatha have made themselves lords and masters over the Fir Bolg, a lesser race descended from the same Nemedian ancestors. With the aid of the Fir Bolg, the Tuatha attacked the Fomorian giants and almost succeeded where the Nemedians failed, but eventually the Fomorians proved too powerful and the Tuatha were driven back to their Blessed Isle. The Tuatha and their Sidhe descendants have turned to crafts, poetry and magical arts, but some have chosen the path of war and have become warriors and generals of great renown. The Fir Bolg, inferior to the Tuatha, but still far superior to ordinary men, compose much of the population and serve as farmers and lowly warriors."
#summary "Race: Tuatha, Sidhe, Fir Bolg, illusions
Military: Fir Bolg infantry, Sidhe infantry, sacred Tuatha warriors
Magic: Glamour, Nature, Water, some Air and Earth
Priests: Average"
#fortera 1
#end

#selectnation 10
#name "EA Fomoria" -- checked
#era 2
#brief "Fomoria is a bountiful land inhabited by malformed giants. The land was attacked by wave after wave of invaders. Of these, the Fir Bolg, lesser descendants of the Nemedians, have established themselves and live in peace with the Fomorians. A few of the magically powerful Nemedians also linger, defeated remnants of an invading people now subject to their old enemies."
#descr "The bountiful land of Fomoria was claimed by giants who once guarded the dark and stormy ocean realm of the drowned dead. With death ever near, their loyalties had changed and their malice grown. With the ascendancy of a previous Pantokrator, they were punished for their sins and banished from their dark home. The full effects of the Curse became evident when the Fomorians settled in a fertile land. Their offspring were short and cursed with monstrous appearance. The few surviving Fomorian giants saw their once proud race degenerate and die. Then came the Invasions. Partholonians, Nemedians, Fir Bolg and Tuatha all claimed the land of Fomoria. Twice the Fomorians were all but defeated by foreign magic, but twice they conjured a plague that slew the invaders. The third wave of invaders, the Fir Bolg, accepted Fomorian rule and aided the giants in defeating the Tuatha. Now Fir Bolg compose much of the Fomorian population. Fomorians are skilled shipwrights, powerful storm crafters and have a legacy of mastery over the dead."
#summary "Race: Malformed Fomorian giants, Fir Bolg, remnant Nemedians. Ocean sailing and units able to enter the sea.
Military: Fir Bolg infantry, Fomorian infantry, Nemedian infantry
Magic: Air, Glamour, Death, some Water and Nature
Priests: Mostly weak, Fomorian King of average skill"
#fortera 1
#end

#selectnation 30
#name "EA Vanheim" -- 
#era 2
#brief "Vanheim is a nation ruled by Vanir, ancient enemies of the Jotun giants. Vanir can sail across the oceans and hide themselves with illusions. They mostly use infantry and sacred berserkers. Their Dwarven smiths are powerful Earth mages."
#descr "Vanheim is a land of misty moors and bitter forests inhabited by a tall and innately magical race known as the Vanir. The Vanir are mortal enemies of the giants of Jotunheim and since the beginning of time they have waged a great war upon each other. They are masters of illusions and are able to trick mortals with their glamour. In halls under the mountains of Vanheim live Dwarves, smiths capable of crafting fabulous items. Vanheim is a land of magic and even the horses are enchanted and exceptionally fast.
Vanir are skilled shipwrights and navigators and can sail the oceans. Lesser beings are not held in high regard and their blood is sacrificed to sate the Awakening God."
#summary "Race: Ocean sailing, trace income across oceans, illusions, prefers Cold scale +1
Military: Vanir
Magic: Air, Glamour, Earth, Blood, some Fire and Death
Priests: Average, can perform blood sacrifices"
#fortera 1
#end

#selectnation 31
#name "EA Helheim" --
#era 2
#brief "Helheim is a nation of Vanir ruled by Hanged Kings guarding the entrance to Hel. Vanir can hide themselves with illusions. They utilize many unique troops, including flying Valkyries. The Hangadrotts are powerful Death and Air mages and the Svartalf smiths are skilled in Earth and Death magic."
#descr "Helheim is a land of shadows, windswept moors and silent mountains. Here lies Gnipahålan, the Stone Cave, where the dead pass through on their way to Hel. The Hanged Kings, ancient Vanir who have hanged themselves to learn the secrets of Death, rule the land from their thrones in Helhalla. Helheim is inhabited by Vanir, a race of tall and innately magical beings who are able to trick mortals with their glamour. The Vanir of Helheim have sequestered themselves from the Vanir of Vanheim and have not been part of the great war with the giants. For ages they have been guiding the dead on their way to Hel in service of a dead god. Now a new God is arising and the old ways are changing. The Valkyries, guides of the dead, have become messengers of death and sacred warriors of the new God. Valkyries, the female Vanir of Helheim, are able to fly, a gift from the dead god they once served. Lesser beings are not held in high regard and their blood is sacrificed to sate the Awakening God. Unlike their cousins in Vanheim, the Vanir of Helheim are not shipwrights and sailors."
#summary "Race: Flying troops, illusions, prefers Cold scale +1
Military: Vanir heavy infantry, Valkyries, Vanir cavalry
Magic: Death, Glamour, Air, Earth, some Fire
Priests: Average."
#fortera 1
#end

#selectnation 33
#name "EA Niefelheim" --
#era 2
#brief "Niefelheim is a frozen realm and the home of the Niefel Giants, descendants of the Rimtursar. Giants are immune to the cold and dislike hot lands. Their mages are versatile and powerful sorcerers."
#descr "Niefelheim, the Land of Eternal Frost, was once the home of the frost giants. The Rimtursar, ancient giants who possessed godlike powers, were the undisputed rulers of the world. The giants of Jotunheim are the descendants of the Rimtursar. From the cold glaciers in Niefelheim, frost giants have emerged anew. These Niefel Giants are not nearly as powerful as their ancestors, but they are stronger by far than the giants of later ages. Giants are immensely strong and resilient, but their size makes them easy targets. They are born in the cold and do not suffer from cold climates. Niefelheim is ruled by several Jarls who rarely join forces. Gygjas, old and wicked hags, serve the Niefel giants with sorcerous advice. The people of Niefelheim prefer to live in very cold provinces. The icy winds of Niefelheim cause the cold climate to expand beyond the Dominion of the Pretender God."
#summary "Race: Cold resistant, prefers Cold scale +3
Military: Niefel Giants, giant infantry and skinshifters
Magic: Water, Blood, Death, Glamour, Nature, Astral
Priests: Average"
#fortera 1
#end

#selectnation 34
#name "EA Muspelheim" --
#era 2
#brief "Muspelheim is a valley of fire and ash surrounded by frozen lands. It is the home of the Muspel Giants, sprung from primordial fires. The Muspel Giants are impervious to fire and radiate heat, but the giants of the surrounding lands, who comprise most of the population, are cold resistant and dislike hot lands."
#descr "Far away in the frozen lands of the jotuns lies a vast valley of fire and ash. This is Museplheim, a gloomy land lit by streams of lava. The acrid air is thick with soot and flowing embers, and the skies are dark and covered in clouds of smoke and sulfur. From the fires of Muspelheim primordial giants once emerged and now their descendants make the valley of fire and ash their home.
The muspel giants have allied themselves with jotuns of the surrounding lands and most of the population is of jotun stock, but in the ashen fields of Muspelheim descendands of the first fire giants still live.
The jotuns in general prefer cold climates, but the jotuns in Muspelheim are resistant to fire and do not suffer from the extreme heat of their ancestral home."
#summary "Race: Cold resistant, prefers Cold scale +2 (home province prefers Heat scale +3). Fire resistant giants in home province.
Military: Muspel Giants, giant infantry
Magic: Fire, Air, Death, Glamour, Astral, Blood and Nature
Priests: Average"
#fortera 1
#end

#selectnation 32
#name "EA Rus" --
#era 2
#brief "Rus is a kingdom of the frozen lands. It is a nation of humans and mighty Chudes divided into two moieties."
#descr "Rus is a land of harsh winters and short summers inhabited by humans and Chudes, an exalted race of great strength and beauty. The Chudes and the humans have intermingled and neither race dominate the other. The Rusian society is divided into two moieties. The first is composed of hunters and nomads living in the deep forests. They worship the Bear and the Thunder and eat their meat raw. The warriors of the wild moiety are known for their fury and battle prowess. Their most prominent warriors are even able to take the shape of the sacred bear. The other moiety lives in houses of wood and in caves underneath the ground. They cook their meat and practice a new kind of magic. The Chudes of the second moiety call themselves sons and daughters of gods previously unheard of.
Most of the Rusian armies are composed of human infantry, but the elites of the kingdom are mighty Chudes. Yet the humans also field mighty warriors. The axe wielding Bear Warriors are respected and feared even by the warriors of Ulm.
The peoples of Rus prefer a cold climate."
#summary "Race: Humans and Chudes. All Rusian peoples have partial cold resistance and prefer Cold scale +2.
Military: Human infantry, hunters and berserkers, Chud warriors, sacred Chud Skinshifters.
Magic: Air, Nature, Fire, some Earth and Astral, summonable beings of Rus.
Priests: Medium, but expensive and few."
#fortera 1
#end


#selectnation 20
#name "EA Kailasa" -- checked
#era 2
#brief "Kailasa is a realm of intelligent apes ruled by Yakshas and Yavanas, divine beings living on the Sacred Mountain of Kailasa."
#descr "On the sacred Mount Kailasa, beings from an earlier era still linger. They are blessed with mystical powers but are few in number. With the emergence of the New God they have mustered aid from a most unsuspected source. Deep in the forests below the Sacred Mountain, apes of uncanny brightness have evolved. The apes are uncivilized and have only recently mastered the mysteries of metalworking."
#summary "Race: Yakshas and apes, prefers Heat scale +2
Military: A multitude of missile weapons and light infantry
Magic: Water, Earth, Astral, Glamour and Nature
Priests: Weak"
#fortera 1
#end

#selectnation 21
#name "EA Lanka" -- checked
#era 2
#brief "Lanka is a realm of intelligent apes ruled by Rakshasas, demon ogres skilled in dark sorcery and necromancy."
#descr "On the dark and densely forested island of Lanka, Rakshasas, demon ogres from an earlier era, still linger. Gifted with tremendous strength, they once fought the Devatas of Kailasa, but since then the most powerful of the Rakshasas have left this world for the Nether Realms. The remaining Rakshasas have captured and enslaved the monkey people of Kailasa and made them serve as warriors, hunters or food. The Rakshasas had no use for the peaceful White Ones and Kala-Mukhas, Rakshasa halfbreeds, lead the monkey people of Lanka. Since the enslavement of the apes, the ancient conflict between the Devatas of Kailasa and the Rakshasas of Lanka has been renewed. Rakshasas have an affinity for blood magic and in times of strife they are drawn to the blood of innocents."
#summary "Race: Demon ogres, apes and undead, prefers Heat scale +2
Military: Strong Rakshasa infantry, missile units and light infantry, reanimated apes
Magic: Air, Blood, Death, Glamour, Nature
Priests: Medium. National priests can reanimate the dead.
Dominion: Blood hunts give more blood slaves in turmoil and less in order"
#fortera 1
#end

#selectnation 23
#name "EA Yomi" -- checked
#era 2
#brief "Yomi is a nation of Oni and their servants. Oni are demons of the mountain wilderness. They are magically powerful and almost immortal, but few in number and rather stupid."
#descr "Yomi is a land of inhospitable mountains, steaming, sulphuric pools and sudden volcanic eruptions. At the center of this unforgiving land lies a great cone-shaped mountain at the top of which is an entrance to the Netherworld. From this gate the Oni have come, one by one or in small groups. Oni are demons of the wild, ugly, pot-bellied and mischievous. They are ruled by Oni Kings who occasionally emerge from the Netherworld to wreak havoc on the land of the living. Oni are almost immortal and must be killed in spirit as well as in body to stay dead. They are worshipped by human priests who build profane temple-gates through which even more Oni can enter the land."
#summary "Race: Demons. Reduced income. Halved income effects of heat and cold scales. Extra gold and resources in cave forts.
Military: Semi-immortal Oni, Bakemono and human servants. Light infantry, medium infantry. No sacred troops
Magic: Death, Fire, Earth, some Air and Nature. Powerful mages, bad at research. Some national summons
Priests: Weak, Provinces with temples spawn Oni"
#end

#selectnation 17
#name "EA Hinnom" -- checked
#era 2
#brief "Hinnom is a wasteland inhabited by several kinds of giants. The Rephaite lords rule the lesser giants by fear and force."
#descr "Hinnom is a dry wasteland inhabited by giants. At the dawn of time, on the sacred Mount Hermon, six Angels in full celestial splendor descended to aid and instruct the giants of the land. The Avvim were a people strong and beautiful of mind and body. They were adept students and their culture flourished under the tutelage of the Grigori, the angelic Watchers. But before long the Angels became enamored with the Avvim and taught them things that should not be taught. Tempted by the beauty of the Avvim, they took their daughters as wives and sinned before the Celestial Powers. Their offspring were the Nephilim, giants of godlike power, abominable to the world. The Angels were imprisoned in the Infernal Realms for their sins, but the Nephilim were partly of this world and could not be banished by the Celestial Powers. The Nephilim made themselves kings over the Avvim, and they fathered sons who became known as the Rephaim. The Nephilim and their sons had unnatural appetites and consumed food, livestock, beasts and finally their own offspring. With time, the Nephilim left Hinnom in search of a purpose and left their sons to rule the Avvim."
#summary "Race: Rephaite giants with enormous appetites. Lesser Avvite and Horite giants. Prefers Heat scale +2
Military: Horite cave dwellers, Avvite giants, chariots.
Magic: Fire, Earth, Astral, Blood, some Air, Nature and Death.
Priests: Weak, sacred Rephaite giants, can perform blood sacrifices."
#fortera 1
#end

#selectnation 19
#name "EA Ur" -- checked
#era 2
#brief "Ur is a nation of wild men, Enkidus, led by the priest-kings of the First City."
#descr "Ur is a warm plain inhabited by Enkidus, large, hairy wild men with horns and unkempt hair. Once upon a time all Enkidus lived in the wild, frolicking with feral beasts, but when the Enkidus met with the Avvim, some Enkidus adopted their ways of life. Now there are three Enkidu tribes. The members of the first tribe live pastoral lives and are led by shamans of remarkable power. The second one is a ferocious, swamp dwelling hunter-gatherer society led by Head Hunters and Bone Readers. The third tribe are the ones who adopted the Avvite way of life, agriculture and metalworking. It is they who founded Eridu, the First City. In the city a great temple was built and the kings of Eridu were inaugurated as priest-kings and rulers of the young nation. In the cities of Ur, where metalworking is common, medium and heavy infantry is raised. On the plains and in the swamps of the nation nomadic Enkidus gather and form quickly levied raiding parties. In the Swamps of Ur, near Eridu, live ancient dragon-kin known as Sirrushes. They are benevolent and powerful beings sacred to the Enkidus."
#summary "Race: Large, can recruit shamans and light infantry anywhere. Can recruit special units in swamps. Prefers Heat scale +1
Military: Enkidu infantry and sacred Sirrush dragons
Magic: Nature, Earth, Water, Air and some Death.
Priests: Strong, good at recalling dead God. Recalled god doesn't lose magic skills. Sacred Mushussus"
#fortera 1
#end

#selectnation 29
#name "EA Berytos" --
#era 2
#brief "Berytos is a nation of sailors and tradesmen who have founded dozens of colonies. Since the founding of a colony near Ashdod in Hinnom, they have become influenced by the blood cult of the Melqarts."
#descr "The people of Berytos are the descendants of a civilization created by the Telkhines, titanic storm demons defeated by a previous Pantokrator. The Telkhines taught shipbuilding, sailing and metalcrafting to the human ancestors of Berytos. When the Telkhines were defeated, the humans fled to the sea, led by the Storm Callers, disciples of the Telkhines. With the knowledge of ironcrafting and the magical might of the Storm Callers, new colonies were founded on distant shores. Like a phoenix, the dying empire was reborn. But the Telkhine gods were dead and the humans sought divine leadership. They found the Melqarts of Hinnom. One of the colonies was situated near Ashdod and the bloody cult of the Melqarts soon spread through the Phoenix Empire. In the capital colony of Berytos, a great temple to the Melqarts was built. But soon another power found its way into the cult. Refugee Colossi, great men of the Machakan royal family, arrived in Berytos and established themselves as rulers of the bloody cult. Their sorceresses claimed divinity and called themselves Brides-in-Waiting. Now Berytos is a seafaring people led by sorcerer queens from the great temple in Berytos."
#summary "Race: Ocean sailing, trace income across oceans, income bonus in coastal castles. Can recruit special mages in coastal castles. Prefers Heat scale +1
Military: Archers, light and medium infantry, lancers and Elephants
Magic: Blood, Fire, Air, Water, Earth and some Astral
Priests: Strong, can perform blood sacrifices"
#end

#selectnation 26
#name "EA Xibalba" --
#era 2
#brief "Cave dwelling bat people that once guided the sun on its night time passage through their caves."
#descr "Xibalba is a vast realm of dark caverns beneath the forests of Mictlan. According to legend, the sun and the moon passed through the labyrinthine caverns on their daily journey to the eastern horizon. On this journey they were guarded by the bat people, Zotz, that dwelled in the dark reaches of the Xibalban underworld. Being almost blind, they would not see and not covet the splendor sun. No one has seen the sun or the moon pass through Xibalba for ages, but the Zotz keep their vigil and their traditions alive. But lately the bat people has lost purpose and the priestly rulers of Xibalba looks to the surface world to once more bask in the splendor of the sun and the moon. The Zotz are led by priest kings from various cities, and only the priesthood represent centralized power. They still train the sacred Sun Guides once tasked with guarding the celestial entities through the dark world of Xibalba. The Zotz have mainly had contacts with surface dwellers of Mictlan and has adopted some of their technology and practices. The Zotz have an affinity for blood hunting and black magic. Despite being guides of the sun, their skills in solar magic is limited. The Zotz are numerous and live in great swarming cave colonies. Numbers rather than strength make them win their battles."
#summary "Race: Swarms of cheap, flying, stealthy cave dwellers, prefers Heat scale +1, extra gold and resources in cave forts
Military: Flying, stealthy light infantry and scorpions
Magic: Death, Blood, Earth, Fire, some Air and Nature
Priests: Average, can perform blood sacrifices"
#fortera 1
#end


#selectnation 43
#name "EA Atlantis" --
#era 2
#brief "Atlantis is an underwater nation of amphibious beings. They do not use missile troops. They have powerful Earth and Water mages and powerful priests."
#descr "For centuries the seas have been the domain of the Tritons, but recently a nation of beings resembling a cross between fish, frog and human has emerged in the deepest gorges of the oceans. The race is not entirely unknown, for there are a few of them who have made shallow coastal reefs their home, but the Triton Kings never imagined that they were numerous or powerful enough to form a nation. These Atlantians of the deeps never stop growing and will live for several hundred years unless killed. The Atlantian society is organized in a strict hierarchy of size and age. The oldest and most cunning Atlantians have made themselves kings and queens of The Basalt City in the deepest reaches of the ocean. The Atlantians of the deeps use weapons of enchanted basalt made by the Basalt Kings."
#summary "Race: Amphibious
Military: Light infantry, shamblers, no missile weapons
Magic: Earth, Water, Fire, some Astral
Priests: Powerful"
#end

#selectnation 44
#name "EA R'lyeh" --
#era 2
#brief "R'lyeh is an underwater nation. An ancient race of mentally superior beings has enslaved other races to work for it. R'lyeh has Atlantian and Oceanian troops as well as their own Aboleths. The Aboleths are powerful Astral and Water mages."
#descr "In the deepest of oceans lives the strange fishlike race called the Aboleths. These beings are highly intelligent and the older Aboleths called Mind Lords can enslave lesser beings with the force of mind alone. Having this power means they have enslaved Mermen and Deep Ones to do the daily work and to fill up the ranks of their armies. In a deep gorge the enslaved workers have built a score of small but magnificent cities for their rulers. In this gorge live the greatest of the Aboleths."
#summary "Race: Underwater
Military: Atlantian and Oceanian slaves, Aboleths
Magic: Astral, Water, some Death, Earth, Glamour and Nature
Priests: Average"
#fortera 1
#end

#selectnation 40
#name "EA Pelagia" --
#era 2
#brief "Pelagia is an underwater realm of tritons and mermen. Tritons are unable to leave the sea, but mermen can shed their tails and walk on dry land. Both races have mages, but only the merman mages can leave the sea."
#descr "Pelagia was the first kingdom to form in the deeps. It is a nation of tritons, humanoid beings with fin-like legs. The tritons of the Coral Clan and the Pearl Clan have formed a kingdom and allied themselves with mermen. Under the wise rule of the ancient Pearl Kings they dominate the oceans and harvest their riches. Pearls, corals, kelp silk and purple dyes are traded at coastal markets in Berytos and before that in Therodos. But recently other races have been stirring in the depths and new powers are forming. Wild beings of the kelp forests have spread, strange beings have emerged from the deepest seas and the ghosts of ancient Therodos are stirring. The Pearl Kings muster their forces and tribal tritons of the Turtle and Shark Tribes have joined forces with the triton kingdom. Tritons are unable to leave the sea, but mermen can shed their tails and walk on dry land to trade or wage war. The extensive trade with Berytos has given Pelagia a much needed ally. In the few coastal cities Pelagia has built, Berytian infantry have helped in the defense. Over time the mermen have adopted Berytian and Therodian culture and tactics. Now there are few Berytian soldiers left in the cities and Pelagia fields it's own mermen infantry. Both tritons and mermen have mages, but only the merman mages can leave the sea."
#summary "Race: Underwater
Military: Aquatic tritons and amphibious mermen. Light infantry, medium infantry, sacred, aquatic infantry
Magic: Water, Astral, Nature, some Air and Earth. Mages weaker on dry land. Mages can convert water gems into astral pearls
Priests: Powerful, weak on dry land"
#fortera 1
#end

#selectnation 41
#name "EA Oceania" --
#era 2
#brief "Oceania is a realm of the underwater wild and the clashing tides of the shores. The half-man inhabitants can remove their tails to raid and settle on dry land. The Capricorn is a powerful mage of the underwater wild and transition, whose powers changes when he leaves the sea. Sirens can take birdshape and lure enemies into the sea. Haliades, ancient sea nymphs serve as priestesses of the underwater wild."
#descr "Everything on land has a correspondence under water. Just like kingdoms formed on dry land, so did kingdoms form in the Sea, and just like the wild rebelled against encroaching civilization, so did the first triton kingdom suffer the wrath of the underwater wild. Oceania is an underwater realm of wild half-men, animals and guardians of the kelp forests. But Oceania is also a realm of the shores, where the stormy seas meet stable land. It is a nation of borders and transition, change and adaptability. Most of its inhabitants have the ability to change their shapes and cross the boundaries of the sea. Sirens, Capricorns and Ichtysatyrs all share the ability and affinity for change and adaptability. Sirens use it to change their shape and lure the unwary to a watery grave. Capricorns and Ichtysatyrs use it to raid and spread turmoil and chaos in coastal provinces. With the coming of the Awakening God the Capricorns lead the half-men in conquest above as well as beneath the waves. The dominion of the God of Oceania increases turmoil in coastal provinces."
#summary "Race: Underwater
Military: Amphibious half-men. Light infantry, medium infantry, sacred, aphroi ichtycentaurs
Magic: Nature, Water, Glamour, some Air and Earth. Mages weaker on dry land
Priests: Powerful, underwater only
Dominion: +2 turmoil in coastal provinces, +1 order in other provinces"
#end

#selectnation 42
#name "EA Therodos" --
#era 2
#brief "Therodos is the shattered remnants of the Telkhine kingdom cast beneath the sea by divine powers. Most inhabitants of the kingdom were killed and are now ghosts that are still unaware of their undead state of existence. Some Daktyloi master smiths survived the wrath of the gods and still rule the kingdom."
#descr "Therodos was once a kingdom of sages and craftsmen ruled by the Telkhines, sea daimones of almost godlike powers. When the Telkhines made themselves god-kings and threatened the divine order, their entire kingdom was drowned and cast under the waves. The people of the old kingdom suffered the full wrath of the divine judgment and unaware became ghosts inhabiting the ruins of a sunken kingdom. Of the Telkhine kingdom a few islands remain, inhabited by survivors of the cataclysm. On these islands the living serve the unaware dead out of fear and respect. On the islands of the shattered kingdom also lives the Daktyloi, dwarven smiths and servants of the Telkhines. With the death of of the Telkhines the Daktyloi replaced them and became revered by the Therodian ghosts. Now Therodos is drowned kingdom of ghosts and human islanders ruled by Daktyloi master smiths."
#summary "Race: Ghosts, Kouretes and humans. Ghosts do not need supplies, can enter the sea. Kouretes can enter the sea.
Military: Spectral hoplites and infantry, kourete and human sacred war-dancers.
Magic: Nature, Water, Earth, Air, and some Fire and Death. Daktyloi are skilled mage-smiths.
Priests: Average. Can incite fury in sacred war-dancers.
Dominion: Kills population, Summons spectral troops. Death scale increases the numbers of ghosts summoned. Dominion kills population, but forts prevent the death of the entire population."
#end

#selectnation 50
#name "MA Arcoscephale" --
#era 2
#brief "An ancient human kingdom led by Astrologers, Arcoscephale mainly uses heavy infantry, chariots and war elephants. The Astrologers are powerful Astral mages. Mystics skilled in Astral and Elemental magic give Arcoscephale great magical versatility. The priestesses of Arcoscephale can heal wounded soldiers."
#descr "Arcoscephale is an old kingdom. Although its glory days are long past, the ancient Astrologers who aided past kings in building Arcoscephale into a mighty empire have recently emerged from their centuries-old seclusion, to restore the Old Kingdom to world domination once more. Priestesses with great knowledge of healing are trained in ancient temples built during the peak of the Old Kingdom. The priestesses are able to scry upon enemy troops and provinces that are located within the God's Dominion. The war machine of ancient Arcoscephale has not changed over the past centuries. Cumbersome plate hauberks and long spears are still used and the cavalry is primitive. Elephants and chariots, unpredictable but devastating, are still popular."
#summary "Race: Humans
Military: Heavy spear-armed infantry, elephants, chariots
Magic: Astral, Fire, Earth, Water, some Nature
Priests: Average, healing
Dominion: Scry (accurate and automatic military reports inside dominion)"
#end

#selectnation 54
#name "MA Ermor" --
#era 2
#brief "Ermor was a human empire that was corrupted and fell into darkness. Now Ermor is a land of the dead. Skeletal legions march from the Ashen Empire to conquer the lands of the living."
#descr "Ermor was once a great empire that had conquered most of the known world. The realm crumbled as the great mages of the Empire studied dark magic under the Sauromancers of C'tis. Unaware of the dangers of dark sorcery, priests performed unholy rites in the capital city of Eldregate. But there were voices who demanded the foul practices to stop. Theurgs and Thaumaturgs foresaw the cataclysm and advised generals, governors and consuls to revolt. When the Apostate Emperor marched on Ermor itself, the Augurs and Bishops of the Empire were forced to act in concert. In one cataclysmic event, Death was let loose and the empire was shattered. The Cataclysm attracted attention from an earlier God, a dark and hungry God. The vast power of this Awakening God erased the boundaries between the land of the living and the land of the dead. Ermor is now a cursed land of ashes and darkness where nothing grows. The bones of long-dead inhabitants reassemble to form legions of undead under the leadership of the cursed priests of the old Ermorian faith. Undead legions march forth to reconquer a world once theirs. The Ermorian Dominion reanimates the dead without the aid of unholy priests. It also destroys the land, turning crops and forests into ashes and people and livestock to bones. The Pretender God of Ermor will also be able to sense where any corpses are in provinces under his Dominion."
#summary "Race: Undead. Do not need supplies, can enter water, are unbreakable and can walk day and night. Do not recruit regular armies, but summons or reanimates undead.
Military: Undead legionnaires, wailing ladies, unholy knights and hordes of the newly dead.
Magic: Death, some Fire, Astral and Elements
Priests: Powerful. All priests can reanimate the dead.
Dominion: Reanimates the dead. Kills population, sense corpses."
#end

#selectnation 55
#name "MA Sceleria" --
#era 2
#brief "Sceleria is a splinter empire that emerged when the great Empire of Ermor was swallowed by powers from the Underworld. Now Sceleria is a land where the dead and the living walk side by side. Sceleria uses legionnaires and undead. Their Thaumaturgs are skilled mages of Death and Astral magic. They are also unholy priests capable of reanimating the dead."
#descr "Sceleria is a splinter empire of the great Empire of Ermor. As dark arts were practiced in the heart of the Empire, a new order of Thaumaturgs emerged. Guided by the stars and knowledge of the Underworld, they foresaw the Cataclysm that would destroy the empire and led the emperor's twin brother in rebellion. The great empire was torn apart in a civil war that ended with the siege of Ermor. In desperation the Augurs and Bishops let Death loose, and everything went still. The great city of Eldregate and everything within leagues became an ashen waste. Ermor was no more, and the provinces of the old empire formed into new kingdoms and lesser empires. The twin brother of the last Ermorian emperor claimed the imperial crown. With the aid of the Thaumaturgs he reformed the empire and built a new capital named to always be a reminder of the wickedness that brought the great empire down. Now Sceleria is an empire permeated with the Death Cult of the Thaumaturgs. While the young kingdom of Marignon uses fire and faith to hold Death at bay, Sceleria trusts in the Laws of Death itself to persevere. The Thaumaturgs of Sceleria regard themselves as defenders of the living world and the last hope for mankind. With litanies and masses for the dead, they prevent the spread of the shadow by reanimating the dead under strict control. Now the dead serve the living and fight their wars.
The war machine of Sceleria is based on the old legionnaire army of Ermor with the added might of the walking dead."
#summary "Race: Men and undead. Undead do not need supplies, can enter water, are unbreakable and can walk day and night.
Military: Human legionnaires and undead hordes of lesser quality.
Magic: Astral, Death, some Water and Air
Priests: National priests can reanimate the dead"
#end

#selectnation 56
#name "MA Pythium" --
#era 2
#brief "Pythium is a splinter empire that broke free from Ermor when it fell. Pythium uses legionnaires, but also has Serpent Cataphracts and hydras. The Theurgs of Pythium are powerful priests and Astral mages. Pythium uses Theurgical communion to empower their mages in battles."
#descr "The Emerald Empire of Pythium is a splinter empire of the great Empire of Ermor. As dark arts were practiced in the heart of the Empire, the stars warned the Theurgs of Pythia to flee the impending doom. They led Pythia away from the falling Empire and formed an imperial theocracy under their wise rule. But this was not enough to save them. As Ermor crumbled, the provinces of Pythium rebelled and broke away from their old masters. The Emperor of Pythium could not reclaim the rebelling lands and the power of the Emerald Empire diminished over the centuries.
The war machine of Pythium is based on the old legionnaire army of Ermor with some minor modifications. During Ermorian times, part of the Pythian lands were under the sway of the Sauromatian tribes. The Androphags used hydras of the Pythian Marshes in warfare. For a long time hydras were only used in the Pythian arenas, but now the old practice has been adopted along with the usage of serpent mounts."
#summary "Race: Humans
Military: Legionnaires, serpent cataphracts, gladiators, hydras
Magic: Astral, Air, Water, some Fire. High magic gem income.
Priests: Powerful"
#end

#selectnation 57
#name "MA Man" --
#era 2
#brief "Man is a feudal kingdom of humans. They use knights and skilled longbowmen. They have powerful mages of Nature and Air, but their priests are weak. They have powerful special troops of Avalon."
#descr "The realm of Man is a feudal kingdom. Their kingdom was established by conquering a race of tall and magically powerful beings known as the Tuatha. When the Tuatha were destroyed, their greatest treasure was found: The magical Forest of Avalon. Hidden deep within was great magic. The Witches of Man entered the forest, learned the old lore, and helped Man to grow in power and influence. The infantry of Man is limited and lacks heavy troops. Their regular armies most often consist of powerful knights and skilled longbowmen. The Witches train their own special troops, the Wardens and Knights of Avalon. These troops are very skilled and are also magically enchanted by the Witches. The monks who serve the God of Man are divinely inspired scholars who gather and record knowledge in the monasteries scattered throughout the land. Descendants of the Logrian people displaced by the Witches and their servants dwell in outside the fortified castles of the nobility."
#summary "Race: Humans
Military: Infantry, longbowmen, knights, special troops of Avalon
Magic: Nature, Glamour, some Water, Earth and Air
Priests: Weak, divinely inspired researchers."
#end

#selectnation 58
#name "MA Eriu" --
#era 2
#brief "Eriu was founded when humans defeated the Tuatha in ages past. Now the Tuatha and their Sidhe descendants re-emerge from their hiding places to lead the humans. The Sidhe and Tuatha are able to weave illusions to hide their true appearance. They are skilled Air and Nature mages."
#descr "When men came to the land of the Tuatha and the Fir Bolg, there was a drawn out battle which ended with the defeat and total withdrawal of the Tuatha. The Land of the Ever Young was forever lost to this world and Avalon was taken by the Witches of Man. The Sidhe, descendants of the Tuatha, retreated into strange twilight realms with entrances hidden in ancient mounds. The land of the Fir Bolg was split by the invading forces: Man and their Witches, and the Milesians. The Milesians named their land Eriu. Most of the Eriu population is composed of humans of Milesian ancestry, but a few Fir Bolg still survive in remote villages. With the coming of the New God, the Daoine Sidhe have re-emerged from their magical mounds to lead the Milesians. Eriu is now a nation of humans and Fir Bolg led by the awakening Sidhe."
#summary "Race: Milesian humans and Fir Bolg ruled by Sidhe and Tuatha, illusions
Military: Milesian infantry, Fir Bolg infantry, sacred Sidhe infantry
Magic: Glamour, Air, Nature, Water, some Earth
Priests: Average"
#end

#selectnation 60
#name "MA Ulm" --
#era 2
#brief "Ulm is a human kingdom famous for its steel. They use heavy infantry and heavy knights. Even their crossbowmen use heavy armor. Their smiths, Earth mages of limited skill, are able to forge magic items at a reduced cost. The priests of Ulm are weak."
#descr "Ulm is a young kingdom, risen from the Ulmic tribes conquered by the fallen Empire of Ermor. From the ashes of Ermor emerged a new kingdom true to its ancient legacy, the Enigma of Steel. Where Marignon relied on religion to build a kingdom, Ulm relied on steel. The mines of Ulm are famous for their riches and the smiths of Ulm work the iron into the blacksteel armor used by the knights and infantry of Ulm. The people of Ulm are heavily built by human standards. Their infantry use full chain or plate armor made of blacksteel. The feared Black Knights of Ulm are the most heavily armored troops known to man. The leaders of Ulm have never approved of magic and only the Master Smiths are allowed to use it. The smiths are used to working in conditions that are magically unfavorable and are therefore not adversely affected by provinces that have a strong Drain dominion. The smiths craft armor and weaponry for lords and kings, but the strength of steel is preferred over magic. Even religion is of secondary importance in Ulm, though an Iron Cult that worships steel in a more devout fashion has emerged in recent times."
#summary "Race: Stocky humans, production bonus in all castles
Military: Heavy infantry, crossbows, knights, superior armor
Magic: Earth, Fire, rarely Air and Astral. Superior magic item forging. Smiths' research not affected by Drain scale
Priests: Weak, inquisitors"
#end

#selectnation 61
#name "MA Marignon" --
#era 2
#brief "Marignon is a human kingdom based on religious zeal. Holy knights and Inquisitors ride out to purge the world of enemy faiths. Marignon has powerful Fire and Astral mages and powerful priests."
#descr "Marignon is a feudal theocracy. The Inquisition controls all aspects of the country, including warfare. The feudal lords pay tithes and tax the peasants, but all political decisions are made solely by the Church. Marignon rose out of the ashes of Ermor and has succeeded in holding the shadow of the fallen empire at bay through religious zeal and austerity. The widespread fanaticism in Marignon has done wonders for its survival thus far. The heavy infantry of Marignon is armed with large weapons such as great swords and halberds. All units carry the bright red-and-orange livery of Marignon. The Inquisitors of Marignon are trained in the House of Fiery Justice together with Witch Hunters. The Witch Hunters are mage-priests who use Astral magic."
#summary "Race: Humans
Military: Heavy infantry, crossbows, sacred knights and flagellants
Magic: Fire, Astral, some Air and Earth
Priests: Powerful, Inquisitors
Inquisition: Automatically reduces enemy dominion and spreads own dominion up to 1 in owned provinces"
#end

#selectnation 62
#name "MA Pyrène" --
#era 2
#brief "Pyrène is a feudal mountain kingdom befouled by dark magic and blood sacrifices. The last of their giant allies have died and been replaced by the Black Goats, dark beings reminiscent of the Pandemoniacs of Pangaea."
#descr "Pyrène was once a kingdom of cavern dwelling humans and their allies, the Sorginak witches and the Jentilak hiants. Now the humans have more of less abandoned their cavernous realm and established a fuedal kingdom in the surrounding mountains. The young kingdom was drawn into a long lasting war with Abysia and suffered heavy losses. The last of the Jentilak and Basajaunak died in the defense of the Pyrène caves, but the Abysians were defeated. With the loss of their mightiest mages and warriors new powers established themselves. Lasting exposure to Abysian blood magic had prepared the nation for a sinister reshaping. From some dark woodland came the Akerbeltz, the Black Goats. Their influence slowly transformed the kingdom into a nation of dark rituals and bloody ceremonies. The Akerbeltz seduced the Sorginak and made them abandon their former mistress and embrace blood magic. Now even the priesthood have adopted blood magic and sacrifice humans to further the goals of the nation. Recently the dark practices have drawn the attention of Marignon and its inquisitors."
#summary "Race: Humans of cave-man descent with dark-vision and elemental resistance.
Military: Humans infantry, crossbows and knights, sacred mouflon knights.
Magic: Blood, Nature, Air and some Earth and Fire.
Priests: Average, can perform blood sacrifices."
#end

#selectnation 73
#name "MA Mictlan" --
#era 2
#brief "Mictlan is an old kingdom ruled by priest-kings. Mictlan has powerful priests, but its infantry uses archaic weapons."
#descr "Mictlan is an ancient tribal empire that has been isolated for centuries. The foul practices of the priest-kings of Mictlan have caused most neighbors to leave or face slavery or death by sacrifice. Since the dawn of the kingdom, blood has been spilled in the temples of the capital. Now a new era has dawned and the isolation is broken with the coming of the Lawgiver. The Blood Cult has been abolished and the priests now follow the Lawgiver. Isolation has made Mictlan a backward nation and its warriors use archaic weaponry and armor. The armies are mainly composed of slaves from newly conquered lands. The mage-priests of Mictlan celebrate the two Faces and the two Dominions of the Lawgiver, namely the Sun and the Moon, the Rain and the Forest."
#summary "Race: Humans, prefers Heat scale +1
Military: Light infantry with slings and javelins, tribal kings can levy slaves, sacred Eagle and Jaguar Warriors
Magic: Air, Fire, Astral, Nature, Water
Priests: Powerful"
#end

#selectnation 69
#name "MA T'ien Ch'i" --
#era 2
#brief "T'ien Ch'i is a bureaucratic empire. Versatile mages of The Way of the Five Elements, Celestial Masters and religious ministers serve the Emperor. The cavalry of the Empire is well known and sacred Celestial Beings form the elite core of the armies. Eunuch administrators can increase provincial defense for free."
#descr "The Celestial Empire of T'ien Ch'i is ancient. Since the founding of the Empire, peace has reigned and a Bureaucracy of great efficiency has evolved. Ministers and officials chosen by skill rather than birth govern the Empire. The Emperor and his family are considered divine, but are not involved in the administration. The cavalry of T'ien Ch'i is well known and the infantry is varied and versatile. The eunuchs who run the Bureaucracy are able to conscript troops for the defense of provinces as part of the taxes due to the Emperor. A magic tradition called The Way is practiced by hermits and scholars in the kingdom. Prominent Masters of the Way come to the Heavenly Gate in the capital to be ordained as Celestial Masters. These mage-priests can summon heavenly beings from the Celestial Sphere to serve the Empire."
#summary "Race: Humans
Military: Cavalry, heavy infantry, archers, crossbows. Conscription
Magic: Water, Astral, Fire, Air, Earth, Nature and Glamour, Summon Celestial Beings
Priests: Average."
#end

#selectnation 76
#name "MA Machaka" --
#era 2
#brief "A human kingdom ruled by priests. Machaka uses great spider mounts and has both light infantry and heavy hoplites. Witch doctors and Black Sorcerers give Machaka a wide range of magical skills. Machakans dislike cold lands."
#descr "Machaka is an old sacral kingdom where the well-being of the land is thought to be dependent on the will of the king. The king is the highest priest of the kingdom, but should he fail in his duties, he is sacrificed and replaced by one of his numerous sons or brothers. The priests of the kingdom are the true rulers of the land. Religious ceremonies, judicial tasks and the gathering of intelligence are all performed by the Eyes, Ears, and Voices of the Lord. Only warfare is handed over to secular commanders. Machaka uses light infantry, archers and heavy hoplites second only to those of Arcoscephale. In the forests of Machaka, giant spiders are caught and used as mounts. One other area is left untouched by the priests: Magic. Simple witch doctors living outside villages grudgingly serve the priests. In the depths of the God Forest lies a lonely mountain filled with caves. Here resides the true power of Machaka - the Black Sorcerers, Sorceresses and their Spider Warriors. Machakans prefer hot lands."
#summary "Race: Humans, prefers Heat scale +2
Military: Heavy infantry, light infantry, spider riders, assassins
Magic: Fire, Earth, Death, Nature and Glamour
Priests: Average"
#end

#selectnation 59
#name "MA Agartha" --
#era 2
#brief "A cavern realm of humans and a few remaining Pale Ones. Pale Ones can grow to huge proportions and the old ones are rare and sacred. The Agarthan humans have only limited night vision, whereas the Pale Ones see perfectly in the dark."
#descr "In dark caverns under the Roots of the Earth a strange kind of one-eyed humanoids has evolved. Untouched by the sun, they have become known to humans as the Pale Ones. When humans first met these pale giants, it was in war. With the destruction of the false god of the Pale Ones, an ancient Seal was broken and vast powers of destruction were released. The Pale Ones were almost wiped out of existence and humans could move down into the caverns of Agartha. Here they found fabulous riches and ancient secrets. The humans replaced the Pale Ones and now most of Agartha's inhabitants are pale-skinned humans with large eyes. Everything left by the Ancient Ones has become subject to worship by the humans. Ancient statues are enchanted and given life by Golem Crafters, priest-mages of the Agarthan Golem Cult. A few surviving Oracles lead the Cult and keep the memories of past ages alive."
#summary "Race: Humans and Pale Ones. Darkvision. Poor amphibians. Extra gold and resources in cave forts.
Military: Light and heavy infantry, huge and sacred Ancient Ones, troglodyte slaves.
Magic: Earth, some Fire, Water and Death.
Priests: Powerful
Dominion: Constructs receive increased HP inside dominion"
#end

#selectnation 63
#name "MA Abysia" --
#era 2
#brief "Abysians are lava-born humanoids that radiate heat. Abysians mainly use heavy infantry. They have skilled Fire, Astral and Blood mages and their priests can perform blood sacrifices. Abysians dislike cold provinces."
#descr "Abysia is a hot wasteland, at the center of which lies a great volcano whose lava-lit caverns are inhabited by magma-born humanoids. Their flesh radiates heat and they are not harmed by flames. Abysians are stronger than humans and prefer heavy armor and weaponry. Bows are not used, because they would burn to cinders in the glowing hands of the Abysians. The war machine of Abysia also includes Salamanders, lizardlike beings composed of the same hot lava-born flesh as the Abysians. Abysian Warlocks are very powerful Blood mages and skilled crossbreeders. The Anathemant Priests of the Flame Cult practice blood sacrifice to strengthen the power of the Awakening God. Abysians prefer to live in extremely hot places. They do not farm or hunt for a living, so their income and supplies are not affected by the Growth or Death scale of a province. However, population will still die slowly in Abysia-controlled provinces with Death scales."
#summary "Race: Radiates heat, fire resistance, prefers Heat scale +3, wasteland survival. Death and Growith scales have half the standard effect on income and population growth and no effect on supplies. Extra gold and resources in cave forts.
Military: Heavy infantry, no missile weapons, salamanders
Magic: Fire, Blood, Astral, some Earth
Priests: Powerful, can perform blood sacrifices"
#end

#selectnation 71
#name "MA Caelum" --
#era 2
#brief "Caelum is a magocracy of slender, winged beings living on the coldest mountaintops. They are skilled archers and train war mammoths. The heavy infantry of Caelum uses arms and armor of magical ice. Caelian Seraphs are powerful mages of wind and frost. They are cold resistant and dislike warm lands."
#descr "Caelum is a magocracy of winged humanoids who inhabit the highest mountain peaks. In ancient times, there were three Caelian clans led by semi-divine beings known as Yazatas. The Raptor clan was accepted by the Yazatas even though they were held responsible for the corruption of Catharsis. When the Harab Seraphs of the Raptor clan began to study dark magic once more, the purifying flames were tainted and Catharsis remained Anthrax, King of Banefires. As a result many of the Seraphines died from a wasting disease and their sacred task was abandoned. The Harab Seraphs were condemned and civil war broke out. The Raptor Clan was banished and scattered across the world. The last of the Eagle Kings disappeared and were replaced by the High Seraphs of the Airya clan. The Seraphs are administrators, judges and temporal leaders of Caelum. They are masters of Air magic and craft the magical ice that Caelians use instead of regular metal. The ice tempers with lower temperatures and the heavy ice armor is more durable in cold climates than in warmer ones. All weapons crafted from the ice are magical and capable of harming magical beings. The Airyas live in the coldest mountain peaks and are unaffected by low temperatures. They are thin and light. Spire Horn Caelians are less resistant to cold but have partial resistance to lightning. Since the fall of the Harab Seraphs more of them have turned to martial occupations. The Caelians are skilled archers and prefer hit-and-run tactics, even though they do have some heavy troops, such as huge Mammoths."
#summary "Race: Flying, cold resistant, partially shock resistant, prefers Cold scale +3
Military: Flying units, skilled archers, mammoths
Magic: Air, Water, some Astral and Death, weak Fire
Priests: Weak, Guardian Spirits."
#end

#selectnation 75
#name "MA C'tis" --
#era 2
#brief "C'tis is an ancient kingdom of lizardmen. They do not use cavalry or archers, but use poison slingers instead. C'tis has powerful priest-kings. The Dominion of C'tis causes lands to turn into rotting marshlands that causes disease in everyone who is not cold-blooded or not accustomed to swamps and marshes. The lizards dislike cold provinces."
#descr "C'tis is a swampy river valley surrounded by sandy deserts. In the fertile valley a sacral kingdom of lizardlike humanoids has formed. The kingdom is ancient by human standards and its wisdom and magical knowledge are great. At the top of the society is the Lizard King. The King is the highest priest of C'tis. Under the king are the High Priests with their sacred serpents. The lizards are herbivores, but have enslaved a race of carnivorous lizardmen who serve as soldiers and workers. The C'tissians are somewhat slow in movement, but have thick hides that protect them from cuts and bruises. Both lizard races are cold-blooded and become exhausted very quickly when fighting in cold provinces. They have partial resistance to poisons. The inhabitants of C'tis prefer to live in warm provinces. With the coming of the new God, the swamps of C'tis have begun to spread. Dense rains and oppressive heat turn the land into unhealthy marshlands, thick with the stench of rotting vegetation. Marshmasters have taken the place of the Sauromancers of old and the Swamp Guard has replaced the chariots as elite troops. In this land, the lizards prosper. Within provinces influenced by this Dominion, income is increased by 1 percent per level of Dominion, and the income of enemy provinces is reduced by 5 percent per level of Dominion. Unless cold-blooded, soldiers inside the Dominion will suffer from disease. The pretender and all his sacred units are immune to this effect."
#summary "Race: Thick hides, cold-blooded, poison resistance, prefers Heat scale +2
Military: Infantry, slave warriors, sacred serpents, large Sobek warriors and sacred guards
Magic: Death, Nature, Water, some Astral
Priests: Powerful"
#end

#selectnation 52
#name "MA Pangaea" --
#era 2
#brief "Pangaea is a woodland realm of wild halfmen. Pangaea has stealthy satyrs, flying harpies, strong centaurs, and raging minotaur warriors. The Panii are powerful mages of Nature and Earth and are able to lure women into the wild."
#descr "Pangaea is a woodland nation inhabited by wild beings connected with nature. Halfmen such as satyrs, centaurs and minotaurs serve the lords of the Sacred Groves deep in the forests. In ancient times, the woods covered much of the world, but that has changed. Man is no longer beast and animals are no longer wild. The world of the wild is disappearing. Centaurs have developed civilized societies and donned armor. The Panii, guardians of the Groves, have decided that it is time to act to preserve their dwindling habitat."
#summary "Race: Forest beings, stealthy troops, troops will heal battle afflictions
Military: Satyr and minotaur infantry, centaur cataphracts, warriors and archers
Magic: Magical Tunes, Nature, Earth, Blood, some Water and Glamour
Priests: Average"
#end

#selectnation 53
#name "MA Asphodel" --
#era 2
#brief "Asphodel was once part of Pangaea, a woodland realm of wild halfmen. Now Asphodel is a land of vengeful woods and living carrion. Satyrs, harpies, centaurs and minotaurs walk side by side with beasts of animated vines and bones. Panic Apostates practice necromancy and magic of the wild."
#descr "Asphodel was once part of Pangaea, a woodland nation inhabited by wild beings connected with nature. Halfmen such as satyrs, centaurs and minotaurs serve the lords of the Sacred Groves deep in the forests. In ancient times, the woods covered much of the world, but that has changed. Man is no longer beast and animals are no longer wild. The world of the wild is disappearing. In response to the destruction of the wild forests a dark and hungry God has arisen. The Panii of the sacred groves could not prevent the destruction of the wilderness and a few of them have revolted and struck back with dark fury upon the civilized world. The Panic Apostates and their followers have been touched by the Dark God and their hides are colored as black as the mood of the vengeful forest. But victory comes at a price. Halfmen as well as civilized men succumb to the Curse of the Carrion Woods. Asphodel is slowly turning into a cursed forest realm haunted by living carrion."
#summary "Race: Forest beings and reanimated carrion beings, stealthy troops, troops will heal battle afflictions, undead carrion beasts
Military: Satyr and minotaur infantry, centaur warriors and archers, harpies, hordes of manikins and carrion beasts.
Magic: Nature, Death, some Earth and Water.
Priests: Average. Undead priests can reanimate carrions.
Dominion: Reanimates the unburied dead as manikins. Carrion beasts everywhere but more in forests. Temples and a growth scale increase reanimation rates. Magic scale increases the chance of better reanimations. Dominion kills population."
#end

#selectnation 78
#name "MA Vanheim" --
#era 2
#brief "Vanheim is a human nation ruled by Vanir, ancient enemies of the Jotun giants. Vanir can sail across the oceans and hide themselves with illusions. They mostly use infantry, but utilize many unique troops, including flying Valkyries, human berserkers and skinshifters. Their Dwarven smiths are powerful Earth mages."
#descr "Vanheim is a land of misty moors and bitter forests. Humans compose most of the population, but the rulers of the land belong to a tall and innately magical race known as the Vanir. The Vanir once fought the giants of Jotunheim, but with the coming of man, they have turned their attention elsewhere. Now only a precious few of the Vanir remain and humans are no longer slaves.
Humans compose the basic infantry units of Vanheim. The Vanir have blessed some loyal humans with superior fighting skills and the ability to enter a state of wild rage or wolven shape. The Vanir are masters of illusion who fight while mounted on exceptionally fast horses. Female Vanir are called Valkyries and have the ability to fly. This ability was a gift from a dead god who used them as messengers of death. During those days, blood was sacrificed. The old ways have not been used in ages, but still the oldest of the Vanir remember how to sate nature with blood. The Vanir are very skilled sailors and can sail the oceans."
#summary "Race: Ocean sailing, trace income across oceans, flying troops, illusions, prefers Cold scale +1
Military: Heavy infantry, skinshifters, Valkyries, Vanir
Magic: Air, Glamour, Earth, Blood, some Fire and Death
Priests: Average, can perform blood sacrifices"
#end

#selectnation 80
#name "MA Jotunheim" --
#era 2
#brief "Jotunheim is the home of the giants of the north. Jotuns are immune to the cold and dislike hot lands. Their Vaetti allies use wolf riders, but no heavy cavalry or bows are used. Their mages are versatile and powerful sorcerers."
#descr "Jotunheim is a land of bitter winters and cool summers. It is the home of giants and goblins. The giants of Jotun are immensely strong and resilient. They are born in the cold and do not suffer from cold climates. Jotunheim is ruled by several Jarls who rarely join forces. In the heart of Jotunheim lies an ancient Forest of Iron and Ice. Here live the Gygjas, old wicked hags with great sorcerous skills. They are served by the Vaettir, who are small, wicked goblins of the Jotun woodlands. They rarely venture outside the woodlands, but do join the armies of Jotunheim when the Gygjas bid them to. The people of Jotunheim prefer to live in very cold provinces."
#summary "Race: Cold resistant, needs lots of supplies, prefers Cold scale +2
Military: Giant infantry, Vaettir, and Wolf Riders
Magic: Water, Blood, Death, Glamour, Astral and Nature
Priests: Average"
#end

#selectnation 81
#name "MA Nidavangr" --
#era 2
#brief "Nidavangr is a jarldom of tribal warriors who follo their totemic spirits, the Bear, the Wolf and the Crow. They are led by mighty shamans who perform horrible rituals on prominent warriors to make them immortal."
#descr "Nidavangr is a land of windswept moors and frozen mountains. This cold and inhospitable land once belonged to the Jotuns or perhaps the Vanir, but it was conquered and settled by strong and fierce men in ages past. Ever since they have fought bitter wars with the former inhabitants of the land. Centuries of war have tempered the will and the ways of the Nidings of Nidvangr. Men as well as women are taught to fight at an early age and failure to survive combat or the harsh climate is more prevalent than dying from disease or old age. To most Nidings death in a bed is a failture of life as a whole.
Nidavangr is composed of three clans, named after their totemic animals, the Bear, the Wolf and the Crow. The warriors of the clans adopt the battle tactics of their totem. The clans are ruled by Jarls, but it is the Seithberenders, the clan shamans, who are the true masters of Nidavangr and the ones who perform the Nidalögning, Nidbath, on the sacred warriors of the Jarldom. The Nidbathed are ghastly warriors who are not even stopped by death. Should a Nidbathed be killed he rises again, and continues to fight, for he has several lives.
Out of necessity, the perpetual conflict with the Vanir has made the Nidings search for ways to avoid the effects of glamour in their lands. And so the Awakening God taught the clan shamans the art of seith and how to scry their lands for what which cannot be seen."
#summary "Race: Humans of barbarian descent, partial cold resistance, prefers Cold scale +2.
Military: Some stealthy raiding infantry, berserking infantry, semi-immortal sacreds.
Magic: Death, AStral, Air, Nature, Water and some Earth and Blood.
Priests: Weakm can perform blood sacrifices.
Dominion: Scry (accurate and automatic military reports inside dominion)"
#end

#selectnation 79
#name "MA Vanarus" --
#era 2
#brief "Vanarus is a kingdom of the frozen lands. It is a nation of humans, Chudes and Vanir. Old traditions of the three peoples intermingle and new ones are formed. The Vanir were always few and their numbers are ever dwindling. The Chudes are more numerous, but it is clear that the humans will dominate the land in a distant future."
#descr "Rus is a land of harsh winters and short summers. When the Vanir arrived the land was inhabited by humans and Chudes, an exalted race of great strength and beauty. The Chudes and the humans had intermingled and neither race dominated the other. The Vanir came as explorers and traders, but conflict over a sacred site led to war. The Vanir were victorious and founded the city of Novgård at the ancient site. The Chudes and the humans of Rus joined causes and tried to drive the Vanir out, but the humans were weak and easily tricked by the illusions and magic of the Vanir. Soon the Chudes found themselves at war with Vanir as well as their former human allies. Then arrived the Black Knights of Ulm. The former conflict between Vanir and Chudes ended as the three peoples of Rus rallied under Novgård to defend their land. When the Ulmic threat was averted, a kingdom had formed under the rulership of the Vanir.
Humans comprise most of the Vanarusian population. A large portion are Chudes and a precious few are Vanir.
Most of the Vanarusian armies are human infantry. The elites of the kingdom are mighty Chudes and Vanir.
The peoples of Vanarus prefer a cold climate."
#summary "Race: Humans, Chudes and vanir. All Vanarusian peoples have partial cold resistance and prefer Cold scale +2. 
Military: Human medium infantry, Chud hirdmen and skinshifters, sacred Van infantry.
Magic: Air, some skills in all other paths except Astral, summonable beings of Rus.
Priests: Medium, but expensive and few. Can perform blood sacrifices."
#end

#selectnation 68
#name "MA Bandar Log" --
#era 2
#brief "In the dense forests of the Bandar is a realm of intelligent apes. The exceptionally smart white apes are sacred and blessed with the gift of magic. The apes have a multitude of missile weapons and have trained elephants and tigers to be used in warfare."
#descr "In the dense forests of the Bandar realm, apes of uncanny brightness have emerged. Under the influence of semi-divine beings, the apes have evolved intelligence and culture. When the former rulers of Bandar Log returned to their Celestial Realms, the apes were left without leadership. A warlike, hierarchical society was formed with the large Bandar apes at the top. But the influence of the former masters was not forgotten and the blessed white apes who were gifted with higher intelligence and magical powers were able to keep their influence and power. Bandar Log is a divided society. Small Markatas are at the bottom of the society. Vanara apes of human size are the most common. Large Bandar apes rule most of the society and form the military. Sacred white apes are trained as sages, priests and holy warriors."
#summary "Race: Apes, prefers Heat scale +2
Military: A multitude of missile weapons, light and medium infantry, elephants, sacred tiger riders
Magic: Astral, Nature, some Water and Earth
Priests: Weak"
#end

#selectnation 70
#name "MA Shinuyama" --
#era 2
#brief "Shinuyama is a nation of Bakemono, ghostly goblins of the wilderness. Some of them have supernatural abilities such as an aura of fear or shapeshifting abilities."
#descr "When the entrance to the Netherworld closed, the Oni became fewer and fewer. Their Bakemono slaves and human servants rebelled, and when the last of the Dai Oni died, the realm was taken over by Bakemono Kings. Human smiths were forced to reveal the secrets of metalcraft and the Bakemono have become ready to conquer the lowlands from the humans. The Bakemono still live in a tribal society ruled by the strongest and most powerful of their kin. The Bakemono are a diverse kind. Huge lumbering O-Bakemono, proud Dai-Bakemono, strange shapeshifters and ghostly apparitions all heed the call of the Bakemono Kings and the Awakening God."
#summary "Race: Bakemono. Extra gold and resources in cave forts. Lesser bakemonos rebated in mountain.
Military: Light infantry, medium infantry, heavy infantry. Kappas able to enter the sea, supernatural commanders. No sacred troops
Magic: Death, Fire, Earth, Water, Nature. Many national summons
Priests: Weak"
#end

#selectnation 64
#name "MA Ashdod" --
#era 2
#brief "Ashdod is a wasteland inhabited by giants. The giants have degenerated since earlier times and only in the Twin Cities live the Anakim of pure blood."
#descr "Ashdod is a dry wasteland inhabited by the Rephaim, giants descended from the Nephilim of primordial times. The Rephaim have degenerated and lost the prodigal powers of their predecessors, but they are still mighty in comparison to other beings. While not as mighty as they once were, there are still a few Rephaim with pure blood. In the Twin Cities of Ashdod and Ashkelon live the Anakim, mightiest of the Rephaim, and the Anakite priest-kings. With the disappearance of the Nephilim and the pureblooded Rephaim, the Nephilim Cult has been replaced by ancestor worship. Malikum, Rephaite kings of old, are worshipped at sacred banquets for the dead. The Kohanim of earlier times have been replaced by the Zamzummim, priest-mages and shepherds of the dead, who fulfill their purpose in life by being devoured at the funerary banquets."
#summary "Race: Giants
Military: Rephaite giant infantry and human slaves. Prefers Heat scale +2
Magic: Fire, Earth, Astral, Death.
Priests: Weak, with one medium priest, sacred Anakite giants"
#end

#selectnation 66
#name "MA Uruk" --
#era 2
#brief "Uruk is a nation of wild men, Enkidus, led by the Ensi kings and the high priestesses of the Sacred City."
#descr "Uruk is a warm plain inhabited by Enkidus, large, hairy wild men with horns and unkempt hair. Since the founding of Eridu, the First City, civilization has spread and the kingdom expanded. Other cities were founded in the image of Eridu, each with its own character. Administrators from the City of Scribes aided local rulers, while traders and merchants from the City of Trade improved the economic infrastructure of the kingdom. But the Ensi of Eridu lost power and petty kings of the new cities rose to power and claimed the Ensi title. Strife and turmoil tore the kingdom apart. One of the new cities, the City of Gods was blessed by the Awakening God and saw the first Entu of the Moon erect a great temple in the city. It soon replaced the First City as religious center and the Entu priestesses of the First City moved to the City of Gods, no longer bound in marriage to the ruling Ensi.
With the coming of the Awakening God, the city states have set their differences aside and joined a common cause. In the plains of Uruk the First City still stands as a symbol of civilization, although its temporal and religious power has diminished. Now each city has its own Ensi ruler. The wild men are no longer wild, and the shamans and Bone Readers of old have been replaced by the priests and mages of the cities."
#summary "Race: Large. Prefers Heat scale +1
Military: Enkidu Infantry and fearsome Mushussu Chariots
Magic: Astral, Nature, Earth, Water and some Air.
Priests: Strong, good at recalling a dead God."
#end


#selectnation 72
#name "MA Nazca" --
#era 2
#brief "Nazca is a necrocracy of living winged humanoids ruled by mummified dead kings."
#descr "Nazca is a mountain necrocracy of winged humanoids. It was once a far off Caelian colony, but with the fall of the Raptors and the disappearance of the Eagle Kings contact with Caelum was broken and the descendants of the Eagle Kings became Nazcan Sun Kings, Incas. With the demise of the last Eagle Kings steps were taken to preserve the wisdom of the kings of old. The necromantic practices of the Raptor clan were not banned in Nazca and the divine kings were mummified and preserved, should their advice be needed in the future. Priests of the dead began to mummify other influential members of society as well. Since old kings and queens were supposed to be wiser than the living, a council of mummies was formed to aid and guide the Incas. The priests would listen to the mummies and divine their will. Now Nazca has turned into a necrocracy, a kingdom ruled by mummies of the silent council. The Sun Kings rule in their name, but it is the mummies of ancient kings and their interpreters who have the true power in the kingdom. The mummies of nobles and priests are transported to and fro to decide in judicial matters as well as attending feasts and ceremonies. The royal mummies are too valuable to disturb unless the matters at hand are of utmost importance. The ice crafting of Caelum has been lost and Nazca use light armors of cloth and bronze. The Nazcan can field vast armies of unskilled soldiers. Commoners indebted to the mummies, allied soldiers from conquered human mountain kingdoms, and walking dead reanimated by the mummies of dead priests form most of the armies of the kingdom."
#summary "Race: Flying, cold resistant, commanders mummified on death, prefers Cold scale +1
Military: Flying units, free recruits of low quality, reanimated dead, sacred Sun Guard
Magic: Fire, Earth, Air, Death, Astral and some Nature
Priests: Powerful, undead priests can reanimate the dead"
#end

#selectnation 74
#name "MA Xibalba" --
#era 2
#brief "Cave dwelling amphibians that have replaced the bat people when their caves were flooded."
#descr "Xibalba is a vast realm of dark water-filled caverns beneath the forests of Mictlan. According to legend, the sun and the moon passed through the cavernous realm on their daily journey to the eastern horizon. On this journey they were guarded by the bat people, Zotz, that dwelled in the dark reaches of the Xibalban underworld. But the cavernous realm was struck by a great disaster. A star fell into the ocean and a great deluge flooded the caves of Xibalba. The bat people drowned or fled the caves, but other inhabitants soon emerged. The Zotz were replaced by refugees from the shattered Atlantis. The fallen star, or possibly the dark magic of Xibalba, changed the Atlantians. The Atlantians of Xibalba developed more toadlike traits and different broods emerged. They called themselves Muuch, toad people. Their kings, the Bacabs, mighty mages of the deluge, conquered the last Xibalban city and built a Muuch kingdom in the caves underneath the forests of Mictlan. After a while the Muuch began to settle the forests above their caverns and a new brood of Muuch appeared. A brittle alliance of Muuch and Zotz has formed in the forests. Meanwhile the Bacabs hunted down the remaining Zotz hiding in dried-out caves and forced them into servitude. Now Xibalba is a Muuch kingdom with a small subjugated Zotz population."
#summary "Race: Amphibious cave dwellers, a few Zotz remain, prefers Heat scale +1
Military: Amphibious infantry, flying stealthy light infantry
Magic: Water, Earth, Death, Nature and some Blood and Air
Priests: Average"
#end


#selectnation 88
#name "MA Atlantis" --
#era 2
#brief "Atlantis is an underwater nation of amphibious beings. They do not use missile troops. They have powerful Water mages and powerful priests."
#descr "When the Star fell into the sea, the Basalt City and the Dark Crystal were destroyed, the reign of the Basalt Queens was ended and the surviving Atlantians reformed the kingdom. Atlantis is an underwater nation of strange beings resembling a cross between fish, frog and human. Atlantians never stop growing and will live for several hundred years unless killed. The Atlantian society is organized in a strict hierarchy of size and age. The oldest and most cunning Atlantians are trained as priests or mages. Because the Atlantians find it difficult to use magic, they often capture human children and train them in magic in the Coral Towers. The soldiers of Atlantis use spears tipped with living coral shards and wear armor made of coral chunks. The coral is poisonous and is cultivated solely for purposes of war."
#summary "Race: Amphibious
Military: Coral-armed infantry, shamblers, war lobsters, no missile weapons
Magic: Water, Astral, Fire, Earth
Priests: Powerful"
#end

#selectnation 89
#name "MA R'lyeh" --
#era 2
#brief "R'lyeh is an underwater nation. An ancient race of mentally superior beings from a fallen star has enslaved a colony of Atlantians. R'lyeh has Atlantian slave troopers, strange hybrids and Illithids who use mind blasts. The Starspawns of R'lyeh are powerful Astral mages."
#descr "In ages past, a distant star inhabited by a great race of strange, alien beings was struck with an unimaginable catastrophe. The star fell from the heavens, breaking into tiny shards. One such shard fell through the Spheres and down upon the world. The shard came to rest on the ocean floor and there a remnant of this great race adapted and survived. They multiplied and enslaved a race of fishlike humanoids by sheer strength of mind.
R'lyeh, the Sunken City, is a mind-defying place built under the sea with an architecture unlike any known to man. In the halls of R'lyeh the Starspawns, the Great Ones who survived the Fall, plan the re-emergence of their Great Race. The Starspawns are powerful mages with great knowledge of distant stars and all of the Great Race are powerful mindcrafters.
All coastal forts of R'lyeh have a special well where women can submerge themselves in the hope of being impregnated by a Great One. However, most will be taken by Deep Ones instead, and the women's offspring will be strange, fishlike humanoids instead of the noble Starchildren they wanted. These half-human hybrids are usually devoted to the cause of putting mankind below the sea and often join the army of R'lyeh free of charge."
#summary "Race: Underwater
Military: Atlantian and Oceanian slaves, hybrids, Illithids
Magic: Astral, Water, Earth, some Glamour and Nature
Priests: Average, can summon Void Beings"
#end

#selectnation 86
#name "MA Pelagia" --
#era 2
#brief "Pelagia is an underwater realm of tritons and mermen. Tritons are unable to leave the sea, but mermen can shed their tails and walk on dry land. In recent times Pelagia has started to use bronze armor. Both races have mages, but only the merman mages can leave the sea."
#descr "Pelagia was the first kingdom to form in the deeps. It is a nation of tritons, humanoid beings with fin-like legs. Ruled by powerful triton priest-kings, it dominated much of the seas. After the devastating event that shattered the ocean depths, Pelagia quickly recovered. R'lyeh was destroyed and reformed under a strange race and Atlantis lost much of its former power when their basalt cities toppled and their kings were buried under broken pillars. Pelagia on the other hand was never dependent on the deeper seas and the Fallen Star did not touch their home. The triton kingdom survived and evolved. The Triton Kings of earlier times lost much of their priestly authority. Respected, but not worshipped like divine beings, they turned themselves from their lesser kin. Now they rule in name only, looking inwards and trying to master the secrets of the seas. The tribal division of the kingdom has lessened over time and the Shark Tribe and the Turtle Clan are now part of the greater Pelagian culture. The mermen and their coastal traders have found other partners since the destruction of Berytos, but they are still an important part of the Pelagian economy, and they have brought bronze to the deeps. Now Pelagian soldiers have abandoned the crude armor of earlier times and fight in armor of gleaming bronze. The former contacts with Berytos and Therodos has kindled an interest in Telkhine lore and secrets. With the final rest of Therodos the secrets of the Telkhines are available to Pelagian sages."
#summary "Race: Underwater
Military: Aquatic tritons and amphibious mermen. Light infantry, heavy infantry, sacred, aquatic knights
Magic: Water, some Astral, Nature, Air and Earth. Mages weaker on dry land. Mages can convert water gems into astral pearls
Priests: Medium, weak on dry land"
#end

#selectnation 87
#name "MA Oceania" --
#era 2
#brief "Oceania is a realm of the underwater wild and the clashing tides of the shores. The half-man inhabitants can remove their tails to raid and settle on dry land. The Capricorn is a powerful mage of the underwater wild and transition, whose powers changes when he leaves the sea. Sirens can take birdshape and lure enemies into the sea. Haliades, ancient sea nymphs serve as priestesses of the underwater wild."
#descr "Oceania is an underwater realm of half-men. Since the Atlantians emerged from the deeps, the half-men have lost more and more of their former domains. Ravenous deep ones have consumed fish and kelp alike. The kelp groves have been desecrated and murky water has spread in the kelp. Only with the Fall of the Star was the Atlantian onslaught halted. The Starspawns of the Sunken City enslaved the Atlantians and consumed their will. During the war between Atlantis and R'lyeh, a new God emerged from the depths and the Capricorns able to muster their forces. Now it is time to reclaim the deeps and conquer the world. The Capricorns, wild mages of the sea and the shores lead the nation in the conquest of a sea once theirs. Sirens, mermaids with shapeshifting powers, who lure men to watery graves with their beautiful songs, aid them in conquering the shores."
#summary "Race: Underwater
Military: Amphibious half-men. Light infantry, medium infantry, sacred, aphroi ichtycentaurs
Magic: Nature, Water, Glamour, some Air and Earth. Mages weaker on dry land
Priests: Powerful, underwater only
Dominion: +1 turmoil in coastal provinces, +1 order in other provinces"
#end

#selectnation 85
#name "MA Ys" --
#era 2
#brief "Once a city of unrivaled splendor Ker-Ys was sunken beneath the waves as a place of refuge for the tuatha of Tir na n'Og. Ker-Ys is now inhabited by mermen known as merrow and the Morgen descendants of the Tuatha sorceresses that fled the fall of Tir na n'Og. With the coming of the new god the city has risen from beneath the waves and the splendor of the bronze-walled city has returned for all to witness."
#descr "Ker-Ys was a tuatha city of unrivaled splendor. It’s walls of crystal and bronze rose above the shores of Kernou, a former Marverni province conquered by the tuatha of Tir na n'Og. Through trade and sorcery it became a city of marvels inhabited by tuatha, humans and merrow, a race of mermen that lived in the seas near Tir na n'Og and Kernou. 
With the fall of Tir na n'Og, Dahut, a mighty tuatha sorceress and queen of the city, hid Ker-Ys beneath the waves, creating a refuge for the sorceresses of Tir na n'Og. The city became inhabited by tuatha and their Merrow allies. 
Living in the enchanted city underneath the waves transformed the tuatha and they turned themselves into Morgen, a superior race of semi-divine beings, who are to the merrow what the tuatha were to men. 
Ys is an underwater queendom ruled by Morgen. Humans of Kernou ancestry comprise most of the coastal population."
#summary "Race: Humans on land and Merrow under water ruled by the Morgen.
Military: Merrow and Human infantry and cavalry. Sacred Morgen elite units. All but the humans are amphibious.
Magic: Glamour, Water, Earth, some Astral, Nature and Fire.
Priests: Average"
#end


#selectnation 95
#name "LA Arcoscephale" --
#era 2
#brief "An ancient human kingdom led by Astrologers, Arcoscephale mainly uses heavy infantry backed up by strong ape warriors from a distant land and heavily armed war elephants. Both Sibyls and Mystics are powerful Astral mages. The priestesses of Arcoscephale have some skill in Nature magic and can heal wounded soldiers."
#descr "Arcoscephale is an old kingdom that once ruled much of the known world. With the fall of the Old Kingdom centuries ago, tradition was the only thing that remained to the population. Mystics and priestesses of the old cult still serve the kings of Arcoscephale. The infantry and cavalry are still hopelessly archaic, but the Awakening of the New God has brought some changes. Some traditions have been abandoned and the cavalry has been improved. Skilled and lightly armed phalangites are starting to replace the heavier hoplites and the cardaces. Although the wise Astrologers who aided past kings were killed or disbanded, a new breed of seeresses called the Sibyls has appeared. The Sibyls offer great help in maneuvering the once-mighty kingdom to a powerful platform for the Awakening God. Priestesses with great knowledge of healing are trained in ancient temples built during the peak of the Old Kingdom. The priestesses are able to scry upon enemy troops and provinces that are located within the God's Dominion.
The former conquest of the known world has led to an acceptance of strange cultures and beliefs. The Arcoscephalian population re quick to adopt foreign cults, but only to incorporate them into their own belief system. The Awakening God is viewed as the Master of All and all other gods are just aspects of the Great One. Temples and religious sites of other faiths are converted and the faith of the Awakening One is imposed upon newly conquered lands."
#summary "Race: Humans
Military: Heavy spear-armed infantry, elephants, companion cavalry, ape warriors
Magic: Astral, Nature, Fire, Earth, Water, Death and some Glamour
Priests: Average, healing
Dominion: Scry (accurate and automatic military reports inside dominion)
Syncretism: Enemy temples are not razed, but converted if a priest is in the army. God starts with one additional divine title."
#fortera 3
#end

#selectnation 98
#name "LA Pythium" --
#era 2
#brief "Pythium is a splinter empire that broke free from Ermor when it fell. Pythium uses legionnaires, but also has Serpent Cataphracts and hydras. Since the heyday of the Empire, the Theurgs have lost much of their power. Instead, a multitude of heretical mystery cults flourish."
#descr "The Emerald Empire of Pythium was a splinter empire of the great Empire of Ermor. As dark arts were practiced in the heart of the Empire, the stars warned the Theurgs of Pythia to flee the impending doom. They led Pythia away from the falling Empire and formed an imperial theocracy under their wise rule. As Ermor slowly crumbled, the Emerald Empire struggled to keep the old Ermorian provinces under their rule. From these provinces came strange cults and foreign beliefs. Just as Ermor was seduced by the C'tissian cults of Death, the Pythians were fascinated by the exotic practices of the lizardmen. With shadows lingering near, the C'tissian cults were particularly seductive. No other people had such knowledge of Death and the dead. The popularity of the Theurgs diminished and the Serpent Cult gradually replaced the old state cult. But the Serpent Cult was not the only foreign cult that got a foothold in the Empire. Heretical mystery cults flourish and threaten to cast the Empire into disorder.
Pythium uses a reformed legionnaire army with frontier soldiers and mobile field troops. The Serpent Cataphracts have received special status and they have become the most respected force in the Empire."
#summary "Race: Humans
Military: Heavy legionnaires, sacred Serpent Cataphracts, gladiators, sacred hydras
Magic: Access to weak mages of all paths, with stronger mages of Nature
Priests: Weak, one available priest of average level. Heretical mystics who lower Dominion."
#fortera 3
#end

#selectnation 99
#name "LA Lemuria" --
#era 2
#brief "Lemuria is a withering realm of ghosts and shadows. Sceleria, the surviving part of old Ermor was destroyed due to its dependence on the living dead. Now spectral legions of the former empire reenter a world through the soul gates created by the thaumaturgs."
#descr "With the second fall of Ermor, hope finally came to the scelerian remnants of the ancient empire. The fear of the dead ceased and undead legions were no longer needed. Instead the soulless were put to menial labor. But the Thaumaturgs turned their attentions elsewhere. The common people became ever more dissatisfied. Some soulless slaves still toiled the land, but with the Thaumaturgs less interested in reanimating slaves for the populace, the common men felt abandoned. Demands were made that the Thaumaturgs should provide slaves to keep the kingdom going. The conflict escalated and finally, in an act of remarkable hubris, the Thaumaturgs decided to settle the problem once and for all. In a great ceremony every Thaumaturg in the kingdom joined a communion and poured their lower souls into a ritual that would open a gate to the underworld, so that the dead willingly might return to the land of the living as workers and farmers. the ritual succeeded, in a way. The gate opened, but the lower souls of the thaumaturgs were ripped apart and swallowed by the gate. And from the gate emerged, not dead servants, but a spectral host of legionnaires and shadows. Now the land is slowly withering and falling under the dominion of a God of darkness. Ghosts and spectral legions reclaim a land once theirs and the shattered souls of the former Thaumaturgs are mustering the shadows and memories of a glorious past."
#summary "Race: Ghosts and shadows. Do not need supplies, can enter water. Do not recruit regular armies, but summons or reanimates spirits of the dead.
Military: Spectral legionnaires, ghosts, shadows and hordes of dispossessed spirits.
Magic: Death, Astral, and some Air and Water. Increased research in magic lands.
Priests: Powerful. Immortal. All priests can call shadows and spirits.
Dominion: Summons ghosts and shadows. Kills population."
#end

#selectnation 100
#name "LA Man" --
#era 2
#brief "Man is a feudal kingdom of humans who have almost lost the magic of an earlier age. They use knights, skilled longbowmen and crossbowmen. They have mage scholars who are able to study in magically drained lands. The surviving Wardens of Avalon are sacred stealthy troops."
#descr "The realm of Man is a feudal kingdom. Their kingdom was established by conquering a race of tall and magically powerful beings known as the Tuatha. When the Tuatha were destroyed, their magic was taken by the Witches of Man. They helped Man to grow in power and influence, but with the great magic came a great Curse and the Witches dwindled in number and magic left the kingdom. To contain the Curse, the Old Magic was banned and a scholarly order of Magisters replaced the Witches of Avalon and their wild ways. The infantry of Man has evolved since the Age of Avalon and the crossbow is common, but knights and longbowmen still make up a large part of the armies. The Wardens of Avalon have escaped the Curse and are the only remnant of the Old Ways."
#summary "Race: Humans
Military: Infantry, longbowmen, crossbow-equipped heavy infantry, knights, Wardens of Avalon
Magic: Air, Earth, Astral, some Fire and Glamour, rarely Death. Mages' research not affected by Drain scales.
Priests: Average, inquisitors"
#fortera 3
#end

#selectnation 101
#name "LA Ulm" --
#era 2
#brief "Ulm is a human kingdom destroyed by civil war and a great curse. Hunger for mortal flesh plagues the nobles of the land. An Iron Inquisition controls the kingdom and all magic is banned. Secretive occultists of the Illuminated Order hide in the shadows and manipulate leaders near and far."
#descr "After years of civil war, the Iron Kingdom crumbled. During the Night of Treason a great Malediction was placed upon the kingdom. The forests became dark and hostile. Wolves and creatures even worse stalked the land. Slowly the kingdom recovered, but it was not what it once was. The knightly order was all but destroyed and the Master Smiths had disappeared. The secrets of blacksteel were forgotten. An order of Black Priests emerged in Ulm in the last days before the civil war. They formed an Iron Cult, consolidated their position and forbade the use of magic. Magic outside religion was announced to be sacrilegious and the few surviving Master Smiths were put to the flames. Although magery is forbidden, there are some fortune tellers and members of the Order of the Illuminated Ones who secretly ply their trade in the arcane."
#summary "Race: Stocky humans, production bonus in all castles
Military: Medium infantry, stealthy rangers, knights, ghoul guardians
Magic: Astral, Blood, some Earth, Air, Death and Nature, rarely Fire and Glamour.
Priests: Weak, inquisitors"
#fortera 3
#end

#selectnation 103
#name "LA Marignon" --
#era 2
#brief "Marignon is a human kingdom based on religious zeal. Missionaries sail out to spread the word of the True God. Marignon has powerful priests as well as Fire and Blood mages."
#descr "Marignon is a feudal theocracy that rose out of the ashes of Ermor. Through religious austerity and fanaticism the young kingdom prevailed when death walked the land. When kingdom after kingdom crumbled under the might of the Ashen Empire, the leaders of Marignon turned to desperate measures. The Grand Masters of the House of Fiery Justice struck a bargain with infernal forces. Devils started to fill the ranks of the human armies and with time Marignon became dependent on devils to survive. Devils and the Holy Knights of the Chalice were all that kept death at bay. In a cataclysmic battle the knights fought a great army of walking dead. Both armies were annihilated, but new Ermorian legions would soon re-emerge from the ashen realm. The Grand Masters called their Infernal Lords and a host of demons was released upon Eldregate. The Holy Chalice was captured and brought to the House of Fiery Justice. Ermor was destroyed, but the Infernal Lords demanded continued sacrifice and devil-worship became part of the faith. Imps are bound as jesters and servants and most noble families have their own imp familiar.
Order has returned to the kingdom and Marignon is slowly turning its interests outwards. Recent developments in shipbuilding and navigation have allowed the priests and nobles of Marignon to expand the influence of God to distant shores. To bring the True Faith to the heathens has become more important than hunting heretics at home. Witch Hunters have been replaced by Navigators and Chartmakers who serve under the command of admirals to spread the might of the kingdom to distant shores."
#summary "Race: Humans, Ocean sailing, trace income across oceans
Military: Heavy infantry, crossbows, Flagellants
Magic: Fire, Blood, Glamour, Astral, Earth, Air, some Water and a little Nature
Priests: Powerful, Inquisitors, can perform blood sacrifices
Inquisition: Automatically reduces enemy dominion and spreads own dominion up to 1 in owned provinces"
#fortera 3
#end

#selectnation 111
#name "LA Mictlan" --
#era 2
#brief "Mictlan is an old kingdom taken over by Atlantian Kings. Their God hungers and must be sated with blood sacrifice. Mictlan has powerful Water and Blood mages and priests, but its infantry uses archaic weapons."
#descr "When Atlantis was destroyed by R'lyeh and the Atlantians scattered, some fled into the deep swamps and jungles of Mictlan. Here they found a people who worshipped the Rain as one aspect of their God. The Atlantian Kings became Kings of Rain and reshaped the faith to their needs. They found the secrets of the long abandoned Blood Cult and reinstated the foul practices of ancient times. Then the New God rose, hungry for blood. Now Mictlan is once again expanding its territories to feed the hunger of its Lord. Isolation has made Mictlan a backward nation and its warriors use archaic weaponry and armor. The armies are mainly composed of slaves from newly conquered lands. The mage-priests of Mictlan celebrate the two Faces and the two Dominions of the Hungry God, namely the Sun and the Moon, the Rain and the Forest."
#summary "Race: Humans and Atlantians, prefers Heat scale +1
Military: Light infantry with slings and javelins, tribal kings can levy slaves, sacred Jaguar and Eagle Warriors. Sacred Atlantians that can enter the sea.
Magic: Water, Blood, Fire, Astral, Nature
Priests: Powerful, can perform blood sacrifices, Dominion does not spread unless blood is sacrificed"
#end

#selectnation 109
#name "LA T'ien Ch'i" --
#era 2
#brief "The Celestial Empire is crumbling and the Bureaucracy is all but destroyed. The Imperial Guard is no more and the cavalry of old has been replaced by skilled barbarian horsemen. Ancestral worship is popular once more and barbarian priest-mages of an Ancestor Cult are replacing the priests of the Bureaucracy."
#descr "The Celestial Empire is crumbling. Constant invasions from the barbaric khans have all but destroyed the Imperial Bureaucracy. The Imperial family has been replaced by Barbarian Kings. The Imperial Guard is no more and the cavalry of old has been replaced by skilled barbarian horsemen. Ancestral worship is popular once more and priest-mages of barbarian heritage who lead the Ancestor Cult are replacing the priests of the Bureaucracy. With the displacement of the eunuchs from power, conscription has fallen out of use."
#summary "Race: Humans
Military: Cavalry, heavy infantry, archers.
Magic: Water, Earth, Death, Nature, Air, Astral and some Glamour, Summon Celestial Beings
Priests: Weak"
#fortera 3
#end

#selectnation 110 -- 
#name "LA Jomon"
#era 2
#brief "Jomon is a feudal nation of human warlords and their samurai warriors. Ninja assassins complement the military forces."
#descr "The rice fields of Jomon were the first to be attacked by the Bakemono onslaught. After years of slavery and mistreatment, the human inhabitants rebelled as the Bakemono had once rebelled against their Oni masters. One by one the Bakemono tribes were replaced by human Daimyos and their sworn warriors. A strict, feudal warrior society replaced the disorganized rule of the Bakemono Kings. Even war has become ritualized and peasants are left largely in peace. With the coming of the God, the Daimyos have joined forces and look for other realms to conquer."
#summary "Race: Humans
Military: Light infantry, samurai archers, samurai infantry, samurai cavalry, ninja assassins
Magic: Weak. Astral, Earth, Nature, Fire, Air, Water. Many national summons
Priests: Average"
#fortera 2 -- I think they already have this, but just in case
#end

#selectnation 102
#name "LA Agartha" --
#era 2
#brief "A cavern realm of humans who worship and consult the remains of the older race of Pale Ones. Cave drakes are tamed and used as mounts for their knights. Ktonian necromancers skilled in Death and Earth magic reanimate the dead so they can continue to assist the realm."
#descr "In dark caverns under the Roots of the Earth a strange kind of one-eyed humanoids once evolved. Untouched by the sun, they became known to humans as the Pale Ones. When humans first met these pale giants, it was in war. With the destruction of the false god of the Pale Ones, an ancient Seal was broken and vast powers of destruction were released. The Pale Ones were almost wiped out of existence and humans could move down into the caverns of Agartha. Here they found fabulous riches and ancient secrets. The humans replaced the Pale Ones and now all Agarthans are pale-skinned humans with large eyes. Everything left by the Ancients became subject to worship in Agartha. At first, statues of the Ancients were adored and animated by the Golem Crafters, but most of the statues were destroyed during the great war and new forms of worship have evolved. The mummified remains of the now-extinct Pale Ones are worshipped and reanimated by necromancer-priests. While the mummies of Pale Ones are sacred, the human dead are not treated with the same respect. Used for menial tasks and warfare, the dead of Agartha now walk side by side with the living."
#summary "Race: Humans with limited darkvision. Extra gold and resources in cave forts.
Military: Light and heavy infantry, steel crossbows, cave drake knights.
Magic: Earth, Death, Fire, some Water and Astral
Priests: Average"
#fortera 3
#end

#selectnation 104
#name "LA Abysia" --
#era 2
#brief "Abysians are lava-born humanoids that radiate heat. With the dilution of their blood, humanbreds have become increasingly common and now pureblooded Abysians are rare and sacred. Abysians mainly use heavy infantry. They have skilled Fire, Astral and Blood mages and their priests can perform blood sacrifices. Abysians dislike cold provinces."
#descr "When the Warlocks began their horrible breeding experiments, they unknowingly spelled the doom of Abysia. But it was not the Demonbreds that posed a threat. The real threat came from the Humanbreds, who where multiplying and swarming the kingdom like vermin. Now the heat of the Smouldercone is faltering with the declining number of pure Abysians and magic is seeping from the land. Other sources of magic are needed and the Blood Cult of ancient times is renewed with fervor. Pureblooded Abysians, now rare, serve as priests and sacred warriors."
#summary "Race: Humanbred Abysians. Fire resistance, prefers Heat scale +2, wasteland survival. Death and Growth scales have half the standard effect on income and population growth and no effect on supplies.
Military: Light and heavy infantry, axe throwers
Magic: Fire, Blood, Astral, Death, some Earth
Priests: Powerful, can perform blood sacrifices"
#fortera 3
#end

#selectnation 106
#name "LA Caelum" --
#era 2
#brief "Caelum is a magocracy of winged mountain beings. The mages are skilled in Air, Earth and Death magic. They also have Earth smiths capable of producing magic items with very few magic resources. Caelum has very skilled archers and trains mammoths."
#descr "Caelum is a magocracy of winged humanoids who inhabit the highest mountain peaks. In ancient times, there were three Caelian clans led by semi-divine beings known as Yazatas. Centuries ago the Harab Seraphs of the Raptor clan were accused of polluting the purifying flames and tainting the sacred task of the Seraphines. They were condemned by the High Seraphs of the Airya clan and civil war broke out. The Raptors were banished and scattered across the world. But now a new God is rising and the scattered tribes have gathered. The Raptors have returned to Caelum and overthrown the magocracy. Harab Seraphs, the mage-priests of this new and dark faith, have replaced the High Seraphs and black-winged Raptors have become the ruling elite. Now the Raptors have cast their eyes upon other nations. The Harab Seraphs are skilled in Air, Death and Earth magic. A few of the Airya Seraphs remain, but the ice crafters have been replaced by iron crafters, Raptorian mage-smiths who forge weapons of  iron and steel. The secrets of the magical ice of former times are all but forgotten. Caelians are thin and light. The Raptorians are slightly stronger and are martially superior to the other clans. They are not as resistant to the elements as the other Caelians. Airya clan Caelians are resistant to cold, but few of them remain. Spire Horn Caelians are less resistant to cold but have partial resistance to lightning. They are skilled archers and prefer hit-and-run tactics, even though they do have some heavy troops, such as huge Mammoths."
#summary "Race: Flying, cold resistant, prefers Cold scale +1
Military: Flying units, skilled archers, mammoths
Magic: Air, Death, Earth, some Water and Fire
Priests: Average"
#fortera 3
#end

#selectnation 113
#name "LA C'tis" --
#era 2
#brief "C'tis is an ancient kingdom of lizardmen. They do not use cavalry or archers. C'tis has powerful priest-kings and Death mages able to reanimate mummified kings of ancient times. The lizards dislike cold provinces."
#descr "C'tis is a river valley surrounded by sandy deserts. Once the valley was fertile and great swamps surrounded the great river. Now the deserts spread and the swamps grow fewer and smaller each passing year. The valley is the home of an ancient sacral kingdom of lizardlike humanoids. In ancient times, the High Priests of C'tis mastered the craft of embalming to preserve the remains of their kings. Since the dawn of the kingdom, tombs have been constructed in the desert to contain the mummified kings and priests. With the Awakening of the God, the Sauromancers, great mages of death and rebirth, have re-emerged and taken the place of the Marshmasters. Through studies of ancient lore they have perfected dark rituals that awaken the kings of old to lead the stirring dead as the Lizard Kings lead the kingdom of the living. At the top of the C'tissian society is the Lizard King. The King is the highest priest of C'tis. Under the King are the High Priests and the enigmatic Sauromancers. After a great rebellion most of the carnivorous lizardmen were slain or fled to distant lands. There is a widespread fear that the predators and their Sobek masters will return as foreseen in their Seventh Book. The C'tissians are somewhat slow in movement, but have thick hides that protect them from cuts and bruises. Both lizardmen are cold-blooded and become exhausted very quickly when fighting in cold provinces. They have partial resistance to poison. The inhabitants of C'tis prefer to live in warm provinces. The Tomb Kings and Tomb Priests are able to reanimate the dead."
#summary "Race: Thick hides, cold-blooded, poison resistance, prefers Heat scale +2. Reanimated dead
Military: Infantry, undead
Magic: Death, Fire, some Nature, Astral and Earth
Priests: Powerful, undead priests can reanimate the dead."
#fortera 3
#end

#selectnation 97
#name "LA Pangaea" -- 
#era 2
#brief "Civilization has finally reached Pangaea and the halfmen have built cities and are using iron armaments. The strong and well-armed minotaurs and centaurs are formidable warriors, but the priests have diminished in power."
#descr "Pangaea is a woodland nation inhabited by wild beings connected with nature. Halfmen such as satyrs, centaurs and minotaurs serve the lords of the Sacred Groves deep in the forests. In ancient times, the woods covered much of the world, but that has changed. Civilization has finally reached the forests of Pangaea. The old ways are giving way to new traditions. Archaic weapons are replaced by new ones of tempered steel. Ancient cultic practices have all but disappeared and human females once attracted to the wild dances and songs no longer seek the revelry of the Panic tunes."
#summary "Race: Forest beings, stealthy troops, troops will heal battle afflictions
Military: Infantry composed of minotaurs, centaurs, satyrs and sacred dryads, centaur cataphracts
Magic: Magical Tunes, Nature, Earth, some Astral, Water and Air
Priests: Weak"
#fortera 2
#end

#selectnation 115
#name "LA Midgård" --
#era 2
#brief "Midgård is a human nation whose religious leaders are the few remaining Vanir. Vanir can sail across the oceans and hide themselves with illusions. They mostly use infantry, but utilize many unique troops, including human berserkers and skinshifters. Their human mages are accomplished at Air and Astral magic."
#descr "Once Midgård was called Vanheim, home of the Vanir. But since the coming of man, the Vanir have dwindled in number. At first, the Vanir were the undisputed rulers of the land, but the growing human population has taken over the land and renamed it Midgård. Only a few Vanir survive, but their magic has not yet departed the land. The Vanir are sacred to the human population and the few surviving Vanjarls carry great influence. The humans of Midgård themselves have become altered by the ancient magic of the Vanir and skinshifters are more common than they once were."
#summary "Race: Ocean sailing, trace income across oceans, illusions, prefers Cold scale +1
Military: Heavy infantry, skinshifters, berserkers, Vanir
Magic: Air, Astral, Blood, Earth, Death and some Glamour
Priests: Average, can perform blood sacrifices"
#fortera 3
#end

#selectnation 117
#name "LA Utgård" --
#era 2
#brief "Utgård is the home of the giants of the north. Jotuns are immune to the cold and dislike hot lands. With their numbers dwindling, the giants have allied with humans. They don't use heavy cavalry or bows. The human Norns are versatile and powerful sorceresses and seeresses."
#descr "Utgård is a land of bitter winters and cool summers. It was once Jotunheim, the home of giants. But with the coming of man, their population has dwindled. After man ventured to the icy lands of Jotunheim, the giants of Jotun discovered the humans to be resourceful allies. With the Awakening God, all grudges have been cast aside and men and giants fight side by side. The alliance with the humans has estranged the Gygjas and their Vaetti servants, who no longer aid the giants. Instead, human seeresses have become influential. In the heart of Utgård lies the magical Well of Urd where the Norns gather and divine the future of the world. The giants of Utgård are immensely strong and resilient. They are born in the cold and do not suffer from cold climates. The people of Utgård prefer to live in cool provinces."
#summary "Race: Cold resistant, prefers Cold scale +1
Military: Giant infantry, human infantry
Magic: Water, Astral, Death, Glamour, Blood and some Nature
Priests: Average"
#fortera 3
#end

#selectnation 116
#name "LA Bogarus" --
#era 2
#brief "Bogarus is a nation of humans who have replaced the Vanir as rulers of a cold and inhospitable land. From mighty cities, princes and religious leaders carve an empire out of the frozen lands. Mages of various traditions ply their trade sponsored by the princes. In villages across the land, fanatic cults of flagellants have formed."
#descr "Bogarus is a land of harsh winters and short summers. When the Vanir claimed this cold and bitter land of the north, they named it Vanarus and carved a kingdom out of the frozen land. Now humans have replaced the last of the Vanjarls and the kingdom is guided by Eparchs and Exarchs of the religious order. Mighty cities under the rule of warring princes have united under a few Grand Princes and a reformed faith. Bogatyrs of heroic stature and prowess, defenders and champions of the faith, occasionally emerge to lead and protect the people from the wicked.
The Grand Princes use infantry as well as elite cavalry forces. Mages of various traditions ply their trade in the palaces of the Grand Princes. The people of Bogarus prefer a cold climate."
#summary "Race: Humans with partial cold resistance, prefers Cold scale +2
Military: Heavy cavalry, mounted archers, infantry
Magic: Fire, Astral, Blood, some Air and Death, Summonable beings of earlier eras
Priests: Powerful"
#fortera 3
#end

#selectnation 108
#name "LA Patala" --
#era 2
#brief "Patala is a realm of intelligent apes ruled by Nagas, divine serpent beings of the Underworld Realm of Patala."
#descr "In the dense forests of the Bandar realm, apes of uncanny brightness have emerged. Under the influence of semi-divine beings, the apes evolved intelligence and culture. When the former rulers of Bandar Log returned to their Celestial Realms, the apes were left without leadership and innovation in the nation ground to a halt. A warlike hierarchical society was formed with the large Bandar apes at the top. Later, Nagas arrived from the Nether Realm of Patala, from where all rivers spring. The Nagas are divine beings of the Underworld and its rivers and are to the apes what the Yakshas had been in ages past. With mesmerizing stares and dancing serpentine bodies, they entranced the Bandar Log and claimed their empire as their own. Patala is a divided society. Small Markatas are at the bottom of the society. Vanara apes of human size are the most common. Large Bandar apes rule most of the society and form the military. Above all are the sacred Nagas and their kings."
#summary "Race: Nagas and apes, prefers Heat scale +2
Military: A multitude of missile weapons, light and medium infantry, sacred naga warriors
Magic: Water, Earth, Nature, Astral and Glamour
Priests: Average"
#fortera 3
#end

#selectnation 107
#name "LA Gath" --
#era 2
#brief "Gath is a nation of human tribes subjugated by the giants of Gath, the last of the Rephaim."
#descr "Gath is a dry land that has only recently recovered from the devastation caused by its earlier inhabitants. For ages the land has been dominated by giants, but under constant pressure from human immigrants and the Abysian Tide of Fire, the original inhabitants of the land were forced to retreat and watch as city after city was destroyed. Now there is but one city left: Gath, the City of Giants. The Gittite descendants of the Anakites of Ashdod still dominate the surrounding land and have subjugated several human tribes. While the human tribes comprise much of the population of the kingdom, the Gittites are the undisputed rulers of the land. By keeping iron-working from the human population and through a strictly centralized cult focused around bloody sacrifices at the Great Temple, the Gittites have kept control of the land. The Gittites are small compared to the ancient Rephaim, but still large by human standards."
#summary "Race: Gittite giants and humans. Prefers Heat scale +1
Military: Gittite infantry, several human tribes with different skills.
Magic: Fire, Earth, Astral, Blood, Nature, Death.
Priests: Medium with powerful priest at capital, sacred Gibborite giants, can perform blood sacrifices."
#end

#selectnation 105
#name "LA Ragha" --
#era 2
#brief "Ragha is a dual kingdom of cold resistant and winged Airyas and heat resistant Turans. The mages are skilled in most paths except Nature. Ragha has skilled archers and trains Gryphon rider Immortals."
#descr "Ragha is a dual kingdom of fire and ice, rage and serenity. Half of the population are Abysian descendants from the isolated colony of Tur, and half the population are Airyan refugees from Caelum. Tur was a distant and prosperous Abysian colony founded after a successful military campaign against the giants of Ashdod. But the war with Ashdod had been taxing and the colony was cut off from the kingdom by a Arcoscephalean campaign through the fertile lands previously conquered from the giants. For centuries Tur was left alone and an independent kingdom formed. Then came the Caelians. A great host of iceclad warriors descended upon the Turan armies on the plain of Ragha in the mid of winter. The Turan Shah realized that Tur could not stand up to the Caelians for long. Tur was on the brink of destruction when the attacks suddenly stopped. Civil war had broken out in Caelum and the campaign was aborted. Instead Caelian refugees and deserters settled on the plain of Ragha. Airyan Seraphs approached the Turan Shah and peace was negotiated. When the Harab Seraphs of Caelum attacked, the Airyas were saved by the Gryphon riders of Tur. This sealed the truce and a strange alliance was formed. Ragha is now a society of two peoples united out of necessity. During winter the Airya reigns and during summer the Tur reigns. Even faith has evolved to mimic the legacy of the two peoples. Two different groups of beings are adored and worshipped. But this is starting to change. The One True God has arisen. The peoples of Ragha suffer less from hot or cold climates than other nations."
#summary "Race: Flying, cold resistant, heat resistant, do not suffer as much from heat or cold
Military: Flying units, gryphon riders
Magic: Air, Water, Astral, Fire, Death and Blood
Priests: Average, Guardian spirits, Temples expensive but generate fire gems."
#fortera 3
#end

#selectnation 112
#name "LA Xibalba" --
#era 2
#brief "Cave dwelling bat people that have returned to their ancestral home. Here they awoke powerful amphibious beings that became their masters."
#descr "Xibalba is a vast realm of dark caverns beneath the forests of Mictlan. Living in the caverns were the bat people, Zotz, but that changed when the cavernous realm was struck by a great disaster. A star fell into the ocean and a great deluge flooded the caves of Xibalba. The Zotz were almost wiped out and their realm was conquered by atlantian refugees. For a long time the toad people ruled Xibalba and became powerful. Eventually the Bacabob left the caverns to conquer the sun-lit world. There they met Mictlan and the Lawgiver. The humans were more numerous and while the Xibalban Bacabob were mighty, they could not prevent the death of their kin. Slowly the Xibalbans were decimated and the Bacabob withdrew into the flooded city and fell into a centennial torpor. When the caves begun to dry up the Zotz started to return in numbers. In the still waterfilled depths of Xibalba the Zotz priests found and unwittingly awoke the Bacabob. Now the Zotz once more inhabit their ancestral home, but serve the divinities of subterranean waters and the Awakening God."
#summary "Race: Swarms of cheap, flying, stealthy cave dwellers, a few Muuch toad men remain. Prefers Heat scale +1
Military: Flying, stealthy light infantry, amphibious infantry
Magic: Water, Death, Earth, Blood, Nature and some Air
Priests: Powerful, can perform blood sacrifices"
#fortera 2 -- actually listed as very primitive forts, so maybe fortera 1?
#end

#selectnation 126
#name "LA Atlantis"
#era 2
#brief "Atlantis is a nation of amphibious beings that have been forced out of the water. They do not use missile troops. They have powerful Water and Death mages who can sail across the seas."
#descr "With the Second Fall of Atlantis and the demise of the Coral Queens at the hands of R'lyeh, the Atlantians were forced to retreat from the seas. A few surviving Kings of the Deep entered a pact with a sleeping God at a forsaken coast of ice and bones. The Atlantian Angakut, Shaman Kings, lead the Bone Cult and practice Death magic previously unheard of in Atlantian history. The Angakut have coerced captured Caelian ice crafters to yield the secrets of their skills and now most of the Atlantians use arms of enchanted ice. Even their great city is built on interlinked ice floes."
#summary "Race: Amphibious, ocean sailing, trace income across oceans, prefers Cold scale +2
Military: Polearms, magical ice armaments, no missile weapons other than harpoons
Magic: Water, Death, some Air, Earth and Astral
Priests: Medium"
#fortera 3 -- does this mess up their ice forts?
#end

#selectnation 127
#name "LA R'lyeh" --
#era 2
#brief "R'lyeh is an underwater nation. A God Dreaming of the Void is awakening and inflicting insanity on this world. The army of R'lyeh consists of madmen, Void Beasts, Atlantian slave troopers, strange hybrids, and Illithids who use mind blasts. The Starspawns of R'lyeh are powerful Astral mages."
#descr "In ages past, a distant star inhabited by a great race of strange, alien beings was struck with an unimaginable catastrophe. The star fell from the heavens, breaking into tiny shards. One such shard fell through the Spheres and down upon the world. The shard came to rest on the ocean floor and there a remnant of this great race adapted and survived. They multiplied and enslaved a race of fishlike humanoids by sheer strength of mind and conquered the underwater realms of the world.
In the halls of R'lyeh the Starspawns, the Great Ones who survived the Fall opened a gate into the Void and unleashed its horrors upon the world. But the Void was not to be controlled even by the Starspawns. The very fabric of the Veil was weakened and madness struck the inhabitants of mighty R'lyeh. Only the most powerful of the Starspawns were able to keep their minds intact. The Empire crumbled as insanity took the leaders and the former slaves and servants of the Empire were able to lift the yoke of R'lyeh.
But now a God is awakening, and it is a God Dreaming of the Void. Mind-defying Dreams of the Sleeping God are plaguing the inhabitants of coastal and underwater cities and with the Dreams come the horrors. Strange, cannibalistic cults worshipping the Void call them from Beyond. The Dreamlands of R'lyeh threaten to destroy the world.
All coastal forts of R'lyeh have a special well where women can submerge themselves in the hope of being impregnated by a Great One. However, most will be taken by Deep Ones instead and the women's offspring will be strange, fishlike humanoids instead of the noble Starchildren they wanted. These half-human hybrids are usually devoted to the cause of putting mankind below the sea and often join the army of R'lyeh free of charge."
#summary "Race: Underwater
Military: Atlantian and Oceanian slaves, hybrids, Illithids
Magic: Astral, Water, Glamour, Earth and some Nature
Priests: Average, can summon Void Beings, might get additional insane prophets
Dominion effect: Kills population. Creates dreamers, madmen and Void Beings. Makes all non-Void Beings insane."
#fortera 3
#end


#selectnation 125
#name "LA Erytheia" --
#era 2
#brief "Erytheia is a coastal realm of mermen, Tritons and humans. Tritons are unable to leave the sea, but mermen can shed their tails and walk on dry land."
#descr "Trade and contacts with dry land have increased to the point where Pelagian mermen have established colonies in coastal lands. A former Arcoscephalian colony and the Pelagian colony of Erytheia, the Red Land, were joined through marriage. When the Triton Kings of the deeps succumbed to a strange slumber the former capital of Pelagia was almost abandoned. The mermen had become more numerous and those Tritons who did not succumb to sleep gradually became a privileged minority ruling the scattered Pelagian seas. Eventually civil war between the Triton princes broke out. While the Tritons battled in the seas, the mermen withdrew and formed a new coastal kingdom of mermen, Tritons and humans in Erytheia. When the Triton principalities isolated themselves the Pelagian traditions and legacy were carried on by the mystics of the Red Land. Under the rule of the mermen - Kings of Both Worlds - the former colony thrived and expanded on land and in the seas.
Now Erytheia is a coastal kingdom with some under-water provinces governed by a marginalized Triton nobility unable to visit the high court of the merman king. The Tritons resent the current situation and some fear this might lead to a another civil war. Triton nobles and generals have started to gather armies to reclaim the deeps once theirs to gain wealth, or fiefdoms, or simply to prove their worth to the Kings of Both Worlds."
#summary "Race: Land and underwater, prefers Heat scale +1
Military: Amphibious mermen, aquatic Tritons and some humans. Light infantry, heavy infantry
Magic: All Elements, Astral and some Nature. Triton mages can convert water gems into astral pearls
Priests: Strong, but possibly insane."
#fortera 3
#end


#selectnation 6
#name "EA Mekone" -- checked
#era 2
#brief "Mekone is a marvelous city inhabited by arrogant and warlike Gigantes who have enslaved their neighbors and declared war upon the Gods of men. To their aid they have the crafts of the Elder Cyclopes."
#descr "Mekone is a city of gold and marble inhabited by Gigantes, a race of exalted giants descended from an ancient God. Proud and endowed with mythical strength the Gigantes of Mekone have enslaved their neighbors and made themselves rulers over men. For ages the Gigantes have watched the lesser races and seen their kingdoms rise and fall. They witnessed the fall of Telkhinis and the injustices done to the races of old. With the aid of the Elder Cyclopes the Gigantes of Mekone have taken it upon themselves to rid the world of the gods of men. Most of Mekone's population consists of human slaves, helotes. The population of human slaves is discontent and unrest will increase in all forts."
#summary "Military: Few Gigantes armed with magical weapons. Mostly human slave soldiers. No sacred troops
Magic: Fire, Earth, Air and some Water. Cyclops smiths
Priests: weak and few, inquisitors
Dominion: Conflict Bonus +1 (good at suppressing enemy dominion)"
#end


#selectnation 51
#name "MA Phlegra" -- 
#brief "Phlegra is a kingdom of cursed Gigantes descendant of the Gigantes of Mekone who declared war upon the gods of men. The Gigantes are few and mos tof the population is made up of enslaved humans, but there is also a tribe of sheep-herding cyclopes living in the land. The human population is divided and unscrupulous individuals serve the Gigante Tyrants in exchange for power."
#descr "Phlegra is a kingdom of giants who have enslaved the much more numerous human population. The Gigantes of Phlegra are the descendants of the Gigantes of Mekone, who made war upon the gods of men. Punished for their sins the descendants of Mekone no longer appear as proud hoplites in gleaming armor, instead they are deformed and cursed with a violent temper. Since the fall of Mekone, the Gigantes resent pretending gods and religious faiths, and only the human population of the kingdom devote themselves to the awakening God. Phlegra is also the home of the sheep-herding Cyclopes, another tribe of giants. Like their predecessors the Gigantes of Phlegra have enslaved their neighbors and formed a kingdom under the rule of their Tyrants.
Unscrupulous human mages have developed ways to serve the Tyrants by dominating less fortunate magically adept humans. Now human taskmasters and oppressors cause more fear in the populace than the Tyrants themselves."
#summary "Race: Humans, Cyclopes and Gigantes
Military: Few Gigante Warriors. Mostly human slave soldiers. No sacred troops.
Magic: Fire, Earth, and some Water, Death and Nature. Arcane Slave Communions. Cyclops smiths
Priests: Weak and few
Dominion: Increases unrest"
#end


#selectnation 77
#name "MA Phaeacia" --
#brief "Phaeacia is an island queendom of half-giant sailors and tradesmen. Their fabled Dark Ships traverse the seas without oars or captains."
#descr "Phaeacia is an island queendom of dark-skinned men of great stature, the Collosi. Their fabled Dark Ships traverse the seas without oars or captains. Once a colony of Berytos, the island flourished and became rich and influential, known for its traders, craftsmen and marvelous shipwrights. When Berytos was destroyed by the armies of Arcoscephale the island of Phaeacia was able to stave off the conquerors thanks to ample tributes and its remote location. The queendom has since grown in power and influence. Their traders and explorers have traveled to the far reaches of the world and brought one of the world's greatest marvels back to Phaeacia, a sapling of the golden tree of the blessed gardens of the Hesperides. Now most inhabitants of Phaeacia live unnaturally long and blissful lives detached from the strife of the world beyond their island.
Phaeacia is also the home of giants descendant of Mekone. When the Gigantes' futile war upon gods came to a disastrous end, the Gigantes that did not join the armies of the God-slayer fled to Black Korkyra, an inhospitable island of the Phaeacian archipeligo. The king of the Gigantes married the Colossi queen of Phaeacia and their daughters have ruled the island ever since. Most nobles of the island trace a legacy of the Berytian Colossi as well as to the Gigantes of Mekone. There are also a frew of the pure blooded Gigantes remaining on Black Korkyra. Upholding the old bargain they arrive each spring to pledge the Queen their allegiance. They are not cursed as their Phlegran kin and retain some of their former glory."
#summary "Race: Humans and Colossi. Starts on an extra rich island if possible. Ocean sailing, trace income across oceans, income bonus in coastal castles. Prefers Heat scale +1
Military: Human and Colossi infantry. Can recruit special mages in coastal castles. A few Gigantes arrive yearly.
Magic: Air, Water, Astral, Glamour, some Earth.
Priests: Few of medium power
Dominion: All commanders can use the dark vessels to cross oceans between two provinces within the Pretender's dominion"
#end


#selectnation 96
#era 2
#name "LA Phlegra" --
#brief "Phlegra is a kingdom of human slaves ruled by a warrior-caste of Younger Cyclopes. The human population is divided and oppressor mages have made themselves masters over their fellow men and are the true rulers of the kingdom."
#descr "Phlegra is a kingdom of human slaves living in constant terror of the monstrous giants that once claimed the lands as theirs. For centuries the giants have been absent and only memories of their tyranny remain. Most of the Phlegran population are human slaves and slave masters dominated by a warrior-caste of Younger Cyclopes, previously living pastoral lives on the slopes of the Phlegran hills.
The Tyrants who once ruled the land were descendants of the Gigantes of Mekone, who made war upon the gods of men. Punished for their sins the Gigantes were imprisoned and cursed with monstrous appearence. Those who avoided imprisonment became Tyrants and rulers of Phlegra and formed a slave kingdom with the aid of human servants. But the Tyrants destroyed each other and the very lands they ruled. Slowly their numbers and influence dwindled and their servants made themselves rulers in all but name. Now human slave masters rule the kingdom in the name of absent Tyrants, hoping that the sleeping giants never wake up."
#summary "Race: Humans and Younger Cyclopes. Monstrous imprisoned Laestrygonians will eventually break free
Military: Few but mighty Cyclope Soldiers. Mostly human slave soldiers led by taskmasters. No sacred troops
Magic: Fire, Earth, and some Death, Water and Astral. Arcane Slave Communions. Cyclope Smiths
Priests: Weak and few
Dominion: Increases unrest"
#fortera 3
#end


#selectnation 67
#name "MA Ind" --
#brief "Ind is a hidden kingdom of virtuous piety surrounded by heathen lands inhabited by cannibals, dog-headed men and other strange tribes."
#descr "Ind is a fabled kingdom of marvelous riches hidden beyond hidden lands. Led by righteous kings of unequalled piety, rumors of the kingdom have attracted the attention of other lords. But even the most ambitious expiditions have yet failed to find magnificent Ind. Ind is a theocratic empire with subservient heathen petty kings and tribes of wild men. Only Ind itself is a bastion of piety and marvelous riches. Every important official in Ind is also a priest, bishop or archbishop, and every noble is a king. The armies are righteous and every soldier fulfills a sacred task. But it is not the soldiers of the land that wage the wars of Ind. Instead it is the subservient tribes of heathens, flesh-eaters, and Cynocephalians that the righteous Prester King unleashes upon the enemies of the True Lord.
Ind is hidden by the will of the Awakening God."
#summary "Race: Humans and strange tribesmen. Prefers Heat scale +1
Military: Sacred human infantry, cannibal warriors, Cynocephalians and subservient kingdoms.
Magic: Astral, Earth, Fire, Blood and some Water, Nature and Death.
Priests: Powerful. All commanders are priests. Only high ranking priests can become prophets. Every temple adds one to the sacred recruit limit.
Dominion: Conflict bonus -2. Dominion hides province ownership."
#end


#selectnation 65
#name "MA Na'Ba" --
#brief "Na'Ba is a queendom of the sands hidden by ancient magic. Most of the population are humans and 'Adite giants, but the rulers of the land are Jinni-blooded descendants of the lords of Ubar."
#descr "Na'Ba is a desert queendom ruled by Jiniri descendants of the Lords of Ubar. The capital of the queendom is carved out of the rocks of Ubar where the ancient magic of the Jinn still lingers. From the hidden abode, traders with silver tongues travel far and wide with luxurious wares imbued with ancient magic. The hidden paradise with its enchanted springs is long since lost, but the craftsmen of Na'Ba have erected a great dam that supplies the hidden city and the surrounding lands with water. In ancient times Ubar was a nation of men and Jinn, but magic waned and the Jinn slowly disappeared from the world. With the arrival of refugees from Hinnom, a new era began. The Avvites, a race of giants that with an inclination to intermingle with supernatural beings, formed an alliance with the few remaining Jinn and a new ruling class was born. The last of the Jinni Sultans too Avvite wives and their daughters became the first queens of Na'Ba. Now the Nabaean population is made up of humans ruled by Jinni-blooded half-giants and their Jiniri Queens"
#summary "Race: Humans, 'Adite giants and Jann. Prefers Heat scale +2
Miltary: Humans, giant infantry, sacred Jann warriors.
Magic: Fire, Air, Glamour, Earth and some Astral and Nature.
Priests: Average.
Dominion: Dominion hides province ownership."
#end


#selectnation 118
#era 2
#name "LA Vaettiheim" --
#brief "Vaettiheim is the home of the small goblins known as Vaettir. They are led by giant Jotun Gygjas and there are also a few giants remaining. All Vaettir and their Jotune allies are immune to the cold. The giant Gygjas are versatile and powerful sorceresses that can foresee the future."
#descr "Vaettiheim is a land of bitter winters and cool summers. It is the home of Vaettir, small and wicked goblins who once dwelled in the icy forests of Jotunheim. When the Jarls of Jotunheim sealed the alliance with humankind the remaining Gygjas and their Vaetti servants retreated to the wild woods. With the guidance of the few remaining Gygjas the Vaettir formed a nation of their own. Vaettiheim is a land of Vaettir and giants centered at the Iron Wood, the ancient home of the Jotun Gygjas. With the coming of the Awakening God the Vaetti Hags of earlier times have been more or less replaced by the Vaetti Gyghas trained in the Iron Wood and the Vaettir have adopted the weapons and armaments used by Jotuns and humans."
#summary "Race: Cold resistant, prefers Cold scale +2
Military: Small stealthy Vaettir, Wolf Riders and a few giants
Magic: Death, Nature, Blood, Water, Astral
Priests: Weak"
#fortera 2 -- primitive forts
#end

#selectnation 119
#era 2
#name "LA Feminie" -- checked
#brief "Feminie is a magocratic queendom, hidden from outsiders by sorceresses and Sage-Queens of great power. Feminie is ruled by women, a legacy from its amazon past."
#descr "Feminie is a hidden queendom in a faraway land ruled by women. It was once an amazon queendom subservient to Magnificent Ind, but when the Khans of T'ien Ch'i defeated the sacred armies of Ind and killed the Prester King himself, the dominion of Ind was broken and the subservient tribes and kingdoms found themselves free from the yoke of the Magnificent Kingdom. The sorceresses of Feminie salvaged the esoteric knowledge of the sage-priests of Ind and have become keepers of their hidden lore. Throughout the queendom monasteries filled with ancient texts can be found. Abesses and their servants search the books for arcane secrets to further the mgaical might of Feminie. The queendom is now rules by wise and able Sage-Queens who hide their lands from outside threats."
#summary "Race: Humans. Prefers Heat scale +1
Military: Human infantry and knights. Sacred human infantry.
Magic: Astral, Glamour, Fire and some Water and Nature.
Priests: Medium, divinely inspired researchers.
Dominion: Dominion hides province ownership."
#fortera 3
#end

#selectnation 120
#era 2
#name "LA Piconye" -- checked
#brief "Piconye is a theocracy of small, horned men led by priest kings. The kingdom was once subservient to the Prester King of Magnificent Ind, and when Ind fell Piconye inherited much of its relgious traditions."
#descr "Piconye is a kingdom of little horned men located in a fabulous land. It was once subservient to Magnificent Ind, but when the Khans of T'ien Ch'i defeated the sacred armies of Ind and killed the Prester King himself, the dominion of Ind was broken and the subservient tribes and kingdoms found themselves free from the yoke of the Magnificent Kingdom. The little men of Piconye had never had a unified kingdom apart from Magnificent Ind and struggled to form a kingdom of their own. Heavily influenced by their former masters Piconye turned into a theocratic monarchy with priest-soldiers and religious potentates ever present. But where Ind had hidden their virtue from the outside world, Piconye instead turned itself outwards in an attempt to spread the faith of the awakening God."
#summary "Race: Little horned men. Prefers Heat scale +1
Military: Small sized infantry, Bird Knights, sacred infantry and crossbowmen.
Magic: Astral, Earth, some Fire, Water and Nature.
Priests: Powerful. Most commanders are priests. Every temple adds one to the sacred recruit limit."
#fortera 3
#end

#selectnation 121
#era 2
#name "LA Andramania" -- checked
#brief "Andramania is a republic of cynocephalians, dog-men, who have abandoned their violent and barbaric past. The cynocephalians tribes were once subservient to the Magnificent Kingdom of Ind and Andramania has inherited many traditions from Ind, but the role of religion has become secondary to the importance of fair and just rule of the Magistrates."
#descr "Andramania is a republic of Calystrii, civilized and culturally advanced Cynocephalians. The Cynocephalian clans of Gog and Magog once served Magnificent Ind and their barking hordes were released upon the enemies of the Prester King. But when the Khans of T'ien Ch'i defeated the sacred armies of Ind and killed the Prester King himself, the dominion of Ind was broken and all subservient tribes and kingdoms found themselves free from the yoke of the Magnificent Kingdom. The Cynocephalians had become increasingly more civilized under the benevolent ruler of the Prester King and when Ind fell cynocephalian magistrates replaced the viceroys of Ind and united the cynocephalian tribes in a nation of virtue far beyond that of the kingdoms of men. They called themselves Calystrii and promised never to fall back into the barbarism and gruesome practices of old. Now most Calystrii regard men with disdain as the inferior beings they are."
#summary "Race: Cynocephalian dog-men. Prefers Heat scale +2
Military: Skilled and disciplined infantry and crossbowmen. Conscription.
Magic: Fire, Astral, Nature, Earth and some Water. Rarely Blood or Death.
Priests: Mostly weak."
#fortera 3
#end

#selectnation 123
#name "LA Pyrène" --
#era 2
#brief "Pyrène is a feudal mountain kingdom ruled by noble houses reshaped by infernal powers. The Black Goats and witches of erlier times have ben replaced by a ruling class of half demons known as Cambion."
#descr "Pyrène is a a feudal kingdom ruled by cambion, demon half breeds. For centuries Pyrène was torn with strife as noble houses fought for the throne. For a long time no house was dominant, but then matters changed. A few lesser houses were secretly given the support of the church. With the aid of the priesthood they were given the opportunity to sire demonic offspring with succubi and incubi devils summmoned by priests versed in blood magic. Their cambion offspring, gifted with demonic charms and physique, made the houses rise in power and influence and with the support of the church the power balance of the kingdom shifted. Eventually the cambion ousted their parents and now there are almost no pure-blooded humans left in the high nobility.
With the increasing prominence of the Cambion and the priests, the Akerbeltz have been purged from the land and their Sorginak servants lost much of their former influence."
#summary "Race: Humans of cave-man descent with dark-vision and elemental resistance.
Military: Human infantry, crossbows and knights, sacred demon knights.
Magic: Blood, Glamour, Air and some Earth and Fire.
Priests: Average, can perform blood sacrifices."
#fortera 3
#end


#selectnation 18
#era 2
#name "EA Ubar" -- checked
#brief "Ubar is the kingdom of the Jinnun, hidden in the sands by ancient magic. It is ruled by the Jinnun, invisible beings sprung from the Smokeless Flame, but most of the population are human slaves. Ubar is sealed and its rulers are imprisoned until their Pretender God awakens."
#descr "Ubar is the kingdom of the Unseen, the Jinnun of the deserts. Its heart is a paradise hidden beyond three deserts of scorching heat, one red, one white, and one as black as the night. Beyond the three deserts lies a plateau hidden with the mirages of the Jinnun. There is but one entrance in the cliffside of the plateau, and it is always guarded by invisible sentinels. Once you have passed the entrance you enter a city covered in sand. This is Iram of a Thousand Pillars, home of the Jinnun. Once this was a paradise with date palms, fountains, and palaces in abundance. Towers of brass and marble rose towards the heavens, fist-sized rubies and diamonds lit the streets and palaces, and the air was filled with music and pleasant fragrances. This was the City of Brass. But the Lords of Ubar rebelled against the powers that were and the city was sealed by a divine decree. The afarit, the mightiest of the Jinnun, were imprisoned in their palaces with their rebel God. Now Iram is a desert city inhabited by a few Jinn and their human slaves, waiting for the Gates of Brass to open, and the return of the Ifrit Sultan."
#summary "Race: Jinn and human slaves. Prefers Heat scale +3
Military: Human infantry and camel riders, Ghuls, Jinn Warriors, sacred Ifrit warriors.
Magic: Fire and Air some Earth and very little Astral.
Priests: Weak, Guardian Spirits.
Dominion: Dominion hides province ownership."
#fortera 1
#end


#selectnation 124
#name "LA Zemaitia" --
#era 2
#brief "Zemaitia is a nation of Chudes and humans who have lived hidden in their forests since the Black Knights of Ulm conquered their heartland. With time the Ulmish conquerors succumbed to the dweomer of the forests and became part of the nation. Now the Chudes and humans of Zemaitia emerge from the forests accompanied by antlered knights to reclaim lands once theirs. The shamans of Zemaitia are skilled in nature magic and the glamour magic of the fay."
#descr "Zemaitia is a woodland realm of harsh winters and short summers inhabited by humans and Chudes, an exalted race of great strength and beauty. Once the Chudes were at war with the Vanir, but with the arrival of the Black Knights all changed. While some of their kin allied with the Vanir to fight the Black Knights, the Chudes of Zemaitia withdrew and defended their forest home. But the Black Knights were unstoppable and the Chude armies were defeated. The knights entered the heart of the forest and erected teh mighty fortress Fort Vedun where the dewomer of the land was strongest. But over time the Chudes regrouped. For a time Fort Vedun stood fast, but as the war against Vanarus dragged on the Iron Kingdom withdrew. Fort Vedun was left to defend itself and became isolated in a hostile land steeped in magic. The fortress and its inhabitants were slowly transformed by the magic of the Dreamwild. The last human Hochmeister struck a deal with the Chudes and swore them allegiance. With the aid of the Black Knights the Chudes of Zemaitia defended their forests from the nascent Vanarusian kingdom. For centuries the Zemaitians went into hiding. When Vanarus eventually crumbled and human princes replaced teh last of the Vanjarls, the Chudes of Zemaitia and their Sylvan Knights emerged from their sequestration and challenged the Princes of Bogarus."
#summary "Race: Humans and Chudes. Zemaitian peoples have partial cold resistance and prefer Cold scale +1.
Military: Human medium infantry, Chud warriors, Skinshifters, sacred Sylvan Knights.
Magic: Nature, Glamour, Earth, some skills in air and fire, summonable beings of Rus.
Priests: Weak."
#fortera 2
#homefort 4 -- citadel
#end

