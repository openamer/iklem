# iklem desktop app

A professional Electron desktop app for iklem — chat, sessions, and settings.

## Structure

```
desktop/
├── main.js        # main process: spawns the iklem server, opens the window
├── preload.js     # context-isolated bridge (exposes server URL)
├── index.html     # the UI shell
├── styles.css     # dark theme
├── renderer.js    # talks to the iklem HTTP server via fetch
└── package.json   # electron dependency
```

## Run

```bash
cd desktop
npm install
npm start
```

The app spawns the iklem HTTP server (`iklem --server`) on port 8787 and
renders a chat UI that talks to it. Sessions, chat, and settings are backed
by the server's JSON API.

## Architecture

- **Main process** (`main.js`) spawns the iklem server and manages the window.
- **Renderer** (`renderer.js`) is sandboxed (contextIsolation, no Node) and
  talks to the server over HTTP — the same API any client could use.
- **Preload** (`preload.js`) exposes only the server URL, nothing else.
