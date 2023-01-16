# LinkyDinky

LinkyDinky is a selenium based bot designed to automate LinkedIn actions, especially for sourcing or recruiting talent.

It also helps you send connect messages in HEBREW, or your native language (requires a bit more work from you)

The project already contains translations to hebrew for more than 1700 names, but it helps you add more as you work.
## This repo is for educational purposes only, and you bear full responsibility if you use it for real.

## I am not responsible if you use this against LinkedIn terms of service.
### You can be temporarily or completely banned from LinkedIn for using automated services, especially in high volume. 

Links:
[Usage](#usage),
[Sending Connections](#connecting-with-users--friend-requests--),
[Resending Messages to my connections](#sending-messages-again-to-existing-connections-),
[Withdrawing Invites](#withdrawing-invites),
[Translation](#translating-names),
[Advanced Configuration](#advanced-configuration)


## Installation

1) Clone the repo
```bash
git clone https://github.com/elam91/LinkyDinky.git
```

2) Install dependencies:

This project uses [python poetry](https://python-poetry.org/docs/) to manage package dependencies

```bash
poetry install
poetry shell
```

## Usage

All commands should be run inside poetry shell.

### First edit the [config.json](config/config.json) file:
Please make sure you have all the fields in your file even if you're not actually using them all.
```json
{
    "user": "johndoe",
    "loops": 3,
    "skip_days": [
        "friday",
        "saturday"
    ],
    "exact_match": false,
    "webhook_url": "https://discord.com/api/webhooks/YOURWEBHOOKHERE",
    "delayed_start": false,
    "resend_amount": 30,
    "connect_amount": 50,
    "withdraw_amount": 200,
    "chromedriver_path": "/usr/bin/chromedriver",
    "minimum_experience": 2,
    "old_connects_loops": 2,
    "name_collect_amount": 100,
    "sleep_between_loops": 25,
    "mandatory_first_word": false,
    "send_connect_message": false,
    "maximum_daily_connects": 52,
    "minimum_daily_connects": 36,
    "old_connect_month_delta_answered": 6,
    "old_connect_month_delta_unanswered": 6,
    "location" : "Israel"
}
```
### Make sure you have a cookie file, you can use [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=en) to extract your cookie from LinkedIn.
> :warning: **DO NOT SHARE YOUR COOKIE WITH ANYONE, DO NOT UPLOAD IT TO GIT! IT CAN BE USED TO ACCESS YOUR ACCOUNT**. keep it locally only! :warning:
### Name the cookie file {user}cookie.json, and place it in the cookies folder, for example: 

#### **`johndoecookie.json`**
```javascript
// Paste the cookie for user johndoe in this file in the cookies/ directory
```

### Put some keywords in the [keywordskeep.json](config/keywordskeep.json)  file:

**`config/keywordskeep.json`**
```json
["senior developer", "software engineer"]
```


### Then, run the program you want:

```bash
python request_minimum.py
```

### You can override most config options with bash arguments:

```bash
python request_loops.py --user janedoe
```

### You can also choose a custom keyword instead of the one in the json file:

```bash
python request_loops.py --user janedoe --keyword java expert
```
 The program skips to the last page it visited for this keyword and user every time you run it, but you can add a start_page to force it to skip to the page you want:

```bash
python request_minimum.py --user janedoe --start_page 99
```
It's a good practice to make sure that page exists for your keyword, or the bot will get stuck.

[Back to top](#linkydinky)


### Let's breakdown different programs and their configuration:

## Connecting with users (friend requests):
This searches for LinkedIn users you are not connected to according to the keyword,
excluding whats written in the blacklists, and collects users, after it has collected enough users, it visits their
profile one by one, checks the experience and makes sure there are no blacklisted companies/roles. 
Then it connects, if send_connect_message is set, it sends one with their translated name.

* Put at least 1 keyword in [keywordskeep.json](config/keywordskeep.json)
* make sure your config.json is set up correctly, or use bash arguments
* choose which program to run:
  * **`request_loops.py`** will run the number of loops specified and stop.
  * **`request_minimum.py`** will run until either the minimum requirement has been met and a loop has ended, or the maximum requirement has been met.
  *  **`scheduler.py`** can be used for simple scheduling (but using cron is better)
  
```bash
  python  scheduler.py --scheduled_time 13:00
```
* If you are using `send_connect_message` you also need to put a message in messages.json.
**When sending connect messages, people that have names that have not yet been translated will not be connected with, and their names will be saved for later**
### configuration:

**`config/config.json`**

| Property  | Description                                                                                                                     | Example Value                                        |
|-----------|---------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| `user`    | The user to connect to. Must have a cookie.json file (e.g. `johndoecookie.json`).                                               | `"johndoe"`                                          |
| `loops`   | The number of loops to run.                                                                                                     | `3`                                                  |
| `skip_days` | List of days to skip automation, mainly for scheduling. You can also use python numbers for days (e.g. 0 for Monday).           | `["friday", "saturday"]`                             |
| `exact_match` | If `true`, only connect if ALL words in the keyword appear in title or current position.                                        | `false`                                              |
| `webhook_url` | If not blank, will send discord notifications at the start and end of automation                                                | `"https://discord.com/api/webhooks/YOURWEBHOOKHERE"` |
| `delayed_start`| If `true`, will add first word of keyword to mandatory list                                                                     | `false`                                              |
| `connect_amount`  | How many people to collect in each loop before trying to connect.                                                               | `50`                                                                                                                                                                                                              |
| `chromedriver_path` | The path to chromedriver. If left blank, will look for chromedriver in PATH.                   | `"/usr/bin/chromedriver"`                                                                                                                                                                                        |
| `minimum_experience` | The minimum experience in **years**. Will look for the last word to match the keyword, and also count engineer/developer roles. | `2`                                                                                                                                                                                                              |
| `sleep_between_loops`     | Time to sleep between loops in minutes.                                                                                         | `25`                                                                                                                                                                                                              |
| `mandatory_first_word`    | If `true`, will add the first word of the keyword to the mandatory list.                                                        | `false`                                                                                                                                                                                                           |
| `send_connect_message`    | If `true`, will send a connect message when connecting. Will use the message in `messages.json` and the name from `translated_names.json`.                                                               | `false`                                                                                                                                                                                                           |
| `maximum_daily_connects`  | The program will stop when this number of connects is reached. Only counts people who were successfully connected with.         | `52`                                                                                                                                                                                                              |
| `minimum_daily_connects`  | If running `request_minimum.py`, will continue again and again until this number has been reached.                               | `36`                                                                                                                                                                                                              |
| `location`                | The location to use in search. If not provided, will default to Israel.                                                        | `"Israel"`                                                                                                                                                                                                       |

[Back to top](#linkydinky)

## Sending messages again to existing connections:
Will search your connections for the keyword, open the chat with the user, and checks to make sure a phone number hasnt already been shared, 
and enough time has passed since the last message according to the number of months specified in the config.json.
it then opens all the users in different tabs, so you can review and see if there's a reason to send them another message.

**This does not check for experience as it would be too slow.**

also skips if a phone number was sent.

* make sure your config.json is set up correctly, or use bash arguments
* run the program:
```bash
python old_connects.py --keyword software engineer
```

if you don't provide a keyword, one will be taken from the **`keywordskeep.json`**

* saves the profile links to a json inside **`config/saved_old_connects/`**
  * you can open tabs of any json file in that folder using the **`open_tabs_from_json.py file`**

### configuration:

**`config/config.json`**

| Property                             | Description                                                                                     | Example Value |
|--------------------------------------|-------------------------------------------------------------------------------------------------|---------------|
| `old_connects_loops`                 | The number of loops to run.                                                                     | `3`           |
| `old_connect_month_delta_answered`   | How many months should pass from last message, if the user has replied to you before            | `12`          |
| `old_connect_month_delta_unanswered` | How many months should pass from last message, if the user has  **never** replied to you before | `6`           |
| `resend_amount`                      | How many users to collect in each loop, **HIGHLY DISCOURAGE MORE THAN 30, MORE USUALLY FAILS**  | `30`          |
| `dont_open_tabs`                      | Only saves the links in a json and does not open the tabs                                       | `true`         |

[Back to top](#linkydinky)

## Withdrawing invites
Will search your pending invitations and withdraw anyone over a month old.


* make sure your config.json is set up correctly, or use bash arguments
* run the program:
```bash
python withdraw_requests.py
```

### configuration:

**`config/config.json`**

| Property                             | Description                                                                                     | Example Value |
|--------------------------------------|-------------------------------------------------------------------------------------------------|---------------|
| `withdraw_amount`                    | How many invites to withdraw, if not provided, defaults to 10.                                  | `100`         |

[Back to top](#linkydinky)

## Translating names
While using the other programs, they will collect first names that have not already been translated,
and save them, but you can also run a search to collect more names:

```bash
python search_first_names.py
```

After you have names in [untranslated_names.json](config/untranslated_names.json), you can run the translation program and it will show you every name, and you can type in the correct translation and it will save it, to blacklist a name input the hebrew letter `ע` (Ayin)
and to skip a name input the hebrew letter `ד` (Dalet).

* run the program:
```bash
python translate.py

11
leonardo
```
type in the name and press enter:
```bash
python translate.py

11
leonardo לאונרדו

10
donnatello
```


### configuration:

**`config/config.json`**

| Property              | Description                                                                | Example Value |
|-----------------------|----------------------------------------------------------------------------|---------------|
| `name_collect_amount` | How many first names to collect | `100`         |

[Back to top](#linkydinky)

## Advanced configuration

### **`config/blacklist.json`**

Blacklist of keywords to skip in collection phase:

```javascript
['ceo', 'manager'] // must be single word, case insensitive.
```


### **`config/nameblacklist.json`**

Blacklist of names first/last to skip in collection phase, don't know why you would use this
maybe someone named Count Rugen killed your father, so you don't want to hire him:

```javascript
['rugen', 'vizzini', 'jeff'] // must be single word, case insensitive.
```


### **`config/currentworkblacklist.json`**

Used in the **connect** phase, when checking experience, skips if the current employer is defined here
or if the current title is defined here, only the most recent job is checked.

```javascript
{
  "position": [
    "head",
    "count"
  ],
  "employer": [
    "nso",
    "humperdinck"
  ]
}
```

### **`config/mandatory.json`**

Only collects the user if one of the words on this list is present in the title. 
There is no need to add the word `senior` because it is automatically added if your keyword contains senior.

```javascript
['pirate', 'dread'] // must be single word, case insensitive.
```

### More keywords:
`--download_config` `--download_keywords`
you can store your jsons for keywords on configs in a remote place, and add these flags to download the
updated config/keyword list when starting, this way, say you're running on a raspberry pi, you can change settings from your
browser without connecting to the machine directly.

```bash
python request_minimum.py --download_config https://api.npoint.io/1234567abcd
```

[Back to top](#linkydinky)


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

