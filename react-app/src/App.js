import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import PasswordForm from './components/PasswordForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isPasswordCorrect, setIsPasswordCorrect] = useState(false);

  const handlePasswordSubmit = (code) => {
    const requestBody = {
      code: code,
    };
    fetch("/code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    })
      .then((response) => {
        if (response.status == 401) {
          setIsPasswordCorrect(false);
          alert("Invalid code.")
        }else if(response.status == 200){
          setIsPasswordCorrect(true);
        }else{
          alert("Unexpected error, please try again later.")
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        setIsPasswordCorrect(false);
        alert("Unexpected error, please try again later.")
      });
  };

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <Switch>
            <Route path="/" exact>
              {isPasswordCorrect ? (
                <ChatPage />
              ) : (
                <PasswordForm onSubmit={handlePasswordSubmit} />
              )}
            </Route>
          </Switch>
        </header>
      </div>
    </Router>
  );
}

export default App;
