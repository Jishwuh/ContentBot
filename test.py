import json
jsonValue = {"categories": {
        
            "welcome": {
                "name": "๏▬▬▬▬(WELCOME)▬▬▬▬๏",
                "channels": [
                    {
                        "name": "👋│welcome",
                        "allow":"66625",
                        "deny":"377957124096"
                    },
                    {
                        'name': "📄|about",
                        "allow":"66625",
                        "deny":"377957124096"
                    },
                    {
                        'name': "📜│rules",
                        "allow":"66625",
                        "deny":"377957124096"
                    },
                    {
                        'name': "🔰|roles",
                        "allow":"66625",
                        "deny":"377957124096"
                    },
                    {
                        'name': "😄|introductions",
                        "allow":"330816",
                        "deny":"2147483648"
                    }
                ]
            },
            "info": {
                "name": "๏▬▬▬▬(INFO)▬▬▬▬๏",
                "channels" : [
                    {
                        'name': "📺|socials",
                        "allow":"66625",
                        "deny":"377957124096"
                    }
                ]
            },
            "text": {
                "name": "๏▬▬▬▬(TEXT)▬▬▬▬๏",
                "channels" : [
                    {
                        "name": "general"
                    }
                ]
            },
            "media": {
                "name": "๏▬▬▬▬(MEDIA)▬▬▬▬๏",
                "channels" : [
                    {}
                ]
            },
            "voice": {
                "name": "๏▬▬▬▬(VOICE)▬▬▬▬๏",
                "channels" : [
                    {}
                ]
            },
            "gaming": {
                "name": "๏▬▬▬▬(GAMING)▬▬▬▬๏",
                "channels" : [
                    {}
                ]
            }
        
    }}

#Print out the categories and then the names of the categories
channels = {}
for category in jsonValue['categories']:
    channels[category] = []
    print(channels)
# print(jsonValue['categories'][category]['channels'])
for category in jsonValue['categories']:
    for channel in jsonValue['categories'][category]['channels']:
        print(channel)
        channels[category].append(channel)

print(channels)
        

# print(channels)