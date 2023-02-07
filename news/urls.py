from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
  path('', NewsList.as_view()),
  # path('<int:pk>', NewsDetail.as_view()),
  path('search/', NewsSearch.as_view()),
  path('<int:pk>/', cache_page(60*10)(NewsDetailView.as_view()), name='news_detail'),
  path('<int:pk>/edit', NewsUpdateView.as_view(), name='news_edit'),
  path('add/', NewsCreateView.as_view(), name='news_add'),
  path('<int:pk>/delete', NewsDeleteView.as_view(), name='news_delete'),
  
  path('categories/', CategoryList.as_view(), name='categories'),
  path('categories/<int:pk>/add_subscribe/', add_subscribe, name='add_subscribe'),
  path('categories/<int:pk>/del_subscribe/', del_subscribe, name='del_subscribe'),
  path('categories/<int:pk>/', CategoryDetail.as_view(), name='category_subscription'),
]