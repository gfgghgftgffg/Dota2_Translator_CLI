# -*- coding: utf-8 -*-
"""Dota 2 glossary in editable `??:??` line format."""

from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Iterable

GLOSSARY_TEXT = """
# Dota2 翻译词库 - 只需维护一份
# 模式1 (中→英): 中文 → 英文
# 模式2 (英→中): 英文 → 中文 (自动反转)

# ==================== 位置/角色 ====================
一号位:carry
二号位:mid
三号位:offlane
四号位:soft support
五号位:hard support
辅助:support
开团:initiate
前排:tank
近战:melee
远程:range
驱散:dispel
团控:crowd control

# ==================== 英雄全称+简称 ====================
    # 核心英雄
露娜:luna
虚空假面:fv
虚空:fv
剑圣:jugg
骷髅王:wk
snk:wk
幽鬼:spec
变体精灵:morphling
水人:morphling
飞机:gyro
血魔:bs
巨魔:troll
熊战士:ursa
熊战:ursa
拍拍:ursa
拍拍熊:ursa
克林克兹:clinkz
骨弓:clinkz
小骷髅:clinkz
小黑:drow
卓尔游侠:drow
狙击手:sniper
火枪:sniper
火枪手:sniper
敌法:am
敌法师:am
幻刺:pa
幻影刺客:pa
小鱼人:slark
斯拉克:slark
隐形刺客:riki
隐刺:riki
sa:riki
蚂蚁:weaver
美杜莎:medusa
一姐:medusa
恐怖利刃:tb
naix:ls
小狗:ls
奶绿:muerta
凯:kez
圣堂:ta

    # 中单英雄
哈斯卡:huskar
神灵:huskar
女王:qop
痛苦女王:qop
风暴之灵:storm
蓝猫:storm
黑鸟:od
拉席克:lesh
老鹿:lesh
帕格纳:pugna
骨法:pugna
卡尔:invoker
祈求者:invoker
帕克:puck
精灵龙:puck
滚滚:pango
弧光:arc
电狗:arc
毒龙:viper
老奶奶:snapfire
电棍:razor
剃刀:razor
宙斯:zeus
大圣:mk
火女:lina
丽娜:lina
莱恩:lion
拉比克:rubick
死灵法师:nec
死灵法:nec
帕吉:pudge
屠夫:pudge
影魔:sf

    # 劣势路
半人马:centaur
人马:centaur
马尔斯:mars
钢背:bb
钢背兽:bb
钢背猪:bb
熊猫:brewmaster
酒仙:brewmaster
熊猫酒仙:brewmaster
伐木机:timber
斧王:axe
军团指挥官:lc
军团:lc
潮汐:tide
潮汐猎人:tide
裂魂人:sb
白牛:sb
夜魔:ns
暗夜魔王:ns
斯拉达:slardar
大鱼人:slardar
大鱼:slardar
孽主:underlord
大屁股:underlord
屁股:underlord
尸王:undying
大锤:db
破晓晨星:db
兽王:bm
兽:pb
沙王:sk


    # 辅助英雄
剧毒:venom
凤凰:phoenix
水晶室女:cm
冰女:cm
巫妖:lich
巫医:witch doctor
光法:kotl
双头龙:jakiro
萨尔:disruptor
戴泽:dazz
暗影萨满:ss
小y:ss
小Y:ss
神谕者:oracle
神谕:oracle
小精灵:io
精灵:io
米拉娜:pom
白虎:pom
蝙蝠:batrider
蝙蝠骑士:batrider
海民:tusk
天怒:sm
墨客:grim
松鼠:hoodwink
小松鼠:hoodwink
冰龙:ww
发条:clock
炸弹人:techies
大树:treant
小鹿:enchant
陈:chen
德鲁伊:ld
全能:omni
全能骑士:omni
死亡先知:dp
先知:np
术士:warlock
谜团:enigma
小牛:es
小强:nyx
赏金猎人:bh
赏金:bh
土猫:earth spirit
火猫:ember
紫猫:void spirit
大牛:et
毒狗:sd
暗影恶魔:sd
猛犸:magnus


    # 其他
米波:meepo
蜘蛛:broodmother
小小:tiny
斯温:sv
混沌:ck
ga:alchemist
炼金术士:alch
炼金:alch
coco:kunkka
船长:kunkka
狼人:lycan
小娜迦:naga
幻影长矛手:pl
猴子:pl
小花仙:willow
花仙:willow
食人魔:ogre
蓝胖:ogre
冰魂:AA
马西:marci
百戏:ringmaster
亚巴顿:abaddon
死骑:abaddon
死灵龙:visage
维萨吉:visage
朗格:largo
蛤蟆:largo
黑贤:ds
兔子:ds
黑暗贤者:ds
风行:wr
风行者:wr
大圣:mk
龙骑:dk
龙骑士:dk
末日:doom


# ==================== 物品装备 ====================
眼:ward
守卫:ward
假眼:observer
真眼:sentry
粉:dust
雾:smoke
诡计之雾:smoke
开雾:smoke
吃树:tango
大药:healing salve
小蓝:clarity
净化:clarity
芒果:mango
仙灵:faerie fire
大魔棒:magic stick
魔棒:magic stick
瓶子:bottle
魔瓶:bottle
魂戒:soul ring
骨灰:urn
大骨灰:vessel
大勋章:solar
阳炎纹章:solar
相位:phase boots
假腿:power treads
飞鞋:boots of travel
绿鞋:tranquil
秘法:arcane
秘法鞋:arcane
推推:force
大推推:hurrican
微光:glimmer
莲花:lotus
盘子:aeon
跳刀:dagger
跳:dagger
黑黄:bkb
黑黄杖:bkb
分身:manta
分身斧:manta
林肯:linken
晕锤:bash
金箍棒:mkb
大炮:daedalus
蝴蝶:butterfly
暗灭:desolator
黯灭:desolator
否决:nullifier
隐刀:shadow blade
大隐刀:silver edge
羊刀:hex
紫苑:orchid
血棘:bloodthorn
散失:diffusal
电锤:mael
陨星锤:hammer
刷新球:refresher
撒旦:satanic
龙心:heart
冰眼:skadi
刃甲:blademail
反甲:blademail
先锋:vanguard
强袭:ac
梅肯:mek
笛子:pipe
天堂:heaven's halberd
雷锤:mjollnir
大电:mjollnir
大电锤:mjollnir
臂章:armlet
血精石:bloodstone
血精:bloodstone
辉耀:rad
狂战:bf
点金:midas
圣剑:divine
大根:dagon
支配:dominator
坚韧球:perseverance
吹风:eul
风杖:eul
大吹风:wind waker
缚灵索:gleipnir
冰甲:shiva
买活:buyback
补刀斧:quelling blade
穷鬼盾:poor man's shield
天鹰:ring of aquila
战鼓:drum
勋章:medallion of courage
祭品:vlad
A杖:agha
出A:agha
魔晶:shard
魔方:tmt
慧光:kaya
夜叉:yasha
散华:sange
魔龙枪:dragon lance
大鞋:greaves
大晕:abyssal
大晕锤:abyssal
以太:ether
虚灵刀:ether blade
巫师之刃:witch blade
阿托斯:atos
赤红甲:crimson
血腥榴弹=grenade
榴弹=grenade
榴子=grenade



# ==================== 游戏机制/地图 ====================
小地图:map
地图:map
肉山:rs
盾:aegis
不朽盾:aegis
超级兵:mega creep
兵营:barracks
塔:tower
基地:base
高地:high ground
前哨:outpost
野区:jungle
打野:jungle
远古:ancient camp
上路:top lane
下路:bottom lane
中路:mid lane
河道:river
符点:rune
神符:rune
赏金:bounty
双倍:dd
急速:haste
haste:haste
隐身:invi
恢复:regen
护盾:shield
奥术:arcane
幻象:illu
illu:illu
智慧:wisdom
疗伤莲花:lotus

# ==================== 战术用语 ====================
gank:gank
抓人:gank
游走:roam
支援:rotate
先手:initiate
开团:initiate
后手:follow up
推塔:push
拆塔:just push
打塔:hit tower
打团:teamfight
团战:teamfight
带线:push lane
rat:split push
抱团:stick
勾引:bait
保护:protect
蹲:protect
防守:defend
视野:vision
风筝:kite
拉扯:kite
换血:trade
深入:dive
刷钱:farm
打钱:farm
发育:farm
输出:damage
补刀:last hit
反补:deny
堆野:stack
拉野:pull
控线:control lane
反眼:deward
克制:counter
前期:early game
后期:late game
小兵:creeps
中立:neutrals
野怪:neutrals
肉:tank
前排:tank
核心:carry
大哥:carry
辅助:support
酱油:support
劣势路:offlane
优势路:safelane
别送:dont feed
别浪:dont throw
盾过:aegis expire
盾过期:aegis expire

# ==================== 技能相关 ====================
技能:spell
控制:stun
晕:stun
减速:slow
沉默:silence
驱散:dispel
缠绕:root
爆发:burst
跳进去:blink in
talent:talent
天赋:talent
大招:ulti
有大:ult ready
没大:no ult
破坏:break
决斗:duel

# ==================== 常见交流 ====================
没血:low hp
没蓝:out of mana
# 合并手动词库和其他反转词
""".strip()


def _parse_glossary_lines(lines: Iterable[str]) -> "OrderedDict[str, str]":
    glossary: "OrderedDict[str, str]" = OrderedDict()
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        source, target = line.split(":", 1)
        source = source.strip()
        target = target.strip()
        if not source or not target:
            continue
        glossary[source] = target
    return glossary


def load_glossary_text() -> str:
    return GLOSSARY_TEXT


def load_glossary_pairs() -> "OrderedDict[str, str]":
    return _parse_glossary_lines(GLOSSARY_TEXT.splitlines())


def build_zh_to_en() -> Dict[str, str]:
    pairs = load_glossary_pairs()
    return dict(sorted(pairs.items(), key=lambda item: len(item[0]), reverse=True))


def build_en_to_zh() -> Dict[str, str]:
    pairs = load_glossary_pairs()
    reverse: "OrderedDict[str, str]" = OrderedDict()
    for chinese_term, english_term in pairs.items():
        reverse.setdefault(english_term, chinese_term)
    return dict(sorted(reverse.items(), key=lambda item: len(item[0]), reverse=True))


ZH_TO_EN = build_zh_to_en()
EN_TO_ZH = build_en_to_zh()
