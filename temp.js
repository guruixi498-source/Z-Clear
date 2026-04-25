
        const translations = {
            en: {
                title: "Z-Clear Trade Compliance",
                inputLabel: "Invoice Text",
                placeholder: "Paste unstructured invoice text here...",
                submitBtn: "Extract Information",
                loadingBtn: "Processing...",
                resultTitle: "Extraction Results",
                lblItem: "Item Name",
                lblHsCode: "HS Code",
                lblWeight: "Weight",
                lblStatus: "Status",
                statusCompleted: "COMPLETED",
                statusIncomplete: "INCOMPLETE",
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
                msgRequired: "Item Name and HS Code are required!"
            },
            zh: {
                title: "Z-Clear 贸易合规系统",
                inputLabel: "发票文本",
                placeholder: "在此处粘贴非结构化发票文本...",
                submitBtn: "提取信息",
                loadingBtn: "处理中...",
                resultTitle: "提取结果",
                lblItem: "品名 (Item Name)",
                lblHsCode: "海关编码 (HS Code)",
                lblWeight: "重量 (Weight)",
                lblStatus: "状态",
                statusCompleted: "已完成",
                statusIncomplete: "不完整",
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
                msgRequired: "商品名称和HS编码为必填项！"
            },
            ms: {
                title: "Pematuhan Perdagangan Z-Clear",
                inputLabel: "Teks Invois",
                placeholder: "Tampal teks invois tidak berstruktur di sini...",
                submitBtn: "Ekstrak Maklumat",
                loadingBtn: "Sedang diproses...",
                resultTitle: "Hasil Pengekstrakan",
                lblItem: "Nama Barang",
                lblHsCode: "Kod HS",
                lblWeight: "Berat",
                lblStatus: "Status",
                statusCompleted: "SELESAI",
                statusIncomplete: "TIDAK LENGKAP",
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
                msgRequired: "Nama Barang dan Kod HS diperlukan!"
            }
        };

        let currentLang = 'en';

        function updateStatusUI(statusData, displayStatusObj) {
            const t = translations[currentLang];
            const statusEl = document.getElementById('res-status');
            
            // If the server provides a translated display string, use it
            let displayText = '-';
            if (displayStatusObj && displayStatusObj[currentLang]) {
                displayText = displayStatusObj[currentLang];
            } else if (statusData === 'COMPLETED') {
                displayText = t.statusCompleted;
            } else if (statusData === 'INCOMPLETE') {
                displayText = t.statusIncomplete;
            } else if (statusData === 'AUDITING') {
                displayText = t.statusAuditing;
            } else if (statusData === 'RETRIEVING') {
                displayText = t.statusRetrieving;
            } else if (statusData === 'ERROR') {
                displayText = t.statusError;
            } else {

            statusEl.innerText = displayText;
            
            if (statusData === 'COMPLETED') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-green-100 text-green-800 border border-green-200';
            } else if (statusData === 'INCOMPLETE') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-red-100 text-red-800 border border-red-200';
            } else if (statusData === 'ERROR') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-red-600 text-white border border-red-700';
            } else if (statusData === 'AUDITING') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-blue-100 text-blue-800 border border-blue-200';
            } else if (statusData === 'RETRIEVING') {
                statusEl.className = 'font-semibold px-3 py-1 rounded-full text-sm inline-block bg-purple-100 text-purple-800 border border-purple-200 animate-pulse';
            } else {
        }

        function changeLanguage(lang) {
            currentLang = lang;
            const t = translations[lang];
            
            document.title = t.title;
            document.getElementById('app-title').innerText = t.title;
            document.getElementById('input-label').innerText = t.inputLabel;
            document.getElementById('invoice-text').placeholder = t.placeholder;
            
            // Handle button text specifically to not overwrite spinner when not loading
            const spinner = document.getElementById('loading-spinner');
            if (spinner.classList.contains('hidden')) {
                document.getElementById('btn-text').innerText = t.submitBtn;
            } else {
                document.getElementById('btn-text').innerText = t.loadingBtn;
            }

            document.getElementById('result-title').innerText = t.resultTitle;
            document.getElementById('lbl-item').innerText = t.lblItem;
            document.getElementById('lbl-hscode').innerText = t.lblHsCode;
            document.getElementById('lbl-weight').innerText = t.lblWeight;
            document.getElementById('lbl-status').innerText = t.lblStatus;

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
            }

            // Re-render the status badge to update the translation
            const currentStatus = document.getElementById('res-status').getAttribute('data-status');
            const displayStatusRaw = document.getElementById('res-status').getAttribute('data-display');
            if (currentStatus) {
                let displayObj = null;
                try {
                    if (displayStatusRaw) displayObj = JSON.parse(displayStatusRaw);
                } catch(e) {}
                updateStatusUI(currentStatus, displayObj);
            }
        }

        async function processInvoice() {
            const text = document.getElementById('invoice-text').value;
            if (!text.trim()) return;

            const t = translations[currentLang];
            const btnText = document.getElementById('btn-text');
            const spinner = document.getElementById('loading-spinner');
            const btn = document.getElementById('submit-btn');
            const resultSection = document.getElementById('result-section');

            // UI Loading state
            btnText.innerText = t.loadingBtn;
            spinner.classList.remove('hidden');
            btn.disabled = true;
            btn.classList.add('opacity-75', 'cursor-not-allowed');
            
            // Hide result section smoothly
            resultSection.classList.remove('opacity-100');
            resultSection.classList.add('opacity-0');
            setTimeout(() => { resultSection.classList.add('hidden'); }, 300);

            // Generate a random session ID for this request
            const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId, text: text })
                });

                if (!response.ok) throw new Error('Server returned ' + response.status);

                const data = await response.json();
                
                // Display results
                document.getElementById('res-item').innerText = data.progress.item_name || 'N/A';
                document.getElementById('res-hscode').innerText = data.progress.hs_code || 'N/A';
                document.getElementById('res-weight').innerText = data.progress.weight || 'N/A';
                
                const statusEl = document.getElementById('res-status');
                statusEl.setAttribute('data-status', data.status);
                if (data.display_status) {
                    statusEl.setAttribute('data-display', JSON.stringify(data.display_status));
                }
                updateStatusUI(data.status, data.display_status);

                // Show result section smoothly
                setTimeout(() => {
                    resultSection.classList.remove('hidden');
                    // slight delay to allow display:block to apply before changing opacity
                    setTimeout(() => {
                        resultSection.classList.remove('opacity-0');
                        resultSection.classList.add('opacity-100');
                    }, 50);
                }, 300);

            } catch (error) {
                alert('Error processing invoice: ' + error.message);
            } finally {
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
        }



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

            // ADDED: Automatic Compliance Retrieval trigger
            const resHsCode = document.getElementById('res-hscode') ? document.getElementById('res-hscode').innerText : null;
            const resItem = document.getElementById('res-item') ? document.getElementById('res-item').innerText : null;
            if (resHsCode && resHsCode !== 'N/A' && resHsCode !== '-' && resItem && resItem !== 'N/A' && resItem !== '-') {
                setTimeout(() => {
                    performAutoComplianceRetrieval(sessionId, resHsCode, resItem);
                }, 400);
            }
        }

        // Initialize UI with default language on load
        window.onload = () => {
            changeLanguage(document.getElementById('lang-select').value);
        };
    