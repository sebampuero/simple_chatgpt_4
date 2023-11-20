import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const PasswordForm = () => {
  const [error, setError] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Your form submission logic goes here
    // For example, you can check the password and set the error state accordingly
    // setError(true);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <form
        id="password-form"
        action="/password-code" // You may adjust the action accordingly
        method="POST"
        onSubmit={handleSubmit}
      >
        <div className="container">
          <div className="row">
            <div className="col-xs-12 col-sm-10 col-sm-offset-3 col-md-10 col-md-offset-4">
              <h2 className="text-center">Código de acceso</h2>
              <div className="form-group">
                <input
                  type="password"
                  className="form-control"
                  id="password-code"
                  name="password-code"
                  placeholder="Código"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary btn-block">
                Enviar
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default PasswordForm;
