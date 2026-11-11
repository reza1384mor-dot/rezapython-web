from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # Public Website & Articles
    path("", views.home_view, name="home"),
    path("articles/", views.articles_list_view, name="articles_list"),
    path("articles/<str:slug>/", views.article_detail_view, name="article_detail"),
    path("robots.txt", views.robots_txt_view, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml_view, name="sitemap_xml"),

    # Auth
    path("panel/login/", views.panel_login_view, name="panel_login"),
    path("panel/logout/", views.panel_logout_view, name="panel_logout"),

    # Management Panel - Settings & Projects
    path("panel/", views.panel_home_view, name="panel_home"),
    path("panel/update/", views.panel_update_settings_view, name="panel_update_settings"),
    path("panel/projects/", views.panel_projects_view, name="panel_projects"),
    path("panel/projects/add/", views.panel_project_create_view, name="panel_project_create"),
    path("panel/projects/<int:pk>/edit/", views.panel_project_edit_view, name="panel_project_edit"),
    path("panel/projects/<int:pk>/delete/", views.panel_project_delete_view, name="panel_project_delete"),
    path("panel/messages/<int:pk>/toggle/", views.panel_toggle_message_read, name="panel_toggle_message"),

    # Management Panel - Articles Publishing & Editing
    path("panel/articles/", views.panel_articles_view, name="panel_articles"),
    path("panel/articles/add/", views.panel_article_create_view, name="panel_article_create"),
    path("panel/articles/<int:pk>/edit/", views.panel_article_edit_view, name="panel_article_edit"),
    path("panel/articles/<int:pk>/delete/", views.panel_article_delete_view, name="panel_article_delete"),
    path("panel/articles/<int:pk>/toggle-publish/", views.panel_article_toggle_publish, name="panel_article_toggle_publish"),
]
