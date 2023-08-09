import scrapy


class AllrecipeScraperSpider(scrapy.Spider):
    name = "category_scraper"
    allowed_domains = ["www.allrecipes.com"]
    #start_urls = ["http://www.allrecipes.com/recipes"]
    start_urls = ["file:///home/taz/Desktop/recipeDataScraping/allrecipe/recipes.html"]

    def parse(self, response):
        
        # all recipes under the category
        recipes = response.css("a.comp.mntl-card-list-items.mntl-document-card.mntl-card.card.card--no-image::attr(href)").getall()

        for recipe in recipes:
            #yield scrapy.Request(url=recipe, callable= self.parse_recipe)
            print(recipe)
    

    def parse_recipe(self, response):
        pass
