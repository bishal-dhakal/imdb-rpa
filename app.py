results = browser.get_webelements(f"//section[@data-testid='find-results-section-title']//a[text()='{movie_name}']")


latest_movie_title = ""
latest_movie_year = 0

try:
    for index, result in enumerate(results):
        title = browser.get_text(result)
        print(title)
        if title == movie_name:
        # Extract the movie year from the result
            year_element = browser.find_element(f"//section[@data-testid='find-results-section-title']//li[{index + 1}]//a[text()='{movie_name}']/following-sibling::ul[1]//span")
            year = int(browser.get_text(year_element))
            print(year, latest_movie_year)
        

        
        #  latest_movie_year = max(year, latest_movie_year)
        # Check if this movie is the latest
        if year > latest_movie_year:
            latest_movie_year = year
            latest_movie_title = title
            latest_movieyear_element=result
            print(year)

    
    # Click on the latest "Halloween" movie
    if latest_movie_title:
        browser.click_element(latest_movieyear_element)