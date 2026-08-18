// iklem desktop — preload bridge.
// Exposes a minimal, safe API to the renderer (no Node access).

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('iklem', {
  // The renderer talks to the HTTP server directly via fetch; this bridge
  // only exposes the server base URL and app metadata.
  serverUrl: 'http://127.0.0.1:8787',
  version: '0.1.0',
});
