import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const EmailForm = ({ onSubmit }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e.target.elements['email'].value);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <form
        id="email-form"
        action=""
        method="POST"
        onSubmit={handleSubmit}
        className="col-12 col-md-6"
      >
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-xs-12 text-center">
              <h2>Email address</h2>
              <div className="form-group">
                <input
                  type="email"
                  className="form-control"
                  id="email"
                  name="email"
                  placeholder="Email address"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Send
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default EmailForm;
