#!/usr/bin/env python3
#
# Thomas Lundqvist, 2017-2021
#
# 1. set APIKEY (and maybe MAP_CACHE file path)
# 2. get mapfile using the -map option
# 3. fill in SELECTED_COINS (look in map-cache.txt)
# 4. run with no options to print out selected coins on console
#
# Example output (usd price, price in btc, price in eth, percent change 24h/7d):
#
#                         usd        btc         eth             24h     7d
#          bitcoin   BTC  46594.1381 1.00000000  13.806098871     4.93   -1.92
#         ethereum   ETH  3374.89529 0.07243176  1.0000000000     5.29   -4.77
#          cardano   ADA  2.40289668 0.00005157  0.0007119915    -0.96   -3.64
#              xrp   XRP  1.07590520 0.00002309  0.0003187966     2.26   -5.62

import requests
import json
import argparse
import datetime

# An api key from coinmarketcap.com is needed. Sign up for free:
# https://pro.coinmarketcap.com/account

APIKEY='12345678-1234-abcd-12ab-123123abcabc'
LIMIT = 5000   # Get max this many coins for html table

MAP_CACHE = 'map-cache.txt'

BASE_URL = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/'
GETALL_URL = f'{BASE_URL}listings/latest?limit={LIMIT}&CMC_PRO_API_KEY={APIKEY}'
GETSELECTED_URL = f'{BASE_URL}quotes/latest?CMC_PRO_API_KEY={APIKEY}&id='
GETMAP_URL = f'{BASE_URL}map?CMC_PRO_API_KEY={APIKEY}'

# Normally, get only these selected coins

SELECTED_COINS = [
    'BTC','ETH','XRP','ADA']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='all', action='store_const',
                        const=True, default=False,
                        help='print all coins (default False)')
    parser.add_argument('-html', dest='html', action='store_const',
                        const=True, default=False,
                        help='generate html on stdout of all coins, all fields (default False)')
#    parser.add_argument('-csv', dest='csv', action='store_const',
#                        const=True, default=False,
#                        help='generate csv on stdout of all coins (default False)')
    parser.add_argument('-map', dest='map', action='store_const',
                        const=True, default=False,
                        help='fetch and update new coin map (default False)')
    parser.add_argument('searchstring', metavar='searchstring', nargs='?',
                        help='search string to filter output')
    args = parser.parse_args()

    if args.map:
        fetch_map()
        return
    
    if args.html or args.all:
        r = requests.get(GETALL_URL)
    else:
        selected_coins = translate_to_id()
        r = requests.get(GETSELECTED_URL + ','.join(selected_coins))

    if not 'data' in r.json():
        print(json.dumps(r.json(), indent=2, sort_keys=True))
        raise Exception('API error')

    coins = r.json()['data']
    if type(coins) == dict:
        coins = list(coins.values())   # Selected coins has extra id dict on top
        coins.sort(key = lambda coin: coin['cmc_rank'])

    # Now, coins should be a ranked list of coins
    price_btc = 0
    price_eth = 0
    for c in coins:
        if c['symbol'] == 'BTC':
            price_btc = c['quote']['USD']['price']
        if c['symbol'] == 'ETH':
            price_eth = c['quote']['USD']['price']
        if price_btc > 0 and price_eth > 0:
            break

    if args.html:
        generate_html(coins, price_btc, price_eth)
#    elif args.csv:
#        generate_csv(coins)
    else:
        print_coins(coins, price_btc, price_eth, args.searchstring, args.all)
    
#####################################################
# Fetch new map and store as local file
# Example file: (id;name;symbol;slug)
#  1;Bitcoin;BTC;bitcoin
#  2;Litecoin;LTC;litecoin
#  3;Namecoin;NMC;namecoin
#  4;Terracoin;TRC;terracoin

def fetch_map():
    r = requests.get(GETMAP_URL)

    if not 'data' in r.json():
        print(json.dumps(r.json(), indent=2, sort_keys=True))
        raise Exception('API error')

    coins = r.json()['data']
    # print(coins)
    with open(MAP_CACHE, 'w') as f:
        for coin in coins:
            f.write(f"{coin['id']};{coin['name']};{coin['symbol']};{coin['slug']}\n")
    print("Wrote new or updated file: " + MAP_CACHE)
    
#####################################################
# Translate coin names to id:s using MAP CACHE

def translate_to_id():
    slug_to_id = {}
    symbol_to_id = {}
    try:
        with open(MAP_CACHE) as f:
            for line in f:
                cid, name, symbol, slug = line.strip().split(';')
                slug_to_id[slug] = cid
                symbol_to_id[symbol] = cid
    except:
        pass
    translated = [ slug_to_id.get(coin) or symbol_to_id.get(coin) for coin in SELECTED_COINS]
    #print(translated)
    if None in translated:
        print(translated)
        raise Exception("Could not translate all coins to id.")
    return translated
        

#####################################################
# Print one line, single coin on console

def p(coin, price_btc, price_eth):
    usd = coin['quote']['USD']
    price = usd['price']
    print("%17s %5s  %-10s %-11s %-13s %7s %7s"%(coin['slug'][0:17],coin['symbol'],
                                            ('%.8f'%(price))[0:10],
                                            '%.8f'%(price/price_btc),
                                            ('%.10f'%(price/price_eth))[:12],
                                            round(usd['percent_change_24h'],2),
                                            round(usd['percent_change_7d'],2)))

