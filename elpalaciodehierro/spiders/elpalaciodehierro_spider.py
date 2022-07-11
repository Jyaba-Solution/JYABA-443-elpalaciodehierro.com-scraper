import scrapy
import datetime


# scrapy.spiders.SitemapSpider
class ElpalaciodeSpider(scrapy.spiders.SitemapSpider):
    name = 'elpalaciode'
    sitemap_urls = [f'https://www.elpalaciodehierro.com/sitemap_{x}-product.xml' for x in range(0,20)]
    sitemap_rules = [(r'.html', 'parse')]
    #start_urls = ['https://www.elpalaciodehierro.com/under-armour-tenis-para-correr-shadow-hombre-41726918.html']

    def parse(self, response):

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
            item['Final Price']= min(low_price, high_price) if low_price else float(high_price)
            yield item
        except Exception as e:
            print("Error: ",e)
            with open('errors.txt', 'a') as f:
                f.write(response.url+"\n")
