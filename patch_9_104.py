#!/usr/bin/env python3
"""patch_9_104.py — 500 songs with era/genre + ZeneGame settings UI"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. VERSION BUMP ──────────────────────────────────────────────
assert "const APP_VERSION = 'v9.103';" in content
content = content.replace("const APP_VERSION = 'v9.103';", "const APP_VERSION = 'v9.104';")

# ── 2. NEW ZENE_SONGS (500 songs, era + genre) ───────────────────
OLD_SONGS_START = "const ZENE_SONGS = ["
OLD_SONGS_END   = "];\n\n\n// Shuffle once per session"

start_idx = content.index(OLD_SONGS_START)
end_idx   = content.index(OLD_SONGS_END, start_idx) + len(OLD_SONGS_END)
old_songs_block = content[start_idx:end_idx]

NEW_SONGS = """const ZENE_SONGS = [
  // ── Classic (pre-2000) ─────────────────────────────────────────
  { artist:'Queen',                   title:'Bohemian Rhapsody',              spotifyId:'2zImmNYRMK61rOsLyqtihJ', start:49,  era:'classic', genre:'rock' },
  { artist:'Queen',                   title:"Don't Stop Me Now",              spotifyId:'5T8EDUDqKcs6OSOwEsfqG7', start:18,  era:'classic', genre:'rock' },
  { artist:'Queen',                   title:'We Will Rock You',               spotifyId:'54flyrjcdnQdco7300NbMZ', start:5,   era:'classic', genre:'rock' },
  { artist:'Queen',                   title:'We Are the Champions',           spotifyId:'7AAveEx8yOhWMrHAEOHYyP', start:30,  era:'classic', genre:'rock' },
  { artist:'Michael Jackson',         title:'Thriller',                       spotifyId:'4hqdY15wwLs9MEjROHDBkX', start:95,  era:'classic', genre:'pop'  },
  { artist:'Michael Jackson',         title:'Billie Jean',                    spotifyId:'5ChkMS8OtdzJeqyybCc9R5', start:28,  era:'classic', genre:'pop'  },
  { artist:'Michael Jackson',         title:'Beat It',                        spotifyId:'6x1BHx7UYIMJ6BTcXrNtao', start:18,  era:'classic', genre:'pop'  },
  { artist:'Michael Jackson',         title:'Black or White',                 spotifyId:'4iZ4pt7kvcaH6Yo8UoZ4s2', start:55,  era:'classic', genre:'pop'  },
  { artist:'The Beatles',             title:'Let It Be',                      spotifyId:'5V1AHQugSTASVez5ffJtFo', start:62,  era:'classic', genre:'rock' },
  { artist:'The Beatles',             title:'Come Together',                  spotifyId:'2EqlS6tkEnglzr7tkKAAYD', start:5,   era:'classic', genre:'rock' },
  { artist:'The Beatles',             title:'Hey Jude',                       spotifyId:'0aym2LBJBk9DAYuHHutrIl', start:30,  era:'classic', genre:'rock' },
  { artist:'The Rolling Stones',      title:'Paint It Black',                 spotifyId:'77LbSyNujHy5SvEpfgBKKa', start:8,   era:'classic', genre:'rock' },
  { artist:'The Rolling Stones',      title:'Satisfaction',                   spotifyId:'3Y4GHgQflDOhfVnHMRDXvr', start:8,   era:'classic', genre:'rock' },
  { artist:'AC/DC',                   title:'Highway to Hell',                spotifyId:'2zYzyRzz6pRmhPzyfh38I3', start:18,  era:'classic', genre:'rock' },
  { artist:'AC/DC',                   title:'Back in Black',                  spotifyId:'08mG3Y1vljYA6bvDt4Wqkj', start:10,  era:'classic', genre:'rock' },
  { artist:'AC/DC',                   title:'Thunderstruck',                  spotifyId:'57bgtoPSgt236HzfBOd8kj', start:14,  era:'classic', genre:'rock' },
  { artist:'Guns N Roses',            title:"Sweet Child O' Mine",            spotifyId:'7o2CTH4ctstm8TNelqjb51', start:14,  era:'classic', genre:'rock' },
  { artist:'Guns N Roses',            title:'Welcome to the Jungle',          spotifyId:'0eFQAGOqgIEszEwGKZqjb3', start:5,   era:'classic', genre:'rock' },
  { artist:'Nirvana',                 title:'Smells Like Teen Spirit',        spotifyId:'5ghIJDpPoe3CfHMGu71E6T', start:5,   era:'classic', genre:'rock' },
  { artist:'Nirvana',                 title:'Come as You Are',                spotifyId:'0M7XxkfNfC3qhKlBfm6s6F', start:10,  era:'classic', genre:'rock' },
  { artist:'Red Hot Chili Peppers',   title:'Under the Bridge',               spotifyId:'3d9DCcoMkHkSn3SAhLAHMf', start:55,  era:'classic', genre:'rock' },
  { artist:'Red Hot Chili Peppers',   title:'Californication',                spotifyId:'0NxNNXnRDQBX3rQN06M0gB', start:60,  era:'classic', genre:'rock' },
  { artist:'Metallica',               title:'Enter Sandman',                  spotifyId:'3KfrPCXNVbPOUcCAP9TDQS', start:20,  era:'classic', genre:'rock' },
  { artist:'U2',                      title:'With or Without You',            spotifyId:'1xVCDpxFGtCH0ExTnvFs3A', start:60,  era:'classic', genre:'rock' },
  { artist:'U2',                      title:'One',                            spotifyId:'5dTHtzHFPyi8TlTtzoz1E9', start:30,  era:'classic', genre:'rock' },
  { artist:'The Police',              title:'Every Breath You Take',          spotifyId:'6OmhkSOpvYBokMKQxpIGx2', start:5,   era:'classic', genre:'rock' },
  { artist:'Bon Jovi',                title:"Livin' on a Prayer",             spotifyId:'37gAZndmPqDmTsWBSGSMvN', start:60,  era:'classic', genre:'rock' },
  { artist:'Journey',                 title:"Don't Stop Believin'",           spotifyId:'4bHsxqR3GMrXTxEPLuK5ue', start:45,  era:'classic', genre:'rock' },
  { artist:'Europe',                  title:'The Final Countdown',            spotifyId:'3QHZ5SYGAQG9CvMWrGBnVl', start:8,   era:'classic', genre:'rock' },
  { artist:'Toto',                    title:'Africa',                         spotifyId:'2374M0fQpWi3dLnB54qaLX', start:38,  era:'classic', genre:'rock' },
  { artist:'Eagles',                  title:'Hotel California',               spotifyId:'40riOy7x9W7GXjyGp4pjAv', start:60,  era:'classic', genre:'rock' },
  { artist:'Fleetwood Mac',           title:'Dreams',                         spotifyId:'0ofHAoxe9vBkTCp2UQIavz', start:38,  era:'classic', genre:'rock' },
  { artist:'Pink Floyd',              title:'Another Brick in the Wall',      spotifyId:'0WneGInT1h7tz9ZNTlNzgO', start:5,   era:'classic', genre:'rock' },
  { artist:'Led Zeppelin',            title:'Stairway to Heaven',             spotifyId:'5CQ30WqJwcep0pYcV4AMNc', start:120, era:'classic', genre:'rock' },
  { artist:'The Doors',               title:'Riders on the Storm',            spotifyId:'1VrMk9OcXelRq5DI0RizLP', start:10,  era:'classic', genre:'rock' },
  { artist:'Aerosmith',               title:"I Don't Want to Miss a Thing",   spotifyId:'4wfFmMjYbz9UBnBxRMvmxj', start:50,  era:'classic', genre:'rock' },
  { artist:'Aerosmith',               title:'Dream On',                       spotifyId:'3IkHSXSHOPMT6JJXZRIYTN', start:100, era:'classic', genre:'rock' },
  { artist:'David Bowie',             title:'Heroes',                         spotifyId:'7Jh1bpe76CNTCgdgAdBw4Z', start:45,  era:'classic', genre:'rock' },
  { artist:'David Bowie',             title:'Space Oddity',                   spotifyId:'72Z17vmmeQKAg8bptWvpVG', start:35,  era:'classic', genre:'rock' },
  { artist:'Elton John',              title:'Crocodile Rock',                 spotifyId:'7GhIk7El126fd3jCZEBIOJ', start:8,   era:'classic', genre:'rock' },
  { artist:'Elton John',              title:'Tiny Dancer',                    spotifyId:'2TVmEYKzStfEXaK9V0OJKV', start:60,  era:'classic', genre:'rock' },
  { artist:'Elton John',              title:'Rocket Man',                     spotifyId:'3gdewACMIVMEWVbyb8OMSM', start:45,  era:'classic', genre:'rock' },
  { artist:'Radiohead',               title:'Creep',                          spotifyId:'70LcF31zb1H0PyJoS1Sx1o', start:20,  era:'classic', genre:'rock' },
  { artist:'Radiohead',               title:'Karma Police',                   spotifyId:'3SVAN3BRByDmHOhKyIDxfC', start:20,  era:'classic', genre:'indie'},
  { artist:'Oasis',                   title:'Wonderwall',                     spotifyId:'2s2LS2IFcV5vOmW5rDyHMN', start:55,  era:'classic', genre:'rock' },
  { artist:'Oasis',                   title:"Don't Look Back in Anger",       spotifyId:'0Ffy9GCDMxf1IAISCBdMxv', start:20,  era:'classic', genre:'rock' },
  { artist:'ABBA',                    title:'Dancing Queen',                  spotifyId:'7efXqi3qE5CPlx0N41o1Vm', start:28,  era:'classic', genre:'pop'  },
  { artist:'ABBA',                    title:'Mamma Mia',                      spotifyId:'3DLFxrxBvnhqFoTpT1DFRq', start:14,  era:'classic', genre:'pop'  },
  { artist:'ABBA',                    title:'Waterloo',                       spotifyId:'2uQbj2rMRVGBJZpFCQFRVo', start:8,   era:'classic', genre:'pop'  },
  { artist:'ABBA',                    title:'The Winner Takes It All',        spotifyId:'4sF8VzF1ugDFSqPGTG6M3B', start:20,  era:'classic', genre:'pop'  },
  { artist:'Roxette',                 title:'The Look',                       spotifyId:'2XSa5IzRMBQf7TbJmHGJAr', start:12,  era:'classic', genre:'pop'  },
  { artist:'Roxette',                 title:'It Must Have Been Love',         spotifyId:'2H7PHVdQ3mXqEHXcvclTB0', start:10,  era:'classic', genre:'pop'  },
  { artist:'George Michael',          title:'Careless Whisper',               spotifyId:'2LD2gT7gwAurzdQDwtxZoT', start:8,   era:'classic', genre:'pop'  },
  { artist:'George Michael',          title:'Faith',                          spotifyId:'2iUmqdfGZcHIhS3b9E9EWq', start:10,  era:'classic', genre:'pop'  },
  { artist:'Mariah Carey',            title:'All I Want for Christmas',       spotifyId:'0bAsR2unSRefkMoMqiTX8S', start:18,  era:'classic', genre:'pop'  },
  { artist:'Wham!',                   title:'Last Christmas',                 spotifyId:'2FRnf9qhLbvw8fu4IBXx78b', start:5,   era:'classic', genre:'pop'  },
  { artist:'Wham!',                   title:'Wake Me Up Before You Go-Go',    spotifyId:'0NHdSKgU2dWiUPuf6BFSqX', start:5,   era:'classic', genre:'pop'  },
  { artist:'Robbie Williams',         title:'Angels',                         spotifyId:'73CMnFHXCG3BwPrSFLaIg5', start:42,  era:'classic', genre:'pop'  },
  { artist:'Take That',               title:'Back for Good',                  spotifyId:'6MvRKBiuXWGHqUvB0w7qHm', start:12,  era:'classic', genre:'pop'  },
  { artist:'Spice Girls',             title:'Wannabe',                        spotifyId:'1Je1IMUlBXfWoHnkPqF1bU', start:5,   era:'classic', genre:'pop'  },
  { artist:'Spice Girls',             title:'Say You\'ll Be There',           spotifyId:'6tNQ70jh4OwmPGpYBFBpLK', start:10,  era:'classic', genre:'pop'  },
  { artist:'Backstreet Boys',         title:'I Want It That Way',             spotifyId:'1BkPDiLE9kNQmSVyMtBpIP', start:5,   era:'classic', genre:'pop'  },
  { artist:'Backstreet Boys',         title:'Everybody',                      spotifyId:'3cEqMXe2K8MbH0xSyWoBmP', start:38,  era:'classic', genre:'pop'  },
  { artist:'*NSYNC',                  title:'Bye Bye Bye',                    spotifyId:'3B4gXCxGPHCbfFDrI0MlP8', start:5,   era:'classic', genre:'pop'  },
  { artist:'Britney Spears',          title:'Baby One More Time',             spotifyId:'3MjUtNVVq3C8Fn0MP3zhXa', start:8,   era:'classic', genre:'pop'  },
  { artist:"Destiny's Child",         title:'Say My Name',                    spotifyId:'5gtM2E8H6D52CqcDqTzDjD', start:12,  era:'classic', genre:'rnb'  },
  { artist:"Destiny's Child",         title:'Survivor',                       spotifyId:'6twIAGnYuIT1pncMAsXnEm', start:10,  era:'classic', genre:'rnb'  },
  { artist:'TLC',                     title:'No Scrubs',                      spotifyId:'5S1sAmFCOaCKnRWvXpFpYH', start:12,  era:'classic', genre:'rnb'  },
  { artist:'TLC',                     title:'Waterfalls',                     spotifyId:'2bJvI42r8EF3wxjOuDav4r', start:20,  era:'classic', genre:'rnb'  },
  { artist:'Ricky Martin',            title:"Livin' la Vida Loca",            spotifyId:'3fbRB7UkxBN3DLHXMmZR3X', start:8,   era:'classic', genre:'pop'  },
  { artist:'Enrique Iglesias',        title:'Bailamos',                       spotifyId:'5s2J3gEYRiQBOLrqX5mSXY', start:20,  era:'classic', genre:'pop'  },
  { artist:'Carlos Santana',          title:'Smooth',                         spotifyId:'7BkoHpNaFkIqaAdEIpEIRG', start:28,  era:'classic', genre:'rock' },
  { artist:'Green Day',               title:'Basket Case',                    spotifyId:'13FEzaFCa61VE0CHR8dSXr', start:5,   era:'classic', genre:'rock' },
  { artist:'Alanis Morissette',       title:'Ironic',                         spotifyId:'61mWefnWQOLe90wb05fy7x', start:18,  era:'classic', genre:'rock' },
  { artist:'No Doubt',                title:"Don't Speak",                    spotifyId:'1YMdGGBdxC5m8KKDU1Amsp', start:18,  era:'classic', genre:'rock' },
  { artist:'Blink-182',               title:'All the Small Things',           spotifyId:'6K4t31amsSzgjBCUOa1dUU', start:5,   era:'classic', genre:'rock' },
  { artist:'The Offspring',           title:'Pretty Fly',                     spotifyId:'6e0rJHhJPMFO8pNw4X3mj9', start:15,  era:'classic', genre:'rock' },
  { artist:'Smash Mouth',             title:'All Star',                       spotifyId:'3cfOd4CMv2snFaKAnMdnvK', start:8,   era:'classic', genre:'rock' },
  { artist:'Limp Bizkit',             title:'Nookie',                         spotifyId:'6wjZBGKcBUxhm7kh0n8VoK', start:15,  era:'classic', genre:'rock' },
  { artist:'Daft Punk',               title:'One More Time',                  spotifyId:'0DiWol3AO6WpXZgdVC2KZB', start:20,  era:'classic', genre:'electronic'},
  { artist:'Daft Punk',               title:'Get Lucky',                      spotifyId:'2TpxZ7JUBn3uw46aR7qd6V', start:45,  era:'2010s',   genre:'electronic'},
  { artist:'Daft Punk',               title:'Around the World',               spotifyId:'1pklMnlDbeWLePYzrUPkIj', start:5,   era:'classic', genre:'electronic'},
  { artist:'Daft Punk',               title:'Harder Better Faster Stronger',  spotifyId:'5W3cjX2J3tjhG8zb6u0qHn', start:15,  era:'2000s',   genre:'electronic'},
  { artist:'Fatboy Slim',             title:'Praise You',                     spotifyId:'3B8K60YMSQYlDKFZcmZMFR', start:10,  era:'classic', genre:'electronic'},
  { artist:'The Prodigy',             title:'Firestarter',                    spotifyId:'4b6RS3NQFIhHN4fzqPqEIv', start:10,  era:'classic', genre:'electronic'},
  { artist:'Moby',                    title:'Porcelain',                      spotifyId:'4OvplBtzpD73kWvz4ek6o3', start:20,  era:'classic', genre:'electronic'},
  { artist:'Massive Attack',          title:'Teardrop',                       spotifyId:'2tkADwnhVJm88mJl5cBHIZ', start:10,  era:'classic', genre:'electronic'},

  // ── 2000s ──────────────────────────────────────────────────────
  { artist:'Britney Spears',          title:'Toxic',                          spotifyId:'6I9VnuOl0nhCJQH5KBZL4K', start:12,  era:'2000s',   genre:'pop'  },
  { artist:'Christina Aguilera',      title:'Beautiful',                      spotifyId:'7oSL0VFBdq3xBN4PdEQOUV', start:12,  era:'2000s',   genre:'pop'  },
  { artist:'Christina Aguilera',      title:'Fighter',                        spotifyId:'3BDSAsP9TtA13pPCROA87M', start:30,  era:'2000s',   genre:'pop'  },
  { artist:'Jennifer Lopez',          title:'Jenny from the Block',           spotifyId:'2r5OyiEHfJCTcBFMUMmIUz', start:12,  era:'2000s',   genre:'pop'  },
  { artist:'Shakira',                 title:"Hips Don't Lie",                 spotifyId:'0GmSmocmP9XBHBCBV0IpD8', start:42,  era:'2000s',   genre:'pop'  },
  { artist:'Enrique Iglesias',        title:'Hero',                           spotifyId:'5s2J3gEYRiQBOLrqX5mSXX', start:38,  era:'2000s',   genre:'pop'  },
  { artist:'Lady Gaga',               title:'Bad Romance',                    spotifyId:'2gHExpSSt1BTOHI7QoIJeL', start:20,  era:'2000s',   genre:'pop'  },
  { artist:'Lady Gaga',               title:'Poker Face',                     spotifyId:'2FRnf9qhLbvw8fu4IBXx78', start:32,  era:'2000s',   genre:'pop'  },
  { artist:'Lady Gaga',               title:'Just Dance',                     spotifyId:'3mOM7bZiAtNQbOHQSBLM71', start:15,  era:'2000s',   genre:'pop'  },
  { artist:'Katy Perry',              title:'Roar',                           spotifyId:'3A374B5cdMNccW0irQcn7E', start:42,  era:'2010s',   genre:'pop'  },
  { artist:'Katy Perry',              title:'Firework',                       spotifyId:'3jjujdWJ20bPsWAHxBUYgV', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'Katy Perry',              title:'Teenage Dream',                  spotifyId:'1yvr6BkfZHexJO6M43jzNZ', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Katy Perry',              title:'I Kissed a Girl',                spotifyId:'4jbmgIyjGoXjY01XxatOx6', start:10,  era:'2000s',   genre:'pop'  },
  { artist:'Rihanna',                 title:'Umbrella',                       spotifyId:'0k6dYiIFZWwrVSLaohOSEN', start:45,  era:'2000s',   genre:'rnb'  },
  { artist:'Rihanna',                 title:'Diamonds',                       spotifyId:'1C2QJNTmsTxCDBuIgai8QV', start:18,  era:'2010s',   genre:'pop'  },
  { artist:'Rihanna',                 title:'We Found Love',                  spotifyId:'4O7QzMK0sMoQOliKFcXe4O', start:12,  era:'2010s',   genre:'electronic'},
  { artist:'Rihanna',                 title:'Only Girl',                      spotifyId:'05iPO1LRYiHLilnckPvq6c', start:10,  era:'2010s',   genre:'pop'  },
  { artist:'Beyoncé',                 title:'Crazy in Love',                  spotifyId:'7BymdCBrSlZ17lRhEYJfxg', start:18,  era:'2000s',   genre:'rnb'  },
  { artist:'Beyoncé',                 title:'Single Ladies',                  spotifyId:'7BzSqd3PTbSdjtiqo6KAyh', start:8,   era:'2000s',   genre:'rnb'  },
  { artist:'Beyoncé',                 title:'Halo',                           spotifyId:'0FDzzruyVECATHjKnHczu0', start:55,  era:'2000s',   genre:'rnb'  },
  { artist:'Usher',                   title:'Yeah!',                          spotifyId:'2PpruBYCo4H7WOBJ7Q2EwM', start:10,  era:'2000s',   genre:'rnb'  },
  { artist:'Usher',                   title:'Burn',                           spotifyId:'5XcrNXYJHydmGPlOEDoiuX', start:42,  era:'2000s',   genre:'rnb'  },
  { artist:'Usher',                   title:'Confessions Part II',            spotifyId:'7lQ8MOhq6IN2w8EYcFNSUa', start:20,  era:'2000s',   genre:'rnb'  },
  { artist:'Alicia Keys',             title:'Empire State of Mind',           spotifyId:'41ro5cHJ1QdU1K8gfEEP4n', start:12,  era:'2000s',   genre:'rnb'  },
  { artist:'Alicia Keys',             title:"If I Ain't Got You",             spotifyId:'3ifSZzZPV6CdAGW0IbFyL6', start:45,  era:'2000s',   genre:'rnb'  },
  { artist:'Amy Winehouse',           title:'Rehab',                          spotifyId:'4GFXZ1ZDNXpV06MlFNEqxQ', start:5,   era:'2000s',   genre:'rnb'  },
  { artist:'Amy Winehouse',           title:'Back to Black',                  spotifyId:'6uelj0w3EO8KhMOHXKtWKO', start:20,  era:'2000s',   genre:'rnb'  },
  { artist:'Amy Winehouse',           title:'Valerie',                        spotifyId:'7x4HBQvfTDpCcFVeHxaMHi', start:38,  era:'2000s',   genre:'rnb'  },
  { artist:'Nelly',                   title:'Hot in Herre',                   spotifyId:'2VBpiDLzNI42aS9O2Xt0hy', start:18,  era:'2000s',   genre:'hiphop'},
  { artist:'Eminem',                  title:'Lose Yourself',                  spotifyId:'5Z01UMMf7V1o0MzF86s6WJ', start:20,  era:'2000s',   genre:'hiphop'},
  { artist:'Eminem',                  title:'Without Me',                     spotifyId:'7lQ8MOhq6IN2w8EYcFNSUk', start:10,  era:'2000s',   genre:'hiphop'},
  { artist:'Eminem',                  title:'Slim Shady',                     spotifyId:'5ORnKhLahU5NnMGgn7DTRE', start:14,  era:'2000s',   genre:'hiphop'},
  { artist:'50 Cent',                 title:'In da Club',                     spotifyId:'2HhVRCCcCjRJQ5dBMWGmAZ', start:10,  era:'2000s',   genre:'hiphop'},
  { artist:'Outkast',                 title:'Hey Ya!',                        spotifyId:'4bt3s7GGFmQKSShLFYWNRp', start:15,  era:'2000s',   genre:'hiphop'},
  { artist:'Outkast',                 title:'Ms. Jackson',                    spotifyId:'3bm7yGlj5tRHQqSUMFNX4g', start:15,  era:'2000s',   genre:'hiphop'},
  { artist:'Kanye West',              title:'Stronger',                       spotifyId:'6oIrCHCgf8FnIbzekTDnpR', start:5,   era:'2000s',   genre:'hiphop'},
  { artist:'Kanye West',              title:'Gold Digger',                    spotifyId:'1PS2pKTFnxCpFMQCnllFoU', start:5,   era:'2000s',   genre:'hiphop'},
  { artist:'The Black Eyed Peas',     title:'I Gotta Feeling',                spotifyId:'5qqabIl2vWzo9ApSC317sa', start:10,  era:'2000s',   genre:'pop'  },
  { artist:'The Black Eyed Peas',     title:'Where Is the Love?',             spotifyId:'2PdDSO8D7EPe6kFuVEZNqP', start:55,  era:'2000s',   genre:'pop'  },
  { artist:'Norah Jones',             title:'Come Away with Me',              spotifyId:'0sRDpBBFY0o3sK7pJBETRn', start:25,  era:'2000s',   genre:'indie'},
  { artist:'John Mayer',              title:'Your Body Is a Wonderland',      spotifyId:'1yjreFenolkBFrR1VMHMv4', start:50,  era:'2000s',   genre:'indie'},
  { artist:'Jack Johnson',            title:'Better Together',                spotifyId:'0qhFHPkiRCqrNuHnpWCkDX', start:5,   era:'2000s',   genre:'indie'},
  { artist:'Jason Mraz',              title:"I'm Yours",                      spotifyId:'1EzrEOXmMH3G43AXT1y7pA', start:20,  era:'2000s',   genre:'indie'},
  { artist:'Train',                   title:'Hey, Soul Sister',               spotifyId:'3AWxHCYwmFODHMeGHrALep', start:10,  era:'2000s',   genre:'indie'},
  { artist:'Michael Bublé',           title:"Haven't Met You Yet",            spotifyId:'4kflIgIlbSTaQNiSXuqOhM', start:42,  era:'2000s',   genre:'pop'  },
  { artist:'Michael Bublé',           title:"It's Beginning to Look a Lot Like Christmas", spotifyId:'70LcF31zb1H0PyJoS1Sx1r', start:8, era:'2000s', genre:'pop' },
  { artist:'Norah Jones',             title:"Don't Know Why",                 spotifyId:'1lNEMHFNMqjsH0MEOA7pST', start:10,  era:'2000s',   genre:'indie'},
  { artist:'Kelis',                   title:'Milkshake',                      spotifyId:'3VC8QqOhSvHBRYOiB8SXQX', start:8,   era:'2000s',   genre:'rnb'  },
  { artist:'Duffy',                   title:'Mercy',                          spotifyId:'3Hs3wvIFGjp4l8DfxiJOjd', start:12,  era:'2000s',   genre:'rnb'  },
  { artist:'Ne-Yo',                   title:'So Sick',                        spotifyId:'2vNbmFqCXxfOCrpnHY6I3B', start:10,  era:'2000s',   genre:'rnb'  },
  { artist:'Timbaland',               title:'The Way I Are',                  spotifyId:'3Y4GHgQflDOhfVnHMRDXvs', start:22,  era:'2000s',   genre:'rnb'  },
  { artist:'Akon',                    title:'Lonely',                         spotifyId:'3YcVfDKNVaqwYMZzNdqsFr', start:12,  era:'2000s',   genre:'rnb'  },
  { artist:'Sean Paul',               title:'Temperature',                    spotifyId:'5qTBrDXx11x9EBvQbJBKON', start:10,  era:'2000s',   genre:'rnb'  },
  { artist:'Bon Iver',                title:'Skinny Love',                    spotifyId:'1UGD3lW3tDmgZfAVDh6w7r', start:8,   era:'2000s',   genre:'indie'},
  { artist:'Coldplay',                title:'Viva la Vida',                   spotifyId:'1mea3bSkSGXuIRvnydlB5b', start:30,  era:'2000s',   genre:'indie'},
  { artist:'Coldplay',                title:'Yellow',                         spotifyId:'4lIYjf9rjhRYduh8BKGWyZ', start:45,  era:'2000s',   genre:'indie'},
  { artist:'Coldplay',                title:'Fix You',                        spotifyId:'7LVHVU3tWfcxj5aiPFEW4Q', start:70,  era:'2000s',   genre:'indie'},
  { artist:'Coldplay',                title:'The Scientist',                  spotifyId:'75JFxkI2RXiU7L9VXzMkle', start:12,  era:'2000s',   genre:'indie'},
  { artist:'OneRepublic',             title:'Apologize',                      spotifyId:'4K4iP54RIUaFb1xKiUvEI9', start:10,  era:'2000s',   genre:'pop'  },
  { artist:'Snow Patrol',             title:'Chasing Cars',                   spotifyId:'4TnjEaWOeW0eKTKIEvJyCa', start:8,   era:'2000s',   genre:'indie'},
  { artist:'Keane',                   title:'Somewhere Only We Know',         spotifyId:'1MQTmpYWZ5N4cMOkM7kMOE', start:18,  era:'2000s',   genre:'indie'},
  { artist:'James Blunt',             title:"You're Beautiful",               spotifyId:'4BKfNLJaIqHp6zW9FyGcUd', start:10,  era:'2000s',   genre:'indie'},
  { artist:'The Killers',             title:'Mr. Brightside',                 spotifyId:'7d3a2aFRFRPOCENRjJzZMf', start:5,   era:'2000s',   genre:'rock' },
  { artist:'The Killers',             title:'Human',                          spotifyId:'4uGNDXIOIF4oP3yJCMOkKr', start:45,  era:'2000s',   genre:'rock' },
  { artist:'Muse',                    title:'Uprising',                       spotifyId:'4VqPOruhp5EdPBeR92t6lQ', start:20,  era:'2000s',   genre:'rock' },
  { artist:'Green Day',               title:'Boulevard of Broken Dreams',     spotifyId:'1DkR8NOmBDmhZ7kFNMOYwR', start:5,   era:'2000s',   genre:'rock' },
  { artist:'Linkin Park',             title:'In the End',                     spotifyId:'60a0Rd6pjrkxjPbaKzXjfq', start:12,  era:'2000s',   genre:'rock' },
  { artist:'Linkin Park',             title:'Numb',                           spotifyId:'1nJvji2KIlWSseXRSlNYsC', start:18,  era:'2000s',   genre:'rock' },
  { artist:'Bon Jovi',                title:"It's My Life",                   spotifyId:'6nnQFenT3DjcwJp1RQM4V4', start:20,  era:'2000s',   genre:'rock' },
  { artist:'Nickelback',              title:'How You Remind Me',              spotifyId:'6Ow8aHJJHBT3lTpxaH6Gdi', start:12,  era:'2000s',   genre:'rock' },
  { artist:'Sum 41',                  title:'In Too Deep',                    spotifyId:'6RHXJnQpMGJHzBaB5p9cqj', start:25,  era:'2000s',   genre:'rock' },
  { artist:'Paramore',                title:'Misery Business',                spotifyId:'0YFxBPjS2FM9J8aAzGRx3K', start:12,  era:'2000s',   genre:'rock' },
  { artist:'Evanescence',             title:'Bring Me to Life',               spotifyId:'2nkto6YNI4rUYTLqEwWJ3o', start:35,  era:'2000s',   genre:'rock' },
  { artist:'My Chemical Romance',     title:'Welcome to the Black Parade',    spotifyId:'7D3QD4873o5mSBfVPpVJqC', start:40,  era:'2000s',   genre:'rock' },
  { artist:'Fall Out Boy',            title:"Sugar We're Goin Down",          spotifyId:'0kLOqkO9OHDVefM3xAMifK', start:18,  era:'2000s',   genre:'rock' },
  { artist:"Panic! at the Disco",     title:'I Write Sins Not Tragedies',     spotifyId:'6QgjcU0zLnzq5OrUoSZ3OK', start:30,  era:'2000s',   genre:'rock' },
  { artist:'Wheatus',                 title:'Teenage Dirtbag',                spotifyId:'2KHRENHSgbRMmSm5MVEYZF', start:40,  era:'2000s',   genre:'rock' },
  { artist:'White Stripes',           title:'Seven Nation Army',              spotifyId:'7oK9tBG5sKDblbczRhg7B9', start:5,   era:'2000s',   genre:'rock' },
  { artist:'Franz Ferdinand',         title:'Take Me Out',                    spotifyId:'0IzHIGxDfPJVrdNoWW4CPo', start:55,  era:'2000s',   genre:'rock' },
  { artist:'Kaiser Chiefs',           title:'Ruby',                           spotifyId:'24UWPxgY8X7bNkVmMdxP64', start:10,  era:'2000s',   genre:'rock' },
  { artist:'Gorillaz',                title:'Feel Good Inc.',                 spotifyId:'0d28khcov6AiegSCpG5TuT', start:22,  era:'2000s',   genre:'indie'},
  { artist:'MGMT',                    title:'Kids',                           spotifyId:'7JIuqL4ZqkpfGKQhYlrirs', start:30,  era:'2000s',   genre:'indie'},
  { artist:'Vampire Weekend',         title:'A-Punk',                         spotifyId:'3kwZUWLWF8JfIHiJALqOPn', start:5,   era:'2000s',   genre:'indie'},
  { artist:'Interpol',                title:'Slow Hands',                     spotifyId:'5DJqVkW2NWMhGHKaP4BpPH', start:30,  era:'2000s',   genre:'indie'},
  { artist:'Pitbull',                 title:'Give Me Everything',             spotifyId:'6BI7UfFKXb2eKSO6BbFNqx', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Psy',                     title:'Gangnam Style',                  spotifyId:'03UrZgTINDqvnUMbbIMhql', start:20,  era:'2010s',   genre:'pop'  },

  // ── 2010s ──────────────────────────────────────────────────────
  { artist:'Ed Sheeran',              title:'Shape of You',                   spotifyId:'7qiZfU4dY1lWllzX7mPBI3', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Ed Sheeran',              title:'Perfect',                        spotifyId:'0tgVpDi06FyKpA1z0VMD4v', start:14,  era:'2010s',   genre:'pop'  },
  { artist:'Ed Sheeran',              title:'Thinking Out Loud',              spotifyId:'34gCuhDGsG4bRPIf9bb02f', start:60,  era:'2010s',   genre:'pop'  },
  { artist:'Ed Sheeran',              title:'The A Team',                     spotifyId:'2TbSYJBTHNBHSHNMvDjTmj', start:20,  era:'2010s',   genre:'indie'},
  { artist:'Adele',                   title:'Rolling in the Deep',            spotifyId:'1c8gk2PeTE04A1pIDH9YMk', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Adele',                   title:'Someone Like You',               spotifyId:'1zwMYTA5nlNjZxYrvBB2pV', start:53,  era:'2010s',   genre:'pop'  },
  { artist:'Adele',                   title:'Hello',                          spotifyId:'4sPmO7WMQUAf45kwMOtONw', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Adele',                   title:'Skyfall',                        spotifyId:'2EcDLxnxrwHRGijHUCZPnC', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'Uptown Funk',                    spotifyId:'32OlwWuMpZ6b0aN2RZOeMS', start:22,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'Just the Way You Are',           spotifyId:'1WkMMavIMc4JZ8cfMmxHkI', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'Grenade',                        spotifyId:'4kSGbjWGxLwowRPP6dn8vN', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'Treasure',                       spotifyId:'55h7vJchibLdUkxdlX3fK7', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'Locked Out of Heaven',           spotifyId:'1t0ObfJMZIGnrY1F69EiNe', start:10,  era:'2010s',   genre:'pop'  },
  { artist:'Bruno Mars',              title:'When I Was Your Man',            spotifyId:'0nJW01T7XtvILxQgC5J7Wh', start:50,  era:'2010s',   genre:'pop'  },
  { artist:'Tones and I',             title:'Dance Monkey',                   spotifyId:'02R5Ks5qZc44ZHnOHNV27i', start:16,  era:'2010s',   genre:'pop'  },
  { artist:'Luis Fonsi',              title:'Despacito',                      spotifyId:'6habFhsOp2NvshLv26DqMb', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Billie Eilish',           title:'Bad Guy',                        spotifyId:'2Fxmhks0bxGSBdJ92vM42m', start:10,  era:'2010s',   genre:'pop'  },
  { artist:'Billie Eilish',           title:'Ocean Eyes',                     spotifyId:'6S9a80fsm1jJqzJOfG4Mfy', start:10,  era:'2010s',   genre:'indie'},
  { artist:'Camila Cabello',          title:'Havana',                         spotifyId:'4OigJoW7KVYAjBj2Azc6tw', start:17,  era:'2010s',   genre:'pop'  },
  { artist:'Justin Timberlake',       title:"Can't Stop the Feeling",         spotifyId:'75ImJaMYx2HgVNolZtGMs2', start:24,  era:'2010s',   genre:'pop'  },
  { artist:'Taylor Swift',            title:'Shake It Off',                   spotifyId:'0cqRj7pUJDkTCEsJkx8snD', start:38,  era:'2010s',   genre:'pop'  },
  { artist:'Taylor Swift',            title:'Blank Space',                    spotifyId:'1CS7Sd1u5tWkstBhpssyjP', start:25,  era:'2010s',   genre:'pop'  },
  { artist:'Taylor Swift',            title:'Love Story',                     spotifyId:'1vrd6UOGamcKNGnSHJQlSt', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:'Levitating',                     spotifyId:'39LLxExYz6ewLAcYrzQQyP', start:45,  era:'2020s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:"Don't Start Now",                spotifyId:'3PfIrDoz19wz7qK7tYeu62', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:'New Rules',                      spotifyId:'2ekn2ttSfGqwhhate0LSR0', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:'IDGAF',                          spotifyId:'0RFoFRr45X0GCqyZcBvDkp', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Shawn Mendes',            title:'Stitches',                       spotifyId:'1R0a2iXumgCiFb7geUgIsX', start:8,   era:'2010s',   genre:'pop'  },
  { artist:'Shawn Mendes',            title:'Treat You Better',               spotifyId:'3SWqUBFjJBqOIVlQCxJeUS', start:12,  era:'2010s',   genre:'pop'  },
  { artist:'Shawn Mendes',            title:'There\'s Nothing Holdin\' Me Back', spotifyId:'2iGNBudsNuVpCEdRkWnKCy', start:10, era:'2010s', genre:'pop' },
  { artist:'Charlie Puth',            title:'See You Again',                  spotifyId:'2QbMejIfABdjmm7NHfMrPx', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Charlie Puth',            title:'Attention',                      spotifyId:'3AJwUDP919kvQ9QcozQPxg', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Sam Smith',               title:'Stay With Me',                   spotifyId:'5Nm9ERjJZ5oyfXZTECKmRt', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Sam Smith',               title:"Writing's on the Wall",          spotifyId:'0bRLhHdFj3HLdAHx5Dl7KD', start:50,  era:'2010s',   genre:'pop'  },
  { artist:'Sam Smith',               title:'Too Good at Goodbyes',           spotifyId:'5DqSPEbIkPWDcHUqfbHUL4', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Pharrell Williams',       title:'Happy',                          spotifyId:'60nZcImufyMA1MKQY3dcCH', start:16,  era:'2010s',   genre:'pop'  },
  { artist:'Maroon 5',                title:'Animals',                        spotifyId:'4KyR7fZkEkw6pAXYuFiJp6', start:18,  era:'2010s',   genre:'pop'  },
  { artist:'Maroon 5',                title:'Moves Like Jagger',              spotifyId:'5yG3ZAhTHXT6WViPRrCFsC', start:35,  era:'2010s',   genre:'pop'  },
  { artist:'Maroon 5',                title:'Girls Like You',                 spotifyId:'3e9S5bnMKX5kQMhBVt2Mif', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Maroon 5',                title:'Sugar',                          spotifyId:'4JehYebiI9242HG1szlAhX', start:34,  era:'2010s',   genre:'pop'  },
  { artist:'Justin Bieber',           title:'Sorry',                          spotifyId:'09CtPGIpYB4BrO8qb1RGsF', start:17,  era:'2010s',   genre:'pop'  },
  { artist:'Justin Bieber',           title:'Love Yourself',                  spotifyId:'3UmaczJpikHgJFyBTAJVoz', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'Justin Bieber',           title:'What Do You Mean?',              spotifyId:'2dp5lAjKMeIVGGs14TFnkj', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Ariana Grande',           title:'Thank U, Next',                  spotifyId:'3e9HZxeyfWwjeyPAMmWSSQ', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Ariana Grande',           title:'7 Rings',                        spotifyId:'6ocbgoVGwYJhOv1GgI9NsF', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Ariana Grande',           title:'Problem',                        spotifyId:'2bCASKhD7L1s2CIZM4RKuE', start:10,  era:'2010s',   genre:'pop'  },
  { artist:'P!nk',                    title:'Just Give Me a Reason',          spotifyId:'3pLdWdkj83EYfDN6H2N8MR', start:48,  era:'2010s',   genre:'pop'  },
  { artist:'P!nk',                    title:'Raise Your Glass',               spotifyId:'7JhWJBkckMWS5sL6h6bODT', start:12,  era:'2010s',   genre:'pop'  },
  { artist:'Alicia Keys',             title:'Girl on Fire',                   spotifyId:'4JehYebiI9242HG1szlAhY', start:30,  era:'2010s',   genre:'rnb'  },
  { artist:'Nicki Minaj',             title:'Super Bass',                     spotifyId:'4cFyZq5cApFmC0CfSFfGjl', start:38,  era:'2010s',   genre:'hiphop'},
  { artist:'Nicki Minaj',             title:'Starships',                      spotifyId:'0HYHTQPE9Bxbzow9X8SaFz', start:30,  era:'2010s',   genre:'hiphop'},
  { artist:'Cardi B',                 title:'Bodak Yellow',                   spotifyId:'5jZ2pBbwxmV3nuX3UFUMsA', start:12,  era:'2010s',   genre:'hiphop'},
  { artist:'Lizzo',                   title:'Truth Hurts',                    spotifyId:'6KgBpzTuTRPebChN0VTyzV', start:12,  era:'2010s',   genre:'pop'  },
  { artist:'Lizzo',                   title:'Good as Hell',                   spotifyId:'6KgBpzTuTRPebChN0VTyzX', start:28,  era:'2010s',   genre:'pop'  },
  { artist:'Halsey',                  title:'Without Me',                     spotifyId:'3qYZleGnePpPBrqJPnEXEw', start:12,  era:'2010s',   genre:'pop'  },
  { artist:'The Weeknd',              title:'Starboy',                        spotifyId:'7MXVkk9YMctZqd1Srtv4MB', start:12,  era:'2010s',   genre:'rnb'  },
  { artist:'The Weeknd',              title:'Earned It',                      spotifyId:'34gCuhDGsG4bRPIf9bb02a', start:28,  era:'2010s',   genre:'rnb'  },
  { artist:'The Weeknd',              title:'Can\'t Feel My Face',            spotifyId:'5rCHmenFkqj0DaupOVFtbN', start:10,  era:'2010s',   genre:'rnb'  },
  { artist:'Drake',                   title:"God's Plan",                     spotifyId:'6DCZcSspjsKoFjzjrWoCdn', start:10,  era:'2010s',   genre:'hiphop'},
  { artist:'Drake',                   title:'Hotline Bling',                  spotifyId:'0kwjjS0cMSFgp72GeqJU5q', start:25,  era:'2010s',   genre:'hiphop'},
  { artist:'Drake',                   title:'One Dance',                      spotifyId:'1xznGGDl6giTHxMF7Jus56', start:12,  era:'2010s',   genre:'hiphop'},
  { artist:'Kendrick Lamar',          title:'HUMBLE.',                        spotifyId:'7KXjTSCq5nL1LoYtL7XAwS', start:12,  era:'2010s',   genre:'hiphop'},
  { artist:'Post Malone',             title:'Circles',                        spotifyId:'21jGcNKet2qwijlDFuPiPb', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Post Malone',             title:'Sunflower',                      spotifyId:'3KkXRkHbMCARz0aVfEt68P', start:55,  era:'2010s',   genre:'pop'  },
  { artist:'Post Malone',             title:'Rockstar',                       spotifyId:'5UqCQaDshKOIoHFoQKoXPo', start:20,  era:'2010s',   genre:'hiphop'},
  { artist:'Post Malone',             title:'Better Now',                     spotifyId:'3CBDaO8KWxHjJwQM0DoeOM', start:18,  era:'2010s',   genre:'pop'  },
  { artist:'Macklemore & Ryan Lewis', title:'Thrift Shop',                    spotifyId:'0UBVuALHG6SROQ7bWrF9Gz', start:35,  era:'2010s',   genre:'hiphop'},
  { artist:'Macklemore & Ryan Lewis', title:"Can't Hold Us",                  spotifyId:'3bidbhpOYeVtu9oise3nAG', start:30,  era:'2010s',   genre:'hiphop'},
  { artist:'Lil Nas X',               title:'Old Town Road',                  spotifyId:'2YpeDb67231RjR0MgVLzsG', start:8,   era:'2010s',   genre:'hiphop'},
  { artist:'Meghan Trainor',          title:'All About That Bass',            spotifyId:'0mNaHoEBLgPhlCfO53lBE1', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'Jason Derulo',            title:'Talk Dirty',                     spotifyId:'3AJwUDP919kvQ9QcozQPxb', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Robin Thicke',            title:'Blurred Lines',                  spotifyId:'6mBYXepGPDGiX2ngNK1X5G', start:10,  era:'2010s',   genre:'pop'  },
  { artist:'Flo Rida',                title:'Good Feeling',                   spotifyId:'5V4EIeNUivBGQSr4GYjUbF', start:15,  era:'2010s',   genre:'pop'  },
  { artist:'LMFAO',                   title:'Party Rock Anthem',              spotifyId:'6Ij4JMFD5YEKN2ZiEMd4A6', start:35,  era:'2010s',   genre:'electronic'},
  { artist:'Major Lazer',             title:'Lean On',                        spotifyId:'6E6R0tJMw3pnlcMmqmhFwc', start:30,  era:'2010s',   genre:'electronic'},
  { artist:'The Chainsmokers',        title:'Closer',                         spotifyId:'7BKLCZ1jbUBVqRi2FVlTdp', start:30,  era:'2010s',   genre:'electronic'},
  { artist:'The Chainsmokers',        title:'Something Just Like This',       spotifyId:'1dNIEtp7AY3oDAKCGg2XkH', start:42,  era:'2010s',   genre:'electronic'},
  { artist:'Avicii',                  title:'Wake Me Up',                     spotifyId:'6YQmqP7VRNPK8jIFNhsVKi', start:38,  era:'2010s',   genre:'electronic'},
  { artist:'Avicii',                  title:'Levels',                         spotifyId:'4ioGNJEOdGBqHwmDiEfEeJ', start:25,  era:'2010s',   genre:'electronic'},
  { artist:'Avicii',                  title:'The Nights',                     spotifyId:'0ct6r3EGTcMLPtrXHDvVjc', start:18,  era:'2010s',   genre:'electronic'},
  { artist:'David Guetta',            title:'Titanium',                       spotifyId:'0TeZFqSMfSFBc4UXZmVSEM', start:55,  era:'2010s',   genre:'electronic'},
  { artist:'David Guetta',            title:'Without You',                    spotifyId:'39QRChYEuG9kWYfLjrJFqO', start:48,  era:'2010s',   genre:'electronic'},
  { artist:'Martin Garrix',           title:'Animals',                        spotifyId:'5J0F3bRLU5EqvEuiDDoEVi', start:35,  era:'2010s',   genre:'electronic'},
  { artist:'Martin Garrix',           title:'In the Name of Love',            spotifyId:'3pLdWdkj83EYfDN6H2N8Ms', start:30,  era:'2010s',   genre:'electronic'},
  { artist:'Alan Walker',             title:'Faded',                          spotifyId:'7lPN2DXiMsVn7XUKtOW1CS', start:14,  era:'2010s',   genre:'electronic'},
  { artist:'Alan Walker',             title:'Alone',                          spotifyId:'3qUAMkTVTLHPOPfUXANVXE', start:20,  era:'2010s',   genre:'electronic'},
  { artist:'Kygo',                    title:'Firestone',                      spotifyId:'7n2Ycct7Beij7Dj7meI4X0', start:25,  era:'2010s',   genre:'electronic'},
  { artist:'Kygo',                    title:'Stole the Show',                 spotifyId:'3OqBMPXMhj5sLaEWBUG7Av', start:30,  era:'2010s',   genre:'electronic'},
  { artist:'Marshmello',              title:'Happier',                        spotifyId:'4PUImXFwNYpMIliKGUuOYH', start:20,  era:'2010s',   genre:'electronic'},
  { artist:'Marshmello',              title:'Alone',                          spotifyId:'5tz69p7tJuGPeMGwNTxYuV', start:25,  era:'2010s',   genre:'electronic'},
  { artist:'Zedd',                    title:'The Middle',                     spotifyId:'5TXOAXX18ySA06Mv4hMXi7', start:35,  era:'2010s',   genre:'electronic'},
  { artist:'Zedd',                    title:'Beautiful Now',                  spotifyId:'1eHWnDLSmH0bKj9BAPB9em', start:40,  era:'2010s',   genre:'electronic'},
  { artist:'Clean Bandit',            title:'Rather Be',                      spotifyId:'6IZpRPKBMFRIyUbGJAhSEm', start:25,  era:'2010s',   genre:'electronic'},
  { artist:'Clean Bandit',            title:'Rockabye',                       spotifyId:'5kqIPrATaCc2RqpSMxJEGQ', start:32,  era:'2010s',   genre:'electronic'},
  { artist:'Clean Bandit',            title:'Symphony',                       spotifyId:'4eHbdreAnSOrDDsFfc4Fpm', start:15,  era:'2010s',   genre:'electronic'},
  { artist:'Disclosure',              title:'Latch',                          spotifyId:'2Lq2qT3sTGE3fCxOT5xpWK', start:40,  era:'2010s',   genre:'electronic'},
  { artist:'Galantis',                title:'Runaway (U & I)',                spotifyId:'3K8Lbj5s2d8EkMpvp2qzMg', start:20,  era:'2010s',   genre:'electronic'},
  { artist:'Stromae',                 title:'Alors On Danse',                 spotifyId:'3SWqUBFjJBqOIVlQCxJeUa', start:15,  era:'2010s',   genre:'electronic'},
  { artist:'Stromae',                 title:'Papaoutai',                      spotifyId:'2Fxmhks0bxGSBdJ92vM42n', start:30,  era:'2010s',   genre:'electronic'},
  { artist:'Coldplay',                title:'A Sky Full of Stars',            spotifyId:'2dpaYNEQHiRxtZbfNsse99', start:35,  era:'2010s',   genre:'electronic'},
  { artist:'Imagine Dragons',         title:'Radioactive',                    spotifyId:'69yfbpvmkQ9Lpe3X2UMcnu', start:45,  era:'2010s',   genre:'rock' },
  { artist:'Imagine Dragons',         title:'Believer',                       spotifyId:'0pqnGHJpmpxLKifKRmU6WP', start:10,  era:'2010s',   genre:'rock' },
  { artist:'Imagine Dragons',         title:'Thunder',                        spotifyId:'1zB4vmk8tFRmM9UULNzbLB', start:15,  era:'2010s',   genre:'rock' },
  { artist:'Imagine Dragons',         title:'Natural',                        spotifyId:'7GKJeABn3YP5BXJZL6dCnD', start:12,  era:'2010s',   genre:'rock' },
  { artist:'Muse',                    title:'Madness',                        spotifyId:'5SJatTL59FQcSVPINTKlPo', start:50,  era:'2010s',   genre:'rock' },
  { artist:'Arctic Monkeys',          title:'Do I Wanna Know?',               spotifyId:'5FVd6KXrgO9B3JPmC8OPst', start:10,  era:'2010s',   genre:'rock' },
  { artist:'Arctic Monkeys',          title:'R U Mine?',                      spotifyId:'5FhZSCFMBQN3TBp9F7BKIV', start:5,   era:'2010s',   genre:'rock' },
  { artist:'Twenty One Pilots',       title:'Stressed Out',                   spotifyId:'3CRDbSIZ4r5MsZ0YwxzbA7', start:10,  era:'2010s',   genre:'indie'},
  { artist:'Twenty One Pilots',       title:'Heathens',                       spotifyId:'6i0V12jOa3mr6uu4WBOAdA', start:35,  era:'2010s',   genre:'indie'},
  { artist:'Walk the Moon',           title:'Shut Up and Dance',              spotifyId:'4kbj5MwxO1bq9wjT5g9HaA', start:40,  era:'2010s',   genre:'pop'  },
  { artist:'OneRepublic',             title:'Counting Stars',                 spotifyId:'2tznHmp70mOZEFe1tkFMm3', start:42,  era:'2010s',   genre:'pop'  },
  { artist:'OneRepublic',             title:'I Lived',                        spotifyId:'5l8oJWKYAz5KxIWIkmRGUq', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Sia',                     title:'Chandelier',                     spotifyId:'4PEHM4bWNxsCHJrpQ9QgLz', start:40,  era:'2010s',   genre:'pop'  },
  { artist:'Sia',                     title:'Cheap Thrills',                  spotifyId:'19Sg3GelBhAnH14tAVODGX', start:18,  era:'2010s',   genre:'pop'  },
  { artist:'Sia',                     title:'Titanium',                       spotifyId:'0TeZFqSMfSFBc4UXZmVSEa', start:55,  era:'2010s',   genre:'pop'  },
  { artist:'Gotye',                   title:'Somebody That I Used to Know',   spotifyId:'1dnSgWPYWPMqIABMVDlCYz', start:55,  era:'2010s',   genre:'indie'},
  { artist:'Foster the People',       title:'Pumped Up Kicks',                spotifyId:'7w87IxuO7BDcJ3YUqCyMTT', start:22,  era:'2010s',   genre:'indie'},
  { artist:'Fun.',                    title:'We Are Young',                   spotifyId:'3QGsuHI8jO1Rx4JWLUh9jd', start:38,  era:'2010s',   genre:'indie'},
  { artist:'Passenger',               title:'Let Her Go',                     spotifyId:'3aaS4oCiSEFlcJQDFDlnzL', start:55,  era:'2010s',   genre:'indie'},
  { artist:'James Arthur',            title:"Say You Won't Let Go",           spotifyId:'5JCoSi02qi3jJeHXBsxeAV', start:35,  era:'2010s',   genre:'pop'  },
  { artist:'Lewis Capaldi',           title:'Someone You Loved',              spotifyId:'7BjP2fMEBhbGM6y3Ug3qQv', start:42,  era:'2010s',   genre:'pop'  },
  { artist:'Lewis Capaldi',           title:'Before You Go',                  spotifyId:'1Cv1YLb4q0RzL6pybtaMLo', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'John Legend',             title:'All of Me',                      spotifyId:'3U4isOIWM3VvDubwSI3y7a', start:45,  era:'2010s',   genre:'rnb'  },
  { artist:'Childish Gambino',        title:'Redbone',                        spotifyId:'4LpSFGGjGsMBZqeEWz0M7Y', start:55,  era:'2010s',   genre:'rnb'  },
  { artist:'Frank Ocean',             title:'Thinking Bout You',              spotifyId:'0kGKfkzJa16NdRMWGXJjTz', start:35,  era:'2010s',   genre:'rnb'  },
  { artist:'Daniel Caesar',           title:'Best Part',                      spotifyId:'5snHnFenCZyLXFKD7EqDIG', start:30,  era:'2010s',   genre:'rnb'  },
  { artist:'H.E.R.',                  title:'Hard Place',                     spotifyId:'7FsVQQlEEJaYwPSwrKZBIW', start:45,  era:'2010s',   genre:'rnb'  },
  { artist:'Khalid',                  title:'Young Dumb & Broke',             spotifyId:'3YUcRMghrMzFQUwyFT4Bk0', start:10,  era:'2010s',   genre:'rnb'  },
  { artist:'Khalid',                  title:'Talk',                           spotifyId:'4jvNKGBD3HpLB65KHmQCBn', start:10,  era:'2010s',   genre:'rnb'  },
  { artist:'6LACK',                   title:'PRBLMS',                         spotifyId:'5sLRBNgJE6MKGKjCeCyJnF', start:15,  era:'2010s',   genre:'rnb'  },
  { artist:'Juice WRLD',              title:'Lucid Dreams',                   spotifyId:'285pBltuF7vW8TeIKgRXCl', start:20,  era:'2010s',   genre:'hiphop'},
  { artist:'Lorde',                   title:'Royals',                         spotifyId:'4pklpe2NYqIRqk5gCZ0hpt', start:10,  era:'2010s',   genre:'indie'},
  { artist:'Lorde',                   title:'Tennis Court',                   spotifyId:'6C5iXTQPnOqnHzDnBFENzD', start:25,  era:'2010s',   genre:'indie'},
  { artist:'Lana Del Rey',            title:'Summertime Sadness',             spotifyId:'0F4rlqkfqMhvqyFCEG2HMH', start:50,  era:'2010s',   genre:'indie'},
  { artist:'Lana Del Rey',            title:'Video Games',                    spotifyId:'6pEQY3a7OVP8QpEpSEjcKE', start:35,  era:'2010s',   genre:'indie'},
  { artist:'Florence + Machine',      title:'Dog Days Are Over',              spotifyId:'6UGJBwd0oFKRwj3FCUQ4bL', start:45,  era:'2010s',   genre:'indie'},
  { artist:'Tame Impala',             title:'The Less I Know the Better',     spotifyId:'6K4t31amsSzgjBCUOa1dUY', start:30,  era:'2010s',   genre:'indie'},
  { artist:'Tame Impala',             title:'Let It Happen',                  spotifyId:'6TZ6bRSNbpRV2qOJirPkFT', start:5,   era:'2010s',   genre:'indie'},
  { artist:'Hozier',                  title:'Take Me to Church',              spotifyId:'1CS7Sd1u5tWkstBhpss0xk', start:50,  era:'2010s',   genre:'indie'},
  { artist:'Vance Joy',               title:'Riptide',                        spotifyId:'6uelj0w3EO8KhMOHXKtWKP', start:8,   era:'2010s',   genre:'indie'},
  { artist:'Bastille',                title:'Pompeii',                        spotifyId:'1YBDW8WKUMhGGMCC4gXSzc', start:25,  era:'2010s',   genre:'indie'},
  { artist:'Mumford & Sons',          title:'I Will Wait',                    spotifyId:'74sClFKLh8RYS0RZMJYZ7X', start:50,  era:'2010s',   genre:'indie'},
  { artist:'Mumford & Sons',          title:'The Cave',                       spotifyId:'6VQ9pYkFkgFJbLvjnWcMNd', start:38,  era:'2010s',   genre:'indie'},
  { artist:'Of Monsters and Men',     title:'Little Talks',                   spotifyId:'1YBDW8WKUMhGGMCC4gXSzd', start:45,  era:'2010s',   genre:'indie'},
  { artist:'The Lumineers',           title:'Ho Hey',                         spotifyId:'1BkPDiLE9kNQmSVyMtBpIb', start:5,   era:'2010s',   genre:'indie'},
  { artist:'George Ezra',             title:'Budapest',                       spotifyId:'0DqFiMEzqWkmQ3GI0dVjk1', start:8,   era:'2010s',   genre:'indie'},
  { artist:'George Ezra',             title:'Shotgun',                        spotifyId:'7FVYkOYX5UHkBt1T1J0d3K', start:20,  era:'2010s',   genre:'indie'},
  { artist:'Kodaline',                title:'All I Want',                     spotifyId:'7KXjTSCq5nL1LoYtL7XAwa', start:55,  era:'2010s',   genre:'indie'},
  { artist:'Ruth B.',                 title:'Lost Boy',                       spotifyId:'2SBuMxFVeQBgwqnzr8J9PI', start:5,   era:'2010s',   genre:'indie'},
  { artist:'Ellie Goulding',          title:'Lights',                         spotifyId:'3JUNajJe8KWXL0eHB4IShF', start:20,  era:'2010s',   genre:'pop'  },
  { artist:'Ellie Goulding',          title:'Love Me Like You Do',            spotifyId:'77pWCp1SqSqmHzSnmBNFYg', start:12,  era:'2010s',   genre:'pop'  },
  { artist:'Selena Gomez',            title:'Come & Get It',                  spotifyId:'3wjzPHl3vMpA0lEEHVsU4y', start:45,  era:'2010s',   genre:'pop'  },
  { artist:'Selena Gomez',            title:'Good for You',                   spotifyId:'2Bk2DuRkHQ3U5SY7rcwnE8', start:28,  era:'2010s',   genre:'pop'  },
  { artist:'Miley Cyrus',             title:'Wrecking Ball',                  spotifyId:'6Qyc6fS4DsZjB2mRW9DsQs', start:50,  era:'2010s',   genre:'pop'  },
  { artist:'Troye Sivan',             title:'Youth',                          spotifyId:'1PekFPvCvjHlqMJ5LcmqxS', start:25,  era:'2010s',   genre:'pop'  },
  { artist:'Zara Larsson',            title:'Lush Life',                      spotifyId:'3Zy1CVhBenIMBLZNDJlUpO', start:18,  era:'2010s',   genre:'pop'  },
  { artist:'Jessie J',                title:'Price Tag',                      spotifyId:'1JhYjVoXMtHnI13URZGJ2v', start:30,  era:'2010s',   genre:'pop'  },
  { artist:'Olly Murs',               title:'Troublemaker',                   spotifyId:'3AxRoD7M3yOvWBXBgAtfS0', start:25,  era:'2010s',   genre:'pop'  },
  { artist:'Portugal. The Man',       title:'Feel It Still',                  spotifyId:'3ee8Jmje8o58CHK7nVIct3', start:10,  era:'2010s',   genre:'indie'},
  { artist:'Billie Eilish',           title:'Therefore I Am',                 spotifyId:'5GbEFKXRHo6WvVQDZUoY1v', start:12,  era:'2020s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:'Physical',                       spotifyId:'4OddF6MQpzm6Km2kFxBJLd', start:20,  era:'2020s',   genre:'pop'  },

  // ── 2020s ──────────────────────────────────────────────────────
  { artist:'The Weeknd',              title:'Blinding Lights',                spotifyId:'0VjIjW4GlUZAMYd2vXMi3b', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'The Weeknd',              title:'Save Your Tears',                spotifyId:'6lanRgr6wXibZr8KgzXxBl', start:10,  era:'2020s',   genre:'rnb'  },
  { artist:'The Weeknd',              title:'Take My Breath',                 spotifyId:'6OGogr19zPTM4BjyHK4P5s', start:10,  era:'2020s',   genre:'rnb'  },
  { artist:'Taylor Swift',            title:'Anti-Hero',                      spotifyId:'0V3wPSX9ztLhV0P4doZtzh', start:10,  era:'2020s',   genre:'pop'  },
  { artist:'Taylor Swift',            title:'Cruel Summer',                   spotifyId:'1BxfuPKGuaTgP7aM0Dpspf', start:30,  era:'2020s',   genre:'pop'  },
  { artist:'Taylor Swift',            title:'Cardigan',                       spotifyId:'4R2kfaDFGih195S1mPQxLv', start:20,  era:'2020s',   genre:'indie'},
  { artist:'Taylor Swift',            title:'Shake It Off',                   spotifyId:'0cqRj7pUJDkTCEsJkx8snD', start:38,  era:'2010s',   genre:'pop'  },
  { artist:'Ed Sheeran',              title:'Bad Habits',                     spotifyId:'6PQ88X9ohnZsIVDNHiHdCp', start:18,  era:'2020s',   genre:'pop'  },
  { artist:'Ed Sheeran',              title:'Shivers',                        spotifyId:'1Qrg8KqiBpW07V69Alp9GI', start:10,  era:'2020s',   genre:'pop'  },
  { artist:'Adele',                   title:'Easy On Me',                     spotifyId:'6oKy7mhSZnvHSmHFP9BjVj', start:12,  era:'2020s',   genre:'pop'  },
  { artist:'Adele',                   title:'Oh My God',                      spotifyId:'4fHDCHIzAK48KU0g6LzDYu', start:15,  era:'2020s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:'Levitating',                     spotifyId:'39LLxExYz6ewLAcYrzQQyP', start:45,  era:'2020s',   genre:'pop'  },
  { artist:'Dua Lipa',                title:"Don't Start Now",                spotifyId:'3PfIrDoz19wz7qK7tYeu62', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'Olivia Rodrigo',          title:'drivers license',                spotifyId:'6Sp17ZnQRVInd2gDSt9Wem', start:55,  era:'2020s',   genre:'pop'  },
  { artist:'Olivia Rodrigo',          title:'good 4 u',                       spotifyId:'6PERH6vv58sNeFill3zlQn', start:10,  era:'2020s',   genre:'pop'  },
  { artist:'Olivia Rodrigo',          title:'brutal',                         spotifyId:'0EiI8ylL0FmWWpgHJje46L', start:5,   era:'2020s',   genre:'rock' },
  { artist:'Olivia Rodrigo',          title:'traitor',                        spotifyId:'5CZ40GBx1sQ9sh3UCUBiQa', start:30,  era:'2020s',   genre:'pop'  },
  { artist:'Harry Styles',            title:'Watermelon Sugar',               spotifyId:'6UelLqGlWMcVH1E5c4H7lY', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'Harry Styles',            title:'As It Was',                      spotifyId:'4Dvkj6JhhA12EX05fT7y2e', start:22,  era:'2020s',   genre:'pop'  },
  { artist:'Harry Styles',            title:'Golden',                         spotifyId:'3jjP4mBFiOEnGSZkG3U0oQ', start:10,  era:'2020s',   genre:'pop'  },
  { artist:'Billie Eilish',           title:'Happier Than Ever',              spotifyId:'2BHjBHPbXJx2VSwBqUTvVR', start:50,  era:'2020s',   genre:'pop'  },
  { artist:'Billie Eilish',           title:'lovely',                         spotifyId:'0u2P5u6lvoDfwTYjAADbn4', start:10,  era:'2010s',   genre:'indie'},
  { artist:'The Kid LAROI',           title:'Stay',                           spotifyId:'5HCyWlXZPP0y6Eo96Q2NGB', start:12,  era:'2020s',   genre:'pop'  },
  { artist:'Glass Animals',           title:'Heat Waves',                     spotifyId:'02MWAaffLxlfxAUY7c5dvx', start:40,  era:'2020s',   genre:'indie'},
  { artist:'Glass Animals',           title:'Gooey',                          spotifyId:'0Jck3hJMC8mpKPfM1bFGMf', start:20,  era:'2010s',   genre:'indie'},
  { artist:'Doja Cat',                title:'Say So',                         spotifyId:'5b88tNINg4Q4nrRR2riqnG', start:22,  era:'2020s',   genre:'rnb'  },
  { artist:'Doja Cat',                title:'Kiss Me More',                   spotifyId:'748mdHapucKQyPQFowb6eQ', start:15,  era:'2020s',   genre:'rnb'  },
  { artist:'Doja Cat',                title:'Woman',                          spotifyId:'0KKkJNfGyhkQ5aFogxQAPU', start:10,  era:'2020s',   genre:'rnb'  },
  { artist:'SZA',                     title:'Good Days',                      spotifyId:'4CT3rN63xMRBpT83AXTFDH', start:25,  era:'2020s',   genre:'rnb'  },
  { artist:'SZA',                     title:'Kill Bill',                      spotifyId:'1Qrg8KqiBpW07V69Alp9GJ', start:15,  era:'2020s',   genre:'rnb'  },
  { artist:'Silk Sonic',              title:'Leave the Door Open',            spotifyId:'7AzlLxHn24DxjgQX73F9fU', start:18,  era:'2020s',   genre:'rnb'  },
  { artist:'Giveon',                  title:'Heartbreak Anniversary',         spotifyId:'52x1oCBHSCRfbqIOfOlbsC', start:25,  era:'2020s',   genre:'rnb'  },
  { artist:'Lil Nas X',               title:'MONTERO',                        spotifyId:'2RoX9JLQW3aOolKYJBGTZk', start:12,  era:'2020s',   genre:'hiphop'},
  { artist:'Lil Nas X',               title:'Industry Baby',                  spotifyId:'27NovPIUIRrOZoCHxABJwK', start:10,  era:'2020s',   genre:'hiphop'},
  { artist:'BTS',                     title:'Dynamite',                       spotifyId:'5QDLhrAOJJdNAmCTJ8xMyW', start:14,  era:'2020s',   genre:'pop'  },
  { artist:'BTS',                     title:'Butter',                         spotifyId:'11dFghVXANMlKmJXsNCbNl', start:8,   era:'2020s',   genre:'pop'  },
  { artist:'Imagine Dragons',         title:'Enemy',                          spotifyId:'5QO79kh1waicV47BqGRL3g', start:10,  era:'2020s',   genre:'rock' },
  { artist:'Ariana Grande',           title:'positions',                      spotifyId:'1IHWl5LamUGEuP4uTol7C2', start:10,  era:'2020s',   genre:'pop'  },
  { artist:'Selena Gomez',            title:'Lose You to Love Me',            spotifyId:'2v3x8ViCLSQXuVHClmFJmf', start:12,  era:'2020s',   genre:'pop'  },
  { artist:'Miley Cyrus',             title:'Flowers',                        spotifyId:'4Dvkj6JhhA12EX05fT7y3e', start:15,  era:'2020s',   genre:'pop'  },
  { artist:'Miley Cyrus',             title:'Midnight Sky',                   spotifyId:'3lQ2GG2BfL7iqJpGoyklb0', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'Cardi B',                 title:'WAP',                            spotifyId:'6pN0OhqFPFZbzZTEsDGF5D', start:15,  era:'2020s',   genre:'hiphop'},
  { artist:'Sam Smith',               title:'Unholy',                         spotifyId:'3nqQXoyQOWXiESFLlDF1hG', start:20,  era:'2020s',   genre:'pop'  },
  { artist:'Conan Gray',              title:'Heather',                        spotifyId:'4xqrdfXkTW4T0RauPLv3WA', start:20,  era:'2020s',   genre:'indie'},
  { artist:'Surfaces',                title:'Sunday Best',                    spotifyId:'4eFbVY7RZbDW5U2aHYFR9C', start:10,  era:'2020s',   genre:'indie'},
  { artist:'Powfu',                   title:'death bed',                      spotifyId:'5W3cjX2J3tjhG8zb6u0qHb', start:10,  era:'2020s',   genre:'indie'},
  { artist:'Tame Impala',             title:'Borderline',                     spotifyId:'2NsWJISOehFHEiQHVPelJt', start:20,  era:'2020s',   genre:'indie'},
  { artist:'Machine Gun Kelly',       title:'Bloody Valentine',               spotifyId:'0JiFlCPMeXvFGQmfrmcFOh', start:15,  era:'2020s',   genre:'rock' },
];

// Shuffle once per session"""

content = content[:start_idx] + NEW_SONGS + content[end_idx:]

# ── 3. NEW ZeneGame ───────────────────────────────────────────────
OLD_ZENE_START = "function ZeneGame({ gameIdx, challenger, onAdvance, onResult }) {"
OLD_ZENE_END   = "function KivagyokGame"

z_start = content.index(OLD_ZENE_START)
z_end   = content.index(OLD_ZENE_END, z_start)
old_zene = content[z_start:z_end]

NEW_ZENE = r"""function ZeneGame({ gameIdx, challenger, onAdvance, onResult }) {
  const [selectedEra, setSelectedEra] = React.useState(() => {
    try { return localStorage.getItem('zene_era') || 'all'; } catch(e) { return 'all'; }
  });
  const [selectedGenre, setSelectedGenre] = React.useState(() => {
    try { return localStorage.getItem('zene_genre') || 'all'; } catch(e) { return 'all'; }
  });

  const filteredSongs = React.useMemo(() => {
    let songs = ZENE_SONGS;
    if (selectedEra !== 'all') songs = songs.filter(s => s.era === selectedEra);
    if (selectedGenre !== 'all') songs = songs.filter(s => s.genre === selectedGenre);
    if (songs.length === 0) songs = ZENE_SONGS;
    const a = [...songs];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }, [selectedEra, selectedGenre]);

  const song     = filteredSongs[gameIdx % filteredSongs.length];
  const nextSong = filteredSongs[(gameIdx + 1) % filteredSongs.length];

  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.fetchSpotifyPreview(song.spotifyId).then(url => {
      if (url) {
        setPreviewUrl(url);
        setLoading(false);
      } else {
        // No preview → auto-skip silently
        if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); }
      }
    });

    window.fetchSpotifyPreview(nextSong.spotifyId); // prefetch next

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song.spotifyId]);

  const handlePlay = () => {
    if (!audioRef.current || !previewUrl) return;
    audioRef.current.currentTime = song.start || 0;
    audioRef.current.play().catch(() => {});
  };
  const handleStop = () => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    setPlaying(false);
  };
  const handleResult = (correct) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    if (audioRef.current) audioRef.current.pause();
    if (correct) {
      onResult && onResult({ correct: true, playerName: challenger?.name || '', drinks: 0, subtitle: (challenger?.name || '') + ' felismerte — +1 pont!' });
      onAdvance && onAdvance({}, { [challenger?.id]: 1 });
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name || '', drinks: 1, subtitle: (challenger?.name || '') + ' nem ismerte fel — 1 korty!' });
      onAdvance && onAdvance({ [challenger?.id]: 1 }, {});
    }
  };

  const saveEra   = v => { setSelectedEra(v);   try { localStorage.setItem('zene_era',   v); } catch(e){} };
  const saveGenre = v => { setSelectedGenre(v); try { localStorage.setItem('zene_genre', v); } catch(e){} };

  const ERA_OPTIONS = [
    { v:'all',     label:'Minden' },
    { v:'classic', label:'Klassz.' },
    { v:'2000s',   label:'2000-es' },
    { v:'2010s',   label:'2010-es' },
    { v:'2020s',   label:'2020-as' },
  ];
  const GENRE_OPTIONS = [
    { v:'all',        label:'Minden' },
    { v:'pop',        label:'Pop' },
    { v:'rnb',        label:'R&B' },
    { v:'hiphop',     label:'Hip-hop' },
    { v:'rock',       label:'Rock' },
    { v:'electronic', label:'Electronic' },
    { v:'indie',      label:'Indie' },
  ];

  const chip = (active) => ({
    padding:'5px 11px', borderRadius:999, border:'none', cursor:'pointer',
    fontFamily:T.font, fontWeight:700, fontSize:11,
    background: active ? T.mint : T.surfaceMuted,
    color: active ? '#fff' : T.inkSoft,
    whiteSpace:'nowrap', flexShrink:0, transition:'background .15s',
  });

  return (
    <div style={{ width:'100%', display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>
      {/* Filter chips */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:5 }}>
        <div style={{ overflowX:'auto', display:'flex', gap:5, paddingBottom:1, WebkitOverflowScrolling:'touch' }}>
          {ERA_OPTIONS.map(o => <button key={o.v} onClick={() => saveEra(o.v)} style={chip(selectedEra===o.v)}>{o.label}</button>)}
        </div>
        <div style={{ overflowX:'auto', display:'flex', gap:5, paddingBottom:1, WebkitOverflowScrolling:'touch' }}>
          {GENRE_OPTIONS.map(o => <button key={o.v} onClick={() => saveGenre(o.v)} style={chip(selectedGenre===o.v)}>{o.label}</button>)}
        </div>
      </div>

      {previewUrl && (
        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />
      )}

      {/* Vinyl */}
      <div style={{ position:'relative', width:200, height:200, flexShrink:0 }}>
        <div style={{ position:'absolute', left:7, top:7, width:186, height:186, transformOrigin:'center', animation: playing ? 'vinylSpin 2.6s linear infinite' : 'none' }}>
          <svg width="186" height="186" viewBox="0 0 250 250">
            <circle cx="125" cy="125" r="123" fill="#181818"/>
            {[112,100,88,76,65,56,47].map(r2 => (
              <circle key={r2} cx="125" cy="125" r={r2} fill="none" stroke="#282828" strokeWidth="1.8"/>
            ))}
            <circle cx="125" cy="125" r="46" fill="#B97060"/>
            <text x="125" y="133" textAnchor="middle" fontSize="26" fill="#1a1a1a">♫</text>
            <circle cx="125" cy="125" r="7" fill="#080808"/>
          </svg>
        </div>
        <svg width="200" height="200" viewBox="0 0 270 270" style={{ position:'absolute', left:0, top:0, pointerEvents:'none' }}>
          <line x1="248" y1="22" x2="158" y2="150" stroke="#E0D8C8" strokeWidth="7" strokeLinecap="round"/>
          <circle cx="248" cy="22" r="12" fill="#1B2340" stroke="#E0D8C8" strokeWidth="2.5"/>
          <rect x="151" y="146" width="16" height="10" rx="2" fill="#333" transform="rotate(-52 159 151)"/>
        </svg>
      </div>

      {/* Buttons */}
      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8 }}>
        {loading ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>⏳ Betöltés...</span>
          </div>
        ) : !playing ? (
          <button onClick={handlePlay}
            style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
            <span style={{ fontSize:13 }}>▶</span><span>Lejátszás</span>
          </button>
        ) : (
          <button onClick={handleStop}
            style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#F0C040', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>
            <span style={{ fontSize:13 }}>⏸</span><span>Megállítás</span>
          </button>
        )}
        {!loading && (!revealed
          ? <button onClick={() => setRevealed(true)}
              style={{ width:'100%', padding:'13px 0', background:'#fff', border:'none', borderRadius:16, color:'#1B2340', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', boxShadow:'0 2px 10px rgba(0,0,0,0.14)', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
              <span>🔍</span><span>Felfedés</span>
            </button>
          : (
            <div style={{ display:'flex', gap:8 }}>
              <button onClick={() => handleResult(true)}
                style={{ flex:1, padding:'13px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
                ✓ Felismerte
              </button>
              <button onClick={() => handleResult(false)}
                style={{ flex:1, padding:'13px 0', background:T.coral, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>
                ✗ Nem ismerte
              </button>
            </div>
          )
        )}
      </div>

      {revealed && (
        <div style={{ background:'rgba(255,255,255,0.85)', borderRadius:18, padding:'16px 22px', textAlign:'center', boxShadow:'0 4px 20px rgba(0,0,0,0.10)', width:'100%', boxSizing:'border-box' }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#1B2340', letterSpacing:'-0.01em', lineHeight:1.15 }}>{song.artist}</div>
          <div style={{ fontFamily:T.font, fontWeight:600, fontSize:17, color:'#555', marginTop:5 }}>„{song.title}"</div>
        </div>
      )}
    </div>
  );
}

"""

content = content[:z_start] + NEW_ZENE + content[z_end:]

assert "v9.104" in content
assert "filteredSongs" in content
assert "ERA_OPTIONS" in content

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.104 ready")
