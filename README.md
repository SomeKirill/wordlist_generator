# wordlist_generator

wordlist_generator generates wordlists with unique words with techniques mentioned in tomnomnom's report ["Who, What, Where, When"](https://www.youtube.com/watch?v=W4_QCSIujQ4).
It takes URLs from [gau](https://github.com/lc/gau) and splits them to get words in URLs. Then it requests each URL to fetch all words. Finally, wordlist_generator removes from wordlist everything from "denylists" directory files to keep only unique words, which you can use for domain, directory, parameter, vhosts, etc bruteforcing.

## Usage:
Examples:
```
$ ./wordlist_generator.py -d hackerone.com -a 5000 -t 50
$ ./wordlist_generator.py -d bugcrowd.com -a 1000 
$ ./wordlist_generator.py -d intigriti.com > intigriti_wordlist.txt
```
To display the help for the tool use the -h flag:

```
./wordlist_generator.py -h
```

| Flag | Description | Example |
|------|-------------|---------|
| `-domain` | target domain | `./wordlist_generator.py -d openbugbounty.org` |
| `-threads` | threads amount | `./wordlist_generator.py -d yahoo.com -t 6` |
| `-amount` | amount of URLs to fetch from gau | `/wordlist_generator.py -d twitter.com -a 10000` |


## Installation:
```
$ git clone https://github.com/SomeKirill/wordlist_generator/
$ cd wordlist_generator
$ pip install requests
```
## denylists wordlists used:
- https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/raft-large-directories-lowercase.txt
- https://github.com/oprogramador/most-common-words-by-language/blob/master/src/resources/dutch.txt
- https://github.com/first20hours/google-10000-english/blob/master/google-10000-english.txt
- https://tools.ietf.org/html/rfc1866
