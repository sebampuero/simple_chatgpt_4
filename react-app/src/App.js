import { fetchWithToken } from './api/api';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import EmailForm from './components/EmailForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isEmailAuthorized, setIsEmailAuthorized] = useState(false);
  const [email, setEmail] = useState(null);

  useEffect(() => {
    fetchWithToken(`${process.env.PUBLIC_URL}/api/authorized-email`, {
      method: 'GET',
      headers: {
        "Content-Type": "application/json",
      }
    })
    .then((response) => {
      if(response.status.toString().startsWith("50")){
        throw new Error()
      }
      if(response.status === 200) {
        setEmail(response.json().email);
        setIsEmailAuthorized(true);
      }else{
        setIsEmailAuthorized(false);
      }
    }).catch((e) => {
      console.log("Error loading authorized email", e)
      alert("There was an unknown error, please try again later.")
      setIsEmailAuthorized(false);
    })
  }, []);

  const handleSignIn = (respJson) => {
    setEmail(respJson.email);
    setIsEmailAuthorized(true);
  }

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <Switch>
            <Route path={`${process.env.NODE_ENV === 'production' ? process.env.PUBLIC_URL : process.env.PUBLIC_URL + '/'}`} exact>
              {!isEmailAuthorized ? (
                <EmailForm onSignIn={handleSignIn} />
              ) : (
                <ChatPage email={email}/>
              )}
            </Route>
          </Switch>
        </header>
      </div>
    </Router>
  );
}

export default App;
