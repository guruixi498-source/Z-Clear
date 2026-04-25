const fs = require('fs');
let html = fs.readFileSync('static/index.html', 'utf-8');

// 1. Insert auto_panel before </main>
const auto_panel = `
                <!-- ADDED: Auto Compliance Retrieval Result Panel -->
                <div id="compliance-result-panel" class="mt-6 hidden bg-indigo-50 rounded-xl p-6 border border-indigo-100 shadow-sm transition-opacity duration-300">
                    <h3 id="lbl-compliance-title" class="text-lg font-bold mb-4 text-indigo-700 border-b pb-2 border-indigo-200">Compliance Policy Match</h3>
                    <div class="mb-4">
                        <span id="lbl-compliance-ctx" class="text-xs font-semibold text-indigo-500 uppercase tracking-wider block mb-2">Compliance Context</span>
                        <p id="res-compliance-ctx" class="text-sm text-gray-800 whitespace-pre-wrap bg-white p-4 rounded border border-indigo-50">-</p>
                    </div>
                    <div>
                        <span id="lbl-retrieved-regs" class="text-xs font-semibold text-indigo-500 uppercase tracking-wider block mb-2">Retrieved Regulations</span>
                        <div id="res-retrieved-regs" class="space-y-3"></div>
                    </div>
                </div>
`;
html = html.replace('</div>\n            </div>\n        </main>', '</div>\n' + auto_panel + '\n            </div>\n        </main>');

// 2. Insert manual panel after </main>
const manual_panel = `
        <!-- ADDED: Manual Compliance Retrieval Panel -->
        <section id="manual-compliance-search" class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 mt-8 mb-12">
            <h2 id="manual-title" class="text-xl font-bold mb-5 text-gray-900 border-b pb-2">Manual Compliance Retrieval</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                    <label id="lbl-manual-item" class="block text-sm font-semibold text-gray-700 mb-1">Item Name *</label>
                    <input type="text" id="manual-item" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="e.g. Steel Pipe">
                </div>
                <div>
                    <label id="lbl-manual-hscode" class="block text-sm font-semibold text-gray-700 mb-1">HS Code *</label>
                    <input type="text" id="manual-hscode" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="e.g. 7304">
                </div>
                <div>
                    <label id="lbl-manual-import" class="block text-sm font-semibold text-gray-700 mb-1">Import Country</label>
                    <input type="text" id="manual-import" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="e.g. US">
                </div>
                <div>
                    <label id="lbl-manual-export" class="block text-sm font-semibold text-gray-700 mb-1">Export Country</label>
                    <input type="text" id="manual-export" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="e.g. CN">
                </div>
            </div>
            
            <button id="manual-submit-btn" onclick="manualRetrieve()" class="w-full bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition duration-200 flex justify-center items-center group">
                <span id="manual-btn-text">Retrieve Compliance</span>
                <svg id="manual-loading-spinner" class="animate-spin ml-3 h-5 w-5 text-white hidden" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </button>

            <!-- Manual Results Section -->
            <div id="manual-result-section" class="mt-6 hidden transition-opacity duration-300 opacity-0">
                <div class="bg-teal-50 rounded-xl p-6 border border-teal-100 shadow-sm">
                    <div class="mb-4">
                        <span id="lbl-manual-ctx" class="text-xs font-semibold text-teal-600 uppercase tracking-wider block mb-2">Compliance Context</span>
                        <p id="manual-res-ctx" class="text-sm text-gray-800 whitespace-pre-wrap bg-white p-4 rounded border border-teal-50">-</p>
                    </div>
                    <div>
                        <span id="lbl-manual-regs" class="text-xs font-semibold text-teal-600 uppercase tracking-wider block mb-2">Retrieved Regulations</span>
                        <div id="manual-res-regs" class="space-y-3"></div>
                    </div>
                </div>
            </div>
        </section>
`;
html = html.replace('        </main>\n    </div>\n\n    <script>', '        </main>\n' + manual_panel + '\n    </div>\n\n    <script>');

// 3. Add Translations
const en_add = `statusIncomplete: "INCOMPLETE",
                statusAuditing: "AUDITING",
                statusRetrieving: "Retrieving...",
                statusError: "ERROR",
                lblComplianceTitle: "Compliance Policy Match",
                lblComplianceCtx: "Compliance Context",
                lblRetrievedRegs: "Retrieved Regulations",
                manualTitle: "Manual Compliance Retrieval",
                lblManualItem: "Item Name *",
                lblManualHsCode: "HS Code *",
                lblManualImport: "Import Country",
                lblManualExport: "Export Country",
                btnRetrieve: "Retrieve Compliance",
                msgNoMatch: "No matching regulations found.",
                lblCountry: "Country",
                msgRequired: "Item Name and HS Code are required!"`;

