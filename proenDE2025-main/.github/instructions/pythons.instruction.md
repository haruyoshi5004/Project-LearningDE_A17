---
applyTo: "**.py"
---

these are files for python files.

- file I/O must be separated from main function.  
for example, if "outputs all users in json file" function is needed, getting all users and write list of user in json format should be two different function, and even yet, writing/creating json file and formatting user in json format should be different format/method.
- we use mySQL. with SQLalchemy.
- we don't keep print() in codes in general. we want to use logger.  
warn user about this everytime you see print() in code, even if its unrelated to the subject.  
but don't touch it unless user clearly asked.  
    - when you feel like it, you can assign logger.info as print as temporal solution, since this doesn't affect much lines. still warn user about it when you find your temporal solution in code
    - exception:
        - ./setup.py
