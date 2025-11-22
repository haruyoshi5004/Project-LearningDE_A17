---
applyTo: "**"
---

- about this project / abstract structure of project
    - goal of this project is one web service, scope of development is both frontend and backend, and application.
    - majority of files are web server / web api server combined in one.
    - behind web api, we will develop core application, including:
        - image recognition using YOLO for bicycle and its parts.
        - coordinates data extraction from mp4 files.
    - we will use mySQL as DB.
        - we will implement model class for DB. don't directly access to DB, we will use those classes.

- naming conventions:
    - general
        - in general, name symbols with camel case.  
        it'll be stated in each segment which UCC or LCC should be used. there are exceptions.  
        (UCC: Upper Camel Case, LCC: Lower Camel Case)
        - no romanji for symbol name.
        - in general, no variable name with 2 characters or less.  
        loops are exceptions, you can use like [i, j, k] or [i1, i2, i3] like common custom.
        - for symbol name, outside of very common custom, name it in order from bigger category to smaller category.  
        for example, class for important user, as subclass of "User" class, name it UserImportant.  
        think its same way as in number; "user1" and "user2", "userHim" and "userHer".  
        I'll refer this rule as "order rule" below.
    - class
        - UCC
        - follow order rule.
    - exception
        - UCC
        - generally follow order rule. "Exception" always comes last.  
        for example, if user have something bad condition, appropriate name would be: UserBadConditionException  
        if user is unknown, appropriate name would be: UserUnknownException
    - method
        - LCC
        - if python and private method, start with underscore.
        - for method that manipulate data inside its instance, name should include verb.  
        for example, for user updating password, appropriate name would be: user.updatePassword()
        - for method to get data from its instance, name should include "get" in general.  
        for example, for getting last login date of user, appropriate name would be: user.getLastLoginDate()  
        for method to get boolean data from its instance, name should include "is", "has", "can" or "should". like:  
        user.isExpired(),  
        user.canSubmit(),  
        user.hasDoneUpdate()  
    - variable
        - LCC
        - if python and private field, start with underscore.
        - generally follow order rule.
        - name should tell what type it is. not necessary
    - constant
        - all uper case, underscore puncture. like: USER_MAX_COUNT
    - others
        if type of soemthing is list-like, name should be plural like: list[User] users

- general coding policy
    - use foreach instead of for if possible. consider using enumrate if python.
    - block of code for getting a element from inside list often using loops, should be seperated to a function for readability and distinctive variable scope.

- as AI you should
    - implement only asked thing when asked by user.  
        - if you think another function or class or whatever is needed for the thing, you can define it, but keep it blank if not clearly asked.  
            - put TODO comment in those blank function / class / method.
        - be especially careful and follow the rule around:
            - DB accessing. all functions and models, we will implement it in one. SQL accessing code mustn't scattered across project. don't make function outside proper place.
    - do correction for symbol names in wrong naming convention.  
    if it isn't so related to what user asked, just warn it and leave it there for the moment.  
    prompt user to fix it, in another commit for clarity.
