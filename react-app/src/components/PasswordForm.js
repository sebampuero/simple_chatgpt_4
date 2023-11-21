import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const PasswordForm = ({ onSubmit }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e.target.elements['password-code'].value);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <form
        id="password-form"
        action=""
        method="POST"
        onSubmit={handleSubmit}
        className="col-12 col-md-6"
      >
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-xs-12 text-center">
              <h2>Código de acceso</h2>
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
              <button type="submit" className="btn btn-primary">
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
