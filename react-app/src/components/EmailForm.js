import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useGoogleLogin } from '@react-oauth/google';
import './EmailForm.css';

const EmailForm = ({ onSignIn }) => {

  const handleSignIn = useGoogleLogin({
    flow: 'auth-code',
    onSuccess: ({ code }) => {
      fetch(`${process.env.PUBLIC_URL}/api/login-code`, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"code": code})
      })
      .then((response) => {
        if(response.status === 200) return response.json();
        throw new Error("Not authorized")
      })
      .then((respJson) => {
        onSignIn(respJson);
      })
      .catch((error) => {
        console.log(error);
        alert("Failed to authorize")
      })
    },
    onError: (errorResponse) => {
      console.log(errorResponse);
      alert("Failed to authenticate against Google services")
    }
  });

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <button class="google-btn" onClick={() => handleSignIn()}>
        <span class="google-icon-wrapper">
          <img class="google-icon" src={`${process.env.PUBLIC_URL}/google_g_logo.svg`} alt="Google logo"/>
        </span>
        Sign in with Google
      </button>
    </div>
  );
};

export default EmailForm;
