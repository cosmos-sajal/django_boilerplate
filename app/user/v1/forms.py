from django import forms


class PasswordResetForm(forms.Form):
    password = forms.CharField(label='Password', max_length=255)
    confirm_password = forms.CharField(
        label='Confirm Password', max_length=255)
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )

        return confirm_password
