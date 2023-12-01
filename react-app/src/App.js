import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import EmailForm from './components/EmailForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isEmailAuthorized, setIsEmailAuthorized] = useState(false);
  const [email, setEmail] = useState(null);

  const handleSignIn = (jwt_decoded) => {
    console.log(jwt_decoded);
    const requestBody = {
      email: jwt_decoded.email,
    };
    fetch(process.env.PUBLIC_URL + "/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    })
    .then((response) => {
      if (response.status == 401) {
        setIsEmailAuthorized(false);
        alert("Unauthorized email")
      }else if(response.status == 200){
        setIsEmailAuthorized(true);
        setEmail(jwt_decoded.email);
      }else{
        alert("Unexpected error, please try again later.")
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      setIsEmailAuthorized(false);
      alert("Unexpected error, please try again later.")
    });
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
