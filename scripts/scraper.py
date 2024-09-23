from lxml import html
from dataclasses import dataclass

# Data struct in order to processing scraped products
@dataclass(frozen=True)
class AmazonProduct():

    url: str
    title: str 
    vendor: str
    rating: str
    current_price: float
    availability: bool


class ProductParser:

    __slots__ = ("logger",)

    def __init__(self, logger):
        self.logger = logger

    # Main method of the class assigned to scrape html content using XPath with LXML parser

    async def parse_product_data(self, HTTPResponse: classmethod) -> AmazonProduct:

        try:

                html_tree = html.fromstring(HTTPResponse.request_content.content)
                title = html_tree.xpath("normalize-space(//span[@id='productTitle']/text())") 
                price_decimal = html_tree.xpath("//div[@id='apex_desktop']//div[@id='corePriceDisplay_desktop_feature_div']//span[@class='a-price-whole']/text()")
                price_floating = html_tree.xpath("//div[@id='apex_desktop']//div[@id='corePriceDisplay_desktop_feature_div']//span[@class='a-price-fraction']/text()")

                if price_decimal and price_floating:
                    
                    price = float(f"{price_decimal[0].replace('.','')}.{price_floating[0]}")
                    availability = True

                else:

                    price = 0.0
                    availability = False

                vendor = html_tree.xpath("normalize-space(//div[@id='merchantInfoFeature_feature_div']/div[@class='offer-display-feature-text']/div[@class='offer-display-feature-text a-spacing-none ']/span[@class='a-size-small offer-display-feature-text-message']//text())")

                if not vendor:
                     
                     vendor = "N/A"

                rating = html_tree.xpath("normalize-space(//div[@id='averageCustomerReviews_feature_div']//span[@id='acrPopover']/span[@class='a-declarative']/a[@class='a-popover-trigger a-declarative']/span[@class='a-size-base a-color-base']/text())")

                if not rating:

                    rating = 0

                else:

                    rating = float(rating.replace(",", "."))

                # At the end of parsing, it creates an Amazonproduct dataclass with all the information obtained

                product_data = AmazonProduct(

                    url = HTTPResponse.url,
                    title = title,
                    vendor = vendor,
                    rating = rating,
                    current_price = price,
                    availability = availability

                )

                return product_data

        except Exception as e:  # errors handling
                self.logger.error(f"Generic Scraping Data Error: {e}")