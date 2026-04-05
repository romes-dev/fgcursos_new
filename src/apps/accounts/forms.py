from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Seu nome'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Seu sobrenome'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'seu@email.com'})
    )
    phone = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(61) 99999-9999'})
    )
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-input'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mínimo 8 caracteres'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirme a senha'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.cpf = self.cleaned_data.get('cpf', '')
            user.profile.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Sua senha'})
    )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Nome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label='Sobrenome', max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Profile
        fields = ('phone', 'cpf', 'birth_date', 'avatar', 'address', 'city', 'state', 'zip_code')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'cpf': forms.TextInput(attrs={'class': 'form-input'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'maxlength': '2'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00000-000'}),
            'avatar': forms.FileInput(attrs={'class': 'form-input'}),
        }
