import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import EmailForm from './components/EmailForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isEmailAuthorized, setIsEmailAuthorized] = useState(false);
  const [email, setEmail] = useState(null);
  const [subdir, setSubdir] = useState("");

  useEffect(() => {
    setSubdir(process.env.PUBLIC_URL)
  }, []);

  const handleEmailSubmit = (email) => {
    const requestBody = {
      email: email,
    };
    fetch(subdir + "/login", {
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
          setEmail(email);
        }else{
          alert("Unexpected error, please try again later.")
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsEmailAuthorized(false);
        alert("Unexpected error, please try again later.")
      });
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <Switch>
            <Route path={`${process.env.NODE_ENV === 'production' ? subdir : subdir + '/'}`} exact>
              {isEmailAuthorized ? (
                <ChatPage email={email}/>
              ) : (
                <EmailForm onSubmit={handleEmailSubmit} />
              )}
            </Route>
          </Switch>
        </header>
      </div>
    </Router>
  );
}

export default App;
