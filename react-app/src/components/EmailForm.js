import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { GoogleLogin } from '@react-oauth/google';

const EmailForm = ({ onSignIn }) => {

  const handleSignIn = (credentialResponse) => {
    const jwt_decoded = JSON.parse(atob(credentialResponse.credential.split('.')[1]));
    console.log("Logged in with email " + jwt_decoded.email)
    onSignIn(jwt_decoded);
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <GoogleLogin
        onSuccess={credentialResponse => {
          handleSignIn(credentialResponse)
        }}
        onError={() => {
          console.log('Login Failed');
          alert("Authentication failed.")
        }}
      />;
    </div>
  );
};

export default EmailForm;
