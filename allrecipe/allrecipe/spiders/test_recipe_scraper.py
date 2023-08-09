import scrapy


class AllrecipeScraperSpider(scrapy.Spider):
    name = "recipe_scraper"
    allowed_domains = ["www.allrecipes.com"]
    #start_urls = ["http://www.allrecipes.com/recipes"]
    start_urls = ["file:///home/taz/Desktop/recipeDataScraping/allrecipe/recipe2.html"]

    def parse(self, response):
        
        # all recipes under the category
        title = response.css("h1#article-heading_1-0::text").get()
        author = response.css("a.mntl-attribution__item-name::text").get()
        rating_score = response.css("div#mntl-recipe-review-bar__rating_1-0::text").get()
        ratings = response.css("div#mntl-recipe-review-bar__rating-count_1-0::text").get()
        description = response.css("p#article-subheading_1-0::text").get()
        ingredients_li = response.css("li.mntl-structured-ingredients__list-item").getall()
        ingredients = ""
        for l in range(1,len(ingredients_li)+1):
            sp = response.css("li.mntl-structured-ingredients__list-item p span::text").getall()
            sp = response.css(f"li.mntl-structured-ingredients__list-item:nth-child({l}) > p:nth-child(1) > span::text").getall()
            print(sp)
            for word in sp:
                ingredients += word + " "
            ingredients += "\n"
        directions = response.css("p.comp.mntl-sc-block.mntl-sc-block-html::text").getall()

        yield {
                'title': title,
                'author': author,
                'description': description,
                'rating_score': rating_score,
                'ratings': ratings,
                'ingredients': ingredients,
                'directions': directions
            }
# li.mntl-structured-ingredients__list-item:nth-child(l) > p:nth-child(l) > span::text
    


