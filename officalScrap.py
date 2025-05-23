from playwright.async_api import async_playwright, Playwright
import asyncio
import aioconsole
from bs4 import BeautifulSoup
import csv, json
import datetime
import os
import logging
import preferences


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def is_data_recent(filename, age_limit_days=7):
    if not os.path.exists(filename):
        return False

    file_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
    days_it_has_been = (datetime.datetime.now() - file_modified_time).days
    logging.info(f"{filename} file is {days_it_has_been} days old.")

    if days_it_has_been > age_limit_days:
        logging.info(
            f"File {filename} is older than {age_limit_days} days, deleting it."
        )
        os.remove(filename)
        return False

    return True


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def generate_file_name(
    folder,
    folderType,
    folder_collegeName,
    selected_collegeCode,
    term_selected,
    subjectName,
    whichCareer,
    current_date,
    extension,
):
    return f"{folder}/{folderType}/{folder_collegeName}/{selected_collegeCode}_{term_selected}_{subjectName}_{whichCareer}-{current_date}.{extension}"


async def save_data_to_json(
    data,
    collegeName,
    selected_collegeCode,
    term_selected,
    subjectName,
    whichCareer,
    current_date,
):
    folder = "collegeCourseData"
    jsonFile_path = "jsonFiles"
    create_directory(os.path.join(folder, jsonFile_path, collegeName))

    file_name = generate_file_name(
        folder,
        jsonFile_path,
        collegeName,
        selected_collegeCode,
        term_selected,
        subjectName,
        whichCareer,
        current_date,
        "json",
    )

    with open(file_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)
    logging.info(f"JSON file has been saved: {file_name}")


async def save_data_to_csv(
    data,
    collegeName,
    selected_collegeCode,
    term_selected,
    subjectName,
    whichCareer,
    current_date,
):
    folder = "collegeCourseData"
    csvFile_path = "csvFiles"
    create_directory(os.path.join(folder, csvFile_path, collegeName))

    file_name = generate_file_name(
        folder,
        csvFile_path,
        collegeName,
        selected_collegeCode,
        term_selected,
        subjectName,
        whichCareer,
        current_date,
        "csv",
    )

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
        for course in data:
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
    logging.info(f"CSV file has been saved: {file_name}")


