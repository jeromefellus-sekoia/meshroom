module.exports = {
  assetsDir: "static",
  devServer: {
    port: 8000,
    proxy: {
      "^/api/.*": {
        target: "http://localhost:8001",
        ws: true,
        changeOrigin: true,
        logLevel: "debug",
      },
      "^/websocket": {
        target: "http://localhost:8001",
        ws: true,
        changeOrigin: true,
        logLevel: "debug",
      },
    },
  },
};
