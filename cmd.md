```bash
pip install django-import-export
pip install django-simpleui -i https://pypi.tuna.tsinghua.edu.cn/simple
```

```bash
django-admin startproject mysite django-server
python manage.py startapp smart_class

python manage.py runserver 0.0.0.0:8080

```

```python
# setting.py

INSTALLED_APPS = [
    'simpleui',
    'import_export',
    "smart_class.apps.SmartClassConfig",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "smart_class2",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}

LANGUAGE_CODE = 'zh-hans'

USE_I18N = True

TIME_ZONE = 'Asia/Shanghai'

USE_TZ = False


# 隐藏右侧SimpleUI广告链接和使用分析
SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_LOGO = '/static/image/logo.png'

IMPORT_EXPORT_USE_TRANSACTIONS = True
```


```bash
python manage.py makemigrations
python manage.py migrate

```


```bash
python manage.py createsuperuser
python manage.py runserver
# http://127.0.0.1:8000/admin/ 
```


