"""Real Table state (fixture content, sample names) for screenshots of the phone UI."""
import json, random, sys
from dataclasses import replace
sys.path[:0] = ["/tmp/trpgbot/repo", "/tmp/trpgbot/repo/tests"]
from content_fixture import make_pack
from conftest import scores
from engine_fixture import ScriptedClient, FakeLibrary, choice, noul
from trpg.content.model import MonsterStat
from trpg.engine import Judge, Table, TableConfig
from trpg.engine.narrator import PlainNarrator
from trpg.procedures import prepare_adventure
from trpg.procedures.appearance import LOOK_OPTIONS
from trpg.rules import WEAPONS, ARMORS, CharClass, Dice, NaturalAttack, create_character

RED_CAP = MonsterStat("붉은 모자", "1d6", 4, 12, 1, (NaturalAttack("낫", "1d6"),), "혼돈", 10, "", ("weak_to_iron",), True, 0)
pack = replace(make_pack(), beats=("neighbor_trouble", "lord_message", "lord"), encounters={})
adventure = prepare_adventure(pack, Dice(5), culprits=["(숨겨진 진상)"])
party = [
    create_character("리아", CharClass.ROGUE, scores(dex=15, wis=12), skills=["은신"], weapon=WEAPONS["소검"]),
    create_character("도윤", CharClass.WARRIOR, scores(str_=15, con=13), weapon=WEAPONS["장검"]),
    create_character("세라", CharClass.MAGE, scores(int_=15, wis=13), weapon=WEAPONS["단검"]),
    create_character("한별", CharClass.WARRIOR, scores(str_=13, dex=13), weapon=WEAPONS["창"] if "창" in WEAPONS else WEAPONS["장검"]),
]
for i, pc in enumerate(party):
    pc.look = {"skin": [0, 1, 0, 2][i], "hair_style": [2, 0, 4, 1][i], "hair_color": [3, 0, 6, 1][i], "outfit": [5, 2, 6, 3][i], "trim": [1, 0, 2, 1][i], "headgear": [0, 1, 0, 0][i]}
client = ScriptedClient()
table = Table(party, adventure, pack, Judge(client), PlainNarrator(), Dice(7),
              library=FakeLibrary({"붉은 모자": RED_CAP}),
              config=TableConfig(dice_mode="player", use_board=True, use_scenes=True, use_combos=True))
adventure.title = "울리지 않는 종"
adventure.village.name = "버들골"

def snap(name, you, outputs, extra=None):
    return {"name": name, "you": you, "view": table.public_view(), "outputs": [o.__dict__ for o in outputs], **(extra or {})}

shots, history = [], []
def add(outs):
    history.extend(o.__dict__ for o in outs)
    return outs

def say(who, text, to_master=0.0, **answers):
    """What the server does with a player's line: record it as "say", then let the table answer."""
    client.answers.clear()
    client.set(to_master=noul(to_master), **answers)
    history.append({"kind": "say", "text": text, "to": None, "data": {"speaker": who}})
    return add(table.receive(who, text))

table.scene.time = "dusk"
say("도윤", "해가 지기 전에 우물부터 보자. 종이 멈춘 날 아이들이 거기서 놀았대.")
say("세라", "좋아. 난 게시판 쪽 소문을 읽어 볼게.")
say("리아", "우물 안을 자세히 들여다본다", 0.9, kind=choice("action"), committed=noul(0.95), uncertain=noul(0.9), ability=choice("지혜"))
shots.append(snap("scene_check", "리아", [], {"history": list(history)}))
add(table.receive("리아", "/roll"))
shots.append(snap("scene_after", "리아", [], {"history": list(history)}))
client.answers.clear()
add(table.receive("도윤", "/fight 붉은 모자 3 숲"))
cur = table.combat.current; shots.append(snap("combat", getattr(cur, "name", cur), [], {"history": list(history)}))
print(json.dumps(history[-6:], ensure_ascii=False)[:2500])
print("mode", table.mode, "current", table.combat.current if table.combat else None)
json.dump({"looks": LOOK_OPTIONS, "shots": shots}, open("/tmp/trpgbot/demo/views.json", "w"), ensure_ascii=False, default=str)
