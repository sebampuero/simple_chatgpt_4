import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import PasswordForm from './components/PasswordForm';
import ChatPage from './components/ChatPage';

function App() {
  const [isPasswordCorrect, setIsPasswordCorrect] = useState(false);

  const handlePasswordSubmit = () => {
    // Your password validation logic goes here
    // For example, check the password, and if correct, set isPasswordCorrect to true
    setIsPasswordCorrect(true);
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
