from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from .models import UserProfile, Item, ItemImage

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )
    terms_agreement = forms.BooleanField(required=True)

    # FIXED: made role optional and hidden with default 'user'
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=False,
        initial='user',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username',
            'password1', 'password2', 'terms_agreement', 'role'
        )
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Hide and auto-generate username
        self.fields['username'].required = False
        self.fields['username'].widget = forms.HiddenInput()
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    
    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)

        # Auto-generate username from email
        if not self.cleaned_data.get('username'):
            base_username = self.cleaned_data.get('first_name')
            temp_username = base_username
            counter = 1
            while User.objects.filter(username=temp_username).exists():
                temp_username = f"{base_username}{counter}"
                counter += 1
            user.username = temp_username
        
        if commit:
            user.save()
            
            # Get role, fallback to 'user' if missing
            role = self.cleaned_data.get('role') or 'user'
            
            # Save role in profile
            user.profile.role = role
            user.profile.save()
            
            # Assign to group
            if role == 'admin':
                admin_group, _ = Group.objects.get_or_create(name='Admin')
                admin_group.user_set.add(user)
            else:
                user_group, _ = Group.objects.get_or_create(name='User')
                user_group.user_set.add(user)
                
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Email or Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    role = forms.CharField(required=False, widget=forms.HiddenInput())


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'bio', 'profile_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['bio'].widget.attrs.update({'rows': '4'})


class DeleteAccountForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'item_type', 'name', 'category', 'location', 
            'date_lost_found', 'time_lost_found', 'description',
            'contact_name', 'contact_phone', 'contact_email',
            'preferred_contact', 'additional_notes'
        ]
        widgets = {
            'date_lost_found': forms.DateInput(attrs={'type': 'date'}),
            'time_lost_found': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'additional_notes': forms.Textarea(attrs={'rows': 3}),
        }

class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']
        widgets = {

            'image': forms.ClearableFileInput(),  # no `multiple=True` if only 1 image

        }