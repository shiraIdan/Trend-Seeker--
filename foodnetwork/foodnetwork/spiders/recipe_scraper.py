from pathlib import Path
import scrapy
import requests
from foodnetwork.items import FoodnetworkItem
from scrapy_playwright.page import PageMethod
from urllib.parse import urlencode


def add_https(list_of_link):
    for i in range(len(list_of_link)):
        list_of_link[i] = "https:" + list_of_link[i]


def category_pages(url, number_of_pages):
    urls = []
    for i in range(number_of_pages):
        new_url = url + "/p/" + str(i)
        urls.append(new_url)
    return urls


class RecipeScraperSpider(scrapy.Spider):
    name = "recipe_scraper"
    allowed_domains = ["www.foodnetwork.com"]
    start_urls = ["https://www.foodnetwork.com/recipes/recipes-a-z"]

    def start_requests(self):
        start_url = "https://www.foodnetwork.com/recipes/recipes-a-z"
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):

        # Recipe A-Z section
        # GEtting the alphabets
        alphts = response.css(
            'a.o-IndexPagination__a-Button::attr(href)').getall()

        # getting the number of pages the current category has
        # it is the previous element of "Next" button
        number_of_pages = int(response.css(
            "a.o-Pagination__a-Button::text").getall()[-2])

        add_https(alphts)

        print(alphts)

        # p = 0
        for category in alphts:
            # if p == 1:
            #     break
            pages = category_pages(category, number_of_pages)
            print(f"current category: {category}")
            print(f"The current category has pages: {len(pages)}")

            for page in pages:
                yield scrapy.Request(url=page, callback=self.parse_category)

    def parse_category(self, response):

        self.logger.info(f"Current Category:{response.url}")
        # Recipes under the selected category on the first page
        recipe_links = response.css(
            'li.m-PromoList__a-ListItem a::attr(href)').getall()

        # There could be more pages
        # next pages follows like this -> current_url/p/{count}
        # count starts with 2 after the first page

        add_https(recipe_links)

        self.logger.info(f"Recipes under the category:{len(recipe_links)}")
        self.logger.info(f"First recipe of the page: {recipe_links[0]}")

        # yielding the recipies
        r = 0
        for recipe in recipe_links:
            if r == 10:
                break
            yield scrapy.Request(url=recipe, callback=self.parse_recipe, meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    PageMethod('wait_for_selector', 'h2.reviews-ct')
                ],
                errback=self.errback
            ))
            r += 1
            # yield scrapy.Request(url= recipe, callback=self.parse_recipe)

    async def parse_recipe(self, response):

        page = response.meta["playwright_page"]
        await page.close()

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

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
