#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from typing import Iterable
import sys
import itchat
import csv
import random
import re
import time

"""
称呼：
1、对于姓名分解的策略：
if len(name)<=3:
    第一个字是姓，剩下的是名
else:
    前两个字是姓，后面是名称
"""

call_templates = {
    "teacher_simple": "{0[last_name]:s}老师",
    "teacher": "{0[last_name]:s}{0[first_name]:s}老师",
    "manager_simple": "{0[last_name]:s}经理",
    "manager": "{0[last_name]:s}{0[first_name]:s}经理",
    "leader_simple": "{0[last_name]:s}总",
    "common_name": "{0[last_name]:s}{0[first_name]:s}",
    "doctor_simple": "{0[last_name]:s}博士",
    "doctor": "{0[last_name]:s}{0[first_name]:s}博士",
    "professor_simple": "{0[last_name]:s}教授",
    "professor": "{0[last_name]:s}{0[first_name]:s}教授",
    "old": "老{0[last_name]:s}",
}

message_special_template = {
    "(teacher|professor).*?": [
        "值此辞旧迎新之际，向您致以诚挚的问候，感谢{0}对我的指导，学生袁逸凡祝老师桃李满天下！^_^"
    ],
    "(manager|leader).*?": [
        "值此辞旧迎新之际，向您致以诚挚的问候，感谢{0}在过去的一年对我的支持和理解，祝您在新的一年发大财，行大运，身体健康，万事如意！——^_^袁逸凡",
    ],
    "doctor.*?": [
        "祝{0}新春快乐，祝您在新的一年里Paper大发，顶会随便灌水！——^_^袁逸凡",
    ],
    "old.*?": [
        "{0}，新年快乐，祝你新的一年……充满挑战，波澜壮阔～^_^"
    ]
}

message_common_template = [
    "金鸡辞旧岁，瑞犬迎新春，袁逸凡祝{0}全家阖家欢乐，新春快乐！～，～",
    "祝{0}新的一年发大财，行大运，身体健康，万事如意！——袁逸凡"
]


def name_analysis(name: str) -> Iterable[str]:
    if len(name) > 3:
        return __slice_name(name, 2)
    else:
        return __slice_name(name, 1)


def __slice_name(name: str, slice_index: int) -> Iterable[str]:
    assert 0 <= slice_index <= len(name), "slice index not correct."
    return {
        "last_name": name[:slice_index],  # 姓
        "first_name": name[slice_index:]  # 名
    }


def export_setting_template():
    with open("configure_template.csv", "w") as fp:
        fp.write("id,name," + ",".join(call_templates.keys()) + "\n")
        for my_dear_friend in itchat.get_friends(update=True):
            user_id = my_dear_friend.UserName
            user_name = my_dear_friend.RemarkName
            fp.write("{},{},,,,,,,,,,,\n".format("-", user_name))


def generate_send_text(template_config_file: str, send_task_file: str):
    with open(send_task_file, "w") as fp_task:
        with open(template_config_file, "r") as fp:
            reader = csv.reader(fp)
            head_row = next(reader)
            for row in reader:
                user_id = row[0]
                user_name = row[1]
                search_index = [i for i, x in enumerate(row) if x.lower() == "t"]
                if len(search_index) > 0 and len(user_name) > 0:
                    identify = head_row[search_index[0]]
                    call_name = call_templates[identify].format(name_analysis(user_name))
                    zf = ""
                    if identify == "common_name":
                        zf = random.choice(message_common_template).format(call_name)
                    else:
                        for reexp, templates in message_special_template.items():
                            if len(re.findall(reexp, identify, re.DOTALL)) > 0:
                                zf = random.choice(templates).format(call_name)
                                break
                    fp_task.write("{},{}\n".format(user_name, zf))


def real_send_task(send_task_file: str):
    with open(send_task_file, "r") as fp:
        reader = csv.reader(fp)
        users = itchat.get_friends()
        for row in reader:
            print("{} --> {}".format(row[0], row[1]))
            user_id = [u.UserName for u in users if u.RemarkName == row[0]][0]
            print(itchat.send(row[1], toUserName=user_id))
            time.sleep(10)


if __name__ == "__main__":
    if sys.argv[1] == "export":
        itchat.auto_login(hotReload=True)
        export_setting_template()
    elif sys.argv[1] == "generate":
        generate_send_text(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "send":
        itchat.auto_login(hotReload=True)
        real_send_task(sys.argv[2])
    else:
        raise Exception("Parameter(s) is necessary.")