#####################################################
# Print all coins in 'coins' on console

def print_coins(coins, price_btc, price_eth, searchstring, all):
    print("                         usd        btc         eth             24h     7d")
    for coin in coins:
#        print(json.dumps(coin, indent=2, sort_keys=True))
        if searchstring == None:
            p(coin, price_btc, price_eth)
        else:
            if searchstring in coin['slug'] or searchstring in coin['symbol']:
                p(coin, price_btc, price_eth)

#####################################################
# Generate html table of all coins

def generate_html(coins, price_btc, price_eth):
    fields = ['rank','name','symbol','market_cap_usd','relative_btc','price_usd','price_btc','price_eth',
              '24h_volume_usd','percent_change_1h','percent_change_24h','percent_change_7d']
    header = ['#','Name','Symbol','MarkCap[1e6]','%%btc','Price','Price BTC','Price ETH',
              'Volume (24h)','% 1h','% 24h','% 7d']

    updated = coins[0]['last_updated']
#    updated = datetime.datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S')
    print("<html><head><link href=\"cmc-get.css\" rel=\"stylesheet\" type=\"text/css\">")
    print("</head><body><p class=\"right\">Updated (BTC): %s<table><thead><tr>"%updated)
    markcap_btc = coins[0]['quote']['USD']['market_cap']
    for i,h in enumerate(header):
        print("<th class=\"%s\">%s</th>"%(fields[i],h))
    print("</tr></thead><tbody>")
    for coin in coins:
        print("<tr>")
        pp = {
            'rank': coin['cmc_rank'],
            'name': coin['slug'][0:18],
            'name_full': coin['slug'],
            'symbol': coin['symbol']
        }
        usd = coin['quote']['USD']
        p = str(usd['market_cap'])
        pp['market_cap_usd'] = p
        pp['relative_btc'] = ""
        if p != 'None':
            pp['market_cap_usd'] = "%.3f"%(float(p)/1e6)
            pp['relative_btc'] = "%.2f"%(float(p)/markcap_btc*1000)
        p = str(usd['price'])
        pp['price_usd'] = p
        pp['price_btc'] = ''
        pp['price_eth'] = ''
        if p != 'None':
            if float(p) >= 2.0:
                pp['price_usd'] = "%.2f"%float(p)
            pp['price_btc'] = "%.8f"%(float(p)/price_btc)
            pp['price_eth'] = "%.10f"%(float(p)/price_eth)
        p = str(usd['volume_24h'])
        pp['24h_volume_usd'] = p
        if p != 'None':
            pp['24h_volume_usd'] = "%.0f"%float(p)
        for f in ['percent_change_1h','percent_change_24h','percent_change_7d']:
            p = str(usd[f])
            pp[f] = " "
            if p != 'None':
                pp[f] = "%.2f%%"%float(p)

        for f in fields:
            cls = f
            if f.startswith("percent"):
                cls += " neg" if pp[f][0] == "-" else " pos"
            s = str(pp[f])
            if f == "name":
                s = "<a href=\"https://coinmarketcap.com/currencies/%s/\">%s</a>"%(pp['name_full'],s)
            
            print("<td class=\"%s\">%s</td>"%(cls,s))
                
        print("</tr>")
    print("</tbody></table></body></html>")

# not updated for new API
def generate_csv(r):
    for coin in r.json():
        print('"%s","%s","%s"'%(coin['id'],coin['symbol'],coin['market_cap_usd']))

main()


# OLD API Example:
# {
#   "24h_volume_eth": "6041.14515608", 
#   "24h_volume_usd": "2000740.0", 
#   "available_supply": null, 
#   "id": "bt2-cst", 
#   "last_updated": "1510951472", 
#   "market_cap_eth": null, 
#   "market_cap_usd": null, 
#   "max_supply": null, 
#   "name": "BT2 [CST]", 
#   "percent_change_1h": "-2.82", 
#   "percent_change_24h": "-26.96", 
#   "percent_change_7d": "-34.49", 
#   "price_btc": "0.0180359", 
#   "price_eth": "0.4205588036", 
#   "price_usd": "139.283", 
#   "rank": "1008", 
#   "symbol": "BT2", 
#   "total_supply": null
# }

# new api, dec 2018
# {
#   "circulating_supply": 17533773.4398247, 
#   "cmc_rank": 9, 
#   "date_added": "2018-11-09T00:00:00.000Z", 
#   "id": 3602, 
#   "last_updated": "2018-12-28T08:12:37.000Z", 
#   "max_supply": 21000000, 
#   "name": "Bitcoin SV", 
#   "num_market_pairs": 99, 
#   "platform": null, 
#   "quote": {
#     "USD": {
#       "last_updated": "2018-12-28T08:12:37.000Z", 
#       "market_cap": 1489649377.3938172, 
#       "percent_change_1h": 1.83238, 
#       "percent_change_24h": -8.61978, 
#       "percent_change_7d": -30.6792, 
#       "price": 84.9588585427, 
#       "volume_24h": 87217498.5802754
#     }
#   }, 
#   "slug": "bitcoin-sv", 
#   "symbol": "BSV", 
#   "tags": [
#     "mineable"
#   ], 
#   "total_supply": 17533773.4398247
# }, 
