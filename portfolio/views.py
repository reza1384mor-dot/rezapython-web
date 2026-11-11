import os
import sys
import json
from django.conf import settings as django_settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q, F

from .models import SiteSettings, SkillCategory, Skill, Project, ContactMessage, Article
from .forms import SiteSettingsForm, ProjectForm, CustomLoginForm, ContactMessageForm, ArticleForm
from .ratelimit import get_client_ip, is_rate_limited, reset_rate_limit

def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ==========================================
# Public Views
# ==========================================
def home_view(request):
    settings = SiteSettings.get_settings()

    if request.method == "POST":
        client_ip = get_client_ip(request)
        # محدودسازی نرخ ارسال فرم تماس: حداکثر ۳ پیام در هر ۵ دقیقه به ازای هر IP
        if is_rate_limited(f"contact_ip_{client_ip}", max_attempts=3, window_seconds=300):
            messages.error(request, "تعداد پیام‌های ارسالی شما بیش از حد مجاز است. لطفاً ۵ دقیقه دیگر مجدداً تلاش نمایید.")
            return redirect('/#contact')

        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()

            # ارسال فوری اعلان به ربات تلگرام با متن ایمن‌شده
            try:
                from .telegram_bot import send_telegram_contact_notification
                send_telegram_contact_notification(
                    name=contact_msg.name,
                    email=contact_msg.email,
                    subject=contact_msg.subject,
                    message=contact_msg.message
                )
            except Exception:
                pass

            messages.success(request, "پیام شما با موفقیت ثبت شد و به ربات تلگرام ارسال گردید!")
            return redirect('/#contact')
        else:
            first_err = "خطایی در اعتبارسنجی اطلاعات رخ داد."
            for field, errors in form.errors.items():
                if errors:
                    first_err = errors[0]
                    break
            messages.error(request, f"خطا: {first_err}")
            return redirect('/#contact')

    categories = SkillCategory.objects.prefetch_related('skills').all()
    projects = Project.objects.filter(featured=True)
    latest_articles = Article.objects.filter(published=True).order_by('-featured', '-created_at')[:3]

    context = {
        'settings': settings,
        'categories': categories,
        'projects': projects,
        'latest_articles': latest_articles,
    }
    return render(request, "index.html", context)


def articles_list_view(request):
    """صفحه آرشیو و وبلاگ مقالات (Public Articles List)"""
    settings = SiteSettings.get_settings()
    articles = Article.objects.filter(published=True)

    query = request.GET.get('q', '').strip()
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )

    selected_cat = request.GET.get('cat', '').strip()
    if selected_cat and selected_cat != 'all':
        articles = articles.filter(category=selected_cat)

    categories = Article.CATEGORY_CHOICES

    context = {
        'settings': settings,
        'articles': articles,
        'categories': categories,
        'selected_cat': selected_cat or 'all',
        'search_query': query,
        'total_count': articles.count(),
    }
    return render(request, "articles/list.html", context)


def article_detail_view(request, slug):
    """صفحه مطالعه کامل مقاله (Article Reading View)"""
    settings = SiteSettings.get_settings()
    # اگر کاربر ادمین باشد می‌تواند پیش‌نویس‌ها را نیز مشاهده کند
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        article = get_object_or_404(Article, slug=slug)
    else:
        article = get_object_or_404(Article, slug=slug, published=True)

    # ثبت بازدید
    Article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
    article.refresh_from_db(fields=['views_count'])

    # مقالات مرتبط
    related = Article.objects.filter(published=True).exclude(pk=article.pk)
    cat_related = list(related.filter(category=article.category)[:2])
    if len(cat_related) < 2:
        needed = 2 - len(cat_related)
        extra = list(related.exclude(id__in=[a.id for a in cat_related])[:needed])
        related_articles = cat_related + extra
    else:
        related_articles = cat_related

    # تولید اسکیما ساخت‌یافته JSON-LD (SEO & GEO)
    json_ld_schema = ""
    try:
        from .schema_generator import generate_article_schema, extract_faqs_from_markdown
        art_dict = {
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "tags": article.tags,
            "created_at": article.created_at.isoformat() if article.created_at else "",
        }
        faqs = extract_faqs_from_markdown(article.content)
        schema_dict = generate_article_schema(art_dict, faqs)
        json_ld_schema = json.dumps(schema_dict, ensure_ascii=False, indent=2)
    except Exception:
        json_ld_schema = ""

    context = {
        'settings': settings,
        'article': article,
        'rendered_content': article.get_rendered_content(),
        'related_articles': related_articles,
        'tags': article.get_tags_list(),
        'json_ld_schema': json_ld_schema,
    }
    return render(request, "articles/detail.html", context)


