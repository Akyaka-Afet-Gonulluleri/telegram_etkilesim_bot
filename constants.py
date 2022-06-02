def get_question(name):
    return {
        "text": "Lutfen {} lokasyonunu isaretleyip gonderin".format(name),
        # "location": {
        #     "text": "Lutfen {} resmini gonderin".format(name),
        #     "photo": {}
        # }
    }

REQUEST_INFO_TEMPLATE = "Lutfen simdi {} lokasyonunu ve fotografini paylasin."
DEFAULT_SESSION = {
    "user": {},
    "history": [],
    "data": {
        "location": [],
        "photo": []
    }
}

OPTIONS = {
    "Yangın": {
        "text": "Ne gördünüz?",
        "Duman": get_question("olay"),
        "Ateş": get_question("olay"),
    },
    "Su kaynağı": {
        "text": "Türü nedir?",
        "Hidrant": get_question("hidrant"),
        "Gölet": get_question("golet"),
        "Dere": get_question("dere"),
        "Su motoru": get_question("motor"),
        "Jeneratörlu su pompası": get_question("pompa"),
        "Diğer": get_question("su kaynağı")
    },
    "Tanker": {
        "text": "Tankerin türü nedir?",
        "Su tankeri": get_question("tanker"),
        "Yangın tankeri (püskürtmeli)": get_question("tanker"),
    },
    "Risk": {
        "text": "Türü nedir?",
        "Elektrik tel teması": get_question("tehlike"),
        "Diğer tehlike (kırık cam, söndürülmemiş ateş vb.)": get_question("tehlike"),
    }
}