EXECUTABLE_PATH = r'E:\UdS MSc DSAI\Thesis\Scripts\Scraping\data\chromedriver.exe'
BASE_FOLDER = r'data\\'
ELEMENT_TIMEOUT = 20

CHAPTER_TABLE = 'concept-list-container'
#CHAPTER_ROWS = '//div[@class="NestedExplorer__AccordionItemStyled-sc-8rd5ed-0 jpuChD Accordion__StyledItem-z6hx9p-1 kYcAnH"]'
CHAPTER_ROWS = "//button[starts-with(@id, 'radix-')]"
SUBCHAPTER_ROWS = 'LevelItem__Container-i60d4c-4 gHaOcC'
SUBCHAPTER_URL = '//a[@data-dx-desc="course_toc_section_button"]'

CHAPTER_CONTENT = 'x-ck12-data-concept'
FALLBACK_CHAPTER_CONTENT = 'ck12Content'

OPENSTAX_SUMMARY_MAPPING = {'physics': 'Section Summary',
                            'chemistry': 'Summary',
                            'biology': 'Chapter Summary',
                            'economics': 'Key Concepts and Summary',
                            'political science': 'Summary',
                            'history': 'Section Summary'}

OPENSTAX_CHAPTER_MAPPING = {'biology': 'unit',
                            'chemistry': 'chapter',
                            'physics': 'chapter',
                            'economics': 'chapter',
                            'political science': 'unit',
                            'history': 'unit'}

# Subject-wise file names. Used in merge_subjects.py
CHEMISTRY_FILES = ['brightstorm_chemistry.csv',
                   'ck-12-chemistry-flexbook-2.0_content.csv',
                   'openstax_chemistry.csv']

PHYSICS_FILES = ['brightstorm_physics.csv',
                 'ck-12-physics-flexbook-2.0_content.csv',
                 'openstax_physics.csv']

BIOLOGY_FILES = ['brightstorm_biology.csv',
                 'ck-12-biology-flexbook-2.0_content.csv',
                 'openstax_biology.csv',
                 'ck-12-biology-india_content.csv']

ECONOMICS_FILES = ['openstax_economics.csv',
                   'Economics with Emphasis on the Free Enterprise System_content.csv']

PHYSICAL_SCIENCE_FILES = ['ck-12-physical-science-flexbook-2.0_content.csv']

# KHAN ACADEMY
KHANACADEMY_BIOLOGY_MAPPING = {'middle_school_ngss': 'https://www.khanacademy.org/science/ms-biology/test/x0c5bb03129646fd6:course-challenge',
                               'high_school': 'https://www.khanacademy.org/science/high-school-biology/test/xadc658068d147c42:course-challenge',
                               'high_school_ngss': 'https://www.khanacademy.org/science/hs-biology/test/x4c673362230887ef:course-challenge',
                               'ap_biology': 'https://www.khanacademy.org/science/ap-biology/test/x16acb03e699817e9:course-challenge'}

CLOSE_DONATION_BANNER = '//button[@data-test-id="close-donate-banner"]'
BEGIN_TEST_CLASS = '_1gw4cnik'
CHECK_ANSWER_BTN_XPATH = '//button[@data-test-id="exercise-check-answer"]'
NEXT_QUESTION_BTN = '//button[@data-test-id="exercise-next-question"]'
ANSWER_ROW = '//li[contains(@class, "perseus-radio-option")]'
SLEEP_LOWER_LIMIT = 2.1
SLEEP_HIGHER_LIMIT = 5.1
INCORRECT_POPOVER = '//div[@data-test-id="exercise-feedback-popover-incorrect"]'
CORRECT_POPOVER = '//div[@data-test-id="exercise-feedback-popover-correct"]'
MULTIPLE_POPOVERS = '//div[@data-test-id="exercise-feedback-popover-incorrect" or @data-test-id="exercise-feedback-popover-unanswered"]'
MULTILINE_QUESTION_TEXT = '//div[@class="paragraph" and @data-perseus-paragraph-index]'
QUESTION_TYPE = 'perseus-sr-only'

# PROPROFS
PROPROF_BIO_BASE_URL = 'https://www.proprofs.com/quiz-school/topic/biology'