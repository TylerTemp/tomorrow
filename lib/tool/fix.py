# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

jolla = db.jolla
article = db.article

main_url = 'https://dn-jolla.qbox.me/'

cover = (
    ('Welcome-to-the-official-Jolla-Blog!', 'welcome_image_etusivu.jpeg'),
    ('The-importance-of-why---A-story-powered-by-people', 'post-med-640x480.jpg'),
    ('jolla-tablet-hardware-adaptation-team-day-zero-bootstrapping', 'uus.jpeg'),
    ('merry-xmas-happy-holidays-jolla', 'pieni.jpeg'),
    ('sailfish-os-update-performance-improvements-new-features', 'Blog_lake2.jpeg'),
    ('crowdsourcing-producing-something-love', 'jolla-guys-thumb.png'),
    ('hacknplay-20150109', 'hack-thumb.png'),
    ('from-2014-to-2015', 'asaar-feat.png'),
    ('ringing-new-year-community-love', 'communityvisit03b-640x480.jpg'),
    ('What’s-going-on---Iteration-1-of-2015', 'group_photo1-640x474.jpg'),
    ('hacknplay-23-january-2015', 'hack2-thumb.jpg'),
    ('Jolla-Tablet-returns-to-Indiegogo---introducing-the-64GB-version', 'imgo_narrow.jpeg'),
    ('introducing-jolla-angry-birds-stella-limited-edition', 'stella_01e1_hd-640x400.png'),
    ('hacknplay-20150209', 'hacknplay_thumb.jpg'),
    ('Road-to-Mobile-World-Congress-2015---iteration-2', 'marc-small.png'),
    ('experiencing-fosdem-2015', '20150131_006a-640x480.jpg'),
    ('Sailfish-OS-update-Yliaavanlampi', 'rel11_small1.jpeg'),
    ('Jolla-Tablet:-Hardware-adaptation-video-update', 'hw_adaptation_demo1-640x480.png'),
    ('hacknplay-20150313', 'HP_March13_thumb.jpg'),
    ('mobile-world-congress-2015', 'big_image_thumb.jpg'),
    ('Jolla-iteration-3:-finalizing-the-first-Jolla-Tablet-demo', 'iteration3_thumb.jpg'),
    ('mapbagrag-high-quality-accessories-with-love-from-austria', 'jollablogproductionmapbagrag3-640x480.jpg'),
    ('design-insights-sailfish-os', 'Blog_header_small.jpg'),
    ('hacknplay-20150417', 'HP_Apr17_thumb.jpg'),
    ('Jolla-iteration-4:-news-about-Jolla-Tablet-shipping-schedule-and-more', 'patience-thumb.png'),
    ('Jolla-Ambience-Photo-Campaign-continues---take-part-now!', 'ambience_entry_favs-640x480.jpg'),
    ('Developer-spotlight:-Siteshwar-on-open-source-and-Sailfish-Browser', 'private_browsing_huechange_1-640x480.png'),
    ('Jolla-Tablet-Developer-Device-loan-program-starting-soon', 'pilot_tablet_fb-640x451.jpeg'),
    ('A-Peek-at-our-Ambience-Pic-Picks', 'ambience_street_art1-640x480.jpg'),
    ('sailfish-os-aaslakkajarvi', 'Aaslakka_thumb.jpg'),
    ('lastu-and-jolla', '20150615-IMG_1542_featured.jpg'),
    ('updating-sailfish-os-really-pays-off', 'update_sailfishos-640x480.png'),
    ('flattr-your-favourite-apps-and-devs', 'Flattr_blog-640x480.jpg'),
)

for jolla_slug, img_slug in cover:
    j = jolla.find_one({'url': jolla_slug})
    assert j is not None, jolla_slug
    j['cover'] = main_url + img_slug
    jolla.save(j)

    article.update_many(
        {'board': 'jolla', 'transref': j['url']},
        {'$set': {'transinfo.cover': j['cover'], 'transinfo.headimg': j['headimg']}}
    )
