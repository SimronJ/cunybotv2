from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import csv
import datetime
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def make_abbreviation(name):
    return "".join(word[0].upper() for word in name.split())


def run(playwright: Playwright) -> None:
    try:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        logging.info("Navigating to the CUNY search page...")
        page.goto("https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp")

        # Extracting college names
        college_labels = page.query_selector_all("ul.checkboxes label")
        colleges = [label.text_content().strip() for label in college_labels]

        for index, college in enumerate(colleges, start=1):
            logging.info(f"{index}. {college}")

        selected_index = int(input("Select a college by entering its number: ")) - 1
        selected_college = colleges[selected_index]
        school_name = make_abbreviation(selected_college)

        # Clicking the checkbox for the selected college
        college_labels[selected_index].click()

        # Selecting term, subject, and course career
        # These selections can be further refined as needed
        # ... (your existing code for selections)

        # Extracting course data
        course_name_elements = page.query_selector_all(".testing_msg")
        course_full_names = [
            element.text_content().strip() for element in course_name_elements
        ]

        page.wait_for_selector(".classinfo")  # Wait for the table to load
        html_content = page.content()
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table", class_="classinfo")

        combined_courses = []
        for course_name, table in zip(course_full_names, tables):
            classes = []
            for tbody in table.find_all("tbody"):
                class_row = tbody.find("tr")
                if class_row:
                    cells = class_row.find_all("td")
                    class_info = {
                        "class": cells[0].text,
                        "section": cells[1].text,
                        # ... (rest of your cell processing)
                    }
                    classes.append(class_info)
            combined_courses.append({"course_name": course_name, "classes": classes})

        # Saving data to CSV
        # ... (your existing CSV saving logic)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        context.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
