"""
Seed script to populate MongoDB with 5 YouTube videos and ~100 comments each.
Run from the project root: python scripts/seed_data.py
Requires MONGO_URI to be set in your .env file or environment.
"""

import os
import random
import datetime
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

try:
    from sentence_transformers import SentenceTransformer
    _sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("SBERT model loaded for seeding.")
except Exception as e:
    _sbert_model = None
    print(f"WARNING: SBERT not available, embeddings will be empty: {e}")

MONGO_URI = os.environ["MONGO_URI"]

# ─── 5 Real YouTube Videos ───────────────────────────────────────────────────

VIDEOS = [
    {
        "video_id": 1,
        "title": "Never Gonna Give You Up",
        "description": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
        "duration": "3:33",
        "creator_id": "RickAstleyVEVO",
    },
    {
        "video_id": 2,
        "title": "Despacito",
        "description": "Luis Fonsi - Despacito ft. Daddy Yankee (Official Music Video)",
        "duration": "4:42",
        "creator_id": "LuisFonsiVEVO",
    },
    {
        "video_id": 3,
        "title": "Shape of You",
        "description": "Ed Sheeran - Shape of You (Official Music Video)",
        "duration": "4:24",
        "creator_id": "EdSheeranVEVO",
    },
    {
        "video_id": 4,
        "title": "See You Again",
        "description": "Wiz Khalifa - See You Again ft. Charlie Puth (Official Video) | Fast & Furious 7",
        "duration": "3:58",
        "creator_id": "AtlanticVideos",
    },
    {
        "video_id": 5,
        "title": "Uptown Funk",
        "description": "Mark Ronson - Uptown Funk ft. Bruno Mars (Official Video)",
        "duration": "4:30",
        "creator_id": "MarkRonsonVEVO",
    },
]

# ─── Test Users ───────────────────────────────────────────────────────────────

USERNAMES = [
    "musicfan99", "chill_vibes", "nightowl22", "alex_reviews", "melody_lover",
    "bass_drop", "sarah_k", "dj_spinz", "retro_wave", "pixel_queen",
    "zen_master", "nova_star", "echo_beats", "sunny_days", "cloud9_music",
    "wave_rider", "beat_junkie", "luna_tunes", "vibe_check", "sonic_boom",
    "rhythm_king", "aurora_sky", "deep_bass", "neon_lights", "crystal_clear",
    "thunder_roll", "velvet_voice", "cosmic_dj", "golden_ear", "silver_tone",
]

USERS = [
    {"user_name": u, "password": generate_password_hash("password123"), "isCreator": False}
    for u in USERNAMES
] + [
    {"user_name": "RickAstleyVEVO", "password": generate_password_hash("creator123"), "isCreator": True},
    {"user_name": "LuisFonsiVEVO", "password": generate_password_hash("creator123"), "isCreator": True},
    {"user_name": "EdSheeranVEVO", "password": generate_password_hash("creator123"), "isCreator": True},
    {"user_name": "AtlanticVideos", "password": generate_password_hash("creator123"), "isCreator": True},
    {"user_name": "MarkRonsonVEVO", "password": generate_password_hash("creator123"), "isCreator": True},
]

# ─── Comment Templates Per Video ─────────────────────────────────────────────

