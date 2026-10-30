product_discovery_bot finds every product from a source and adds it to `product_queue`. Each source has its own
adapter in the root `adapters/` folder, which can use a sitemap, the source's API or crawl the listing pages. On start
it adds every `adapters/*/source.json` to `data_sources`.
