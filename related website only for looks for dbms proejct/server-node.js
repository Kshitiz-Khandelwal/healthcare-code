import { createServer } from 'node:http';
import { Readable } from 'node:stream';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { w as workerEntry } from './dist/server/assets/worker-entry-BiTSiwsV.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const port = process.env.PORT || 3000;

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.wav': 'audio/wav',
  '.mp4': 'video/mp4',
  '.woff': 'application/font-woff',
  '.ttf': 'application/font-ttf',
  '.eot': 'application/vnd.ms-fontobject',
  '.otf': 'application/font-otf',
  '.wasm': 'application/wasm'
};

createServer(async (req, res) => {
  const protocol = req.headers['x-forwarded-proto'] || 'http';
  const host = req.headers.host;
  const url = new URL(req.url, `${protocol}://${host}`);

  // 1. Try serving static files from dist/client
  try {
    let filePath = path.join(__dirname, 'dist', 'client', url.pathname);
    if (url.pathname === '/') {
        // SSR will handle the root, but let's check for index.html just in case
    } else {
        const stats = await fs.stat(filePath);
        if (stats.isFile()) {
            const ext = path.extname(filePath).toLowerCase();
            res.setHeader('Content-Type', MIME_TYPES[ext] || 'application/octet-stream');
            const data = await fs.readFile(filePath);
            res.end(data);
            return;
        }
    }
  } catch (e) {
    // File not found, continue to SSR
  }

  // 2. Fallback to SSR (workerEntry.fetch)
  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers)) {
    if (value) {
        if (Array.isArray(value)) {
            value.forEach(v => headers.append(key, v));
        } else {
            headers.set(key, value);
        }
    }
  }

  const request = new Request(url.toString(), {
    method: req.method,
    headers,
    body: req.method !== 'GET' && req.method !== 'HEAD' ? Readable.toWeb(req) : null,
    // @ts-ignore
    duplex: 'half'
  });

  try {
    const response = await workerEntry.fetch(request, process.env, {});
    
    res.statusCode = response.status;
    response.headers.forEach((value, key) => {
      res.setHeader(key, value);
    });

    if (response.body) {
      const reader = response.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(value);
      }
    }
    res.end();
  } catch (err) {
    console.error('SSR Error:', err);
    res.statusCode = 500;
    res.end('Internal Server Error');
  }
}).listen(port, '0.0.0.0', () => {
  console.log(`Server running on port ${port}`);
});
