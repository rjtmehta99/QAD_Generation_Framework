css = 'footer {visibility: hidden}'
tab_title = 'MSc Thesis - Rajat Mehta'
page_title = '<div style="text-align: center; margin: 0 auto;"><h1 style="font-size: 40px;">Beyond Handcrafting Screening Questions<br></h1></div>'

# Distractor
DIST_COLS = ['generated_question', 'generated_answer']
DIST_COLS_2 = ['generated_question', 'generated_answer','T5_distractors', 'cleaned_distr']

DISTRACTOR_LIMIT = 10
COL_PREFIX = 'distractor_'
WORD2VEC_FILE = 'data/word2vec-google-news-300.model'
STOPWORDS = ['a', 'an', 'the', 'from', 'of', 'its', 'it\'s', 'via', 'all', 'or', 'your', 'by', 'it', 'their', 'from']
BLACKLISTED_DISTR_WORDS = ['Dr.', 'phone']
WORD_NUMBER_DICT = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 
                    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 
                    'nineteen': 19, 'twenty': 20, 'twenty one': 21, 'twenty two': 22, 'twenty three': 23, 'twenty four': 24, 'twenty five': 25, 
                    'twenty six': 26, 'twenty seven': 27, 'twenty eight': 28, 'twenty nine': 29, 'thirty': 30, 'thirty one': 31, 'thirty two': 32, 
                    'thirty three': 33, 'thirty four': 34, 'thirty five': 35, 'thirty six': 36, 'thirty seven': 37, 'thirty eight': 38, 'thirty nine': 39, 
                    'forty': 40, 'forty one': 41, 'forty two': 42, 'forty three': 43, 'forty four': 44, 'forty five': 45, 'forty six': 46, 'forty seven': 47, 
                    'forty eight': 48, 'forty nine': 49, 'fifty': 50, 'fifty one': 51, 'fifty two': 52, 'fifty three': 53, 'fifty four': 54, 'fifty five': 55, 
                    'fifty six': 56, 'fifty seven': 57, 'fifty eight': 58, 'fifty nine': 59, 'sixty': 60, 'sixty one': 61, 'sixty two': 62, 'sixty three': 63, 
                    'sixty four': 64, 'sixty five': 65, 'sixty six': 66, 'sixty seven': 67, 'sixty eight': 68, 'sixty nine': 69, 'seventy': 70, 'seventy one': 71, 
                    'seventy two': 72, 'seventy three': 73, 'seventy four': 74, 'seventy five': 75, 'seventy six': 76, 'seventy seven': 77, 'seventy eight': 78, 
                    'seventy nine': 79, 'eighty': 80, 'eighty one': 81, 'eighty two': 82, 'eighty three': 83, 'eighty four': 84, 'eighty five': 85, 
                    'eighty six': 86, 'eighty seven': 87, 'eighty eight': 88, 'eighty nine': 89, 'ninety': 90, 'ninety one': 91, 'ninety two': 92, 
                    'ninety three': 93, 'ninety four': 94, 'ninety five': 95, 'ninety six': 96, 'ninety seven': 97, 'ninety eight': 98, 'ninety nine': 99, 
                    'one hundred': 100, 'hunderd': 100, 'a hundred': 100}

CHEMISTRY_CSV = 'data/chemistry_merged.csv'
PHYSICS_CSV = 'data/physics_merged.csv'
BIOLOGY_CSV = 'data/biology_merged.csv'
ECONOMICS_CSV = 'data/economics_merged.csv'
PHYSICAL_SCIENCE_CSV = 'data/physical_sciences_merged.csv'

BIOLOGY_OSTAX_CSV = 'data/openstax_biology_sample.csv'
BIOLOGY_CK12_CSV = 'data/ck-12-biology-flexbook-2.0_content.csv'
BIOLOGY_BSTORM_CSV = 'data/brightstorm_biology.csv'

SELECTED_ROWS_CSV = 'data/selected_data.csv'