const zh_add = `statusIncomplete: "不完整",
                statusAuditing: "审计中",
                statusRetrieving: "合规政策检索中...",
                statusError: "异常",
                lblComplianceTitle: "合规政策匹配结果",
                lblComplianceCtx: "合规上下文",
                lblRetrievedRegs: "检索到的法规",
                manualTitle: "合规政策手动检索",
                lblManualItem: "商品名称 *",
                lblManualHsCode: "HS编码 *",
                lblManualImport: "进口国",
                lblManualExport: "出口国",
                btnRetrieve: "检索合规政策",
                msgNoMatch: "未检索到匹配的海关合规政策或RCEP规则。",
                lblCountry: "适用国家",
                msgRequired: "商品名称和HS编码为必填项！"`;

const ms_add = `statusIncomplete: "TIDAK LENGKAP",
                statusAuditing: "SEDANG DIAUDIT",
                statusRetrieving: "Sedang mengambil...",
                statusError: "RALAT",
                lblComplianceTitle: "Padanan Dasar Pematuhan",
                lblComplianceCtx: "Konteks Pematuhan",
                lblRetrievedRegs: "Peraturan yang Diperoleh",
                manualTitle: "Pengambilan Pematuhan Manual",
                lblManualItem: "Nama Barang *",
                lblManualHsCode: "Kod HS *",
                lblManualImport: "Negara Import",
                lblManualExport: "Negara Eksport",
                btnRetrieve: "Ambil Pematuhan",
                msgNoMatch: "Tiada peraturan yang sepadan ditemui.",
                lblCountry: "Negara",
                msgRequired: "Nama Barang dan Kod HS diperlukan!"`;

html = html.replace('statusIncomplete: "INCOMPLETE"', en_add);
html = html.replace('statusIncomplete: "不完整"', zh_add);
html = html.replace('statusIncomplete: "TIDAK LENGKAP"', ms_add);

// 4. Update status UI display text
const updateStatusUI_text_add = `            } else if (statusData === 'AUDITING') {
                displayText = t.statusAuditing;
            } else if (statusData === 'RETRIEVING') {
                displayText = t.statusRetrieving;
            } else if (statusData === 'ERROR') {
                displayText = t.statusError;
            } else {`;
html = html.replace('            } else {\n                displayText = statusData;\n            }', updateStatusUI_text_add);

// 5. Update status UI class name
const updateStatusUI_add = `            } else if (statusData === 'AUDITING') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-blue-100 text-blue-800 border border-blue-200';
            } else if (statusData === 'RETRIEVING') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-purple-100 text-purple-800 border border-purple-200 animate-pulse';
            } else {`;
html = html.replace(`            } else {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-blue-100 text-blue-800 border border-blue-200';
            }`, updateStatusUI_add);

// 6. Add Translations mapping
const changeLanguage_add = `            document.getElementById('lbl-status').innerText = t.lblStatus;

            // Added translations safely
            if(document.getElementById('lbl-compliance-title')) document.getElementById('lbl-compliance-title').innerText = t.lblComplianceTitle;
            if(document.getElementById('lbl-compliance-ctx')) document.getElementById('lbl-compliance-ctx').innerText = t.lblComplianceCtx;
            if(document.getElementById('lbl-retrieved-regs')) document.getElementById('lbl-retrieved-regs').innerText = t.lblRetrievedRegs;

            if(document.getElementById('manual-title')) document.getElementById('manual-title').innerText = t.manualTitle;
            if(document.getElementById('lbl-manual-item')) document.getElementById('lbl-manual-item').innerText = t.lblManualItem;
            if(document.getElementById('lbl-manual-hscode')) document.getElementById('lbl-manual-hscode').innerText = t.lblManualHsCode;
            if(document.getElementById('lbl-manual-import')) document.getElementById('lbl-manual-import').innerText = t.lblManualImport;
            if(document.getElementById('lbl-manual-export')) document.getElementById('lbl-manual-export').innerText = t.lblManualExport;
            if(document.getElementById('lbl-manual-ctx')) document.getElementById('lbl-manual-ctx').innerText = t.lblComplianceCtx;
            if(document.getElementById('lbl-manual-regs')) document.getElementById('lbl-manual-regs').innerText = t.lblRetrievedRegs;

            const manualSpinner = document.getElementById('manual-loading-spinner');
            if (manualSpinner && manualSpinner.classList.contains('hidden')) {
                document.getElementById('manual-btn-text').innerText = t.btnRetrieve;
            } else if (manualSpinner) {
                document.getElementById('manual-btn-text').innerText = t.statusRetrieving;
            }`;
html = html.replace("            document.getElementById('lbl-status').innerText = t.lblStatus;", changeLanguage_add);

