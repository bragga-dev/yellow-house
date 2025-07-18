from django.contrib.auth.decorators import user_passes_test

def is_staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)
