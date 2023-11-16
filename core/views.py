from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Profile
from .forms import ProfileForm


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile_user, create = Profile.objects.get_or_create(user=self.request.user)
        return profile_user