COMMENTS_BY_VIDEO = {
    1: {
        "positive": [
            "This song is a timeless masterpiece, never gets old!",
            "Rick Astley's voice is pure gold",
            "I came here voluntarily and I'm proud of it",
            "Best song of the 80s hands down",
            "This deserves every single view it has",
            "Absolute banger, been listening for years",
            "The fact that this is still trending says everything",
            "Rick Astley is a legend, no debate",
            "I love how this song brings everyone together",
            "This song makes me so happy every time",
            "Genuinely one of the best pop songs ever written",
            "The vocals on this track are incredible",
            "I have this on repeat and I'm not ashamed",
            "This song is proof that great music is eternal",
            "Rick really never let us down with this one",
            "Added this to every single playlist I have",
            "This song always puts me in a good mood",
            "What an iconic performance, love it",
            "The world needs more music like this",
            "Can we appreciate how good this beat is?",
            "I smile every time this comes on",
            "Legendary track from a legendary artist",
            "This is the song that defines a generation",
            "Perfect song for any occasion honestly",
            "Rick Astley deserves way more recognition",
            "Been a fan since the 80s, still love it",
            "This song just hits different at night",
            "One of those songs you never skip",
            "Absolute classic, everyone knows this one",
            "The chorus is so catchy it's insane",
            "Rick's dance moves are underrated honestly",
            "This gives me the best vibes every single time",
            "I genuinely love this song unironically",
            "The production quality was ahead of its time",
            "Came for the meme, stayed for the music",
            "This should be the official anthem of the internet",
            "Rick Astley walking in slow motion is peak cinema",
            "My grandma knows this song, that's how iconic it is",
            "The fact this keeps growing in views is wild",
            "Whoever mixed this track deserves an award",
            "I unironically have this as my alarm tone",
            "This song survived multiple generations of the internet",
            "Rick Astley live shows are still incredible",
            "You can hear the passion in every note",
        ],
        "negative": [
            "I've been rickrolled too many times, I'm tired",
            "Honestly this song is so overplayed at this point",
            "Not my style of music at all",
            "The meme ruined this song for me completely",
            "I wish people would stop sending me this link",
            "This song was never that good to begin with",
            "The auto-rickroll culture needs to die already",
            "Can't believe this has so many views for a meme",
            "I skip this every time it comes on",
            "The 80s production sounds really dated now",
            "This doesn't hold up compared to modern music",
            "I'm so sick of hearing this everywhere",
            "This was funny the first time but now it's annoying",
            "There are way better 80s songs than this one",
            "People only know this because of the internet joke",
            "I really don't get why everyone loves this",
            "This song is so repetitive it hurts",
            "Overrated because of a meme, nothing more",
            "The lyrics are pretty basic if you think about it",
            "I cringe every time someone links this to me",
            "The backing track sounds like elevator music honestly",
            "This song is only relevant because of a joke, not talent",
            "I actively avoid any link that could lead here",
            "The drums on this track sound so robotic and stiff",
        ],
        "neutral": [
            "How did this become the biggest meme on the internet?",
            "I wonder how Rick Astley feels about being a meme",
            "What year was this originally released?",
            "Is this the most viewed music video ever?",
            "The rickroll phenomenon is fascinating from a cultural perspective",
            "Does anyone know who produced this track?",
            "I read somewhere that Rick didn't make much money from this initially",
            "The video quality is surprisingly good for the 80s",
            "How many views does this get per day?",
            "I think this was released in 1987 if I remember correctly",
            "The music video was filmed in London apparently",
            "Rick Astley was only 21 when he recorded this",
            "This song has been covered by so many artists",
            "I just realized this song has been around for almost 40 years",
            "The bartender in the music video is a nice touch",
            "Who else got sent here by a friend?",
            "Watching this in 2026, the internet never changes",
            "This has to be one of YouTube's most visited pages",
            "I wonder what the actual view count would be without rickrolls",
            "Someone should do a documentary about this song's internet history",
            "The transition from verse to chorus is pretty smooth",
            "Rick Astley made a comeback recently which is cool",
            "This song charted in like 25 different countries",
            "I always forget how deep his voice actually is",
            "Just here because someone sent me a suspicious link",
            "The stock ticker reference says this was written by Stock Aitken Waterman",
            "This entire genre of pop was called Hi-NRG back in the day",
            "I wonder how many people discover this naturally vs being rickrolled",
            "Rick Astley retired and then came back, interesting career arc",
            "The dance style in the video is so distinctly 80s it's funny",
        ],
    },
    2: {
        "positive": [
            "This song is an absolute masterpiece of Latin pop",
            "The beat on this is infectious, can't stop dancing",
            "Despacito changed the music industry forever",
            "Luis Fonsi and Daddy Yankee are an incredible duo",
            "This song makes every summer feel amazing",
            "The rhythm is so catchy it stays in your head for days",
            "One of the best Latin songs of all time",
            "This song brings so much joy and energy",
            "The music video is gorgeous, the scenery is beautiful",
            "I don't even speak Spanish but I love every second",
            "This song deserved every record it broke",
            "Despacito put Latin music on the global map",
            "The guitar intro is absolutely beautiful",
            "I've played this at every party and it always hits",
            "This song is pure fire from start to finish",
            "Luis Fonsi's voice is so smooth on this track",
            "Best summer anthem of the decade without question",
            "The reggaeton vibes on this are perfect",
            "This song makes me want to learn Spanish",
            "Daddy Yankee's verse goes so hard",
            "I can't hear this without wanting to dance",
            "This is the song that brought everyone together globally",
            "Certified classic, still sounds amazing years later",
            "The way this blends pop and reggaeton is genius",
            "This song is the definition of a worldwide hit",
            "My favorite song to play at barbecues and pool parties",
            "The production on this track is top tier",
            "Everyone in the world knows this song and that's beautiful",
            "Despacito made me fall in love with Latin music",
            "I've listened to this hundreds of times and it never gets old",
            "This is the song of the decade, change my mind",
            "Perfect vibes for driving with the windows down",
            "The collaboration is legendary",
            "This song transcends language barriers completely",
            "Puerto Rico should be so proud of this masterpiece",
            "I learned all the words phonetically and I'm proud",
            "This song is the reason I took Spanish in school",
            "Every summer playlist needs this track",
            "The chemistry between Fonsi and Daddy Yankee is electric",
            "This is what peak Latin pop sounds like",
            "The video has such vibrant colors and energy",
            "This makes any car ride ten times more fun",
            "I wish I could dance like the people in the video",
            "Despacito is literally the soundtrack of summer",
            "This restored my faith in popular music",
        ],
        "negative": [
            "This song was way too overplayed on the radio",
            "I'm so tired of hearing this everywhere I go",
            "The remix with Bieber ruined the original vibe",
            "This got annoying after the millionth time hearing it",
            "Overrated song, there are better Latin tracks out there",
            "I had to hear this in every store for two years straight",
            "The lyrics are honestly pretty inappropriate",
            "This song is catchy but not actually that good musically",
            "I don't understand the massive hype around this",
            "Every restaurant played this nonstop, I'm traumatized",
            "The music video views are inflated by bots probably",
            "There are so many better reggaeton songs out there",
            "This song set an unrealistic standard for Latin music",
            "I can't stand the chorus anymore after hearing it so much",
            "The beat is too repetitive for a four minute song",
            "Not a fan of the autotune on this track",
            "This was popular because of marketing not quality",
            "I wish people would discover other Latin artists",
            "The song peaked in 2017 and should stay there",
            "I have PTSD from this being played everywhere",
            "The lyrics translation is way too suggestive for radio",
            "This killed any chance of other Latin songs getting airplay",
            "I find the video boring compared to the actual song",
            "The auto-tune ruins what could have been a decent track",
            "This song is proof that viral does not mean quality",
        ],
        "neutral": [
            "How many billion views does this have now?",
            "Is this still the most viewed video on YouTube?",
            "I wonder how much revenue this generated for YouTube",
            "The Justin Bieber remix brought a whole new audience",
            "What does Despacito actually mean in English?",
            "This song was number one in how many countries?",
            "Luis Fonsi had been making music for years before this blew up",
            "The music video was filmed in La Perla, Puerto Rico",
            "I read that this was the first Spanish language song to hit #1 in decades",
            "Daddy Yankee is basically the king of reggaeton",
            "The YouTube record this set was incredible",
            "How long did this stay at number one on Billboard?",
            "This song was released in January 2017 for those wondering",
            "The cultural impact of this song is worth studying",
            "I think this proved that non-English songs can dominate globally",
            "Someone told me this song took years to write",
            "The original version without Bieber is quite different",
            "Interesting how this brought reggaeton to mainstream pop",
            "Puerto Rico's music scene really thrived after this",
            "I wonder what Luis Fonsi is working on now",
            "The model in the music video is Zuleyka Rivera",
            "This song has been translated into like 30 languages",
            "I remember when this broke the YouTube view record",
            "The song uses a pretty standard reggaeton beat structure",
            "Fun fact: this was uploaded on January 12, 2017",
            "The music video budget must have been pretty high",
            "I think this was co-written with Erika Ender",
            "Reggaeton as a genre has roots in Panama and Puerto Rico",
            "This helped normalize Spanish language music on US charts",
        ],
    },
    3: {
        "positive": [
            "Shape of You is such an incredibly catchy song",
            "Ed Sheeran is one of the most talented artists alive",
            "This beat makes me want to dance every single time",
            "Love the tropical house vibe on this track",
            "Ed Sheeran knows exactly how to make a hit",
            "This is the perfect song for working out",
            "The melody is so addictive, absolute earworm",
            "Ed's songwriting ability is just on another level",
            "Best pop song of 2017 without question",
            "I've had this on my gym playlist since it came out",
            "The marimba riff is iconic at this point",
            "Ed Sheeran makes music for everyone and that's his gift",
            "This song has such good energy throughout",
            "Love how Ed can make a simple concept sound amazing",
            "The production on this is so clean and polished",
            "This was the soundtrack to my 2017, love it",
            "Ed really showed his versatility with this track",
            "One of those songs that instantly puts you in a good mood",
            "The rhythm section on this is absolutely fire",
            "Been listening to this for years and still not tired of it",
            "Ed Sheeran concerts are amazing and this song live is even better",
            "This is a masterclass in pop songwriting",
            "The way this song builds is really satisfying",
            "Perfect blend of pop and dance music",
            "This deserves all the streams it has gotten",
            "Ed Sheeran is a national treasure for real",
            "I remember hearing this for the first time and being hooked instantly",
            "The chorus is absolutely unforgettable",
            "This was the biggest song of 2017 for good reason",
            "Ed makes it look so easy but this is genius level writing",
            "I could listen to this on repeat all day",
            "The beat drop is so satisfying",
            "This song single-handedly made 2017 a great year for music",
            "Ed Sheeran is the GOAT of modern pop",
            "Play this at any party and everyone starts moving",
            "Ed Sheeran's range as an artist is truly remarkable",
            "I discovered Ed through this song and now I own every album",
            "The way the beat kicks in gets me every time",
            "This is what happens when talent meets the right production",
            "Ed live with just a loop pedal is something else entirely",
            "My favorite workout track, keeps me going every time",
            "The way this song flows is really impressive",
            "Ed makes songwriting look effortless honestly",
            "This track has aged really well compared to other 2017 songs",
            "The percussion arrangement is really clever if you listen closely",
        ],
        "negative": [
            "This is the most generic pop song Ed has ever made",
            "Shape of You ruined Ed Sheeran for me honestly",
            "Way too commercial compared to his earlier work",
            "I miss the old Ed Sheeran who played acoustic guitar",
            "This song was played to death on every radio station",
            "Ed sold out with this track, not authentic at all",
            "The lyrics are pretty shallow compared to his other songs",
            "I skip this every time it comes on shuffle",
            "Ed Sheeran has so many better songs than this one",
            "This was designed to be catchy and nothing more",
            "I preferred Ed when he was making music like A Team",
            "This song represents everything wrong with pop music",
            "Too repetitive, gets old after the first minute",
            "The tropical house trend this started was terrible",
            "Not a fan of how commercialized this sounds",
            "This song has no soul compared to his acoustic work",
            "I'm tired of hearing this in every store and restaurant",
            "Ed can do so much better than this formulaic pop",
            "The lyrics don't mean anything deep at all",
            "Overplayed and overrated honestly",
            "This sounds like every other pop song from 2017",
            "I expected more depth from someone of Ed's caliber",
            "The lyrics are cringeworthy in some parts",
            "I genuinely prefer his acoustic stuff over this produced pop",
            "This song was a cash grab and everyone knows it",
        ],
        "neutral": [
            "Wasn't this originally written for Rihanna?",
            "How long did this stay at number one on the charts?",
            "The music video was choreographed really well",
            "Ed Sheeran apparently wrote this in like 30 minutes",
            "I heard this song was almost not included on the album",
            "The martial arts theme in the video is interesting",
            "This was the lead single from the Divide album",
            "How many Grammys did this win?",
            "I think the marimba sound is actually a sample",
            "Ed Sheeran has had such a long career for his age",
            "This competes with Despacito for views which is crazy",
            "The song uses a pentatonic scale which is why it's so catchy",
            "I wonder how many covers of this exist on YouTube",
            "The boxing gym scene in the video was filmed in Seattle",
            "Ed was already huge before this but this made him a superstar",
            "This is technically a dance-pop track with tropical house elements",
            "I remember this being everywhere in early 2017",
            "Galway Girl is on the same album and it's quite different",
            "Ed Sheeran broke Spotify records with this",
            "The songwriting credits include like five people",
            "I read that the initial demo sounded completely different",
            "This was released on January 6, 2017",
            "The woman in the music video is Jennie Pegouskie",
            "Interesting that this became bigger than Castle on the Hill",
            "Ed Sheeran's concerts sell out in minutes",
            "I think he performed this at the Brit Awards",
            "The original demo was apparently much more minimal",
            "Ed Sheeran has written songs for other major artists too",
            "This charted in basically every country with a music chart",
        ],
    },
    4: {
        "positive": [
            "This song makes me cry every single time I hear it",
            "The most beautiful tribute song ever created",
            "Charlie Puth's piano is absolutely soul-touching",
            "Paul Walker would be so proud of this tribute",
            "This is one of the most emotional songs I've ever heard",
            "The combination of Wiz and Charlie is perfect",
            "I can't listen to this without thinking of Paul Walker",
            "This song heals and hurts at the same time",
            "The piano melody is hauntingly beautiful",
            "Best movie soundtrack song of all time",
            "This song perfectly captures the feeling of loss",
            "Charlie Puth's voice is angelic on this track",
            "I've played this at so many memorials, it speaks to everyone",
            "The lyrics are so meaningful and heartfelt",
            "This song transcends the movie it was made for",
            "I played this at my best friend's funeral and everyone cried",
            "Wiz Khalifa really poured his heart into this verse",
            "The most emotional song to ever exist on YouTube",
            "This is the definition of a song that touches your soul",
            "I can feel every emotion in Charlie Puth's voice",
            "This song helped me through the hardest time of my life",
            "Beautiful tribute that the whole world connected with",
            "The chorus gives me chills every single time",
            "Music has never made me feel this much before",
            "This is more than a song, it's a universal message of love",
            "Every note in this song is absolutely perfect",
            "The world needed this song and it delivered",
            "I don't even watch Fast and Furious but this song is incredible",
            "Charlie Puth wrote this about his friend and you can feel it",
            "This is the kind of song that changes your perspective on life",
            "I have never heard a more sincere and genuine song",
            "The bridge section is the most powerful part for me",
            "This song reminds me to appreciate the people in my life",
            "Pure emotion, pure talent, pure art",
            "I wish I could listen to this for the first time again",
            "This song gives me strength during tough moments",
            "Charlie and Wiz complement each other perfectly",
            "The emotional weight of this track is unreal",
            "I've never seen a comment section so emotional",
            "This song captures the essence of true friendship",
            "Everyone who has lost someone understands this song",
            "The vocal performance here is absolutely stunning",
            "I cry happy tears listening to this now",
            "This is the most played song at memorial services for a reason",
            "Music therapy at its finest, this song heals",
        ],
        "negative": [
            "This song is overly sentimental and manipulative",
            "Hollywood using Paul Walker's death for profit is wrong",
            "Charlie Puth's voice is too whiny for my taste",
            "This song is way too overplayed at this point",
            "I don't like how the movie franchise monetized grief",
            "The auto-tune on Wiz Khalifa's part is too much",
            "There are way better tribute songs out there",
            "This felt more like a marketing move than genuine tribute",
            "I find this song incredibly repetitive and boring",
            "The rap verse doesn't fit the emotional tone at all",
            "This is the most cliche sad song ever made",
            "I can't stand how everyone uses this for clout",
            "The piano loop gets really annoying after a while",
            "This was designed to make people cry, not genuine art",
            "I think the fame went to their heads after this",
            "The song is fine but people overrate it massively",
            "Too slow for my taste, I prefer upbeat music",
            "The mixing on this track could have been better",
            "Wiz Khalifa had way better songs before this",
            "I think this song is only popular because of the context",
            "The song is emotionally manipulative and I don't like that",
            "Charlie Puth's falsetto is grating to listen to",
            "There are more sincere tribute songs that get no attention",
            "The marketing around this song felt exploitative",
            "This gets used for every sad TikTok and it's annoying",
        ],
        "neutral": [
            "Did Charlie Puth actually write this about his own friend too?",
            "How long did this stay at number one on Billboard?",
            "The music video has clips from all the Fast and Furious movies",
            "I think Paul Walker passed away in 2013",
            "This was the second most viewed video for a long time",
            "Charlie Puth was discovered through YouTube originally",
            "The piano riff was apparently written in like 10 minutes",
            "Wiz Khalifa is from Pittsburgh, Pennsylvania",
            "This song was on the Furious 7 soundtrack",
            "How much did this song make in royalties?",
            "I wonder if Vin Diesel had any input on this song",
            "The ending of Furious 7 with this song playing is iconic",
            "Charlie Puth went on to have a really successful solo career",
            "This was released in March 2015",
            "The music video was directed by Marc Klasfeld",
            "I think this won a few awards at various ceremonies",
            "The song samples some classic piano compositions",
            "Paul Walker's brothers helped finish Furious 7",
            "This competed with Uptown Funk on the charts",
            "Interesting how the song works even without the movie context",
            "Wiz Khalifa's verse references his personal experiences",
            "The song was in the Billboard top 10 for like 20 weeks",
            "Charlie Puth can play multiple instruments apparently",
            "This is one of the highest certified singles ever",
            "The YouTube view count on this is insane",
            "I wonder how the cast of Fast and Furious reacted to this",
            "This song has been used in so many tribute compilations",
            "The song structure is pretty standard pop ballad format",
            "Charlie Puth's career really took off after this single",
        ],
    },
    5: {
        "positive": [
            "Uptown Funk is the ultimate party anthem",
            "Bruno Mars absolutely killed it on this track",
            "This song makes it impossible not to dance",
            "Best feel-good song of the 2010s for sure",
            "Bruno Mars is the most entertaining performer alive",
            "The groove on this is absolutely insane",
            "Mark Ronson and Bruno Mars is a legendary combination",
            "I play this at every party and the energy is amazing",
            "This song is pure happiness in audio form",
            "Bruno Mars has the voice, the moves, and the charisma",
            "The bassline on this track is funky perfection",
            "Uptown Funk is a modern classic already",
            "I can't sit still when this song comes on",
            "This is the song that revived funk for a new generation",
            "Bruno Mars was born to make music like this",
            "The energy in this song is absolutely unmatched",
            "Every second of this song is perfectly crafted",
            "This should be played at every celebration ever",
            "Bruno Mars is a generational talent, this proves it",
            "The bridge section of this song is so smooth",
            "I've danced to this at three different weddings",
            "This is the definition of a feel-good banger",
            "Mark Ronson's production on this is flawless",
            "The horn section adds so much flavor",
            "This song never fails to lift my spirits",
            "Bruno Mars channels James Brown energy perfectly here",
            "Uptown Funk is a song everyone on earth loves",
            "The live performances of this are absolutely incredible",
            "Best collaboration in modern music history",
            "I could listen to this every day for the rest of my life",
            "The drum pattern is so groovy it hurts",
            "Bruno Mars is a musical genius and this proves it",
            "This song makes every road trip ten times better",
            "The breakdown at the end is absolute fire",
            "Greatest party song of all time, no competition",
            "The energy in the music video is infectious",
            "Bruno Mars is the king of stage presence",
            "This song deserves to be in the hall of fame",
            "I dare anyone to listen to this and not move their body",
            "The production quality on this is studio perfection",
            "Every time this comes on I feel like I can conquer the world",
            "Bruno Mars channels the best of funk and soul",
            "Mark Ronson knew exactly what he was doing with this beat",
            "This is the most fun I've ever had listening to a song",
            "The swagger in Bruno's delivery is unmatched in modern music",
        ],
        "negative": [
            "This song is way too overplayed and I'm sick of it",
            "Uptown Funk is just a rehash of old funk songs",
            "Bruno Mars doesn't have an original bone in his body",
            "I've heard this so many times I want to scream",
            "This song is catchy but incredibly shallow musically",
            "Mark Ronson doesn't get enough credit, it's all Bruno hype",
            "The plagiarism lawsuits around this song are telling",
            "I skip this every time it comes on the radio",
            "This song tries too hard to be retro and it shows",
            "There's nothing innovative about recycling 80s funk",
            "Bruno Mars is overrated, he just copies older artists",
            "This was played in every commercial and it's annoying",
            "The lyrics are super repetitive and unoriginal",
            "I don't understand why this won so many awards",
            "This song represents the dumbing down of pop music",
            "Every DJ plays this and it's become so predictable",
            "The novelty wore off after the first month",
            "I prefer actual funk music from the 70s and 80s",
            "Bruno Mars can sing but this song is lazy writing",
            "The most overplayed song at weddings and events",
            "Bruno Mars is just doing karaoke of 80s hits at this point",
            "The hook is catchy but the verses are forgettable",
            "I can't take the hype seriously for a retro copycat",
            "This song relies on nostalgia rather than innovation",
            "DJs who still play this in 2026 need new material",
        ],
        "neutral": [
            "How many weeks was this at number one?",
            "This song won the Grammy for Record of the Year I think",
            "Mark Ronson is actually a really accomplished producer",
            "The music video has the classic retro aesthetic",
            "Bruno Mars is from Hawaii originally",
            "I think this song faced some copyright issues",
            "How much money did this song generate in total?",
            "The song was released in November 2014",
            "Bruno Mars has been performing since he was a kid",
            "This samples from several different funk sources",
            "The Saturday Night Live performance made this blow up",
            "Mark Ronson had been making music for decades before this",
            "I heard they went through like 80 versions before the final one",
            "This was on the album Uptown Special",
            "Bruno Mars also co-wrote this along with several others",
            "The choreography in the music video is really tight",
            "I think this was the best selling single of 2015",
            "The 'hot damn' ad lib became a catchphrase",
            "Jeff Bhasker was also a producer on this track",
            "This competed with See You Again for the top spot",
            "The trumpet section is played by real musicians",
            "Bruno Mars Super Bowl performance featured this",
            "Interesting how this blends retro and modern production",
            "The song is in D-flat major which is unusual for pop",
            "Mark Ronson is actually British which surprises people",
            "The song took like two years of studio work apparently",
            "This was part of a whole funk revival wave in pop music",
            "Bruno Mars also did 24K Magic which has similar vibes",
            "The copyright case involved The Gap Band I think",
        ],
    },
}

