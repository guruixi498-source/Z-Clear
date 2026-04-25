const fs = require('fs');
let html = fs.readFileSync('static/index.html', 'utf-8');

// 8. Add hook to processInvoice
// We use exact string replacement for processInvoice end
const pi_end = `            } finally {
                // Reset UI state
                btnText.innerText = t.submitBtn;
                spinner.classList.add('hidden');
                btn.disabled = false;
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        }`;

const pi_new = `            } finally {
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

html = html.replace(pi_end, pi_new);
fs.writeFileSync('static/index.html', html);
