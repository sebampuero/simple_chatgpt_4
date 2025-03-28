import { fetchWithToken } from './api/api';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import EmailForm from './components/EmailForm';
import ChatPage from './components/ChatPage';
import ProtectedRoute from './components/ProtectedRoute';
import Loading from './components/Loading';

function App() {
  const [authStatus, setAuthStatus] = useState('loading'); // 'loading', 'authenticated', 'unauthenticated'
  const [email, setEmail] = useState(null);
  
  const basePath = process.env.NODE_ENV === 'production' ? process.env.PUBLIC_URL : process.env.PUBLIC_URL + '/';

  useEffect(() => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/authorized-email`, {
      method: 'GET',
      headers: {
        "Content-Type": "application/json",
      }
    })
    .then((response) => {
      if(response.status.toString().startsWith("50")){
        throw new Error("Server error");
      }
      if(response.status === 200) {
        return response.json();
      } else {
        setAuthStatus('unauthenticated');
        return null;
      }
    })
    .then((respJson) => {
      if (respJson) {
        setEmail(respJson.email);
        setAuthStatus('authenticated');
      }
    })
    .catch((e) => {
      console.log("Error loading authorized email", e);
      setAuthStatus('unauthenticated');
    });
  }, []);

  const handleSignIn = (respJson) => {
    setEmail(respJson.email);
    setAuthStatus('authenticated');
  }

  if (authStatus === 'loading') {
    return <Loading />;
  }

  return (
    <Router basename={basePath}>
      <div className="App">
        <header className="App-header">
          <Routes>
            <Route 
              path="/login" 
              element={
                authStatus === 'authenticated' 
                  ? <Navigate to="/" replace /> 
                  : <EmailForm onSignIn={handleSignIn} />
              } 
            />
            <Route 
              path="/" 
              element={
                <ProtectedRoute 
                  isAuthenticated={authStatus === 'authenticated'}
                  redirectPath="/login"
                >
                  <ChatPage email={email} />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </header>
      </div>
    </Router>
  );
}

export default App;