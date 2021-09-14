# coinmarketcap-fetch
Python script to fetch prices from coinmarketcap.com and print out on console or generate a compact html table

You need to get an API key first from https://pro.coinmarketcap.com/account

Example printout on console (selected coins):

                         usd        btc         eth             24h     7d
          bitcoin   BTC  46594.1381 1.00000000  13.806098871     4.93   -1.92
         ethereum   ETH  3374.89529 0.07243176  1.0000000000     5.29   -4.77
          cardano   ADA  2.40289668 0.00005157  0.0007119915    -0.96   -3.64
              xrp   XRP  1.07590520 0.00002309  0.0003187966     2.26   -5.62

Example html table (all coins):
![Example html table](https://github.com/tlundqvist/coinmarketcap-fetch/blob/main/example-html-table.png "Example html table")

Columns are hopefully obvious except these:
* MarkCap - market cap in USD divided by 1 million
* %%btc - market cap relative BTC multiplied by 1000 (permille)
