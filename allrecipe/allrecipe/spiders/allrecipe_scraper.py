import scrapy


class AllrecipeScraperSpider(scrapy.Spider):
    name = "allrecipe_scraper"
    allowed_domains = ["www.allrecipes.com"]
    start_urls = ["http://www.allrecipes.com/recipes"]
    #start_urls = ["file:///home/taz/Desktop/recipeDataScraping/allrecipe/categories.html"]

    def parse(self, response):
        
        # Categories
        categories = response.css("a.taxonomy-nodes__link.mntl-text-link.type--squirrel-link::attr(href)").getall()

        # which category to scrape
        print("\n\nChoose which category to scrape. Choose the index (0,1,2...)")
        for (i,c) in enumerate(categories):
            print(f"{i} --- {c.split('/')[-2]}")
        index = int(input("\ncategory index:"))

        print(categories[index] + "\n\n")
        # Continue the scraping with the selected category
        yield scrapy.Request(url= categories[index], callback=self.parse_category)


    def parse_category(self, response):
        
        # all recipes under the category
        recipes = response.css("a.comp.mntl-card-list-items.mntl-document-card.mntl-card.card.card--no-image::attr(href)").getall()

        count = 0
        for recipe in recipes:
            if count == 5:
                break
            yield scrapy.Request(url=recipe, callback= self.parse_recipe)
            count += 1
    

    def parse_recipe(self, response):
        # all recipes under the category
        title = response.css("h1#article-heading_1-0::text").get()
        author = response.css("a.mntl-attribution__item-name::text").get()
        link = response.url
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
                'link': link,
                'description': description,
                'rating_score': rating_score,
                'ratings': ratings,
                'ingredients': ingredients,
                'directions': directions
            }
