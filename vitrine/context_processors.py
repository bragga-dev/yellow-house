from vitrine.forms import SearchForm

def global_search_context(request):
    return {
        'search_form': SearchForm()
    }
