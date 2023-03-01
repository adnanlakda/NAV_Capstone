# NAV_Capstone

### Proposed TODOs:

#### 1. Learn how to _actually_ use github. No more "Add files via upload" :) Either: 
- [x] Learn how to use GitHub Desktop - great GUI interface
- [ ] Learn how to use git from command line

#### 2. Improve GitHub
- [x] Determine what files are needed in GitHub
  - [x] Remove unneeded files
- [ ] Create listing of files with descriptions

```
.
├── .gitignore
├── README.md
├── app.py: main driver application
├── final_df.csv: ? 
├── get_category.py: logic for assigning category scores
├── get_date.py: logic for assigning dates
├── get_location.py: logic for assigning locations
├── get_sub_category.py: logic for assigning sub-category scores
├── kws.csv
├── manifest.json
├── master_urls_independent.csv
├── master_urls_inform.csv
├── master_urls_inform.xlsx
├── requirements.txt
├── rsconnect-python
│   └── kinetic.json
├── sub_kws.csv
├── total_independent.csv
├── total_inform.csv
└── total_pravda.csv

```


- [ ] Create diagram of how app functions and code works together
- [ ] Create technical instructions for future groups 

#### 3. Improve existing code
- [ ] Annotate code:
  - [ ] Add official doc strings to modules, classes, and functions
  - [ ] Add in line comments to other parts of code
- [ ] Figure out a way to test simpler runs that don't take so long.
- [ ] Make code more robust to failures with try/except logic
- [ ] Reduce code repetition by creating functions and external files for key words, etc.
- [ ] Add logging and messages so you know what is happening in the code while it is running
- [ ] Reduce requirements.txt

#### 4. Add Twitter API branch
- [ ] Sign up for Twitter API
- [ ] Add branch for Twitter in Shiny UI and `app.py`

#### 5. Improve Usability
- [ ] Improve non-technical user documentation and instructions
- [ ] Test until the program runs or fails gracefully in all reasonable scenarios