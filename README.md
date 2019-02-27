# metadata-workbench
collection of methods, scripts, and services for managing and enriching metadata and assessing usage

## Purpose

- Make reusable scripts and API wrappers easier to find, understand, debug, and consume
- Identify, coordinate, and standardize the implementation and maintenance of tools to assist metadata management
- Create a single place to create and manage recurring and scheduled jobs

## Usage


### Setup


#### Download and Configure IDE

PyCharm is a popular IDE (Integrated Development Environment) for python that will help you run, edit, and debug 
  your scripts. 

1. [Download](https://www.jetbrains.com/pycharm-edu/download/) and Install PyCharm Community version and follow installation instructions.

2. Open PyCharm and select "Check out from Version Control" > Git. Put `https://github.com/bulib/metadata-workbench.git` (the git url for this repository) in for the 'URL' and set the 'Directory' to wherever on your computer you'd like to store the project (I use `Users/<username>/projects/metadata`). Open the folder once complete.

![pycharm-ui_new-project-from-git](https://user-images.githubusercontent.com/5565284/52804301-eab93000-3051-11e9-8b19-2cbb23584d6c.png)

3. Expand the `metadata-workbench` drop-down on the left to see the file structure, right click on `src`, then go to "Mark Directory As" > "Sources Root"
  
![pycharm-ui_mark-as-src-root](https://user-images.githubusercontent.com/5565284/52809718-ea736180-305e-11e9-84fa-fdc7427a7eba.png)

4. Open `requirements.txt`. You should see a bar at the top of your IDE telling you that you don't have all the requirements installed. Follow the prompt and click "Install Requirements." If you don't see this, open a terminal and type the following commands:
``` 
$ sudo easy_install pip
$ pip install -r requirements.txt
```

#### Setting API_KEYS

Most of the APIs we use require API keys that are sent in some form or fashion with the request. 

1] create a new `secrets.py` file in the `src/services` directory.


> _note: This file should automatically be ignored by the source control (via `.gitignore`) and should never be committed to the 
  git repository in order for our private keys to stay private._
  
2] create a new `API_KEYS` variable with the following value (it's a [python 'dictionary'](https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects))
  
```python
# src/services/secrets.py
API_KEYS = {
    "<api_provider>":{
        "<api_name>": {
            "<environment>":"<API_KEY_VALUE>"
        }
    },
    "alma": {
        "analytics": {
            "production": "<API_KEY_FOR_ALMA_ANALYTICS_API>"
        },
        "bibs": {
            "production": "<API_KEY_FOR_ALMA_BIBS_API__PROD>",
            "sandbox":    "<API_KEY_FOR_ALMA_BIBS_API__STAGING>"
        }
    },
    "primo": {
        "analytics": {
            "production": "<API_KEY_FOR_PRIMO_ANALYTICS>"
        }
    }
}
```

3] Replace `<API_KEY_*>` values with their associated keys from each API provider. 

- The Alma and Primo APIs can be found on the ExLibris developer network at My APIs > [Manage API KEYs](https://developers.exlibrisgroup.com/manage/keys/). 

>note: You can see this variable being imported and used in `src/services/__init__.py`:_
>```python 
>from services.secrets import API_KEYS
>...
>def get_api_key(platform="alma", api="bibs", env="sandbox"):
>    return API_KEYS[platform][api][env]
>```

4] To ensure you have everything set up correctly, right click on `setup_checker.py` and click "Run" (or run the 
   following command). It will let you know if any part of your setup is obviously incorrect.
   
```bash
$ python src/setup_checker.py
```

#### Verifying the Setup

To make sure that everything is set up correctly, try running `src/setup_checker.py` from the command line 
  (via `$ python src/setup_checker.py`) or by right-clicking on the file in PyCharm and clicking "Run 'setup_checker'".

Read the logs to see whether "All initial tests have run successfully", and if not ("exit code 1"), follow the 
  instructions or [create a new issue](https://github.com/bulib/metadata-workbench/issues/new) with the `question` 
  label added.


### Creating a Script

Once everything is setup, you should be able to use the wrappers/helpers in `src/services` to interact with the 
  required APIs. 

See [`src/analytics/run_weekly_alma_reports.py`](https://github.com/bulib/metadata-workbench/blob/master/src/analytics/run_weekly_alma_reports.py) 
  for an example of how to import and utilize them. 

The easiest way to keep this runnable from the command line is to write your scripts in the base `src/` directory.


If the script you write is more than a one-off and/or it needs to be run on a recurring basis, 
  [create a new file](https://github.com/bulib/metadata-workbench/new/master/src) from your github account, making
  sure to select "Create a **new branch** for this commit and start a pull request" at the bottom of the page. 
  If you've already been committing your changes to a new branch (much preferred), remember to 
  [create a pull request](https://github.com/bulib/metadata-workbench/compare). 