async def select_college_and_term(page, user_preferences):
    collegeName = user_preferences.get("collegeName") if user_preferences else None
    selected_index = user_preferences.get("selected_index") if user_preferences else -1
    selected_college_code = (
        user_preferences.get("selected_collegeCode") if user_preferences else None
    )
    term_index = user_preferences.get("term_index") if user_preferences else -1
    term_selected = user_preferences.get("term_selected") if user_preferences else None

    # Define paths and filenames
    collegeDataList_path = "CollegeDataList"
    collegeNTerm_data_file = "collegeNTerm_data.json"

    # Create directories if they don't exist
    create_directory(collegeDataList_path)

    # Join paths correctly
    college_data_file = os.path.join(collegeDataList_path, collegeNTerm_data_file)

    # Try to load existing data
    collegeNTermData = await preferences.load_data(college_data_file)

    # Navigate to the page
    logging.info("Navigating to the CUNY search page...")
    await page.goto("https://globalsearch.cuny.edu/CFGlobalSearchTool/search.jsp")

    # Extract college names
    # Check if the college data is recent and use it if so
    college_checkboxes = await page.query_selector_all(
        "ul.checkboxes input[type='checkbox']"
    )

    if await is_data_recent(college_data_file) and "CollegeList" in collegeNTermData:
        colleges = collegeNTermData.get("CollegeList", [])
    else:
        # Scrape college data
        colleges = [
            (await checkbox.text_content()).strip() for checkbox in college_checkboxes
        ]

    if collegeName is None:
        # Display colleges and ask user to select
        for index, college in enumerate(colleges, start=1):
            logging.info(f"{index}. {college}")

    if selected_index < 0:
        selected_index = (
            int(await aioconsole.ainput("Select a college by entering its number: "))
            - 1
        )

    college_name = (
        "".join(colleges[selected_index].split())
        if collegeName is None
        else collegeName
    )
    if selected_college_code is None and selected_index >= 0:
        selected_college_code = await college_checkboxes[selected_index].get_attribute(
            "id"
        )

    # Find and click the corresponding checkbox
    checkbox = await page.query_selector(f"label[for='{selected_college_code}']")
    if not checkbox:
        logging.error("Selected college not found.")
        return None, None

    await checkbox.click()

    term_select = await page.query_selector("select[name='term_value']")

    # Check if the college data is recent and use it if so
    if await is_data_recent(college_data_file) and "TermList" in collegeNTermData:
        terms = collegeNTermData.get("TermList", [])
    else:
        # Extract terms
        if term_select is None:
            logging.error("Term select element not found.")
            return None, None
        # Scrape terms data
        college_checkboxes = await page.query_selector_all(
            "ul.checkboxes input[type='checkbox']"
        )
        terms = [
            (
                (await option.text_content()).strip(),
                await option.get_attribute("value"),
            )
            for option in await term_select.query_selector_all("option")
            if await option.get_attribute("value")
        ]
        # Save file for faster use
        collegeNTermData = {"CollegeList": colleges, "TermList": terms}
        await preferences.save_data(college_data_file, collegeNTermData)

    if collegeName is None:
        # Display terms and ask user to select
        for index, term in enumerate(terms, start=1):
            logging.info(f"{index}. {term[0]}")

    if term_index < 0:
        term_index = (
            int(await aioconsole.ainput("Select a term by entering its number: ")) - 1
        )
    if term_selected is None:
        term_selected = terms[term_index][1]

    await term_select.select_option(term_selected)

    await page.get_by_role("button", name="Next").click()

    return [
        college_name,
        selected_index,
        selected_college_code,
        term_index,
        term_selected,
    ]


async def select_subject_and_career(page, collegeName, user_preferences):
    subject_name = user_preferences.get("subjectName") if user_preferences else None
    subject_index = user_preferences.get("subject_index") if user_preferences else -1
    which_career = user_preferences.get("whichCareer") if user_preferences else None
    career_index = user_preferences.get("career_index") if user_preferences else -1

    # Define paths and filenames
    collegeName_path = collegeName
    collegeDataList_path = "CollegeDataList"
    subjectNCareer_data_file = "subjectNCareer_data.json"

    # Create directories if they don't exist
    create_directory(os.path.join(collegeDataList_path, collegeName_path))

    # Join paths correctly
    subject_data_file = os.path.join(
        collegeDataList_path, collegeName_path, subjectNCareer_data_file
    )

    # Try to load existing data
    subjectNCareerData = await preferences.load_data(subject_data_file)

    if subjectNCareerData is None:
        subjectNCareerData = {}

    # Process for subjects
    subject_select = await page.query_selector("#subject_ld")
    if subject_select is None:
        logging.error("Subject select element not found.")
        return (
            None,
            None,
            None,
            None,
        )

    if await is_data_recent(subject_data_file) and "SubjectList" in subjectNCareerData:
        logging.info(f"Using cached subject data.")
        subjects = subjectNCareerData.get("SubjectList", [])
    else:
        subjects = [
            (await option.text_content().strip(), await option.get_attribute("value"))
            for option in await subject_select.query_selector_all("option")
            if await option.get_attribute("value")
        ]
        subjectNCareerData["SubjectList"] = subjects

    if subject_name is None:
        # Display subjects and ask user to select
        for index, subject in enumerate(subjects, start=1):
            logging.info(f"{index}. {subject[0]}")

    if subject_index < 0:
        subject_index = (
            int(await aioconsole.ainput("Select a subject by entering its number: "))
            - 1
        )
    if subject_name is None:
        subject_name = subjects[subject_index][1]
    await subject_select.select_option(subject_name)

    # Process for course careers
    course_career_select = await page.query_selector("#courseCareerId")
    if course_career_select is None:
        logging.error("Course career select element not found.")
        return None, None, None, None

    if await is_data_recent(subject_data_file) and "CareerList" in subjectNCareerData:
        logging.info(f"Using cached career data.")
        careers = subjectNCareerData.get("CareerList", [])
    else:
        careers = [
            (await option.text_content().strip(), await option.get_attribute("value"))
            for option in await course_career_select.query_selector_all("option")
            if await option.get_attribute("value")
        ]
        subjectNCareerData["CareerList"] = careers
        # Save the updated data
        await preferences.save_data(subject_data_file, subjectNCareerData)

    if which_career is None:
        # Display careers and ask user to select
        for index, career in enumerate(careers, start=1):
            logging.info(f"{index}. {career[0]}")

    if career_index < 0:
        career_index = (
            int(
                await aioconsole.ainput(
                    "Select a course career by entering its number: "
                )
            )
            - 1
        )

    if which_career is None:
        which_career = careers[career_index][1]
    await course_career_select.select_option(which_career)

    # Turn off show only open button
    await page.locator(".slider").first.click()
    # Click the search button
    await page.get_by_role("button", name="Search").click()

    return [subject_name, subject_index, which_career, career_index]


