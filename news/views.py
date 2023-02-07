from django.shortcuts import render, reverse, redirect
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import *
from .filters import NewsFilter
from .forms import NewsForm

class NewsList(ListView):
  model = Post
  template_name = 'news.html'
  context_object_name = 'news'
  paginate_by = 10
  form_class = NewsForm

  def get_context_data(self, **kwargs): 
    context = super().get_context_data(**kwargs)
    context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
    return context
    
class NewsSearch(ListView):
  model = Post
  template_name = 'news_filter.html'
  context_object_name = 'news'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
    return context

class NewsDetailView(DetailView):
    template_name = 'news_detail.html'
    queryset = Post.objects.all()


class NewsCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    template_name = 'news_add.html'
    form_class = NewsForm
    
    # Реализация отправки письма подписчикам при создании нового поста в их категории
    def post(self, request, *args, **kwargs):
        form = NewsForm(request.POST)  # поле формы
        post_category_pk = request.POST['postCategory']  # получение первичного ключа категории
        sub_text = request.POST.get('text')  # выдергиваем поле с текстом из БД
        sub_title = request.POST.get('title')  # выдергиваем заголовок из БД
        # через запрос и выдернутый первичный ключ, получаем категорию из БД
        post_category = Category.objects.get(pk=post_category_pk)
        # создаем переменную(список) в котором хранятся все подписчики полученной категории
        subscribers = post_category.subscribers.all()
        # получаем адрес хоста и порта (в нашем случае 127.0.0.1:8000), чтоб в дальнейшем указать его в ссылке
        # в письме, чтоб пользователь мог с письма переходить на наш сайт, на конкретную новость
        host = request.META.get('HTTP_HOST')
    
        # валидатор - чтоб данные в форме были корректно введены, без вредоносного кода от хакеров и прочего
        if form.is_valid():
            news = form.save(commit=False)
            news.save()
    
        # в цикле проходимся по всем подписчикам из списка
        for subscriber in subscribers:
            # (6)
            # html_content = render_to_string(
            #     'news/mail_sender.html', {'user': subscriber, 'text': sub_text[:50], 'post': news, 'title': sub_title, 'host': host})
            # указываем шаблон и переменные для отправки в письме
            html_content = render_to_string(
                'mail.html', {'user': subscriber, 'text': sub_text[:50], 'post': news, 'title': sub_title, 'host': host}
            )
    
            # (7)
            msg = EmailMultiAlternatives(
                # Заголовок письма, тема письма
                subject=f'Здравствуй, {subscriber.username}! Новая статья в вашем любимом разделе!',
                # Наполнение письма
                body=f'{sub_text[:50]}',
                # От кого письмо (должно совпадать с реальным адресом почты)
                from_email='mailForSkillfactory@yandex.ru',
                # Кому отправлять, конкретные адреса рассылки, берем из переменной, либо можно явно прописать
                to=[subscriber.email],
            )
    
            # прописываем html-шаблон как наполнение письма
            msg.attach_alternative(html_content, "text/html")
            # отправляем письмо
            msg.send()
        # возвращаемся на страницу с постами
        return redirect('/news/')


class NewsUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post', )
    template_name = 'news_edit.html'
    form_class = NewsForm

    def get_object(self, **kwargs):
      id = self.kwargs.get('pk')
      return Post.objects.get(pk=id)

class NewsDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('news.delete_post', )
    template_name = 'news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    
# D6
class CategoryList(ListView):
    # указываем модель из которой берем объекты
    model = Category
    # указываем имя шаблона, в котором написан html для отображения объектов модели
    template_name = 'category_list.html'
    # имя переменной, под которым будет передаваться объект в шаблон
    context_object_name = 'categories'


# класс-представление для отображения списка категорий
# унаследован от стандартного представления
class CategoryDetail(DetailView):
    # указываем имя шаблона
    template_name = 'category_subscription.html'
    # указываем модель(таблицу базы данных)
    model = Category

    # для отображения кнопок подписки (если не подписан: кнопка подписки - видима, и наоборот)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # общаемся к содержимому контекста нашего представления
        category_id = self.kwargs.get('pk')  # получаем ИД поста (выдергиваем из нашего объекта из модели Категория)
        # формируем запрос, на выходе получим список имен пользователей subscribers__username, которые находятся
        # в подписчиках данной группы, либо не находятся
        category_subscribers = Category.objects.filter(pk=category_id).values("subscribers__username")
        # Добавляем новую контекстную переменную на нашу страницу, выдает либо правду, либо ложь, в зависимости от
        # нахождения нашего пользователя в группе подписчиков subscribers
        context['is_not_subscribe'] = not category_subscribers.filter(subscribers__username=self.request.user).exists()
        context['is_subscribe'] = category_subscribers.filter(subscribers__username=self.request.user).exists()
        return context


# функция-представление обернутая в декоратор
# для добавления пользователя в список подписчиков
# (5)
@login_required
def add_subscribe(request, **kwargs):
    # получаем первичный ключ выбранной категории
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
    # добавляем в выбранную категорию, в поле "подписчики" пользователя, который авторизован и делает запрос
    Category.objects.get(pk=pk).subscribers.add(request.user)
    # возвращаемся на страницу со списком категорий
    return redirect('/news/categories')


# функция-представление обернутая в декоратор
# для удаления пользователя из списка подписчиков
@login_required
def del_subscribe(request, **kwargs):
    # получаем первичный ключ выбранной категории
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
    # удаляем в выбранной категории, из поля "подписчики" пользователя, который авторизован и делает запрос
    Category.objects.get(pk=pk).subscribers.remove(request.user)
    # возвращаемся на страницу со списком категорий
    return redirect('/news/categories')