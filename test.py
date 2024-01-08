
import streamlit as st
    

from getpass import getpass
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import auth



#firebaseConfig = {
#  "apiKey": "#AIzaSyBVIaqjL64gdWSznhgiPshoOIoVU1MeXkc",
#  "authDomain": "rintin-16fee"
#}

#firebase = pyrebase.initialize_app(firebaseConfig)

if not firebase_admin._apps:
    cred = credentials.Certificate('rintin-16fee-firebase-adminsdk-zcrog-536fdf1dfb.json') 
    default_app = firebase_admin.initialize_app(cred)


def app():
    st.header("Todo los Pedidos")
    print("Todo los Pedidos")

    email = input("Please Enter Your Email Address : \n")
    password = getpass("Please Enter Your Password : \n")
    if st.button("Login"):
        #create users
        user = auth.create_user_with_email_and_password(email, password)
        print("Success .... ")


        login = auth.sign_in_with_email_and_password(email, password)

        #send email verification
        auth.send_email_verification(login['idToken'])


        #reset the password
        auth.send_password_reset_email(email)

        print("Success ... ")