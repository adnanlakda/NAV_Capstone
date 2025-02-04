# NAV_Capstone

### Proposed TODOs:



#### 1. Improve GitHub
- [x] Determine what files are needed in GitHub
  - [x] Remove unneeded files
- [x] Create listing of files with descriptions

```
.
├── .gitignore
├── README.md
├── app.py: main driver application
├── final_df.csv: final output of the model combining all the websites scraped 
├── get_category.py: logic for assigning category scores
├── get_date.py: logic for assigning dates
├── get_location.py: logic for assigning locations
├── get_sub_category.py: logic for assigning sub-category scores
├── kws.csv: keywords categories list along with its assigned scores
├── manifest.json: information about the application, its dependencies, and associated files
├── master_urls_independent.csv: list of urls scraped for this website
├── master_urls_inform.csv: list of urls scraped for this website
├── master_urls_inform.xlsx: list of urls scraped for this website
├── requirements.txt: information about all the libraries, modules, and packages
├── rsconnect-python
│   └── kinetic.json: contains information about a Shiny app
├── sub_kws.csv: sub-category keywords list along with its assigned scores
├── total_independent.csv: model output for Kyiv Independent website scraped
├── total_inform.csv: model output for Ukrinform website scraped
└── total_pravda.csv: model output for Ukrainska Pravada website scraped

```
- [x] Create diagram of how app functions and code works together

  <img src=https://github.com/katgrubbs14/NAV_Capstone/blob/main/model.jpeg>

- [x] Create technical instructions for future groups 

#### 2. Improve existing code
- [x] Annotate code:
  - [x] Add official doc strings to modules, classes, and functions: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
  - [x] Add in line comments to other parts of code
- [x] Figure out a way to test simpler runs that don't take so long.
  - [x] The way to do test runs simpler is to create a separate file that pulls the section of the codes out of the def loop
- [x] Make code more robust to failures with try/except logic
- [x] Reduce code repetition by creating functions and external files for key words, etc.
- [x] Debug using try and except logic
- [ ] **(optional)** Add logging and messages so you know what is happening in the code while it is running
- [ ] **(optional)** Reduce requirements.txt

#### 3. Add API branch
- [x] Sign up for Mediastack API 
- [x] Add branch for social in Shiny UI and `app.py`
- [ ] **(optional)** Twitter?

#### 4. Improve Usability
- [x] Improve non-technical user documentation and instructions
- [x] Test until the program runs or fails gracefully in all reasonable scenarios
