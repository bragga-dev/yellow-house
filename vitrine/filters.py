import django_filters
from vitrine.models import Souvenir, ArtWork, ArtworkCategory, SouvenirCategory

class SouvenirFilter(django_filters.FilterSet):
    souvenir_category = django_filters.ModelChoiceFilter(queryset=SouvenirCategory.objects.all(),
        label='Categoria',
        empty_label='Todas as categorias'
    )
    size = django_filters.ChoiceFilter(label="Tamanho", choices=Souvenir.SIZE_CHOICES,
        empty_label="Todos os tamanhos"
    )
    price = django_filters.RangeFilter(label='Faixa de Preço')
    

    class Meta:
        model = Souvenir
        fields = ['souvenir_category', 'size', 'price']

class ArtWorkFilter(django_filters.FilterSet):
    art_work_category = django_filters.ModelChoiceFilter(
        queryset=ArtworkCategory.objects.all(),
        label='Categoria',
        empty_label='Todas as categorias'
    )
    price = django_filters.RangeFilter(label='Faixa de Preço')
    style = django_filters.CharFilter(lookup_expr='icontains', label='Estilo')

    class Meta:
        model = ArtWork
        fields = ['art_work_category', 'price']
