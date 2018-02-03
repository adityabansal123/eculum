**Eculum Main Api**
----

## Twitter Auth


* **URL**
  api/v1/twitter

* **Method:**
  `GET`
  
*  **URL Params**
   `None`


* **Success Response:**
  Redirects to Twitter Auth Page

  * **Code:** 301
 
* **Notes:**
  `None`


## Twitter Callback

* **URL**
  /api/v1/callback/twitter


* **Method:**
  `GET`
  
*  **URL Params**

   **Required:**
 
   `auth_verifier=[string]`

* **Success Response:**
  
  If new user redirect to register page or redirect to app if old user

  * **Code:** 301 <br />

* **Notes:**
  `None`


**Email Auth**
----
  Login using email and password

* **URL**
  /api/v1/auth/email

* **Method:**
  `POST`
* **Data Params**
  `{"email":<email>, "password":<password>}`

* **Success Response:**
	Redirects to App page for fetching auth token
  * **Code:** 301
 
* **Error Response:**
  * **Code:** 401 UNAUTHORIZED
    **Content:** `{ "message" : "Invalid Username or Password" }`

* **Notes:**
  `None`

**Email Callback**
----
  To register user after oauth using email and password

* **URL**
  _api/v1/callback/email_

* **Method:**
  `POST`
  
*  **URL Params**
  `None`

* **Data Params**

  `{"email":<email>, "password":<password>}`
  
* **Session Var**
  `login_hash`

* **Success Response:**
  * **Code:** 200 
    **Content:** `{ "message" : "Successfully Registered" }`
 
* **Error Response:**
  * **Code:** 401 UNAUTHORIZED <br />
    **Content:** `{ "message" : "An error ocurred" }`
* **Notes:**
  `None`