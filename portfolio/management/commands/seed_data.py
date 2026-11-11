from django.core.management.base import BaseCommand
from portfolio.models import SkillCategory, Skill, Project, Article

class Command(BaseCommand):
    help = "Seed initial skills and projects for Reza Mortazavi portfolio"

    def handle(self, *args, **options):
        # 1. Categories & Skills
        cat1, _ = SkillCategory.objects.get_or_create(
            name="پایتون و بک‌اند",
            defaults={"icon": "fa-solid fa-server", "order": 1}
        )
        skills_cat1 = [
            ("Python 3.x", "fa-brands fa-python", 1),
            ("Django & DRF", "fa-solid fa-cubes", 2),
            ("PostgreSQL / SQLite", "fa-solid fa-database", 3),
            ("RESTful APIs", "fa-solid fa-network-wired", 4),
            ("Web Scraping & Automation", "fa-solid fa-gears", 5),
        ]
        for name, icon, order in skills_cat1:
            Skill.objects.get_or_create(category=cat1, name=name, defaults={"icon": icon, "order": order})

        cat2, _ = SkillCategory.objects.get_or_create(
            name="امنیت شبکه و سیستم",
            defaults={"icon": "fa-solid fa-user-shield", "order": 2}
        )
        skills_cat2 = [
            ("مبانی Network Security", "fa-solid fa-shield", 1),
            ("Linux OS & Bash", "fa-brands fa-linux", 2),
            ("استانداردهای امنیتی وب", "fa-solid fa-lock", 3),
            ("مفاهیم پکت و پروتکل‌های شبکه", "fa-solid fa-diagram-project", 4),
            ("تحلیل و تست آسیب‌پذیری وب", "fa-solid fa-bug", 5),
        ]
        for name, icon, order in skills_cat2:
            Skill.objects.get_or_create(category=cat2, name=name, defaults={"icon": icon, "order": order})

        cat3, _ = SkillCategory.objects.get_or_create(
            name="طراحی وب و ابزارهای توسعه",
            defaults={"icon": "fa-solid fa-code", "order": 3}
        )
        skills_cat3 = [
            ("HTML5 / CSS3", "fa-brands fa-html5", 1),
            ("JavaScript", "fa-brands fa-js", 2),
            ("طراحی ریسپانسیو مدرن", "fa-solid fa-mobile-screen", 3),
            ("Git & GitHub", "fa-brands fa-git-alt", 4),
            ("Command Line & DevTools", "fa-solid fa-terminal", 5),
        ]
        for name, icon, order in skills_cat3:
            Skill.objects.get_or_create(category=cat3, name=name, defaults={"icon": icon, "order": order})

        # 2. Projects
        projects_data = [
            {
                "title": "سامانه وب با فریم‌ورک جنگو (Django Web Application)",
                "description": "معماری ماژولار با پنل اختصاصی، احراز هویت ایمن، اعتبارسنجی فرم‌ها و پایگاه‌داده بهینه‌سازی شده.",
                "tech_stack": "Python, Django, PostgreSQL, HTML5, CSS3",
                "github_url": "https://github.com/reza1384mor-dot",
                "icon": "fa-solid fa-cubes",
            },
            {
                "title": "اسکریپت آنالیز پورت و امنیت شبکه (NetSec Scanner)",
                "description": "اسکنر هوشمند با سوکت‌های پایتون برای بررسی وضعیت پورت‌های باز، تشخیص سرویس‌ها و هشدارهای امنیتی.",
                "tech_stack": "Python, Sockets, Network Protocol, Security",
                "github_url": "https://github.com/reza1384mor-dot",
                "icon": "fa-solid fa-shield-virus",
            },
            {
                "title": "ربات اتوماسیون تلگرام با پایتون",
                "description": "توسعه بات تعاملی تلگرام برای خدمات خودکار، پردازش درخواست‌های کاربران و اتصال به وب‌هوک و API.",
                "tech_stack": "Python, Telegram Bot API, AsyncIO",
                "github_url": "https://github.com/reza1384mor-dot",
                "live_url": "https://t.me/reza1384mor",
                "icon": "fa-solid fa-robot",
            },
        ]
        for p in projects_data:
            Project.objects.get_or_create(title=p["title"], defaults=p)

        # 3. Sample Articles
        articles_data = [
            {
                "title": "معماری تمیز در جنگو و الگوهای پیشرفته بهینه‌سازی کوئری‌های ORM",
                "slug": "django-clean-architecture-orm-optimization",
                "summary": "بررسی روش‌های استاندارد پیاده‌سازی لایه‌های سرویس، حل مشکل بحرانی N+1 Query با select_related و prefetch_related، و افزایش سرعت پاسخ‌دهی سرور.",
                "category": "python",
                "reading_time": 6,
                "icon": "fa-brands fa-python",
                "tags": "پایتون, جنگو, ORM, بهینه‌سازی, معماری تمیز",
                "published": True,
                "featured": True,
                "content": """## مقدمه: چرا معماری تمیز در پروژه‌های بزرگ حیاتی است؟

در توسعه سامانه‌های وب با **Django**، معمولاً با گسترش دامنه پروژه، حجم منطق تجاری (Business Logic) درون `views.py` یا `models.py` به شدت افزایش می‌یابد که به پدیده *Fat Views / Fat Models* منجر می‌شود. 

برای ساخت سیستم‌هایی که نگهداری، تست و مقیاس‌پذیری بالایی داشته باشند، پیاده‌سازی معماری لایه‌ای و تمیز ضروری است.

---

### ۱. حل معضل خطرناک N+1 Queries در ORM

یکی از متداول‌ترین اشتباهات در بک‌اند جنگو، فراخوانی روابط کلید خارجی در حلقه‌ها بدون پیش‌بارگذاری است:

```python
# روش ناکارآمد (تولید ده‌ها کوئری مجزا به دیتابیس):
projects = Project.objects.all()
for p in projects:
    print(p.category.name)

# روش بهینه با یکپارچه‌سازی در سطح SQL (فقط یک کوئری JOIN):
projects = Project.objects.select_related('category').all()
for p in projects:
    print(p.category.name)
```

استفاده از `select_related` برای کلیدهای خارجی تک‌مقداری و `prefetch_related` برای روابط چندبه‌چند (ManyToMany) بار پردازشی دیتابیس را تا **۸۰ درصد** کاهش می‌دهد.

---

### ۲. الگوهای لایه سرویس (Service Layer Pattern)

جداسازی منطق بیزینس از Controller/View باعث می‌شود بتوان منطق را به‌طور مجزا در تست‌های واحد (Unit Tests) سنجید یا در سناریوهای مختلف (API، پنل ادمین، کامندهای CLI و ربات تلگرام) استفاده مجدد کرد:

```python
# services/project_service.py
class ProjectService:
    @staticmethod
    def create_featured_project(title, tech_stack, github_url):
        # اعتبارسنجی‌های تخصصی دامنه
        return Project.objects.create(
            title=title,
            tech_stack=tech_stack,
            github_url=github_url,
            featured=True
        )
```

---

### نتیجه‌گیری
معماری استاندارد نه تنها کیفیت کدهای پایتون را تضمین می‌کند، بلکه سرعت اجرای وب‌سایت در پروداکشن را به شکل چشم‌گیری ارتقا می‌دهد."""
            },
            {
                "title": "راهنمای جامع امنیت سرورهای لینوکس و مقابله با آسیب‌پذیری‌های برتر وب",
                "slug": "linux-server-security-and-web-vulnerabilities",
                "summary": "مرور عملیاتی پیکربندی فایروال UFW، ایمن‌سازی سرویس SSH، مسدودسازی اسکنرهای خودکار با Fail2ban و محافظت از وب‌سرویس Nginx در برابر حملات متداول.",
                "category": "security",
                "reading_time": 8,
                "icon": "fa-solid fa-shield-halved",
                "tags": "امنیت شبکه, لینوکس, OWASP, فایروال, Nginx",
                "published": True,
                "featured": True,
                "content": """## مقدمه: اصل دفاع در عمق (Defense in Depth)

امنیت در سرورهای لینوکس یک وضعیت نقطه‌ای نیست، بلکه فرآیندی پیوسته بر پایه مفهوم **دفاع لایه‌به‌لایه** است. اگر یک لایه با شکست مواجه شود، لایه‌های بعدی باید مانع نفوذ یا دسترسی غیرمجاز شوند.

---

### ۱. ایمن‌سازی لایه دسترسی OpenSSH

اولین گام برای هر سرور خام اوبونتو یا دبیان، سخت‌سازی سرویس SSH است:

```bash
# ویرایش فایل تنظیمات امنیتی SSH:
# /etc/ssh/sshd_config.d/security.conf

PermitRootLogin prohibit-password
PasswordAuthentication no
MaxAuthTries 3
LoginGraceTime 30s
MaxStartups 10:30:100
```

> **نکته امنیتی:** استفاده از کلید‌های رمزنگاری نامتقارن (Ed25519 یا RSA 4096-bit) به جای رمزهای عبور سنتی، احتمال حملات Brute-Force را عملاً به صفر می‌رساند.

---

### ۲. سپر دفاعی در وب‌سرور Nginx

مخفی‌سازی مشخصات وب‌سرور و مسدودسازی آنی اسکنرهای فایل‌های حساس (`.env`، `.git`، بکاپ‌ها):

```nginx
# مسدودسازی دسترسی به تمام فایل‌های پنهان و محیطی
location ~ /\\.(?!well-known).* {
    deny all;
    access_log off;
    log_not_found off;
    return 404;
}

# مخفی‌سازی شماره نسخه وب‌سرور
server_tokens off;
```

---

### ۳. محافظت در برابر هدرهای مخرب (Host Injection & Clickjacking)

با افزودن هدرهای مدرن OWASP می‌توان آسیب‌پذیری‌های متداول کلاینت را به طور کامل مهار نمود:
- `X-Frame-Options: DENY` (جلوگیری از Clickjacking)
- `X-Content-Type-Options: nosniff` (جلوگیری از MIME Sniffing)
- `Content-Security-Policy (CSP)` (کنترل منابع لود شده)

---

### نتیجه‌گیری
پیکربندی هوشمندانه و اصولی سرویس‌ها روی لینوکس، بهترین تضمین برای پایداری ۲۴ ساعته پروژه‌های ابری است."""
            },
            {
                "title": "تحلیل پیچیدگی زمانی و بهینه‌سازی ساختارهای داده در پایتون ۳",
                "slug": "time-complexity-and-data-structures-in-python",
                "summary": "بررسی تفاوت‌های مصرف حافظه و سرعت پردازش میان List، Dict، Set و Generatorها به همراه تحلیل نماد Big-O در الگوریتم‌های پرکاربرد.",
                "category": "cs",
                "reading_time": 5,
                "icon": "fa-solid fa-graduation-cap",
                "tags": "علوم کامپیوتر, الگوریتم, Big-O, پایتون, بهینه‌سازی",
                "published": True,
                "featured": True,
                "content": """## مقدمه: چرا نماد Big-O اهمیت دارد؟

در علوم کامپیوتر، نماد بزرگ O (Big-O Notation) معیاری برای سنجش مقیاس‌پذیری یک الگوریتم با رشد حجم ورودی است. در پایتون، انتخاب ساختار داده نادرست می‌تواند زمان اجرای یک عملیات را از میلی‌ثانیه به چندین دقیقه افزایش دهد!

---

### مقایسه عملکرد جستجو: List در برابر Set / Dict

جستجو در یک لیست به صورت خطی انجام می‌شود، در حالی که در `set` و `dict` به واسطه جداول درهم‌سازی (Hash Tables) میانگین زمان اجرا ثابت است:

```python
# زمان O(n) - با افزایش طول لیست زمان دو برابر می‌شود:
if target in large_list:
    pass

# زمان O(1) - تقریباً مستقل از تعداد اعضا:
target_set = set(large_list)
if target in target_set:
    pass
```

---

### صرفه‌جویی در رم با ژنراتورها (Generators)

اگر نیازی به بارگذاری همزمان تمام عناصر در حافظه RAM ندارید، استفاده از Expressions و Generators مصرف رم را از چند گیگابایت به چند کیلوبایت تقلیل می‌دهد:

```python
# تولید لیست در حافظه (مصرف زیاد رم):
squares = [x ** 2 for x in range(10_000_000)]

# تولید در لحظه (Lazy Evaluation با ژنراتور):
squares_gen = (x ** 2 for x in range(10_000_000))
```

---

### جمع‌بندی
درک مبانی نظری ساختمان داده‌ها و پیچیدگی الگوریتم‌ها زیربنای نگارش کدهای پرسرعت و بهینه‌سازی مصرف سرور است."""
            }
        ]

        for art in articles_data:
            Article.objects.get_or_create(slug=art["slug"], defaults=art)

        self.stdout.write(self.style.SUCCESS("Successfully seeded initial data and articles!"))
