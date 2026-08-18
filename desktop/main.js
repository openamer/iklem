// iklem desktop — main process.
// Spawns the iklem HTTP server (the agent backend) and opens the UI window.

const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

const SERVER_PORT = 8787;
let serverProcess = null;

function startServer() {
  // Resolve the iklem CLI. Prefer the venv-installed .exe (spawnable directly
  // on Windows); the .cmd launcher needs shell:true.
  const candidates = [
    path.join(process.env.USERPROFILE || '', 'iklem', '.venv', 'Scripts', 'iklem.exe'),
    path.join(process.env.USERPROFILE || '', '.local', 'bin', 'iklem.cmd'),
    path.join(process.env.USERPROFILE || '', '.local', 'bin', 'iklem'),
  ];
  const iklem = candidates.find((p) => require('fs').existsSync(p));
  if (!iklem) {
    console.error('iklem backend not found — install it first (pip install -e .)');
    return false;
  }
  const isCmd = iklem.endsWith('.cmd');
  serverProcess = spawn(iklem, ['--server'], {
    stdio: 'ignore',
    shell: isCmd,
  });
  serverProcess.on('error', (err) => console.error('server error:', err));
  return true;
}

function stopServer() {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'iklem',
    backgroundColor: '#0d1117',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.loadFile('index.html');
}

app.whenReady().then(() => {
  startServer();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  stopServer();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', stopServer);
