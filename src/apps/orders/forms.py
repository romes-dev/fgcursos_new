from django import forms


class CheckoutForm(forms.Form):
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
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'})
    )
