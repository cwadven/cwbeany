# Beany TECH BLOG

<br>

|                                                         cwbeany                                                          |
|:------------------------------------------------------------------------------------------------------------------------:|
| <img src="https://github.com/cwadven/cwbeany/blob/master/docs/logos/main_logo.webp?raw=true" width="200" alt="cwbeany" /> |
|                                                        **서비스 주소**                                                        |
|                                                   https://cwbeany.com                                                    |
|                                                     **서비스 개발 히스토리**                                                      |
|                      https://indigo-icicle-78e.notion.site/Django-9311506bbf8b4ccb97012a2114cc52fa                       |

## Purpose Of Project

[edit . 2021-10-19]

▶ Django 지식 고도화 및 TECH 블로그 관리를 위해서 개발 계획

<br>

## Project Introduce

[edit . 2021-10-19]

▶ 내가 공부한 지식 및 꿀팁을 보관해 놓을 창고 역할을 하기 위한 목적
<br>
▶ 지속적으로 습득한 지식을 이용해 보다 나은 모습으로 가꾸기 위한 목적

<br>

## Project Duration

[edit . 2021-10-19]

▶ 2021-03-16 ~ 2021-03-21 : 첫 배포 완성
<br>
▶ 2021-03-21 ~ : 유지보수

<br>

## Technologies Used

[edit . 2021-10-19]

![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

<br>

## Deploy

[edit . 2024-09-16]

![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

<br>

## CI/CD

[edit . 2021-12-18]

![GitHub Actions](https://img.shields.io/badge/githubactions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

<br>

## Developer Information

[edit . 2021-10-19]

<br>

#### Developer

##### 👨‍🦱 이창우 (Lee Chang Woo)

- Github : https://github.com/cwadven

<br>

## Project Structure

[edit . 2021-10-19]

```
Project Root
├── 📂 config
│    ├── 📜 settings.py
│    ├── 🔒 PRIVATE_SETTING.py
│    ├── 📜 asgi.py
│    ├── 📜 urls.py
│    └── 📜 wsgi.py
│
├── 📂 App Name
│    ├── 📂 migrations                                                      
│    ├── 📜 admin.py                                
│    ├── 📜 app.py
│    ├── 📜 forms.py
│    ├── 📜 tests.py
│    ├── 📜 urls.py
│    ├── 📜 views.py
│    └── 📜 modles.py                                     
│
├── 📂 App Name
│    ├── 📂 migrations                                     
│    ├── 📜 admin.py                                  
│    ├── 📜 app.py
│    ├── 📜 forms.py
│    ├── 📜 tests.py
│    ├── 📜 urls.py
│    ├── 📜 views.py
│    └── 📜 modles.py  
│  
├── 📂 App Name
│    ├── 📂 migrations                                     
│    ├── 📜 admin.py                                  
│    ├── 📜 app.py
│    ├── 📜 forms.py
│    └ .....
│
├── 📂 temp_static
│    ├── 🖼 XXXXX.png                                     
│    ├── 🖼 XXXXX.png                                  
│    ├── 🖼 XXXXX.png
│    ├── 🖼 XXXXX.png
│    └ .....
│
├── 📂 templates
│    └── base.html    
│
├── 🗑 .gitignore                                        # gitignore
├── 🗑 requirements.txt                                  # requirements.txt
└── 📋 README.md                                        # Readme
```

<br>

## Database Structure

[edit . 2024-05-04]

![img.png](https://github.com/cwadven/cwbeany/blob/master/docs/erd/erd.png?raw=true)


## Django Command

```shell
python manage.py crontab add
```


## Celery Command

```shell
celery -A config worker -l INFO -P solo
```