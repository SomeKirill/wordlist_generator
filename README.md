# wordlist_generator

Tool wordlist_generator generates unique to your target wordlist with techniques mentioned in tomnomnom's video ["Who, What, Where, When"](https://www.youtube.com/watch?v=W4_QCSIujQ4).
It takes URLs from [gau](https://github.com/lc/gau) to extract directories, file names or words on pages. As additional feature it can extract HTML comments. By default tool will only request 2000 URLs, extract all words and directories.

To clean wordlist, wordlist_generator removes from result everything from "denylists" directory files to keep only unique words. Also it cleans result using regexes from BonJarber's [clean_wordlist](https://github.com/BonJarber/SecUtils/tree/master/clean_wordlist) tool. You can adjust which extenctions will be ignored during parsing files and fetching pages in `parsing_allow_extensions.txt` and `scraping_deny_extensions.txt`.

## Usage:
Examples:
```
$ ./wordlist_generator.py -d hackerone.com -a 20 -files
$ ./wordlist_generator.py -d bugcrowd.com -a 7500 -dir
$ ./wordlist_generator.py -d intigriti.com > intigriti_wordlist.txt
```
To display the help for the tool use the -h flag:

```
./wordlist_generator.py -h
```

| Flag | Description | Example |
|------|-------------|---------|
| `-domain` | target domain | `./wordlist_generator.py -d openbugbounty.org` |
| `-amount` | amount of URLs to fetch from gau | `./wordlist_generator.py -d twitter.com -a 10000` |
| `-dir` | Extract only directories | `./wordlist_generator.py -d hackerone.com -dir` |
| `-f` | Extract only filenames | `./wordlist_generator.py -d hackerone.com -f` |
| `-c` | Extract only comments with no filtering | `./wordlist_generator.py -d hackerone.com -c` |


## Installation:
```
$ GO111MODULE=on go get -u -v github.com/lc/gau
$ git clone https://github.com/SomeKirill/wordlist_generator/
$ pip3 install -r requirements.txt
```
## denylists wordlists used:
- https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/raft-large-directories-lowercase.txt
- https://github.com/oprogramador/most-common-words-by-language/blob/master/src/resources/dutch.txt
- https://github.com/first20hours/google-10000-english/blob/master/google-10000-english.txt
- https://tools.ietf.org/html/rfc1866
