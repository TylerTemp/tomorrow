# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote
from pprint import pprint
import json
from pymongo import ReturnDocument

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article, Jolla
sys.path.pop(0)

aoll = Article._article
joll = Jolla._jolla

s = '''
["Welcome-to-the-official-Jolla-Blog!", "Welcome-to-the-official-Jolla-Blog!", ["Jolla Blog", "Jolla Story"]]
["merry-xmas-happy-holidays-jolla", "merry-xmas-happy-holidays-jolla", ["Jolla Story"]]
["The-importance-of-why---A-story-powered-by-people", "The-importance-of-why---A-story-powered-by-people", ["Jolla Story", "Jolla Tablet"]]
["jolla-tablet-hardware-adaptation-team-day-zero-bootstrapping", "jolla-tablet-hardware-adaptation-team-day-zero-bootstrapping", ["Development", "Hardware", "Jolla Tablet"]]
["sailfish-os-update-performance-improvements-new-features", "sailfish-os-update-performance-improvements-new-features", ["Development", "Sailfish OS", "Software Updates"]]
["crowdsourcing-producing-something-love", "crowdsourcing-producing-something-love", ["Development", "Jolla Tablet", "Sailfish OS", "together.jolla.com"]]
["hacknplay-20150109", null, ["Development", "Hack'n'play", "Hardware", "Sailfish OS"]]
["ringing-new-year-community-love", "ringing-new-year-community-love", ["Community", "Events", "Jolla Story"]]
["What\u2019s-going-on---Iteration-1-of-2015", "What\u2019s-going-on---Iteration-1-of-2015", ["Community", "Events", "Jolla Story", "Jolla Tablet", "Sailfish OS"]]
["Jolla-Tablet-returns-to-Indiegogo---introducing-the-64GB-version", "Jolla-Tablet-returns-to-Indiegogo---introducing-the-64GB-version", ["Jolla Tablet"]]
["introducing-jolla-angry-birds-stella-limited-edition", "introducing-jolla-angry-birds-stella-limited-edition", ["Jolla smartphone", "The Other Half"]]
["Road-to-Mobile-World-Congress-2015---iteration-2", "Road-to-Mobile-World-Congress-2015---iteration-2", ["Community", "Development", "Events", "Sailfish OS"]]
["Sailfish-OS-update-Yliaavanlampi", "Sailfish-OS-update-Yliaavanlampi", ["Development", "Jolla smartphone", "Sailfish OS", "Software Updates"]]
["Jolla-Ambience-Photo-Campaign-continues---take-part-now!", "Jolla-Ambience-Photo-Campaign-continues---take-part-now!", ["Community", "Design", "Jolla Tablet", "Sailfish OS"]]
["hacknplay-23-january-2015", null, ["Development", "Hack'n'play", "Hardware"]]
["hacknplay-20150209", null, ["Development", "Hack'n'play", "Hardware"]]
["experiencing-fosdem-2015", "experiencing-fosdem-2015", ["Community", "Events", "Jolla Tablet", "Sailfish OS"]]
["Jolla-Tablet:-Hardware-adaptation-video-update", "Jolla-Tablet:-Hardware-adaptation-video-update", ["Development", "Hardware", "Jolla Tablet", "Sailfish OS"]]
["hacknplay-20150313", null, ["Development", "Hack'n'play", "Hardware"]]
["mobile-world-congress-2015", null, ["Community", "Events", "Jolla Tablet", "Sailfish OS"]]
["Jolla-iteration-3:-finalizing-the-first-Jolla-Tablet-demo", "Jolla-iteration-3:-finalizing-the-first-Jolla-Tablet-demo", ["Development", "Iterations", "Jolla smartphone", "Jolla Tablet", "Sailfish OS", "Software Updates"]]
["mapbagrag-high-quality-accessories-with-love-from-austria", "mapbagrag-high-quality-accessories-with-love-from-austria", ["Accessories", "Jolla smartphone", "Jolla Tablet", "Partner Stories"]]
["design-insights-sailfish-os", "design-insights-sailfish-os", ["Design", "Jolla Tablet", "Sailfish OS"]]
["hacknplay-20150417", null, ["Development", "Hack'n'play"]]
["Jolla-iteration-4:-news-about-Jolla-Tablet-shipping-schedule-and-more", "Jolla-iteration-4:-news-about-Jolla-Tablet-shipping-schedule-and-more", ["Iterations", "Jolla Tablet", "Sailfish OS"]]
["Sailfish-OS-update-\u00c4ij\u00e4np\u00e4iv\u00e4nj\u00e4rvi-now-available-for-everyone!", "Sailfish-OS-update-\u00c4ij\u00e4np\u00e4iv\u00e4nj\u00e4rvi-now-available-for-everyone!", ["Development", "Sailfish OS", "Software Updates"]]
["Developer-spotlight:-Siteshwar-on-open-source-and-Sailfish-Browser", "Developer-spotlight:-Siteshwar-on-open-source-and-Sailfish-Browser", ["Community", "Developer Stories", "Open Source", "Sailfish OS"]]
["Jolla-Tablet-Developer-Device-loan-program-starting-soon", "Jolla-Tablet-Developer-Device-loan-program-starting-soon", ["Community", "Development", "Jolla Tablet", "Sailfish OS"]]
["sailfish-os-aaslakkajarvi", "lastu-and-jolla", ["Development", "Sailfish OS", "Software Updates"]]
["A-Peek-at-our-Ambience-Pic-Picks", "A-Peek-at-our-Ambience-Pic-Picks", ["Community", "Design", "Jolla Tablet", "Sailfish OS"]]
["lastu-and-jolla", "lastu-and-jolla", ["Accessories", "Design", "Jolla smartphone", "Jolla Tablet", "Partner stories", "The Other Half"]]
["updating-sailfish-os-really-pays-off", "updating-sailfish-os-really-pays-off", ["Development", "Jolla smartphone", "Jolla Tablet", "Sailfish OS", "Software Updates"]]
["flattr-your-favourite-apps-and-devs", "flattr-your-favourite-apps-and-devs", ["Applications", "Community", "Development"]]
["july-jolla-tablet-update", "july-jolla-tablet-update", ["Iterations", "Jolla Tablet", "Sailfish OS"]]
["jolla-ambience-photo-campaign", "jolla-ambience-photo-campaign", ["Community", "Design", "Jolla Tablet", "Sailfish OS"]]
["a-look-at-jolla-tablet-backers", "a-look-at-jolla-tablet-backers", ["Accessories", "Community", "Indiegogo", "Jolla Tablet"]]
["early-access-sailfish-os-bjorntrasket", "early-access-sailfish-os-bjorntrasket", ["Development", "Sailfish OS", "Software Updates"]]
["next-pipeline-sailfish-os-2-0", "next-pipeline-sailfish-os-2-0", ["Events", "Jolla Story", "Sailfish OS", "Strategy"]]
["jolla-tablet-display-shipping-update", "jolla-tablet-display-shipping-update", ["Development", "Indiegogo", "Jolla Tablet"]]
["jolla-tablet-hardware-update", "jolla-tablet-hardware-update", ["Development", "Hardware", "Indiegogo", "Jolla Tablet"]]
["first-batch-of-jolla-tablets-completed", "first-batch-of-jolla-tablets-completed", ["Development", "Hardware", "Indiegogo", "Jolla Tablet"]]
["jolla-tablet-developer-loan-devices-shipped", "jolla-tablet-developer-loan-devices-shipped", ["Community", "Development", "Jolla Tablet", "Sailfish OS"]]
["jolla-tablet-sales-box-accessories-update", "jolla-tablet-sales-box-accessories-update", ["Accessories", "Design", "Indiegogo", "Jolla Tablet"]]
["pre-orders-jolla-tablet-now-open", "pre-orders-jolla-tablet-now-open", ["Jolla Story", "Jolla Tablet"]]
["jolla-tablet-differences-old-new-hardware", "jolla-tablet-differences-old-new-hardware", ["Development", "Hardware", "Indiegogo", "Jolla Tablet"]]
["from-2014-to-2015", "from-2014-to-2015",  ["Events","Jolla smartphone","Jolla Story","Jolla Tablet","Sailfish OS","Strategy"] ]
'''

all_tags = set()

for line in s.splitlines():
    if not line.strip():
        continue
    j, a, t = json.loads(line)
    tags = [x.strip().lower() for x in t]
    all_tags.update(tags)

    res = joll.find_one_and_update({'slug': j}, {'$set': {'tag': tags}}, return_document=ReturnDocument.AFTER)
    if a:
        res = aoll.find_one_and_update({'slug': a}, {'$set': {'tag': tags}}, return_document=ReturnDocument.AFTER)

for each in all_tags:
    print(each)