// 7. Add new functions
const js_add = `

        function buildRegulationsHTML(regs) {
            const t = translations[currentLang];
            if (!regs || regs.length === 0) {
                return '<p class="text-sm text-gray-500 italic">' + t.msgNoMatch + '</p>';
            }
            let html = '';
            regs.forEach(reg => {
                html += '<div class="bg-white p-4 rounded border border-gray-100 shadow-sm text-sm">';
                html += '<div class="font-bold text-gray-800 mb-1">' + (reg.title || '') + '</div>';
                html += '<div class="text-gray-600 mb-2 line-clamp-2" title="' + (reg.content || '') + '">' + (reg.content || '') + '</div>';
                html += '<div class="flex space-x-3 text-xs">';
                html += '<span class="bg-gray-100 text-gray-600 px-2 py-1 rounded">HS: ' + (reg.hs_code || 'N/A') + '</span>';
                html += '<span class="bg-blue-50 text-blue-600 px-2 py-1 rounded">' + t.lblCountry + ': ' + (reg.country || 'N/A') + '</span>';
                html += '</div></div>';
            });
            return html;
        }

        async function performAutoComplianceRetrieval(sessionId, hsCode, itemName) {
            const t = translations[currentLang];
            const statusEl = document.getElementById('res-status');
            const autoPanel = document.getElementById('compliance-result-panel');

            if(!autoPanel) return;

            statusEl.setAttribute('data-status', 'RETRIEVING');
            updateStatusUI('RETRIEVING', null);

            autoPanel.classList.remove('hidden');
            document.getElementById('res-compliance-ctx').innerText = t.statusRetrieving;
            document.getElementById('res-retrieved-regs').innerHTML = '';

            try {
                const response = await fetch('/sentinel/retrieve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        hs_code: hsCode,
                        product_name: itemName,
                        import_country: "",
                        export_country: ""
                    })
                });

                if (!response.ok) throw new Error('Server returned ' + response.status);

                const contentType = response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("接口请求异常，请检查后端服务是否正常启动");
                }

                const data = await response.json();

                if (data.status === 'success') {
                    document.getElementById('res-compliance-ctx').innerText = data.regulation_context || t.msgNoMatch;
                    document.getElementById('res-retrieved-regs').innerHTML = buildRegulationsHTML(data.retrieved_regulations);

                    statusEl.setAttribute('data-status', 'AUDITING');
                    updateStatusUI('AUDITING', {en: "Auditing", zh: "审计中", ms: "Sedang Diaudit"});
                } else {
                    throw new Error(data.error_log || "Unknown API error");
                }
            } catch (error) {
                document.getElementById('res-compliance-ctx').innerText = error.message;
                statusEl.setAttribute('data-status', 'ERROR');
                updateStatusUI('ERROR', null);
            }
        }

        async function manualRetrieve() {
            const itemName = document.getElementById('manual-item').value;
            const hsCode = document.getElementById('manual-hscode').value;
            const importCountry = document.getElementById('manual-import').value || "";
            const exportCountry = document.getElementById('manual-export').value || "";

            const t = translations[currentLang];

            if (!itemName.trim() || !hsCode.trim()) {
                alert(t.msgRequired);
                return;
            }

            const btnText = document.getElementById('manual-btn-text');
            const spinner = document.getElementById('manual-loading-spinner');
            const btn = document.getElementById('manual-submit-btn');
            const resultSection = document.getElementById('manual-result-section');

            btnText.innerText = t.statusRetrieving;
            spinner.classList.remove('hidden');
            btn.disabled = true;
            btn.classList.add('opacity-75', 'cursor-not-allowed');

            resultSection.classList.remove('hidden');
            resultSection.classList.remove('opacity-0');
            document.getElementById('manual-res-ctx').innerText = t.statusRetrieving;
            document.getElementById('manual-res-regs').innerHTML = '';

            const sessionId = 'manual_' + Math.random().toString(36).substr(2, 9);

            try {
                await fetch('/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId, text: 'Dummy for manual: ' + itemName + ', ' + hsCode })
                });

                const response = await fetch('/sentinel/retrieve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        hs_code: hsCode,
                        product_name: itemName,
                        import_country: importCountry,
                        export_country: exportCountry
                    })
                });

                if (!response.ok) {
                    throw new Error('Server returned ' + response.status);
                }

                const contentType = response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("接口请求异常，请检查后端服务是否正常启动");
                }

                const data = await response.json();

                if (data.status === 'success') {
                    document.getElementById('manual-res-ctx').innerText = data.regulation_context || t.msgNoMatch;
                    document.getElementById('manual-res-regs').innerHTML = buildRegulationsHTML(data.retrieved_regulations);
                } else {
                    throw new Error(data.error_log || "Unknown API error");
                }

            } catch (error) {
                document.getElementById('manual-res-ctx').innerText = error.message;
            } finally {
                btnText.innerText = t.btnRetrieve;
                spinner.classList.add('hidden');
                btn.disabled = false;
                btn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
        }
`;

html = html.replace('        // Initialize UI with default language on load', js_add + '\n        // Initialize UI with default language on load');

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
