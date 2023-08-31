This work is a parser for the site www.skiddle.com. Parser collects information about festivals (name, date, place).
The data received:
1) data/festivals.csv - table with all information on festivals
2) data/citi_url_list.json, data/fest_url/*.json - list with addresses of cities (so as not to send requests to the site).
3) data/error_citi.json ,error_fest.json - lists with cities and festivals, in the processing of which no information was received (possible mistakes for parsing). Compiled for re -check.
