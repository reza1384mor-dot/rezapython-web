from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import SiteSettings, Project, ContactMessage, Article

class ContactMessageForm(forms.ModelForm):
    """
    فرم اعتبارسنجی جامع سمت سرور برای فرم ارتباط آنلاین
    دارای فیلد مخفی هانی‌پات (website) جهت شناسایی و مسدودسازی خودکار ربات‌های اسپمر
    """
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("نام وارد شده باید حداقل ۲ کاراکتر باشد.")
        if len(name) > 120:
            raise forms.ValidationError("طول نام بیش از حد مجاز است.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email or '@' not in email:
            raise forms.ValidationError("فرمت آدرس ایمیل نامعتبر است.")
        return email

    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '').strip()
        if len(subject) > 200:
            raise forms.ValidationError("طول موضوع پیام بیش از حد مجاز است.")
        return subject

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 5:
            raise forms.ValidationError("متن پیام باید حداقل ۵ کاراکتر باشد.")
        if len(message) > 5000:
            raise forms.ValidationError("متن پیام بیش از حد طولانی است (حداکثر ۵۰۰۰ کاراکتر).")
        return message

    def clean(self):
        cleaned_data = super().clean()
        honeypot = cleaned_data.get('website')
        if honeypot:
            # ربات فیلد مخفی را پر کرده است
            raise forms.ValidationError("ارسال هرزنامه شناسایی شد.")
        return cleaned_data


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'full_name',
            'hero_badge',
            'role_title',
            'bio',
            'about_cs',
            'about_backend',
            'about_security',
            'email',
            'telegram_id',
            'telegram_bot_username',
            'telegram_channel_title',
            'telegram_channel_desc',
            'telegram_channel_status',
            'telegram_channel_url',
            'github_url',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'نام و نام خانوادگی'}),
            'hero_badge': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'نشان متنی بالای هدر'}),
            'role_title': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'عنوان تخصصی'}),
            'bio': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3, 'placeholder': 'خلاصه بیو'}),
            'about_cs': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3}),
            'about_backend': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3}),
            'about_security': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'panel-input', 'dir': 'ltr'}),
            'telegram_id': forms.TextInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'reza1384mor'}),
            'telegram_bot_username': forms.TextInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'Rezapython_bot'}),
            'telegram_channel_title': forms.TextInput(attrs={'class': 'panel-input'}),
            'telegram_channel_desc': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 2}),
            'telegram_channel_status': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'به‌زودی'}),
            'telegram_channel_url': forms.URLInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'https://t.me/yourchannel'}),
            'github_url': forms.URLInput(attrs={'class': 'panel-input', 'dir': 'ltr'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tech_stack', 'github_url', 'live_url', 'icon', 'featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'عنوان پروژه'}),
            'description': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3, 'placeholder': 'توضیحات مختصر درباره پروژه'}),
            'tech_stack': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'مثلاً: Python, Django, PostgreSQL, Docker'}),
            'github_url': forms.URLInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'https://github.com/...'}),
            'live_url': forms.URLInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'https://...'}),
            'icon': forms.TextInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'fa-solid fa-code'}),
            'featured': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
        }


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'panel-input',
            'placeholder': 'نام کاربری ادمین',
            'autofocus': True,
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'panel-input',
            'placeholder': 'رمز عبور',
            'autocomplete': 'current-password',
        })
    )


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title',
            'slug',
            'category',
            'reading_time',
            'icon',
            'poster',
            'poster_url',
            'tags',
            'summary',
            'content',
            'published',
            'featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'عنوان جذاب و تخصصی مقاله'}),
            'slug': forms.TextInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'نامک دلخواه انگلیسی یا فارسی (اختیاری - خودکار تولید می‌شود)'}),
            'category': forms.Select(attrs={'class': 'panel-input panel-select'}),
            'reading_time': forms.NumberInput(attrs={'class': 'panel-input', 'min': 1, 'max': 120, 'placeholder': 'مثلاً: ۵'}),
            'icon': forms.TextInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'fa-solid fa-file-code'}),
            'poster': forms.FileInput(attrs={'class': 'panel-input panel-file-input', 'accept': 'image/*'}),
            'poster_url': forms.URLInput(attrs={'class': 'panel-input', 'dir': 'ltr', 'placeholder': 'https://... یا خالی بگذارید'}),
            'tags': forms.TextInput(attrs={'class': 'panel-input', 'placeholder': 'مثلاً: پایتون, جنگو, امنیت, بهینه‌سازی'}),
            'summary': forms.Textarea(attrs={'class': 'panel-textarea', 'rows': 3, 'placeholder': 'چکیده و خلاصه کوتاه مقاله جهت نمایش در کارت‌های صفحه اصلی و آرشیو...'}),
            'content': forms.Textarea(attrs={'class': 'panel-textarea content-editor', 'rows': 16, 'placeholder': 'متن کامل مقاله (پشتیبانی کامل از مارک‌داون، کدهای پایتون با سه بک‌تیک، لیست‌ها و تیترها)...'}),
            'published': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
            'featured': forms.CheckboxInput(attrs={'class': 'panel-checkbox'}),
        }

