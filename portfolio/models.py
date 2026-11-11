from django.db import models

class SiteSettings(models.Model):
    full_name = models.CharField(max_length=150, default="رضا مرتضوی", verbose_name="نام و نام خانوادگی")
    hero_badge = models.CharField(max_length=150, default="دانشجوی علوم کامپیوتر و توسعه‌دهنده فعال", verbose_name="متن نشان بالای هدر")
    role_title = models.CharField(max_length=200, default="توسعه‌دهنده Python & Django | امنیت شبکه و وب", verbose_name="عنوان تخصص و نقش")
    bio = models.TextField(default="مشتاق به معماری تمیز و پایدار، تحلیل و پیشگیری از رخنه‌های امنیتی وب و شبکه، و ساخت وب‌اپلیکیشن‌های پیشرفته با جنگو و پایتون.", verbose_name="متن معرفی کوتاه (هدر)")
    
    about_cs = models.TextField(default="دید عمیق نسبت به ساختمان داده‌ها، طراحی الگوریتم‌ها، نظریه زبان‌ها و محاسبات و سیستم‌های عامل، که پایه و اساس تولید کدهای استاندارد و بهینه‌سازی مصرف حافظه و پردازش است.", verbose_name="توضیحات بخش علوم کامپیوتر")
    about_backend = models.TextField(default="توسعه وب‌سایت‌ها و سامانه‌های دیتابیس‌محور با فریم‌ورک Django، طراحی ساختار ORM بهینه، احراز هویت‌های مطمئن و ایجاد RESTful APIهای ساخت‌یافته.", verbose_name="توضیحات بخش بک‌اند و جنگو")
    about_security = models.TextField(default="بررسی اصول امنیت داده‌ها، تحلیل پکت‌های شبکه، درک پروتکل‌ها، پیشگیری از آسیب‌پذیری‌های وب (CSRF، SQLi، XSS) و پیکربندی امن سرورها.", verbose_name="توضیحات بخش امنیت شبکه")
    
    email = models.EmailField(default="reza1384mor@gmail.com", verbose_name="ایمیل عمومی")
    telegram_id = models.CharField(max_length=100, default="reza1384mor", verbose_name="آیدی تلگرام (بدون @)")
    telegram_bot_username = models.CharField(max_length=100, default="Rezapython_bot", verbose_name="آیدی ربات رسمی تلگرام (بدون @)")
    telegram_channel_title = models.CharField(max_length=100, default="کانال تخصصی تلگرام", verbose_name="عنوان کانال تلگرام")
    telegram_channel_desc = models.TextField(default="آموزش‌ها و تجربیات پایتون، جنگو و امنیت شبکه در این کانال منتشر خواهد شد.", verbose_name="توضیحات کانال تلگرام")
    telegram_channel_status = models.CharField(max_length=50, default="به‌زودی", verbose_name="وضعیت کانال (مثلاً به‌زودی یا فعال)")
    telegram_channel_url = models.URLField(blank=True, null=True, verbose_name="لینک مستقیم کانال تلگرام (اختیاری)")
    github_url = models.URLField(default="https://github.com/reza1384mor-dot", verbose_name="آدرس گیت‌هاب")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    class Meta:
        verbose_name = "تنظیمات و اطلاعات سایت"
        verbose_name_plural = "تنظیمات و اطلاعات سایت"

    def __str__(self):
        return f"اطلاعات سایت ({self.full_name})"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    icon = models.CharField(max_length=50, default="fa-solid fa-code", verbose_name="کلاس آیکون FontAwesome")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی مهارت"
        verbose_name_plural = "دسته‌بندی‌های مهارت"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name="skills", verbose_name="دسته‌بندی")
    name = models.CharField(max_length=100, verbose_name="عنوان مهارت")
    icon = models.CharField(max_length=50, default="fa-solid fa-check", verbose_name="کلاس آیکون FontAwesome")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت‌ها"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان پروژه")
    description = models.TextField(verbose_name="توضیحات پروژه")
    tech_stack = models.CharField(max_length=255, verbose_name="تکنولوژی‌های استفاده شده (با کاما جدا کنید)")
    github_url = models.URLField(blank=True, null=True, verbose_name="لینک گیت‌هاب")
    live_url = models.URLField(blank=True, null=True, verbose_name="لینک پیش‌نمایش آنلاین / تلگرام")
    icon = models.CharField(max_length=50, default="fa-regular fa-folder-open", verbose_name="آیکون پروژه")
    featured = models.BooleanField(default=True, verbose_name="نمایش در صفحه اصلی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "پروژه"
        verbose_name_plural = "پروژه‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [tech.strip() for tech in self.tech_stack.split(",") if tech.strip()]


class ContactMessage(models.Model):
    name = models.CharField(max_length=120, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل فرستنده")
    subject = models.CharField(max_length=200, blank=True, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")

    class Meta:
        verbose_name = "پیام دریافتی"
        verbose_name_plural = "پیام‌های دریافتی"
        ordering = ['-created_at']

    def __str__(self):
        return f"پیام از طرف {self.name} - {self.email}"


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('python', '🐍 پایتون و جنگو'),
        ('security', '🛡️ امنیت شبکه و سیستم'),
        ('cs', '🎓 علوم کامپیوتر و الگوریتم'),
        ('web', '💻 توسعه وب و فرانت‌اند'),
    ]

    title = models.CharField(max_length=250, verbose_name="عنوان مقاله")
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, blank=True, verbose_name="نامک (Slug) در آدرس اینترنتی")
    summary = models.TextField(verbose_name="چکیده و خلاصه مقاله (نمایش در کارت‌ها)")
    content = models.TextField(verbose_name="متن کامل مقاله (پشتیبانی از Markdown و HTML)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='python', verbose_name="دسته‌بندی موضوعی")
    reading_time = models.PositiveIntegerField(default=5, verbose_name="مدت زمان تخمینی مطالعه (دقیقه)")
    icon = models.CharField(max_length=50, default="fa-solid fa-file-lines", verbose_name="کلاس آیکون FontAwesome")
    tags = models.CharField(max_length=250, blank=True, verbose_name="برچسب‌ها (با کاما جدا کنید)")
    published = models.BooleanField(default=True, verbose_name="منتشر شود (نمایش در سایت)")
    featured = models.BooleanField(default=False, verbose_name="مقاله ویژه (نمایش برجسته در صفحه اصلی)")
    views_count = models.PositiveIntegerField(default=0, verbose_name="تعداد بازدیدها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ انتشار")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")

    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات و یادداشت‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = f"article-{uuid.uuid4().hex[:6]}"
            candidate = base_slug
            counter = 1
            while Article.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_tags_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_rendered_content(self):
        try:
            import markdown
            return markdown.markdown(self.content, extensions=['extra', 'nl2br', 'tables', 'fenced_code'])
        except Exception:
            return self.content
