#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Joshua
@Time    : 2019/1/24 18:41
@File    : pre_predict_subcategory.py
@Desc    : 
"""

import os
import json
from urllib.parse import urlparse

dataDir = "/data/caifuli/news_classification/data"
dataPath = "/data/caifuli/news_classification/pre_classified/"
science_path_classified = dataPath + "science_classified"
international_path_classified = dataPath + "international_classified"
international_path_unclassified = dataPath + "international_unclassified"
national_path_classified = dataPath + "national_classified"
national_path_unclassified = dataPath + "national_unclassified"
tech_path_classified = dataPath + "technology_classified"
tech_path_unclassified = dataPath + "technology_unclassified"
auto_path_classified = dataPath + "auto_classified"
auto_path_unclassified = dataPath + "auto_unclassified"
entertainment_path_classified = dataPath + "entertainment_classified"
entertainment_path_unclassified = dataPath + "entertainment_unclassified"
lifestyle_path_classified = dataPath + "lifestyle_classified"
lifestyle_path_unclassified = dataPath + "lifestyle_unclassified"
sport_path_classified = dataPath + "sports_classified"
sport_path_unclassified = dataPath + "sports_unclassified"

sport_website = ['www.thepapare.com', 'www.cricketcountry.com', 'www.crictracker.com', 'cricket.yahoo.com',
                 'www.espncricinfo.com', 'www.motorsport.com', 'www.foottheball.com', 'sportzwiki.com', 'www.sport24.co.za',
                 'www.sportal.co.in', 'www.espn.in', 'www.icc-cricket.com', 'sports.ndtv.com', 'www.crictoday.com',
                 'www.goal.com', 'www.foxsportsasia.com', 'www.mykhel.com']
tech_website = ['www.androidcentral.com', 'www.androidheadlines.com', 'www.androidauthority.com', 'news.softpedia.com',
                'www.ubergizmo.com', 'www.androidpolice.com', 'www.techtree.com', 'betanews.com', 'www.makeuseof.com',
                'mspoweruser.com', 'www.bgr.in', 'www.tomsguide.com', 'www.imore.com', 'www.thetechbulletin.com',
                'androidandme.com', 'techlomedia.in', 'www.mobilescout.com', 'www.xda-developers.com', 'fossbytes.com',
                'www.mobipicker.com', 'www.windowscentral.com', 'www.androidpit.com', 'www.pcquest.com', 'androidadvices.com',
                'www.techworm.net', 'm.tech.firstpost.com', 'www.androidpure.com', 'forums.windowscentral.com',
                'theusbport.com','www.cultofmac.com', 'www.gizbot.com', 'gadgets.ndtv.com', 'www.gsmarena.com',
                'www.gadgetsnow.com', 'www.techshout.com', 'm.gadgets.ndtv.com', 'gamingcentral.in', 'www.mysmartprice.com',
                'www.phonebunch.com', 'www.game-debate.com', 'www.gsmdome.com']
entertainment_website = ['www.tollywood.net', 'www.bollywoodnews.org', 'www.onlykollywood.com', 'www.bollywoodcat.com',
                         'www.chitramala.in', 'www.cinejosh.com', 'www.televisionpost.com', 'www.bollywoodlife.com',
                         'www.bollywoodhungama.com', 'www.bollywoodbubble.com', 'www.bollywoodmdb.com', 'www,filmfare.com',
                         'www.filmibeat.com', 'www.movietalkies.com', 'movies.ndtv.com', 'www.koimoi.com', 'photos.filmibeat.com']
auto_website = ['indianautosblog.com', 'www.motoroids.com', 'auto.ndtv.com', 'www.team-bhp.com', 'www.zigwheels.com',
                'www.motorbeam.com', 'm.carandbike.com', 'www.autocarpro.in', 'motoroctane.com', 'www.carblogindia.com',
                'm.autocarindia.com', 'www.autocar.co.uk', 'www.drivespark.com', 'www.carwale.com', 'www.wheels24.co.za',
                'www.zigwheels.com', 'www.autocarindia.com', 'bikeindia.in', 'carindia.in', 'www.autox.in', 'www.topgear.com',
                'www.cardekho.com', 'm.autocarindia.com']
lifestyle_website = ['www.fashionlady.in', 'www.vogue.in', 'www.misskyra.com', 'www.ifairer.com', 'www.curejoy.com',
                     'in.style.yahoo.com', 'faithit.com', 'www.womenshealthmag.com', 'stylesatlife.com', 'www.providr.com',
                     'www.yourtango.com', 'www.thehealthsite.com', 'psychcentral.com', 'blogs.psychcentral.com', 'food.ndtv.com',
                     'doctor.ndtv.com', 'm.food.ndtv.com', 'www.femina.in', 'www.theedgymind.com', 'www.boldsky.com', 'www.modasta.com',
                     'thehealthorange.com', 'zenparent.in', 'www.parents.com', 'www.happytrips.com', 'www.motherearthnews.com',
                     'www.momjunction.com', 'new.theastrologer.com', 'recipes.timesofindia.com', 'www.astroyogi.com',
                     'pro.psychcentral.com', 'detechter.com', 'news.mynahcare.com', 'www.boredpanda.com']
science_website = ['www.sci-news.com']
national_website = ['www.naukrinama.com', 'www.livelaw.in']
international_website = ['www.middleeastmonitor.com']

sport_word = {"sport": {"cricket": ["cricket", "bcci"], "football": ["football", "soccer", "fifa", "nfl"], "basketball": ["nba", "basketball", "cba"], "golf": ["golf", "pga", "lpga", "usga"], "tennis": ["tennis", "wta", "atp", "itf"], "rugby": ["rugby", "rwc", "irb"], "badminton": ["badminton"], "boxing": ["boxing", "wbo", "wbc", "wba", "ibf"], "hockey": ["hockey", "nhl"], "wrestling": ["wrestling", "wwe"], "olympic": ["olympic"], "lacrosse": ["lacrosse"], "cycling": ["cycling"], "baseball": ["baseball", "mlb"], "racing": ["f1", "formula", "racing", "motorsport"]}}
tech_word = {"tech": {"sci-tech": ["robot", "driveless", "slam"], "tablet": ["tablet", "ipad", "mediapad", "pad", "zenpad"], "tv": ["tv"], "camera": ["camera", "cameras"], "mobile phone": ["iphone", "nova", "redmi", "zenfone", "phone", "mate", "smartphone"], "computer": ["laptop", "matebook", "macbook", "notebook", "thinkpad", "workstation", "ideapad", "laptops", "workstations", "zenbook", "vivobook", "chromebook"], "internet": ["wifi", "wi-fi", "routers", "router", "switch", "switches", "adapter", "adapters"], "app": ["app", "apps"], "software": ["software"], "gadget": ["gadget", "gadgets", "gpu", "nvidia", "amd", "cpu", "monitor", "audio", "keyboard", "headset", "monitor"], "games": ["xbox", "ps4", "nintendo", "playstation", "playstations"]}}
entertainment_word = {"entertainment": {"celebrity": ["celebrities", "celebrity", "celeb", "celebs", "actress", "actor", "director", "singer"], "gossip": ["gossip"], "movie": ["cinema", "movies", "movienews", "film", "oscar", "horror", "trailer", "films", "movie", "tollywood", "pollywood", "cinemas"], "tv": ["television", "netflix", "tv", "episode"], "music": ["music", "mtv"], "reading": ["book", "books"], "dance": ["dance"], "comic": ["comic", "animation"]}}
science_word = {"science": ["science", "space", "mars", "moon", "satellite", "environmentails", "nasa", "rocket", "ice", "species", "spacecraft", "surface", "soil", "gene", "genes"]}
auto_word = {"auto": {"motor": ["motor", "jawa", "royal", "bike", "bikes", "yamaha", "bajaj", "scooter", "scooters"], "car": ["suzuki", "hyundai", "car", "cars", "suv", "suvs", "mercedes", "bmw", "audi", "volvo", "volkswagan", "nissan", "lamborghini", "ford", "toyota", "tesla", "jaguar", "skoda"]}}
lifestyle_word = {"lifestyle": {"health": ["anxiety", "heroine", "cancer", "diabetes", "disease", "therspist", "illness", "mental", "mind", "spiritual", "spiritually", "yoga", "exercising", "weight-loss", "fitness"], "fashion": ["clothes", "wedding", "weddings", "fashion", "hair", "makeup", "makeups", "skin", "beauty", "lip", "eye", "eyebrows", "handbags", "luxury", "luxuries", "prada", "burberry", "bvlgari", "chanel", "cartier", "dior", "furla", "gucci", "givenchy", "armani", "hermes", "lv", "piaget", "rolex", "tiffany", "tissot", "versace", "ysl"], "funny": ["jokes", "weird", "weirdness", "funny", "humor", "interest", "humors"], "relationship": ["love", "sex", "marriage", "sexual", "relations", "friendship", "relationships", "lgbt", "relationship"], "parenting": ["child", "diaper", "diapers", "kid", "kids", "children", "pregnant", "gravida"], "food": ["recipe", "recipes", "snack", "snacks", "maincourse", "cocktail", "wine", "coffee", "drink", "juices"], "animal": ["pets", "cats", "dogs", "dog", "cat", "pet", "puppy", "kitten", "puppies", "kittens"], "horoscope": ["horoscope", "horoscopes", "libra", "scorpio", "capricorn", "aries", "taurus", "gemini", "virgo", "sagittarius", "aquarius", "pisces"], "travel": ["tourism", "travel"], "zodiac": ["zodiac", "zodiacs", "zodiacal"], "home": ["garden", "gardening", "ikea", "architecture", "decoration"]}}

def pre_predict_subcategory(dataFile, classedFile, unclassedFile, words_list, topcategory):
    cnt_map = dict()
    f = open(dataFile, 'r', encoding='utf-8')
    outf1 = open(classedFile, 'a', encoding='utf-8')
    outf2 = open(unclassedFile, 'a', encoding='utf-8')
    try:
        while True:
            line = f.readline().strip('\n')
            line_json = json.loads(line)
            url = line_json["url"]
            title = line_json["title"].lower()
            top_category = line_json["predict_top_category"]
            # website = urlparse(url).netloc
            if top_category == topcategory:
                flag = 0
                line_json["top_category"] = topcategory
                tmp = list(words_list.values())[0]
                for w in title.split(" "):
                    if w.isalpha():
                        for k, v in tmp.items():
                            if w in v:
                                flag = 1
                                line_json["sub_category"] = k
                                if k in cnt_map:
                                    cnt_map[k] += 1
                                else:
                                    cnt_map[k] = 1
                                outf1.write(json.dumps(line_json) + "\n")
                                outf1.flush()
                            continue
                        continue
                if flag == 0:
                    line_json["sub_category"] = topcategory
                    outf2.write(json.dumps(line_json) + "\n")
                    outf2.flush()
                continue
    except Exception as e:
        print(e)
    finally:
        outf1.close()
        outf2.close()
    return cnt_map


