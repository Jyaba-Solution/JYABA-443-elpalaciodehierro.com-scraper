import scrapy
import datetime
import re

# b-categories_navigation-link_1

# scrapy.spiders.SitemapSpider
class ElpalaciodeSpider(scrapy.Spider):
    name = 'elpalaciode'
    #sitemap_urls = [f'https://www.elpalaciodehierro.com/sitemap_{x}-product.xml' for x in range(0,20)]
    #sitemap_rules = [(r'.html', 'parse')]
    start_urls = ['https://www.elpalaciodehierro.com','https://www.elpalaciodehierro.com/on/demandware.static/-/Library-Sites-palacio-content-global/default/JSON/brands.json']
    def parse(self, response):

        if '.json' in response.url:
            brands = response.text
            urls_list = re.findall('"href": "(.*)"',brands)
            a_links = re.findall('"url": "(.*)"',brands)
            urls_list.extend(a_links)
            for brand in urls_list:
                yield scrapy.Request(brand, callback=self.parse_category)
        categories_list = response.xpath("//a[contains(@class, 'b-categories_navigation-link_2')]/@href").extract()
        for category in categories_list:
            if 'lista-marcas' in category:
                pass
            else:
                yield scrapy.Request(category, callback=self.parse_category)
    
    def parse_category(self, response):
        products = response.xpath("//a[contains(@class, 'b-product_tile-image')]/@href").extract()
        for product in products:
            url = response.urljoin(product)
            yield scrapy.Request(url, callback=self.parse_product)
        next_page = response.xpath("//i[@class='i-arrow-right-thin-after']").extract_first()
        if not products:
            with open('errors.txt', 'a') as f:
                f.write(response.url+"\n")
        if next_page:
            next_page_url = response.xpath("//li[@class='b-pagination-elements_list b-next-btn']/a/@href").extract_first()
            yield scrapy.Request(next_page_url, callback=self.parse_category)

        

    def parse_product(self, response):

        try:
            item = dict()
            item['Date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            item['Canal'] = 'Palacio de Hierro'
            categories = [x.strip() for x in response.xpath("//li[@class='b-breadcrumbs-item']/a/text()").extract()]
            categories_dict = {x:y for x,y in enumerate(categories)}
            item_characteristics = [x.strip().replace('\n','') for x in response.xpath("//div[@class='l-pdp-description']//text()").extract() if x.strip()]
            image = response.css('meta[itemprop=image]::attr(content)').extract_first()
            low_price = response.css('meta[itemprop=lowPrice]::attr(content)').get() 
            high_price = response.css('meta[itemprop=highPrice]::attr(content)').get()
            if low_price == high_price:
                low_price = ''
            item['Category'] = categories_dict.get(0, '')
            item['Subcategory'] = categories_dict.get(1, '')
            item['Subcategory2'] = categories_dict.get(2, '')
            item['Subcategory3'] = categories_dict.get(3, '')
            item['Marca'] = response.css('meta[itemprop=brand]::attr(content)').get()
            model_text=response.css('div.b-product_description-keys > span.b-product_description-key:last-child::text').get()
            model=""
            if model_text:
                model = model_text.replace('Model:','').strip()
            item['Modelo']=model
            item['SKU']=response.css('meta[itemprop=sku]::attr(content)').get()
            item['UPC']=response.css('meta[itemprop=gtin14]::attr(content)').get()
            item['Item']=response.css('h2[class=b-product_main_info-brand] a::text').get().strip()+","+response.css('h1.b-product_main_info-name::text').get().strip()
            item['Item Characteristics']=item_characteristics
            item['URL SKU']=response.url
            item['Image']=image
            item['Price'] = high_price
            item['Sale Price']= low_price
            item['Shipment Cost']=''
            item['Sale Flag']=response.css('.b-product_product-discount::text').get()
            item['Store ID']=''
            item['Store Name']=''
            item['Store Address']=''
            item['Stock']= response.css('meta[itemprop=availability]::attr(content)').get()
            item['UPC WM']=response.css('meta[itemprop=gtin14]::attr(content)').get().zfill(16) if response.css('meta[itemprop=gtin14]::attr(content)').get() else ''
            item['Final Price']= min(float(low_price), float(high_price)) if low_price else high_price
            yield item
        except Exception as e:
            print("Error: ",e)
            with open('errors_again.txt', 'a') as f:
                f.write(response.url+"\n")
                breakpoint()
