const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/upload_resume',
    createProxyMiddleware({
      target: 'http://0.0.0.0:80',
      changeOrigin: true,
    })
  );
};
