from django import template
from eservice.models import EServiceStar

register = template.Library()


@register.filter(name='stars_filter')
def stars_filter(id,filt):
    if filt == 'maximum':
        stars = EServiceStar.objects.filter(average_value__gte=8).count()
    elif filt == 'good':
        stars = EServiceStar.objects.filter(average_value__gte=6, average_value__lt=8).count()
    elif filt == 'average':
        stars = EServiceStar.objects.filter(average_value__gte=4, average_value__lt=6).count()
    elif filt == 'bad':
        stars = EServiceStar.objects.filter(average_value__gte=2, average_value__lt=4).count()
    else:
        stars = EServiceStar.objects.filter(average_value__lt=2).count()

    return stars