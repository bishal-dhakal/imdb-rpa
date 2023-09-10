from robocorp.tasks import task
import pandas as pd
import time
import traceback
import sqlite3
from RPA.Browser.Selenium import Selenium

movies = []

browser = Selenium()


def mainWork():
    try:
        df = pd.read_excel("../movies.xlsx")
        movie = df["Movie"]

        for m in movie:
            movies.append(m)

        conn = sqlite3.connect('imdb.db')
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        movie_name TEXT,
        ratings TEXT,
        storyline TEXT,
        tagline TEXT,
        genres TEXT,
        review_1 TEXT,
        review_2 TEXT,
        review_3 TEXT,
        review_4 TEXT,
        review_5 TEXT,
        status TEXT
        )""")

        browser.open_available_browser("imdb.com/", maximized=True)

        # loop through the list of movies
        for movie in movies:
            print(f'Searching on movie {movie}')
            #open imdb website
            browser.auto_close = False
        
            #search
            browser.wait_until_element_is_visible("//input[@id='suggestion-search']")
            browser.input_text("//input[@id='suggestion-search']", movie)
            browser.click_button_when_visible("//button[@id='suggestion-search-button']")

            # movie_results = browser.find_elements('//li[@class="ipc-metadata-list-summary-item ipc-metadata-list-summary-item--click find-result-item find-title-result"]')

            # if len(movie_results) == 0:
            #     continue 
            
            try:
                movie_filter='//a[@class="more-results-ft-chip ipc-chip ipc-chip--on-base"]'
                browser.click_element_when_visible(movie_filter)

            except Exception as e:
                print(e)
                pass
        
            
            latest_movie_title = ""
            latest_movie_year = 0

        
            results = browser.find_elements(f"//section[@data-testid='find-results-section-title']//a[text()='{movie}']")
            print('result length = ', len(results))

            for index, result in enumerate(results):
                year_element = browser.find_elements(f"//section[@data-testid='find-results-section-title']//a[text()='{movie}']/following-sibling::ul[1]//span")


                title = browser.get_text(result)
                print(title)
                if title == movie:
                # Extract the movie year from the result
                    try:
                        # year_element = browser.find_element(f"//section[@data-testid='find-results-section-title']//a[text()='{movie}']/following-sibling::ul[1]//span")
                        year = int(browser.get_text(year_element[index]))
                        # if title == 'Titanic':
                        #     print(year)
                    except:
                        continue

                    # latest_movie_year = max(year, latest_movie_year)
                    # Check if this movie is the latest
                    if year > latest_movie_year:
                        latest_movie_year = year
                        latest_movie_title = title
                        latest_movieyear_element=result
                        year_element_latest = year_element[index]
                
            print(latest_movie_year)
                    

            if (latest_movie_year):
                # Click on the movie to open its page
                # if title == 'Titanic':
                #     for _ in range(5):
                #         browser.press_keys(None, 'PAGEDOWN')
                #         print('loop le kam garirachha')

                link = browser.get_element_attribute(latest_movieyear_element,'href')
                browser.go_to(link)

                # Get the ratings, storyline, tagline, genres, and top 5 user reviews
                try:
                    ratings = browser.get_text("//div[@class='sc-e226b0e3-3 jJsEuz']//a[@aria-label='View User Ratings']//span[@class='sc-bde20123-1 iZlgcd']")
                except:
                    ratings = 'No Rating Found'
                
                try:
                    storyline = browser.get_text('//p[@class="sc-466bb6c-3 llCpwq"]')
                except:
                    storyline = "No storyline Found"
                
                browser.press_keys(None,'END')
                time.sleep(3)
                browser.press_keys(None,'HOME')
                time.sleep(3)

                tagline = '//li[@class="ipc-inline-list__item test-class-react"]'
                
                try:
                    tagline = browser.get_text(tagline)
                except:
                    tagline = 'No Tag Found'

                try:
                    genres = browser.get_text('//div[@class="ipc-chip-list__scroller"]')

                except:
                    genres = "No Genres Found"
                # review
                for i in range(4):
                    browser.press_keys(None, 'ARROW_DOWN')
                
                try:
                    reviewclick_elements = browser.find_element('//a[@class="ipc-link ipc-link--baseAlt ipc-link--touch-target sc-9e83797f-2 jJzPWH isReview"]')
                    review_linl = browser.get_element_attribute(reviewclick_elements,'href')

                    browser.go_to(review_linl)

                    reviews=[]
                    review_elements= browser.find_elements('//a[@class="title"]')
                    for i in range(min(len(review_elements),5)):
                        reviews.append(browser.get_text(review_elements[i]))
                except:
                    reviews= []
                    pass

                if(len(reviews) < 5 ):
                    for i in range(5-len(reviews)):
                        reviews.append("Not Found")

            status = "Success" if (latest_movie_year and title == movie) else "No exact match found"

            if(status == "Success") :
                cur.execute("""INSERT INTO movies (movie_name, ratings, storyline, tagline, genres, review_1, review_2, review_3, review_4, review_5, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (movie, ratings, storyline, tagline,genres, reviews[0], reviews[1], reviews[2], reviews[3], reviews[4], status))
            
            else:
                cur.execute("""INSERT INTO movies (movie_name, ratings, storyline, tagline, genres, review_1, review_2, review_3, review_4, review_5, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (movie, '', '', '', '', '','', '', '', '', "Not Found"))

            conn.commit()

            print(f'{ movie } added to database')

        
        browser.close_browser()
        browser.close_all_browsers()
    except Exception as e:
        print(e)
        print(traceback.format_exc())

@task
def minimal_task():
    mainWork()

