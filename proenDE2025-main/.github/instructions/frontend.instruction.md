---
applyTo: "**.html"
applyTo: "**.jinja"
applyTo: "**.jinja2"
applyTo: "**.css"
applyTo: "**.js"
---

these are rules and policy for frontend side of this project.
- you shouldn't write JavaScript in html. separate those script in different outside files.
- javascript file goes in src/assets/js/  
which will be published with URL: js/
- html form should be completed inside the form element.  
don't manipulate html form using javascript otherwise absolutely needed.
- make use of jinja as possible as.
