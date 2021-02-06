# LinkSniper
Spider or repeater to find all links in website.


## 

## Use 
```bash
python3 LinkSniper.py https://www.google.com
```
```text
https://www.google.com/advanced_search?hl=en&authuser=0
https://www.google.com/intl/en/ads/
https://www.google.com/services/
https://www.google.com/intl/en/about.html
https://www.google.com/intl/en/policies/privacy/
https://www.google.com/intl/en/policies/terms/
https://www.google.com/intl/en/about/products?tab=ih
```
--------
## How it works
It takes all links from target, if the link belongs to a target like subdomain, then it will work on it. If there was another field, it wouldn't add it to the output, and this process continues until the links map is complete
