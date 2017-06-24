#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
log_path = ''
HOST, USER, PASSWD, DB, PORT = 'localhost', 'root', '123456', 'test', 3306
person_img = {
    'B0AAAAOCAYAAADT0Rc6AAABdklEQVR42qWUMUgDQRBFDwsrsbGw': "董事",
    'CsAAAAOCAYAAAC2POVFAAAB/0lEQVR42rWVQUSDYRjHJ5MOiUw6': "董事长",
    'B0AAAAOCAYAAADT0Rc6AAABaUlEQVR42mNgwA7SgNgUiV8OxEoM': "监事"
}
province = {
    "11": "BEJ",
    "12": "TJN",
    "13": "HEB",
    "14": "SXI",
    "15": "NMG",
    "21": "LNG",
    "22": "JLN",
    "23": "HLJ",
    "31": "SHH",
    "32": "JSU",
    "33": "ZHJ",
    "34": "ANH",
    "35": "FUJ",
    "36": "JXI",
    "37": "SHD",
    "41": "HEN",
    "42": "HUB",
    "43": "HUN",
    "44": "GAD",
    "45": "GXI",
    "46": "HAN",
    "50": "CHQ",
    "51": "SCH",
    "52": "GZH",
    "53": "YUN",
    "54": "XIZ",
    "61": "SHX",
    "62": "GSU",
    "63": "QNH",
    "64": "NXA",
    "65": "XNJ"
}
