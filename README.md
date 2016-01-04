## script.pulsar.ncore

NCore.cc provider for pulsar

## Requirements

1. plugin.video.pulsar

2. script.common.plugin.cache

## Installation & Configuration

Step1: Install pulsar

Step2: Install Common Plugin Cache

Step3: Install nCore Provider

Step4: At the plugin configuration insert your ncore username / password.

## Known issues & Solutions

#### Provider timeout.

Solution: Enable the Custom Provider Timeout settings in Pulsar ( System > Add-ons > My Add-ons > Video Add-ons > Pulsar > Configure > Custom Provider Timeout > Enable | Timeout in seconds: 120 )

#### Stalled at finding ( 0% )

There is no solution yet. Some torrents works well, some not. I'm looking for a solution to make all torrents working.

#### TV Show search

It's a mess... nCore's search isn't smart enough, it should work for some searches but I recommend using the global search instead if you want to watch TV Shows. Be aware of packed TV shows, a lot of tv shows are packed in one torrent which will obviously not work (e.g: tv show name S01 )

#### PULSAR IS SEEDING WHILE YOU WATCH! USE THIS PLUGIN AT YOUR OWN RISK!

nCore requires at least 48h of seeding back or you will get a warn. At the moment this plugin is only for exercising my python skills :) I'm planning to implement a seeding service which will seed back your downloads after the movie was completely or partialy downloaded.

### Coming soon

* configurable filters (you can select the movie categories at the plugin configuration)

* a workaround for issue#2.

* a workaround / complete solution for issue #4.
