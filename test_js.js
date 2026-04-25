const fs = require('fs');
const html = fs.readFileSync('static/index.html', 'utf-8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
if (match) {
    fs.writeFileSync('temp.js', match[1]);
}
