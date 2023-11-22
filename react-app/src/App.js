import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import PasswordForm from './components/PasswordForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isPasswordCorrect, setIsPasswordCorrect] = useState(false);
  const [chatCode, setChatCode] = useState(null);
  const [subdir, setSubdir] = useState(null);

  useEffect(() => {
    setSubdir(process.env.PUBLIC_URL)
  }, []);

  const handlePasswordSubmit = (code) => {
    const requestBody = {
      code: code,
    };
    fetch(subdir + "/code", {
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
          setChatCode(code);
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
            <Route path={`${process.env.NODE_ENV === 'production' ? subdir : subdir + '/'}`} exact>
              {isPasswordCorrect ? (
                <ChatPage code={chatCode}/>
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
