# REST API Wiki

## Authentication

### Signup

request:

`POST /signup  content-type:apllication/json json:{"email": "string", "name": "string", "password":"string"}`

Sending email with confirm token in template `html:confirm_user_create.html`

response: 

1) `code:200 json:{"message": "Successful signup. Please confirm your signup with email."}`

2) `code:401 json:{"message": "User with email [email] or with name [name] already exists."}`


### Confirm Signup (from email)

request:
`GET /confirm?token=string`

response: 
1) `code:200 html:confirm_successful_status.html`

2) `code:401 html:token_error.html` 
____
### Login

request:

`GET /login auth:Basic`

response:

1) `code:200 json:{"message": "Successful login"}`
`cookie:cookie.name.{id}=sha256(password)`

2) `code:401 json:{"message": "Please confirm your account. Check [email] email."}`

3) `code:401 json:{"message": "Please check your login details and try again. Unsuccessful try logging with email [email] and password [password}]"}`



___
### Forgot

request:

`POST /forgot content-type:application/json json:{"email": "string"}` 

If email in the DB:

Sending email with reset token in template `html:send_token.html`.

response:

 - `code:200 json:{"message": "Sending email with token to the [user.email]"}`


Else:

response:

 - `code:400 json:{"message": "Unknown email address [email]"}`

### Reset (from email)

request:
`GET /reset?token=string`

Sending email with new password in template `reset_pass.html`

response:

1) `code:200 html:reset_successful_status.html`

2) `code:401 html:token_error.html`

___
### Change Password

request:

`@login_required POST /change content-type:application/json json:{"old": "string", "new": "string"} headers:{cookie: cookie:cookie.name.{id}=sha256(password)}`

response:

1) `code:200 json:{"message": "Password has benn changed"}`
`cookie:cookie.name.{id}=sha256(password)`

2) `code:500 json:{"message": "Error during password updating: [error]"}`

___
### Logout

request:
`@login_required GET /logout`

response:

 - `redirect -> @login_required GET /profile`
