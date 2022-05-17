def get_question(name):
    return {
        "text": "Lutfen {} lokasyonunu isaretleyip gonderin".format(name),
        "location": {
            "text": "Lutfen {} resmini gonderin".format(name),
            "photo": {}
        }
    }

DEFAULT_SESSION = {
    "user": {},
    "history": [],
    "data": {
        "location": [],
        "photo": []
    }
}

OPTIONS = {
    "Yangin": {
        "text": "Ne gordunuz?",
        "Duman": get_question("olay"),
        "Ates": get_question("olay"),
    },
    "Su kaynagi": {
        "text": "Turu nedir?",
        "Tanker": get_question("tanker"),
        "Hidrant": get_question("hidrant"),
    },
    "Risk": {
        "text": "Turu nedir?",
        "Elektrik tel temasi": get_question("tanker"),
        "Diger tehlike (kirik cam, sondurulmemis ates vb.": get_question("tehlike"),
    }
}