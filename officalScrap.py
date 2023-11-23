from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import csv
import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def make_abbreviation(name):
    words = name.split()
    return "".join(word[0].upper() for word in words)


def run(playwright: Playwright) -> None:
    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the page
        logging.info("Navigating to the CUNY search page...")
        page.goto("https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp")

        # Extract college names
        college_checkboxes = page.query_selector_all(
            "ul.checkboxes input[type='checkbox']"
        )
        colleges = [
            page.query_selector(f"label[for='{checkbox.get_attribute('id')}']")
            .text_content()
            .strip()
            for checkbox in college_checkboxes
        ]

        for index, college in enumerate(colleges, start=1):
            logging.info(f"{index}. {college}")

        selected_index = int(input("Select a college by entering its number: ")) - 1
        selected_college = colleges[selected_index]
        school_name = make_abbreviation(selected_college)

        # Find and click the corresponding checkbox
        checkbox = page.query_selector(
            f"label[for='{college_checkboxes[selected_index].get_attribute('id')}']"
        )
        if checkbox:
            checkbox.click()
        else:
            logging.error("Selected college not found.")
            return

        # Process for terms
        term_select = page.query_selector("select[name='term_value']")
        if term_select is None:
            logging.error("Term select element not found.")
            return
        # Now it's safe to call query_selector_all
        terms = [
            (option.text_content().strip(), option.get_attribute("value"))
            for option in term_select.query_selector_all("option")
            if option.get_attribute("value")
        ]

        for index, term in enumerate(terms, start=1):
            logging.info(f"{index}. {term[0]}")
        term_index = int(input("Select a term by entering its number: ")) - 1
        term_select.select_option(terms[term_index][1])

        page.get_by_role("button", name="Next").click()

        # Process for subjects
        subject_select = page.query_selector("#subject_ld")
        subjects = [
            (option.text_content().strip(), option.get_attribute("value"))
            for option in subject_select.query_selector_all("option")
            if option.get_attribute("value")
        ]
        for index, subject in enumerate(subjects, start=1):
            logging.info(f"{index}. {subject[0]}")
        subject_index = int(input("Select a subject by entering its number: ")) - 1
        subject_select.select_option(subjects[subject_index][1])

        # Process for course careers
        course_career_select = page.query_selector("#courseCareerId")
        careers = [
            (option.text_content().strip(), option.get_attribute("value"))
            for option in course_career_select.query_selector_all("option")
            if option.get_attribute("value")
        ]
        for index, career in enumerate(careers, start=1):
            logging.info(f"{index}. {career[0]}")
        career_index = int(input("Select a course career by entering its number: ")) - 1
        course_career_select.select_option(careers[career_index][1])

        # Turn off show only open button
        page.locator(".slider").first.click()

        # Click the search button
        page.get_by_role("button", name="Search").click()

        # Extract course data
        # Query all the div elements with the class "testing_msg" and extract course full names
        course_name_elements = page.query_selector_all(".testing_msg")
        course_full_names = [
            element.query_selector("span").inner_text().strip()
            for element in course_name_elements
            if element
        ]
        # Get the HTML content of the page
        html_content = page.content()
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        # Find all tables with the class 'classinfo'
        tables = soup.find_all("table", class_="classinfo")
        combined_courses = []

        for course_name, table in zip(course_full_names[2:], tables):
            if table is None:
                print("Table element not found for", course_name)
                continue

            classes = []
            for tbody in table.find_all("tbody"):
                class_row = tbody.find("tr")
                if class_row:
                    cells = class_row.find_all("td")
                    status_img = cells[7].find("img") if len(cells) > 7 else None
                    status = status_img["title"] if status_img else "Unknown"

                    class_info = {
                        "class": cells[0].get_text(strip=True),
                        "section": cells[1].get_text(strip=True),
                        "days_times": cells[2].get_text(strip=True),
                        "room": cells[3].get_text(strip=True),
                        "instructor": cells[4].get_text(strip=True),
                        "instruction_mode": cells[5].get_text(strip=True),
                        "meeting_dates": cells[6].get_text(strip=True),
                        "status": status,
                    }
                    classes.append(class_info)

            course_data = {"course_name": course_name, "classes": classes}
            combined_courses.append(course_data)

        # Save data to CSV
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        folder_path = "collegeCourseData"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = f"{folder_path}/{school_name}_{make_abbreviation(subjects[subject_index][0])}-{current_date}.csv"
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Course Name",
                    "Class",
                    "Section",
                    "Days & Times",
                    "Room",
                    "Instructor",
                    "Instruction Mode",
                    "Meeting Dates",
                    "Status",
                ]
            )
            for course in combined_courses:
                for class_info in course["classes"]:
                    writer.writerow(
                        [
                            course["course_name"],
                            class_info["class"],
                            class_info["section"],
                            class_info["days_times"],
                            class_info["room"],
                            class_info["instructor"],
                            class_info["instruction_mode"],
                            class_info["meeting_dates"],
                            class_info["status"],
                        ]
                    )
        logging.info(f"File has been save: {file_name}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        context.close()
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
