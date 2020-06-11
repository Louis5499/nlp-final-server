# Social Media (Dcard) Keyword crawler
This project aims to fetch keyword from social media(currently working on Dcard) in order to find out the public's reation toward an issue.

## Technology Specification
- TF-IDF Analysis

## Prerequisite
1. Python 3.6^
2. Python flask environment
3. [CkipTagger](https://github.com/ckiplab/ckiptagger)

## How to ?
1. Go to [CkipTagger Github web](https://github.com/ckiplab/ckiptagger), download `iis-ckip` dataset, and put the `./data` directory in the root of the project.
2. Run `python3 api.py`, and localhost:5000 will be listening
3. call `GET http://localhost:5000/search/<WHAT YOU WANT TO SEARCH>`, you may get the result.

## Notice
CkipTagger is project from ckip lab, so please be aware of license restriction, which are elaborated in their github repo README.md.

## Contributor
Pei-Ying Li 
Min-Chi Chiang