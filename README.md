## How to install the requirements

### Install virtual environment and python3
```
    sudo apt-get install python3 python3-virtualenv python3-pip

```

### Initialize a new virtual environment and activate it:
```
    sudo  virtualenv venv
    source venv/bin/activate

```

### Install the requirements in the new virtual environment
```
    cd hashtag_project
    sudo pip install -r requirements.txt

```

## How to run the code

### Set up the parameters in the config.ini file

```
    cd hashtag_project/source
    vim config.ini  # Or any file editor

```

```
    # Default values:

    [reportlab]
    top_words=20
    references_per_document=1

    [hashtag_core]
    min_word_length=6
```

### Execute main.py after initializing the virtualenv

```
    cd hashtag_project/source
    python main.py

```
### Output PDF report file is located in the output directory
```
    cd hashtag_project/output
    firefox test.pdf    # any PDF viewer

```

## Known issues
- Right now it only shows one reference per document (up to 6 references total).  When reporting more than two references per document, ReportLab breaks because the total height of the row is bigger than a page.
- The sentence splitter method sometimes breaks the line in the wrong part.