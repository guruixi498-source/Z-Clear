const fs = require('fs');
let html = fs.readFileSync('static/index.html', 'utf-8');

// 8. Add hook to processInvoice
const search_str = `            } finally {
                // Reset UI state
                btnText.innerText = t.submitBtn;
                spinner.classList.add('hidden');
                btn.disabled = false;
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        }`;

const replace_str = `            } finally {
                // Reset UI state
                btnText.innerText = t.submitBtn;
                spinner.classList.add('hidden');
                btn.disabled = false;
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            }

            // ADDED: Automatic Compliance Retrieval trigger
            const resHsCode = document.getElementById('res-hscode') ? document.getElementById('res-hscode').innerText : null;
            const resItem = document.getElementById('res-item') ? document.getElementById('res-item').innerText : null;
            if (resHsCode && resHsCode !== 'N/A' && resHsCode !== '-' && resItem && resItem !== 'N/A' && resItem !== '-') {
                setTimeout(() => {
                    performAutoComplianceRetrieval(sessionId, resHsCode, resItem);
                }, 400);
            }
        }`;

html = html.replace(search_str, replace_str);
fs.writeFileSync('static/index.html', html);
