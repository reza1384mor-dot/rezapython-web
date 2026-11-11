"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# تغییر عناوین پیش‌فرض پنل ادمین جنگو جهت امنیت و اختصاصی‌سازی
admin.site.site_header = "سامانه مدیریت پورتفولیو رضا مرتضوی"
admin.site.site_title = "پیش‌خوان مدیریت اختصاصی"
admin.site.index_title = "پنل دسترسی ادمین"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