def robots_txt_view(request):
    """خروجی استاندارد robots.txt برای موتورهای جستجو و هوش مصنوعی (Agent 8 SEO/GEO)"""
    robots_path = os.path.join(django_settings.BASE_DIR, "robots.txt")
    if os.path.exists(robots_path):
        with open(robots_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "User-agent: *\nAllow: /\nSitemap: https://rezapython.ir/sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def sitemap_xml_view(request):
    """نقشه سایت XML خودکار برای کرولرها و موتورهای جستجو (Agent 8 SEO/GEO)"""
    sitemap_path = os.path.join(django_settings.BASE_DIR, "sitemap.xml")
    if os.path.exists(sitemap_path):
        with open(sitemap_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>'
    return HttpResponse(content, content_type="application/xml; charset=utf-8")


# ==========================================
# Authentication & Anti-Brute-Force
# ==========================================
def panel_login_view(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('portfolio:panel_home')

    client_ip = get_client_ip(request)
    login_rl_key = f"login_fail_{client_ip}"

    if request.method == "POST":
        # ضد حملات Brute-Force: مسدودسازی موقت پس از ۵ تلاش ناموفق در ۵ دقیقه
        if is_rate_limited(login_rl_key, max_attempts=5, window_seconds=300):
            messages.error(request, "تعداد دفعات ورود اشتباه بیش از حد مجاز است. لطفاً ۵ دقیقه دیگر مجدداً تلاش نمایید.")
            return render(request, "dashboard/login.html", {'form': CustomLoginForm()})

        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                reset_rate_limit(login_rl_key)
                login(request, user)
                messages.success(request, f"خوش آمدید، {user.username} عزیز!")

                # جلوگیری از آسیب‌پذیری Open Redirect (تایید سلامت آدرس مقصد)
                next_url = request.GET.get('next', '')
                if not next_url or not url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                ):
                    next_url = 'portfolio:panel_home'
                return redirect(next_url)
            else:
                messages.error(request, "حساب شما دسترسی لازم به پنل مدیریت را ندارد.")
        else:
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
    else:
        form = CustomLoginForm()

    return render(request, "dashboard/login.html", {'form': form})


def panel_logout_view(request):
    logout(request)
    messages.info(request, "با موفقیت از پنل خارج شدید.")
    return redirect('portfolio:panel_login')


# ==========================================
# Custom Panel (Dashboard)
# ==========================================
@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_home_view(request):
    stats = {
        'total_messages': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.count(),
        'total_articles': Article.objects.count(),
    }
    recent_messages = ContactMessage.objects.all()[:8]
    recent_articles = Article.objects.all()[:5]
    settings = SiteSettings.get_settings()

    return render(request, "dashboard/index.html", {
        'stats': stats,
        'recent_messages': recent_messages,
        'recent_articles': recent_articles,
        'settings': settings,
    })


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_update_settings_view(request):
    """صفحه آپدیت و تنظیمات اطلاعات وب‌سایت"""
    settings = SiteSettings.get_settings()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات وب‌سایت با موفقیت آپدیت و ذخیره شد!")
            return redirect('portfolio:panel_update_settings')
        else:
            messages.error(request, "خطایی در اعتبارسنجی فرم رخ داد. لطفاً فیلدها را بررسی نمایید.")
    else:
        form = SiteSettingsForm(instance=settings)

    return render(request, "dashboard/update_site.html", {
        'form': form,
        'settings': settings,
    })


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_projects_view(request):
    projects = Project.objects.all()
    return render(request, "dashboard/projects.html", {'projects': projects})


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_project_create_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پروژه جدید با موفقیت اضافه شد!")
            return redirect('portfolio:panel_projects')
    else:
        form = ProjectForm()

    return render(request, "dashboard/project_form.html", {'form': form, 'title': 'افزودن پروژه جدید'})


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "پروژه با موفقیت به‌روزرسانی شد!")
            return redirect('portfolio:panel_projects')
    else:
        form = ProjectForm(instance=project)

    return render(request, "dashboard/project_form.html", {'form': form, 'title': f'ویرایش پروژه: {project.title}'})


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, "پروژه مورد نظر حذف گردید.")
        return redirect('portfolio:panel_projects')

    return render(request, "dashboard/project_confirm_delete.html", {'project': project})


@require_POST
@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_toggle_message_read(request, pk):
    """تغییر وضعیت خوانده‌شدن پیام صرفاً از طریق متد امن POST با محافظت توکن CSRF"""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save()
    messages.info(request, f"وضعیت پیام {msg.name} تغییر کرد.")
    return redirect('portfolio:panel_home')


# ==========================================
# Panel Articles Management & Publishing
# ==========================================
@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_articles_view(request):
    """لیست و مدیریت کلیه مقالات در پنل"""
    articles = Article.objects.all()
    return render(request, "dashboard/articles.html", {'articles': articles})


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_article_create_view(request):
    """صفحه اختصاصی انتشار مقاله جدید (Publish Article Page)"""
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            messages.success(request, f"مقاله «{article.title}» با موفقیت منتشر و ذخیره شد!")
            return redirect('portfolio:panel_articles')
        else:
            messages.error(request, "خطایی در اعتبارسنجی فیلدهای مقاله رخ داد.")
    else:
        form = ArticleForm()

    return render(request, "dashboard/article_form.html", {
        'form': form,
        'title': 'انتشار مقاله جدید',
        'is_new': True,
    })


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_article_edit_view(request, pk):
    """ویرایش مقاله ثبت‌شده"""
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f"مقاله «{article.title}» با موفقیت ویرایش شد!")
            return redirect('portfolio:panel_articles')
        else:
            messages.error(request, "خطایی در ذخیره تغییرات مقاله رخ داد.")
    else:
        form = ArticleForm(instance=article)

    return render(request, "dashboard/article_form.html", {
        'form': form,
        'title': f'ویرایش مقاله: {article.title}',
        'article': article,
        'is_new': False,
    })


@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_article_delete_view(request, pk):
    """حذف مقاله با صفحه تایید"""
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        messages.success(request, f"مقاله «{article.title}» با موفقیت حذف گردید.")
        return redirect('portfolio:panel_articles')

    return render(request, "dashboard/article_confirm_delete.html", {'article': article})


@require_POST
@user_passes_test(is_admin_user, login_url='/panel/login/')
def panel_article_toggle_publish(request, pk):
    """تغییر سریع وضعیت انتشار مقاله (منتشر شده / پیش‌نویس)"""
    article = get_object_or_404(Article, pk=pk)
    article.published = not article.published
    article.save(update_fields=['published'])
    status_str = "منتشر شد" if article.published else "به حالت پیش‌نویس درآمد"
    messages.info(request, f"وضعیت مقاله «{article.title}» تغییر کرد: {status_str}.")
    return redirect('portfolio:panel_articles')

