from vitrine.forms import SearchForm, ContactForm

def global_search_context(request):
    return {
        'search_form': SearchForm()
    }


def global_contact_context(request):
    return {
        'contact_form': ContactForm()   
    }