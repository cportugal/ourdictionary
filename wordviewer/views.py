from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from wordviewer.models import WordEntry

class WordEntryForm(forms.ModelForm):
    class Meta:
       model = WordEntry
       exclude = ("user_creator", "user_last_modified")
    
class WordEntryCreationView(CreateView):
    
    form_class = WordEntryForm
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WordEntryCreationView, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        object = form.save(commit=False)
        object.user_creator = self.request.user
        object.user_last_modified = self.request.user
        object.save()
        return HttpResponseRedirect("/words/")

class WordEntryUpdateView(UpdateView):
    model = WordEntry
    form_class = WordEntryForm
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WordEntryUpdateView, self).dispatch(*args, **kwargs)
    def form_valid(self, form):
        object = form.save(commit=False)
        object.user_last_modified = self.request.user
        object.save()
        return HttpResponseRedirect("/words/")

class RichUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label = "First name")
    last_name = forms.CharField(label = "Last name")

    def save(self, commit=True):
        user = super(RichUserCreationForm, self).save(commit=False)
        first_name =self.cleaned_data["first_name"]
        last_name =self.cleaned_data["last_name"]
        user.first_name = first_name
        user.last_name = last_name
        if commit:
            user.save()
        return user

class TokenRegistrationForm(RichUserCreationForm):
    token = forms.CharField(max_length=20, label="Registration Token")
    def clean_token(self):
        data = self.cleaned_data["token"]
        if data != settings.REGISTRATION_TOKEN:
            raise forms.ValidationError("Incorrect Registration Token!")
        return data
            
def register(request):
    if request.method == 'POST':
        if settings.REGISTRATION_TOKEN:
           form = TokenRegistrationForm(request.POST)
        else:
           form = RichUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/login/")
    else:
        if settings.REGISTRATION_TOKEN:
            form = TokenRegistrationForm()
        else:
            form = RichUserCreationForm()
    return render_to_response("registration/register.html", {
        'form': form,
    }, context_instance=RequestContext(request))
