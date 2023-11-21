const { createProxyMiddleware } = require('http-proxy-middleware');

//Only used when developing. CRA disables this when building for production automatically.
module.exports = function(app) {
  app.use(
    '/',  // Your API endpoint path
    createProxyMiddleware({
      target: 'http://localhost:9292',  // Your Sanic server's address
      changeOrigin: true,
    })
  );
};
