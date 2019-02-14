# metadata-workbench
collection of methods, scripts, and services for managing and enriching metadata and assessing usage

## Usage


### Setup


#### Download and Configure IDE

PyCharm is a popular IDE (Integrated Development Environment) for python that will help you run, edit, and debug 
  your scripts. 

1. [Download](https://www.jetbrains.com/pycharm-edu/download/) and Install PyCharm Community version and follow installation instructions.

2. Open PyCharm and select "Check out from Version Control" > Git. Put `https://github.com/bulib/metadata-workbench.git` (the git url for this repository) in for the 'URL' and set the 'Directory' to wherever on your computer you'd like to store the project (I use `Users/<username>/projects/metadata`). Open the folder once complete.

![pycharm-ui_new-project-from-git](https://user-images.githubusercontent.com/5565284/52804301-eab93000-3051-11e9-8b19-2cbb23584d6c.png)

3. Expand the `metadata-workbench` dropdown on the left to see the file structure, right click on `src`, then go to "Mark Directory As" > "Sources Root"
  
![pycharm-ui_mark-as-src-root](https://user-images.githubusercontent.com/5565284/52809718-ea736180-305e-11e9-84fa-fdc7427a7eba.png)

4. Open `requirements.txt`. You should see a bar at the top of your IDE telling you that you don't have all the requirements installed. Follow the prompt and click "Install Requirements." If you don't see this, open a terminal and type the following commands:
``` 
$ sudo easy_install pip
$ pip install -r requirements.txt
```

#### Setting API_KEYS

Most of the APIs we use require API keys that are sent in some form or fashion with the request. 

In order to keep these keys private, we store them in a `secrets.py` file that we don't include in the public
  git repository. This file should contain the variable `API_KEYS` consisting of what looks like a 
  `json` object (it's a [python 'dictionary'](https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects))
  
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

The values to use for the Alma and Primo APIs can be found on the exlibris developer network at My APIs > [Manage API KEYs](https://developers.exlibrisgroup.com/manage/keys/]. 

_note: You can see this variable being imported and used in `src/services/__init__.py`:_
```python 
from services.secrets import API_KEYS
...
def get_api_key(platform="alma", api="bibs", env="sandbox"):
    return API_KEYS[platform][api][env]
```
