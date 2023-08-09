import scrapy
from scrapy_playwright.page import PageMethod
from foodnetwork.foodnetwork.items import FoodnetworkItem


class FoodNetworkSpider(scrapy.Spider):
    name = 'recipe_scraper'
    allowed_domains = ['www.foodnetwork.com']
    start_urls = ['https://www.foodnetwork.com/recipes/recipes-a-z']

    async def start_requests(self):
        for url in self.start_urls:
            page = await PageMethod.from_url(url)
            await page.wait_for_selector('.o-IndexPagination__a-Z li a')

            # Get the list of alphabetical category links
            category_links = await page.querySelectorAll('.o-IndexPagination__a-Z li a')

            # Yield a request for each alphabetical category
            for link in category_links:
                category_url = await link.get_attribute('href')
                yield scrapy.Request(category_url, callback=self.parse_category)

    async def parse_category(self, response):
        # Yield a request for each recipe on the page
        count = 0
        for recipe_link in response.css('.m-MediaBlock__a-Headline a::attr(href)'):
            if count == 10:
                break
            recipe_url = response.urljoin(recipe_link.get())
            count += 1
            yield scrapy.Request(recipe_url, callback=self.parse_recipe)

        # Follow the "Next" button if it exists
        next_button = response.css(
            '.o-Pagination__a-Button--next::attr(href)').get()
        if next_button:
            next_url = response.urljoin(next_button)
            yield scrapy.Request(next_url, callback=self.parse_category)

    async def parse_recipe(self, response):
        recipe = FoodnetworkItem()
        # parsing the content
        recipe["link"] = response.url
        author = response.css('span.o-Attribution__a-Name a::text').getall()
        if len(author) == 0:
            author = response.css('span.o-Attribution__a-Name::text').getall()
        recipe["author"] = response.css(
            'span.o-Attribution__a-Name a::text').getall()
        recipe["title"] = response.css(
            'span.o-AssetTitle__a-HeadlineText::text').get()
        recipe["description"] = response.css(
            'div.o-AssetDescription__a-Description::text').get()
        recipe["ingredients"] = response.css(
            "span.o-Ingredients__a-Ingredient--CheckboxLabel::text").getall()
        recipe["special_equipment"] = response.css(
            'section.o-SpecialEquipment::text').extract()
        recipe["directions"] = response.css(
            'li.o-Method__m-Step::text').getall()
        recipe["rating"] = response.css(
            "div.rating-stars::attr(title)").get().split()[0]
        recipe["reviews"] = response.css(
            "h2.reviews-ct::text").get().split()[0]

        yield recipe
