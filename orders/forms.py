from django import forms
from django.contrib.auth import get_user_model

from .models import Order


User = get_user_model()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer',
            'product',
            'quantity',
            'status',
            'delivery_address',
            'comment',
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'delivery_address': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, user_role='guest', **kwargs):
        super().__init__(*args, **kwargs)
        self.user_role = user_role

        self.fields['customer'].queryset = User.objects.filter(
            is_active=True,
            is_superuser=False,
        ).order_by('username')
        self.fields['product'].queryset = self.fields['product'].queryset.order_by('name')
        self.fields['quantity'].help_text = 'Количество экземпляров в заказе'
        self.fields['delivery_address'].help_text = 'Куда доставить заказ'

        if user_role == 'client':
            self.fields.pop('customer')
            self.fields.pop('status')

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity and quantity > product.quantity:
            self.add_error(
                'quantity',
                f'На складе доступно только {product.quantity} экз.',
            )

        return cleaned_data
