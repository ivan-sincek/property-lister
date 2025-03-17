# Property Lister

Extract and convert property list files from SQLite database files and from other property list files.

Tested on Kali Linux v2024.2 (64-bit).

Made for educational purposes. I hope it will help!

## Table of Contents

* [How to Install](#how-to-install)
	* [Install plistutil](#install-plistutil)
	* [Standard Install](#standard-install)
	* [Build and Install From the Source](#build-and-install-from-the-source)
* [Extracting and Converting](#extracting-and-converting)
* [Usage](#usage)

## How to Install

### Install plistutil

On Kali Linux, run:

```bash
apt-get -y install plistutil
```

---

Windows OS is not supported.

---

On macOS, run:

```bash
brew install libplist
```

### Standard Install

```bash
pip3 install --upgrade property-lister
```

## Build and Install From the Source

```bash
git clone https://github.com/ivan-sincek/property-lister && cd property-lister

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/property_lister-3.2-py3-none-any.whl
```

## Extracting and Converting

Extract and convert property list files inside Cache.db unencrypted SQLite database file:

```fundamental
scp root@192.168.1.10:/var/mobile/Containers/Data/Application/YYY...YYY/Library/Caches/com.someapp.dev/Cache.db ./

property-lister -db Cache.db -o results_db
```

Extract and convert property list files inside an IPA:

```fundamental
unzip someapp.ipa

property-lister -db Payload -o results_db

property-lister -pl Payload -o results_pl
```

Repeat the same for the app specific directories.

Check my other project on how to [search for files](https://github.com/ivan-sincek/ios-penetration-testing-cheat-sheet#3-search-for-files-and-directories) and on how to [extract sensitive data from the files](https://github.com/ivan-sincek/ios-penetration-testing-cheat-sheet#4-inspect-files).

## Usage

```fundamental
Property Lister v3.2 ( github.com/ivan-sincek/property-lister )

--- Extract from an SQLite database file ---
Usage:   property-lister -db database -o out
Example: property-lister -db Cache.db -o results_db

--- Extract from a property list file ---
Usage:   property-lister -pl property-list -o out
Example: property-lister -pl Info.plist    -o results_pl

DESCRIPTION
    Extract and convert property list files
DATABASE
    SQLite database file, or directory containing multiple files
    -db, --database = Cache.db | databases | etc.
PROPERTY LIST
    Property list file, or directory containing multiple files
    -pl, --property-list = Info.plist | plists | etc.
OUT
    Output directory
    All extracted propery list files will be saved in this directory
    -o, --out = results | etc.
DIRECTORY STRUCTURE
    Preserve the directory structure within the output directory
    -ds, --directory-structure
```

## Images

<p align="center"><img src="https://github.com/ivan-sincek/property-lister/blob/main/img/extraction.png" alt="Extraction"></p>

<p align="center">Figure 1 - Extraction</p>
