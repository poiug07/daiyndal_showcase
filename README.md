# daiyndal_showcase

Daiyndal is LMS platform with courses focused on preparation of 6th grade students in Kazakhstan to pass entrance exams to Nazarbayev Intellectual Schools.

This is a showcase version of Daiyndal website. I will try to keep this repository up to date, but the original production code is hidden for obvious reasons. You can try visiting [daiyndal.kz](https://daiyndal.kz), if it is not running then it is probably under maintenance or shut down for other reasons.

This repo is forced to run on local machine, but I included Nginx and Gunicorn setting files in repo.

Project tree should look like this:

```
.
├── 
├── env
├── daiyndal_project
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── daiyndal_project.sock
├── manage.py
├── myapp
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── static
│   │   ├── bootstrap
│   │   ├── css
│   │   ├── favicon.ico
│   │   ├── fonts
│   │   └── img
│   ├── templates
│   │   ├── 404.html
│   │   ├── base.html
│   │   └── myapp
│   │       ├── about.html
│   │       ├── course_detail.html
│   │       ├── course_ended.html
│   │       ├── course_list.html
│   │       ├── index.html
│   │       ├── login.html
│   │       ├── mycourse_list.html
│   │       ├── notes.md
│   │       ├── partials
│   │       │   ├── base-footer.html
│   │       │   └── navbar-step.html
│   │       ├── password_reset_complete.html
│   │       ├── password_reset_confirm.html
│   │       ├── password_reset_done.html
│   │       ├── password_reset_email.txt
│   │       ├── password_reset.html
│   │       ├── profile.html
│   │       ├── registration-continued.html
│   │       ├── registration.html
│   │       ├── step.html
│   │       └── step-test.html
│   ├── urls.py
│   └── views.py
└── static
```

