from django.contrib.admin import RelatedFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import smart_str
from django.utils.html import format_html
try:
    from django.core.urlresolvers import reverse
except ImportError: # Django 1.11
    from django.urls import reverse


from django.contrib.admin.utils import get_model_from_relation
from django.forms.utils import flatatt



class RelatedFieldAjaxListFilter(RelatedFieldListFilter):
    template = 'jet/related_field_ajax_list_filter.html'
    ajax_attrs = None

    def has_output(self):
        return True

    def field_choices(self, field, request, model_admin):
        model = field.remote_field.model
        app_label = model._meta.app_label
        model_name = model._meta.object_name

        self.ajax_attrs = format_html('{0}', flatatt({
            'data-app-label': app_label,
            'data-model': model_name,
            'data-ajax--url': reverse('jet:model_lookup'),
            'data-queryset--lookup': self.lookup_kwarg
        }))

        if self.lookup_val is None:
            return []

        other_model = get_model_from_relation(field)
        if hasattr(field, 'rel'):
            rel_name = field.rel.get_related_field().name
        else:
            rel_name = other_model._meta.pk.name

        queryset = model._default_manager.filter(**{rel_name: self.lookup_val}).all()
        return [(x._get_pk_val(), smart_str(x)) for x in queryset]


try:
    from collections import OrderedDict
    from django import forms
    from django.contrib.admin.widgets import AdminDateWidget
    from rangefilter.filter import DateRangeFilter as OriginalDateRangeFilter
    from django.utils.translation import gettext as _


    class DateRangeFilter(OriginalDateRangeFilter):
        def get_template(self):
            return 'rangefilter/date_filter.html'

        def _get_form_fields(self):
            # this is here, because in parent DateRangeFilter AdminDateWidget
            # could be imported from django-suit
            return OrderedDict((
                (self.lookup_kwarg_gte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('From date')}),
                    localize=True,
                    required=False
                )),
                (self.lookup_kwarg_lte, forms.DateField(
                    label='',
                    widget=AdminDateWidget(attrs={'placeholder': _('To date')}),
                    localize=True,
                    required=False
                )),
            ))

        @staticmethod
        def _get_media():
            css = [
                'style.css',
            ]
            return forms.Media(
                css={'all': ['range_filter/css/%s' % path for path in css]}
            )
except ImportError:
    pass


class OptgroupSimpleListFilter(SimpleListFilter):
    """
        A.simple list filter allowing to use optgroup, working properly with jet and Select2
    """

    template = "jet/optgroup_simple_list_filter.html"
    empty_choice = True

    def lookups(self, request, model_admin):
        """
        Must be overridden to return a list of tuples:
         (value, verbose value)
         or
         (verbose value, (value, verbose value))
        """
        raise NotImplementedError(
            "The OptgroupSimpleListFilter.lookups() method must be overridden to "
            "return a list of tuples (value, verbose value) or (verbose value, (value, verbose value))."
        )

    def get_choice(self, changelist, value, label):
        return {
            "selected": self.value() == str(value),
            "query_string": changelist.get_query_string({self.parameter_name: value}),
            "display": label,
        }

    def choices(self, changelist):
        if self.empty_choice:
            yield (
                None,
                [
                    {
                        "selected": self.value() is None,
                        "query_string": changelist.get_query_string(
                            remove=[self.parameter_name]
                        ),
                        "display": _("All"),
                    }
                ],
            )

        for index, (option_value, option_label) in enumerate(self.lookup_choices):
            if option_value is None:
                option_value = ""

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                choices = option_label
            else:
                group_name = None
                choices = [(option_value, option_label)]
            yield (group_name, subgroup)

            for subvalue, sublabel in choices:
                subgroup.append(self.get_choice(changelist, subvalue, sublabel))


class MultipleChoiceListFilter(OptgroupSimpleListFilter):
    """
        A.mulitple choice list filter, working properly with jet and Select2.
        Inspired from: https://github.com/ctxis/django-admin-multiple-choice-list-filter/
    """

    template = "jet/multiple_choice_list_filter.html"
    empty_choice = False

    def lookups(self, request, model_admin):
        """
        Must be overridden to return a list of tuples (value, verbose value)
        """
        raise NotImplementedError(
            "The MultipleChoiceListFilter.lookups() method must be overridden to "
            "return a list of tuples (value, verbose value)."
        )

    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {self.parameter_name: request.GET[self.parameter_name].split(",")}
            queryset = queryset.filter(**kwargs)
        return queryset

    def value_as_list(self):
        return self.value().split(",") if self.value() else []

    def get_choice(self, changelist, value, label):
        return {
            "selected": str(value) in self.value_as_list(),
            "value": str(value),
            "display": label,
        }