async def extract_course_data(page):
    # Extract course names
    course_name_elements = await page.query_selector_all(".testing_msg")
    course_full_names = []

    for element in course_name_elements:
        span_element = await element.query_selector("span")
        if span_element:
            inner_text = await span_element.inner_text()
            course_full_names.append(inner_text.strip())

    # Get the HTML content of the page
    html_content = await page.content()
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

    return combined_courses


async def run(playwright: Playwright) -> None:
    try:
        user_preferences = preferences.load_preferences("userPreference.json")
        collegeName = None
        selected_index = -1
        selected_collegeCode = None
        term_index = -1
        term_selected = None
        subjectName = None
        subject_index = -1
        whichCareer = None
        career_index = -1
        combined_courses = None

        # Initialize Playwright browser and page
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        if user_preferences is None:
            (
                collegeName,
                selected_index,
                selected_collegeCode,
                term_index,
                term_selected,
            ) = await select_college_and_term(page, user_preferences)
            (
                subjectName,
                subject_index,
                whichCareer,
                career_index,
            ) = await select_subject_and_career(page, collegeName, user_preferences)

        else:
            collegeName = user_preferences.get("collegeName")
            selected_collegeCode = user_preferences.get("selected_collegeCode")
            term_selected = user_preferences.get("term_selected")
            subjectName = user_preferences.get("subjectName")
            whichCareer = user_preferences.get("whichCareer")

            (
                collegeName,
                selected_index,
                selected_collegeCode,
                term_index,
                term_selected,
            ) = await select_college_and_term(page, user_preferences)
            logging.info("Selected College and Term")

            (
                subjectName,
                subject_index,
                whichCareer,
                career_index,
            ) = await select_subject_and_career(page, collegeName, user_preferences)
            logging.info("Selected subject and career")

        logging.info("Now extracting classes")
        combined_courses = await extract_course_data(page)

        if not combined_courses:
            logging.error("No course data found.")
            return

        logging.info("saving data")
        # Save data
        current_date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        await save_data_to_json(
            combined_courses,
            collegeName,
            selected_collegeCode,
            term_selected,
            subjectName,
            whichCareer,
            current_date,
        )
        await save_data_to_csv(
            combined_courses,
            collegeName,
            selected_collegeCode,
            term_selected,
            subjectName,
            whichCareer,
            current_date,
        )

        # Save new preferences
        user_preferences = {
            "collegeName": collegeName,
            "selected_index": selected_index,
            "selected_collegeCode": selected_collegeCode,
            "term_index": term_index,
            "term_selected": term_selected,
            "subjectName": subjectName,
            "subject_index": subject_index,
            "whichCareer": whichCareer,
            "career_index": career_index,
        }
        preferences.save_preferences(user_preferences, "userPreference.json")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


if __name__ == "__main__":
    asyncio.run(main())
