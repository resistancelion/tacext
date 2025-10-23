
# telegram api credentials extractor

Automated Python tool for extraction of CLIEND_ID and CLIENT_HASH for Telegram's MTProto protocol





## Features

- JSON formatted output with optional settings of minified version, self-defined syntax and formatting
- Automatical required tools Installation
- Results unification
- Recognition of official CLIENT_IDS
- Option to output RAW JSON data instead of log into stdout
- Easy-to-edit dynamical converter/analyzer structure
- Same JSON can be used as output and input to join them together
- Almost OS-independent code
- Single-file or folder as input
- Only full support for Ukrainian language
- LICENSE-FREE

Now supports: apk
## Installation

Clone project to a desired location and navigate to main folder

```bash
  git clone http://github.com/resistancelion/telegram_api_credentials_extractor
  cd telegram_api_credentials_extractor
```

install pre-requisites:

```bash
  pip install -r requirements.txt
```

Run
```bash
  python tacext.py
```
## Usage/Examples

```bash
python tacext.py "my_apks_dir" "decompiled_apks" "result.json" -s
```

