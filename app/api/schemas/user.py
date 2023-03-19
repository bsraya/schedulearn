import re
from fastapi import Request
from dataclasses import dataclass
from pydantic import BaseModel

# password should be at least 8 characters
# password should contain at least one number
# password should contain at least one capital letter
password_regex = r'^(?=.*[A-Z])(?=.*[0-9])(?=.{8,})'

# johndoe@gmail.com
# johndoe@gapp.nthu.edu.tw
# johndoe@office365.nthu.edu.tw
email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@dataclass
class UserLogin(BaseModel):
    request: Request
    username: str
    password: str

@dataclass
class UserSignup(UserLogin):
    first_name: str
    last_name: str
    email: str

    async def load_data(self):
        form = await self.request.form()
        self.first_name = form.get("first_name")
        self.last_name = form.get("last_name")
        self.username = form.get("username")
        self.email = form.get("email")
        self.password = form.get("password")

    def is_valid_email(self, email):
        if re.match(email_regex, email):
            return True
        return False
    
    def is_valid_password(self, password):
        if re.match(password_regex, password):
            return True
        return False

    def is_valid(self):
        self.errors = []
        if not self.first_name or not len(self.first_name) > 1:
            self.errors.append("First name is required")
        if not self.last_name or not len(self.last_name) > 1:
            self.errors.append("Last name is required")
        if not self.username or not len(self.username) > 1:
            self.errors.append("Username is required")    
        if not self.email: 
            self.errors.append("Email is required")
        if not self.is_valid_email(self.email):
            self.errors.append("Email is invalid")
        if not self.password:
            self.errors.append("Password is required")
        if not self.is_valid_password(self.password):
            self.errors.append("Password is invalid")
        if self.errors:
            return False
        return True
