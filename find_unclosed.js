const fs = require('fs');
const code = fs.readFileSync('temp.js', 'utf-8');
let braces = 0;
let last_lines = [];
let lines = code.split('\n');
for(let j=0; j<lines.length; j++) {
    for(let i=0; i<lines[j].length; i++) {
        if(lines[j][i]==='{') braces++;
        if(lines[j][i]==='}') braces--;
    }
    if (braces < 0) { console.log('Negative braces at line', j); break; }
}
console.log('Braces balance:', braces);
