import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import EmailForm from './components/EmailForm';
import ChatPage from './components/ChatPage';;

function App() {
  const [isEmailAuthorized, setIsEmailAuthorized] = useState(false);
  const [email, setEmail] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('jwt'); //TODO: jwt token should be stored ina secure, httpOnly cookie. But we need to think how to authenticate the WS connection, too
    if (token) {
      const tokenInfos = JSON.parse(atob(token.split('.')[1]));
      const timestampInMilliseconds = new Date().getTime();
      const timestampInSeconds = Math.floor(timestampInMilliseconds / 1000);
      if (!(timestampInSeconds > tokenInfos.exp)){
        setEmail(tokenInfos.email);
        setIsEmailAuthorized(true);
      }else{
        localStorage.removeItem('jwt')
      }
    }
  }, []);

  const handleSignIn = (respJson) => {
    localStorage.setItem('jwt', respJson.jwt)
    setEmail(respJson.email);
    setIsEmailAuthorized(true);
  }

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <Switch>
            <Route path={`${process.env.NODE_ENV === 'production' ? process.env.PUBLIC_URL : process.env.PUBLIC_URL + '/'}`} exact>
              {isEmailAuthorized ? (
                <ChatPage email={email}/>
              ) : (
                <EmailForm onSignIn={handleSignIn} />
              )}
            </Route>
          </Switch>
        </header>
      </div>
    </Router>
  );
}

export default App;
