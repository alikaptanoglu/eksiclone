from django.http import HttpResponseRedirect

from mainsite.app_models import (
    Title,
    Entry
)
from mainsite.urls import url
from mainsite.views.base_views import ListAndCreateView
from mainsite.views.forms.entry_form import EntryCreateForm
from mainsite.views.view_mixins import (
    UrlMixin,
    PaginatorMixin,
)
from utils.debug import debug
from utils.decorators import order_by, suppress_and_return, confirm_origin, template_switch


@debug
@template_switch
@url(r'^title/(?P<title_text>[a-zA-Z0-9-]+)/$', name='title')
@confirm_origin()
class TitlePage(ListAndCreateView, UrlMixin, PaginatorMixin):
    _template_name = 'mainsite/title/title_page.html'
    context_object_name = 'entries'
    form_class = EntryCreateForm
    success_url = '#'

    def form_valid(self, form):
        data = form.cleaned_data
        Entry.objects.create(**data)
        return HttpResponseRedirect(self.request.get_raw_uri())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['title_text'] = self.title_text
        return kwargs

    @suppress_and_return(Title.DoesNotExist, instead=Title.objects.none())
    @order_by('points', default='date')
    def get_queryset(self):
        title = Title.from_url(self.title_text)
        queryset = title.entry_set.filter(readability=True)
        return queryset

    @property
    def paginate_by(self):
        user = self.request.user
        _paginate_by = getattr(user, 'entry_pref', 10)
        return _paginate_by

    def get_context_data(self, *, object_list=None, **kwargs):
        try:
            title = Title.from_url(self.title_text)
        except Title.DoesNotExist:
            title = Title.objects.none()
        extra_context = {
            'title': title,
            'title_text': self.from_url(self.title_text),
            'order': getattr(self, '_order', None),
            'allowed_to_write': getattr(self.request.user, 'is_author', False),
        }
        return {**super().get_context_data(object_list=object_list, **kwargs), **extra_context}