# ─── Embedding Generation (384-dim SBERT) ────────────────────────────────────


def generate_sbert_embeddings(texts):
    """Generate real SBERT embeddings for a list of texts."""
    if _sbert_model is None:
        return [[] for _ in texts], list(range(len(texts)))
    embeddings = _sbert_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    labels = [i % 4 for i in range(len(texts))]
    return [e.tolist() for e in embeddings], labels


def random_timestamp(days_back=365):
    """Generate a random ISO timestamp within the past N days."""
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = datetime.timedelta(
        days=random.randint(1, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return (now - delta).isoformat()


def build_comments_for_video(video_id, comment_pool):
    """Build comment documents for a single video from its comment pool."""
    all_texts = []
    sentiments_list = []

    for sentiment, texts in comment_pool.items():
        for text in texts:
            all_texts.append(text)
            sentiments_list.append(sentiment)

    n = len(all_texts)
    embeddings, clusters = generate_sbert_embeddings(all_texts)

    # Shuffle to mix sentiments in the comment order
    combined = list(zip(all_texts, sentiments_list, embeddings, clusters))
    random.shuffle(combined)

    # Generate sorted timestamps (older comments first)
    timestamps = sorted([random_timestamp() for _ in range(n)])

    comments = []
    pos_count = neg_count = neu_count = 0

    for i, (text, sentiment, embedding, cluster) in enumerate(combined):
        if sentiment == "positive":
            pos_count += 1
        elif sentiment == "negative":
            neg_count += 1
        else:
            neu_count += 1

        comments.append({
            "video_id": video_id,
            "user_id": random.choice(USERNAMES),
            "comment": text,
            "embedding": embedding,
            "cluster": cluster,
            "sentiment": sentiment,
            "replies": [],
            "timestamp": timestamps[i],
        })

    sentiment_summary = {
        "video_id": video_id,
        "positive": pos_count,
        "negative": neg_count,
        "neutral": neu_count,
    }

    return comments, sentiment_summary


# ─── Main Seed Function ──────────────────────────────────────────────────────


def main():
    print("Connecting to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        retryWrites=True,
        serverSelectionTimeoutMS=10000,
    )
    db = client.get_default_database()

    # Verify connection
    client.admin.command("ping")
    print("Connected successfully!")

    # Clear existing data
    print("Clearing existing collections...")
    for col_name in ["videos", "comments", "sentimentDetail", "users", "clusterReply"]:
        db[col_name].drop()

    # Create indexes
    print("Creating indexes...")
    db.comments.create_index([("video_id", 1)])
    db.comments.create_index([("video_id", 1), ("cluster", 1)])
    db.comments.create_index([("video_id", 1), ("user_id", 1)])
    db.comments.create_index([("video_id", 1), ("timestamp", 1)])
    db.videos.create_index([("video_id", 1)], unique=True)
    db.users.create_index([("user_name", 1)], unique=True)
    db.sentimentDetail.create_index([("video_id", 1)], unique=True)
    db.clusterReply.create_index([("video_id", 1), ("cluster_no", 1)])

    # Insert users
    print(f"Inserting {len(USERS)} users...")
    db.users.insert_many(USERS)

    # Insert videos
    print(f"Inserting {len(VIDEOS)} videos...")
    db.videos.insert_many(VIDEOS)

    # Insert comments and sentiment data
    total_comments = 0
    all_sentiments = []

    for video in VIDEOS:
        vid = video["video_id"]
        comment_pool = COMMENTS_BY_VIDEO[vid]
        comments, sentiment_summary = build_comments_for_video(vid, comment_pool)

        db.comments.insert_many(comments)
        all_sentiments.append(sentiment_summary)
        total_comments += len(comments)
        print(f"  Video {vid} ({video['title']}): {len(comments)} comments "
              f"(+{sentiment_summary['positive']} -{sentiment_summary['negative']} "
              f"~{sentiment_summary['neutral']})")

    # Insert sentiment summaries
    db.sentimentDetail.insert_many(all_sentiments)

    print(f"\nSeed complete!")
    print(f"  Videos: {len(VIDEOS)}")
    print(f"  Users: {len(USERS)}")
    print(f"  Comments: {total_comments}")
    print(f"  Sentiment records: {len(all_sentiments)}")

    client.close()


if __name__ == "__main__":
    main()
