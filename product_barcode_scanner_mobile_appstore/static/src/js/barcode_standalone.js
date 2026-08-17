/**
 * Escáner Móvil PRO - Engine con soporte para Consulta y Conteos Cíclicos
 * Author: Omar Martinez
 */
document.addEventListener("DOMContentLoaded", function () {
    // App State
    let html5QrCode = null;
    let isCameraActive = false;
    let soundEnabled = localStorage.getItem("scanner_sound") !== "false";
    let torchEnabled = false;
    let currentVideoTrack = null;
    let currentMode = "lookup"; // 'lookup' or 'cycle'
    let activeCycleSession = JSON.parse(localStorage.getItem("active_cycle_session") || "null");
    let recentScans = JSON.parse(localStorage.getItem("scanner_recent_scans") || "[]");

    // Audio Synthesizer (Web Audio API)
    function playBeep() {
        if (!soundEnabled) return;
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.12);
        } catch (e) {
            console.warn("Audio Context Error:", e);
        }
    }

    function triggerHaptic() {
        if (navigator.vibrate) {
            try {
                navigator.vibrate(80);
            } catch (e) {}
        }
    }

    // UI Elements
    const elInput = document.getElementById("manual_barcode_input");
    const btnClearInput = document.getElementById("btn_clear_input");
    const btnSearch = document.getElementById("btn_search_barcode");
    const searchForm = document.getElementById("scanner_search_form");
    const btnToggleCam = document.getElementById("btn_toggle_camera");
    const nativeCamInput = document.getElementById("native_camera_input");
    const cameraViewport = document.getElementById("camera_viewport_container");
    const btnStopCam = document.getElementById("btn_stop_camera");
    const btnSwitchCam = document.getElementById("btn_switch_cam");
    const btnToggleTorch = document.getElementById("btn_toggle_torch");
    const btnToggleSound = document.getElementById("btn_toggle_sound");

    const cardEmpty = document.getElementById("scanner_empty_state");
    const cardResult = document.getElementById("scanner_result_card");
    const alertError = document.getElementById("scanner_error_alert");
    const errorMsg = document.getElementById("scanner_error_message");
    const toast = document.getElementById("scanner_toast");
    const toastText = document.getElementById("toast_text");

    // Mode Tabs
    const tabLookup = document.getElementById("tab_mode_lookup");
    const tabCycle = document.getElementById("tab_mode_cycle");

    // Cycle Count UI Elements
    const cycleBanner = document.getElementById("cycle_count_banner");
    const cycleSessionCode = document.getElementById("cycle_session_code");
    const ccStatLines = document.getElementById("cc_stat_lines");
    const ccStatSys = document.getElementById("cc_stat_sys");
    const ccStatCnt = document.getElementById("cc_stat_cnt");
    const btnCcStart = document.getElementById("btn_cc_start");
    const btnCcFinish = document.getElementById("btn_cc_finish");
    const cycleLiveSection = document.getElementById("cycle_count_live_section");
    const cycleLiveTbody = document.getElementById("cycle_live_tbody");
    const ccLiveBadge = document.getElementById("cc_live_badge");

    // Cycle Summary Modal Elements
    const ccSummaryModal = document.getElementById("cc_summary_modal");
    const sumLinesCount = document.getElementById("sum_lines_count");
    const sumSysQty = document.getElementById("sum_sys_qty");
    const sumCntQty = document.getElementById("sum_cnt_qty");
    const sumDiffQty = document.getElementById("sum_diff_qty");
    const sumDiffUsd = document.getElementById("sum_diff_usd");
    const ccSummaryTbody = document.getElementById("cc_summary_tbody");
    const btnDownloadExcel = document.getElementById("btn_download_excel");
    const btnCloseCcSummary = document.getElementById("btn_close_cc_summary");
    const btnCloseCcSummaryX = document.getElementById("btn_close_cc_summary_x");

    // Result Card Elements
    const resBarcode = document.getElementById("res_barcode");
    const resSku = document.getElementById("res_default_code");
    const resStockBadge = document.getElementById("res_stock_badge");
    const resStockText = document.getElementById("res_stock_text");
    const resImgContainer = document.getElementById("res_img_container");
    const resImage = document.getElementById("res_image");
    const resName = document.getElementById("res_name");
    const resCategory = document.getElementById("res_category");
    const resBrand = document.getElementById("res_product_brand");
    const resBrandCar = document.getElementById("res_brand_car");
    const resLocation = document.getElementById("res_location");
    const resUom = document.getElementById("res_uom");

    // Multi-Warehouse Stock Breakdown
    const whDakar = document.getElementById("wh_qty_dakar");
    const whDF = document.getElementById("wh_qty_df");
    const whJQC = document.getElementById("wh_qty_jqc");
    const whKalani = document.getElementById("wh_qty_kalani");
    const whTotalBadge = document.getElementById("res_wh_total_badge");

    // Price Hero
    const resPrice = document.getElementById("res_price");
    const resPriceVes = document.getElementById("res_price_ves");
    const resBcvRate = document.getElementById("res_bcv_rate");

    // Action Buttons
    const btnCopySpecs = document.getElementById("btn_copy_specs");
    const btnShareWhatsapp = document.getElementById("btn_share_whatsapp");
    const btnOpenOdoo = document.getElementById("btn_open_odoo");
    const btnScanNext = document.getElementById("btn_scan_next");

    // Dashboard Stats & History
    const dashScannedCount = document.getElementById("dash_scanned_count");
    const dashBcvVal = document.getElementById("dash_bcv_val");
    const headerBcvRate = document.getElementById("header_bcv_rate");
    const recentScansSection = document.getElementById("recent_scans_section");
    const recentScansList = document.getElementById("recent_scans_list");
    const btnClearHistory = document.getElementById("btn_clear_history");

    // Lightbox & Modal
    const lightboxModal = document.getElementById("image_lightbox_modal");
    const lightboxImg = document.getElementById("lightbox_img");
    const btnCloseLightbox = document.getElementById("btn_close_lightbox");

    const odooModalBackdrop = document.getElementById("odoo_modal_backdrop");
    const odooModalHeading = document.getElementById("odoo_modal_heading");
    const odooModalMessage = document.getElementById("odoo_modal_message");
    const odooModalTechnicalBox = document.getElementById("odoo_modal_technical_box");
    const odooModalTechnicalText = document.getElementById("odoo_modal_technical_text");
    const btnCloseOdooModal = document.getElementById("btn_close_odoo_modal");
    const btnCloseOdooModalX = document.getElementById("btn_close_odoo_modal_x");

    // Initial Data Fetch
    fetchInitialData();
    updateHistoryUI();

    // Setup Mode Tabs
    if (tabLookup && tabCycle) {
        tabLookup.addEventListener("click", () => switchMode("lookup"));
        tabCycle.addEventListener("click", () => switchMode("cycle"));
    }

    function switchMode(newMode) {
        currentMode = newMode;
        if (newMode === "lookup") {
            if (tabLookup) tabLookup.classList.add("active");
            if (tabCycle) tabCycle.classList.remove("active");
            if (cycleBanner) cycleBanner.classList.add("d-none");
            if (cycleLiveSection) cycleLiveSection.classList.add("d-none");
            if (cardResult) cardResult.classList.add("d-none");
            if (cardEmpty) cardEmpty.classList.remove("d-none");
        } else {
            if (tabCycle) tabCycle.classList.add("active");
            if (tabLookup) tabLookup.classList.remove("active");
            if (cycleBanner) cycleBanner.classList.remove("d-none");
            if (cardEmpty) cardEmpty.classList.add("d-none");
            if (cardResult) cardResult.classList.add("d-none");

            if (activeCycleSession) {
                renderCycleSessionUI(activeCycleSession);
            } else {
                renderNoActiveSessionUI();
            }
        }
        if (elInput) elInput.focus();
    }

    // Sound toggle handler
    if (btnToggleSound) {
        updateSoundUI();
        btnToggleSound.addEventListener("click", function () {
            soundEnabled = !soundEnabled;
            localStorage.setItem("scanner_sound", soundEnabled);
            updateSoundUI();
            if (soundEnabled) playBeep();
        });
    }

    function updateSoundUI() {
        if (!btnToggleSound) return;
        const icon = document.getElementById("sound_icon");
        if (soundEnabled) {
            btnToggleSound.classList.add("active");
            if (icon) icon.textContent = "🔊";
        } else {
            btnToggleSound.classList.remove("active");
            if (icon) icon.textContent = "🔇";
        }
    }

    function showToast(msg) {
        if (!toast || !toastText) return;
        toastText.textContent = msg;
        toast.classList.remove("d-none");
        toast.classList.add("show");
        setTimeout(function () {
            toast.classList.remove("show");
            setTimeout(() => toast.classList.add("d-none"), 300);
        }, 2200);
    }

    function showOdooModal(title, msg, techDetails = null) {
        if (!odooModalBackdrop) return;
        odooModalHeading.textContent = title || "Aviso del Lector";
        odooModalMessage.textContent = msg || "";
        if (techDetails) {
            odooModalTechnicalText.textContent = techDetails;
            odooModalTechnicalBox.classList.remove("d-none");
        } else {
            odooModalTechnicalBox.classList.add("d-none");
        }
        odooModalBackdrop.classList.remove("d-none");
    }

    function hideOdooModal() {
        if (odooModalBackdrop) odooModalBackdrop.classList.add("d-none");
    }

    if (btnCloseOdooModal) btnCloseOdooModal.addEventListener("click", hideOdooModal);
    if (btnCloseOdooModalX) btnCloseOdooModalX.addEventListener("click", hideOdooModal);

    function fetchInitialData() {
        fetch("/product_scanner/initial_data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} }),
        })
            .then((r) => r.json())
            .then((res) => {
                if (res.result && res.result.formatted_bcv_rate) {
                    if (headerBcvRate) headerBcvRate.textContent = res.result.formatted_bcv_rate;
                    if (dashBcvVal) dashBcvVal.textContent = res.result.formatted_bcv_rate;
                }
            })
            .catch((err) => console.warn("BCV Rate fetch error:", err));
    }

    if (elInput) {
        elInput.addEventListener("input", function () {
            if (btnClearInput) {
                if (this.value.trim().length > 0) {
                    btnClearInput.classList.remove("d-none");
                } else {
                    btnClearInput.classList.add("d-none");
                }
            }
        });
    }

    if (btnClearInput) {
        btnClearInput.addEventListener("click", function () {
            if (elInput) {
                elInput.value = "";
                elInput.focus();
            }
            btnClearInput.classList.add("d-none");
            if (alertError) alertError.classList.add("d-none");
        });
    }

    if (searchForm) {
        searchForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const val = elInput ? elInput.value.trim() : "";
            if (val) {
                if (currentMode === "lookup") {
                    performBarcodeSearch(val);
                } else {
                    performCycleCountScan(val);
                }
            }
        });
    }

    // --- LOOKUP MODE SEARCH ---
    function performBarcodeSearch(barcodeTerm) {
        if (!barcodeTerm) return;

        if (alertError) alertError.classList.add("d-none");

        fetch("/product_scanner/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: { barcode: barcodeTerm },
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.error) {
                    showOdooModal("Error de Servidor", data.error.message || "Error en el servidor", JSON.stringify(data.error.data || data.error));
                    return;
                }
                const result = data.result;
                if (!result) {
                    showInlineError("No se recibió respuesta del servidor");
                    return;
                }
                if (!result.success) {
                    showInlineError(result.message || "Producto no encontrado");
                    playBeep();
                    return;
                }

                playBeep();
                triggerHaptic();
                renderProductResult(result.product);
                addToHistory(result.product);
            })
            .catch((err) => {
                showInlineError("Error de conexión a la red");
                console.error("RPC Search error:", err);
            });
    }

    // --- CYCLE COUNT SCAN ENGINE ---
    function performCycleCountScan(barcodeTerm) {
        if (!barcodeTerm) return;

        if (!activeCycleSession) {
            startNewCycleSession(() => performCycleCountScan(barcodeTerm));
            return;
        }

        if (alertError) alertError.classList.add("d-none");

        fetch("/product_scanner/cycle_count/add_line", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                    session_id: activeCycleSession.id,
                    barcode: barcodeTerm,
                },
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.error) {
                    showOdooModal("Error de Conteo", data.error.message || "Error al agregar producto", JSON.stringify(data.error));
                    return;
                }
                const res_val = data.result;
                if (!res_val.success) {
                    showInlineError(res_val.message || "Error al escanear producto");
                    playBeep();
                    return;
                }

                playBeep();
                triggerHaptic();

                // Save updated session
                activeCycleSession = res_val.session;
                localStorage.setItem("active_cycle_session", JSON.stringify(activeCycleSession));

                renderCycleSessionUI(activeCycleSession);
                showToast(`✅ +1 ${res_val.product.name}`);

                if (elInput) {
                    elInput.value = "";
                    elInput.focus();
                }
            })
            .catch((err) => console.error("Cycle scan RPC error:", err));
    }

    function startNewCycleSession(callback = null) {
        fetch("/product_scanner/cycle_count/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.result && data.result.success) {
                    activeCycleSession = data.result.session;
                    localStorage.setItem("active_cycle_session", JSON.stringify(activeCycleSession));
                    renderCycleSessionUI(activeCycleSession);
                    showToast(`🚀 Sesión ${activeCycleSession.name} Iniciada`);
                    if (callback) callback();
                } else {
                    showOdooModal("Error", (data.result && data.result.message) || "No se pudo iniciar sesión de conteo");
                }
            })
            .catch((err) => console.error("Start session error:", err));
    }

    function updateLineQty(lineId, newQty) {
        if (!activeCycleSession) return;

        fetch("/product_scanner/cycle_count/update_qty", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: { line_id: lineId, new_qty: newQty },
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.result && data.result.success) {
                    activeCycleSession = data.result.session;
                    localStorage.setItem("active_cycle_session", JSON.stringify(activeCycleSession));
                    renderCycleSessionUI(activeCycleSession);
                }
            })
            .catch((err) => console.error("Update line qty error:", err));
    }

    function finishCycleSession() {
        if (!activeCycleSession) return;

        fetch("/product_scanner/cycle_count/finish", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: { session_id: activeCycleSession.id },
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.result && data.result.success) {
                    const sessionData = data.result.session;
                    activeCycleSession = null;
                    localStorage.removeItem("active_cycle_session");

                    renderNoActiveSessionUI();
                    showCycleSummaryModal(sessionData);
                } else {
                    showOdooModal("Error", (data.result && data.result.message) || "No se pudo finalizar la sesión");
                }
            })
            .catch((err) => console.error("Finish session error:", err));
    }

    // Cycle UI Renderers
    function renderNoActiveSessionUI() {
        if (cycleSessionCode) cycleSessionCode.textContent = "CC/NUEVO";
        if (ccStatLines) ccStatLines.textContent = "0";
        if (ccStatSys) ccStatSys.textContent = "0";
        if (ccStatCnt) ccStatCnt.textContent = "0";
        if (btnCcStart) btnCcStart.classList.remove("d-none");
        if (btnCcFinish) btnCcFinish.classList.add("d-none");
        if (cycleLiveSection) cycleLiveSection.classList.add("d-none");
    }

    function renderCycleSessionUI(s) {
        if (!s) {
            renderNoActiveSessionUI();
            return;
        }

        if (cycleSessionCode) cycleSessionCode.textContent = s.name;
        if (ccStatLines) ccStatLines.textContent = s.total_lines;
        if (ccStatSys) ccStatSys.textContent = s.total_system_qty;
        if (ccStatCnt) ccStatCnt.textContent = s.total_counted_qty;

        if (btnCcStart) btnCcStart.classList.add("d-none");
        if (btnCcFinish) btnCcFinish.classList.remove("d-none");

        if (cycleLiveSection) cycleLiveSection.classList.remove("d-none");
        if (ccLiveBadge) ccLiveBadge.textContent = `${s.total_lines} productos`;

        if (!cycleLiveTbody) return;
        cycleLiveTbody.innerHTML = "";

        s.lines.forEach((l) => {
            const tr = document.createElement("tr");

            let diffBadgeClass = "diff-zero";
            let diffPrefix = "";
            if (l.difference_qty > 0) {
                diffBadgeClass = "diff-pos";
                diffPrefix = "+";
            } else if (l.difference_qty < 0) {
                diffBadgeClass = "diff-neg";
            }

            tr.innerHTML = `
                <td>
                    <div class="line-prod-cell">
                        <img src="${l.image_url}" class="line-prod-img" alt=""/>
                        <div class="line-prod-info">
                            <span class="line-code">${l.default_code} | ${l.barcode}</span>
                            <span class="line-name">${l.product_name}</span>
                        </div>
                    </div>
                </td>
                <td class="text-center font-bold">${l.system_qty}</td>
                <td class="text-center">
                    <div class="qty-control-wrapper">
                        <button type="button" class="btn-qty-step step-dec" data-line-id="${l.id}" data-current-qty="${l.counted_qty}">-</button>
                        <input type="number" class="input-line-qty" data-line-id="${l.id}" value="${l.counted_qty}" step="1" min="0"/>
                        <button type="button" class="btn-qty-step step-inc" data-line-id="${l.id}" data-current-qty="${l.counted_qty}">+</button>
                    </div>
                </td>
                <td class="text-center">
                    <span class="diff-badge ${diffBadgeClass}">${diffPrefix}${l.difference_qty}</span>
                </td>
            `;

            cycleLiveTbody.appendChild(tr);
        });

        // Attach event listeners for +/- and quantity inputs
        cycleLiveTbody.querySelectorAll(".step-dec").forEach((btn) => {
            btn.addEventListener("click", function () {
                const lineId = parseInt(this.dataset.lineId);
                const curQty = float(this.dataset.currentQty);
                updateLineQty(lineId, Math.max(0, curQty - 1));
            });
        });

        cycleLiveTbody.querySelectorAll(".step-inc").forEach((btn) => {
            btn.addEventListener("click", function () {
                const lineId = parseInt(this.dataset.lineId);
                const curQty = float(this.dataset.currentQty);
                updateLineQty(lineId, curQty + 1);
            });
        });

        cycleLiveTbody.querySelectorAll(".input-line-qty").forEach((input) => {
            input.addEventListener("change", function () {
                const lineId = parseInt(this.dataset.lineId);
                const val = float(this.value);
                updateLineQty(lineId, val);
            });
        });
    }

    function float(val) {
        const parsed = parseFloat(val);
        return isNaN(parsed) ? 0.0 : parsed;
    }

    // Session Start & Finish Button Listeners
    if (btnCcStart) btnCcStart.addEventListener("click", () => startNewCycleSession());
    if (btnCcFinish) btnCcFinish.addEventListener("click", () => finishCycleSession());

    // Cycle Summary Modal Renderer
    function showCycleSummaryModal(s) {
        if (!ccSummaryModal) return;

        if (sumLinesCount) sumLinesCount.textContent = s.total_lines;
        if (sumSysQty) sumSysQty.textContent = s.total_system_qty;
        if (sumCntQty) sumCntQty.textContent = s.total_counted_qty;
        if (sumDiffQty) {
            const pref = s.total_diff_qty > 0 ? "+" : "";
            sumDiffQty.textContent = `${pref}${s.total_diff_qty}`;
        }
        if (sumDiffUsd) sumDiffUsd.textContent = s.formatted_total_diff_usd;

        if (btnDownloadExcel) btnDownloadExcel.href = s.excel_url;

        if (ccSummaryTbody) {
            ccSummaryTbody.innerHTML = "";
            s.lines.forEach((l) => {
                const tr = document.createElement("tr");
                let diffClass = "text-emerald";
                let pref = "";
                if (l.difference_qty > 0) {
                    diffClass = "text-blue";
                    pref = "+";
                } else if (l.difference_qty < 0) {
                    diffClass = "text-rose";
                }

                tr.innerHTML = `
                    <td style="font-size:0.82rem;"><strong>[${l.default_code}]</strong> ${l.product_name}</td>
                    <td class="text-center">${l.system_qty}</td>
                    <td class="text-center font-bold">${l.counted_qty}</td>
                    <td class="text-center ${diffClass} font-bold">${pref}${l.difference_qty}</td>
                    <td class="text-center ${diffClass} font-bold">${l.formatted_diff_usd}</td>
                `;
                ccSummaryTbody.appendChild(tr);
            });
        }

        ccSummaryModal.classList.remove("d-none");
    }

    function hideCcSummaryModal() {
        if (ccSummaryModal) ccSummaryModal.classList.add("d-none");
    }

    if (btnCloseCcSummary) btnCloseCcSummary.addEventListener("click", hideCcSummaryModal);
    if (btnCloseCcSummaryX) btnCloseCcSummaryX.addEventListener("click", hideCcSummaryModal);

    function showInlineError(msg) {
        if (errorMsg) errorMsg.textContent = msg;
        if (alertError) alertError.classList.remove("d-none");
    }

    // Render Product Details Card
    function renderProductResult(p) {
        if (!p) return;

        if (cardEmpty) cardEmpty.classList.add("d-none");

        if (resBarcode) resBarcode.textContent = p.barcode || "N/A";
        if (resSku) resSku.textContent = p.default_code || "N/A";

        if (resStockBadge && resStockText) {
            const qty = p.qty_available || 0;
            if (qty > 0) {
                resStockBadge.className = "stock-status-pill in-stock";
                resStockText.textContent = `EN STOCK (${qty})`;
            } else {
                resStockBadge.className = "stock-status-pill out-of-stock";
                resStockText.textContent = "AGOTADO (0)";
            }
        }

        if (resImage) resImage.src = p.image_url || "/web/static/img/placeholder.png";

        if (resName) resName.textContent = p.name || "Producto sin nombre";
        if (resCategory) resCategory.textContent = p.category || "General";
        if (resBrand) resBrand.textContent = p.product_brand || "N/A";
        if (resBrandCar) resBrandCar.textContent = p.brand_car || "N/A";
        if (resLocation) resLocation.textContent = p.location || "Sin Ubicación";
        if (resUom) resUom.textContent = p.uom || "Unidades";

        const whStockGrid = document.getElementById("wh_stock_grid");
        if (whStockGrid) {
            whStockGrid.innerHTML = "";
            if (p.warehouses_stock && p.warehouses_stock.length > 0) {
                p.warehouses_stock.forEach(wh => {
                    const item = document.createElement("div");
                    item.className = "wh-stock-item";
                    item.innerHTML = `<span class="wh-name">${wh.name}</span><span class="wh-val">${wh.qty} Uds</span>`;
                    whStockGrid.appendChild(item);
                });
            } else {
                const item = document.createElement("div");
                item.className = "wh-stock-item";
                item.innerHTML = `<span class="wh-name">Almacén</span><span class="wh-val">${p.qty_available || 0} Uds</span>`;
                whStockGrid.appendChild(item);
            }
        } else {
            if (whDakar) whDakar.textContent = `${p.stock_dakar || 0} Uds`;
            if (whDF) whDF.textContent = `${p.stock_df || 0} Uds`;
            if (whJQC) whJQC.textContent = `${p.stock_jqc || 0} Uds`;
            if (whKalani) whKalani.textContent = `${p.stock_kalani || 0} Uds`;
        }
        if (whTotalBadge) whTotalBadge.textContent = `Total: ${p.qty_available || 0} Uds`;

        if (resPrice) resPrice.textContent = p.formatted_price || `$${(p.list_price || 0).toFixed(2)} USD`;
        if (resPriceVes) resPriceVes.textContent = p.formatted_price_ves || "0.00 Bs.";
        if (resBcvRate) resBcvRate.textContent = p.formatted_bcv_rate ? `(Tasa BCV: ${p.formatted_bcv_rate})` : "";

        if (btnOpenOdoo && p.odoo_url) {
            btnOpenOdoo.href = p.odoo_url;
        }

        cardResult.dataset.activeProduct = JSON.stringify(p);

        cardResult.classList.remove("d-none");
        cardResult.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    if (btnCopySpecs) {
        btnCopySpecs.addEventListener("click", function () {
            if (!cardResult.dataset.activeProduct) return;
            const p = JSON.parse(cardResult.dataset.activeProduct);
            const text = `📦 *${p.name}*
🏷️ Ref/SKU: ${p.default_code}
📊 Barcode: ${p.barcode}
🏷️ Marca: ${p.product_brand} | Carro: ${p.brand_car}
📍 Ubicación: ${p.location}
🏬 Stock Total: ${p.qty_available} Uds (Dakar:${p.stock_dakar} | DF:${p.stock_df} | JQC:${p.stock_jqc} | Kalani:${p.stock_kalani})
💰 Precio: ${p.formatted_price} / ${p.formatted_price_ves}`;

            navigator.clipboard.writeText(text).then(
                () => showToast("📋 Ficha copiada al portapapeles"),
                () => showToast("Error al copiar ficha")
            );
        });
    }

    if (btnShareWhatsapp) {
        btnShareWhatsapp.addEventListener("click", function () {
            if (!cardResult.dataset.activeProduct) return;
            const p = JSON.parse(cardResult.dataset.activeProduct);
            const text = `📦 *${p.name}*
🏷️ Ref: ${p.default_code} | Barcode: ${p.barcode}
🏷️ Marca: ${p.product_brand} | Carro: ${p.brand_car}
🏬 Stock Total: ${p.qty_available} Uds
💰 Precio: ${p.formatted_price} (${p.formatted_price_ves})`;

            const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
            window.open(url, "_blank");
        });
    }

    if (btnScanNext) {
        btnScanNext.addEventListener("click", function () {
            cardResult.classList.add("d-none");
            if (cardEmpty) cardEmpty.classList.remove("d-none");
            if (elInput) {
                elInput.value = "";
                elInput.focus();
            }
            if (btnClearInput) btnClearInput.classList.add("d-none");
        });
    }

    if (resImgContainer) {
        resImgContainer.addEventListener("click", function () {
            if (resImage && resImage.src) {
                lightboxImg.src = resImage.src;
                lightboxModal.classList.remove("d-none");
            }
        });
    }

    if (btnCloseLightbox) {
        btnCloseLightbox.addEventListener("click", function () {
            lightboxModal.classList.add("d-none");
        });
    }

    if (lightboxModal) {
        lightboxModal.addEventListener("click", function (e) {
            if (e.target === lightboxModal) {
                lightboxModal.classList.add("d-none");
            }
        });
    }

    function addToHistory(product) {
        if (!product || !product.id) return;
        recentScans = recentScans.filter((item) => item.id !== product.id);
        recentScans.unshift(product);
        if (recentScans.length > 15) recentScans.pop();
        localStorage.setItem("scanner_recent_scans", JSON.stringify(recentScans));
        updateHistoryUI();
    }

    function updateHistoryUI() {
        if (dashScannedCount) dashScannedCount.textContent = recentScans.length;
        if (!recentScansList || !recentScansSection) return;

        if (recentScans.length === 0) {
            recentScansSection.classList.add("d-none");
            return;
        }

        recentScansSection.classList.remove("d-none");
        recentScansList.innerHTML = "";

        recentScans.forEach((item) => {
            const chip = document.createElement("div");
            chip.className = "recent-scan-chip";
            chip.innerHTML = `
                <img src="${item.image_url || '/web/static/img/placeholder.png'}" class="chip-img" alt=""/>
                <div class="chip-info">
                    <span class="chip-code">${item.default_code || item.barcode}</span>
                    <span class="chip-name">${item.name}</span>
                </div>
                <span class="chip-price">${item.formatted_price}</span>
            `;

            chip.addEventListener("click", function () {
                renderProductResult(item);
            });

            recentScansList.appendChild(chip);
        });
    }

    if (btnClearHistory) {
        btnClearHistory.addEventListener("click", function () {
            recentScans = [];
            localStorage.removeItem("scanner_recent_scans");
            updateHistoryUI();
            showToast("Historial limpiado");
        });
    }

    // --- CAMERA SCANNER ENGINE ---
    if (btnToggleCam) {
        btnToggleCam.addEventListener("click", function (e) {
            if (typeof Html5Qrcode !== "undefined") {
                e.preventDefault();
                startCameraScanner();
            }
        });
    }

    if (nativeCamInput) {
        nativeCamInput.addEventListener("change", function (e) {
            if (e.target.files && e.target.files.length > 0) {
                const file = e.target.files[0];
                if (typeof Html5Qrcode !== "undefined") {
                    const tempReader = new Html5Qrcode("html5qr_code_reader");
                    tempReader
                        .scanFile(file, true)
                        .then((decodedText) => {
                            if (currentMode === "lookup") {
                                performBarcodeSearch(decodedText);
                            } else {
                                performCycleCountScan(decodedText);
                            }
                            tempReader.clear();
                        })
                        .catch((err) => {
                            showToast("No se detectó código en la imagen");
                            tempReader.clear();
                        });
                }
            }
        });
    }

    function startCameraScanner() {
        if (isCameraActive) return;

        if (cameraViewport) cameraViewport.classList.remove("d-none");

        html5QrCode = new Html5Qrcode("html5qr_code_reader");

        const config = {
            fps: 15,
            qrbox: { width: 260, height: 180 },
            aspectRatio: 1.0,
            experimentalFeatures: {
                useBarCodeDetectorIfSupported: true,
            },
        };

        html5QrCode
            .start(
                { facingMode: "environment" },
                config,
                (decodedText, decodedResult) => {
                    playBeep();
                    triggerHaptic();
                    stopCameraScanner();
                    if (elInput) elInput.value = decodedText;
                    if (currentMode === "lookup") {
                        performBarcodeSearch(decodedText);
                    } else {
                        performCycleCountScan(decodedText);
                    }
                },
                (errorMessage) => {}
            )
            .then(() => {
                isCameraActive = true;
                try {
                    const videoEl = document.querySelector("#html5qr_code_reader video");
                    if (videoEl && videoEl.srcObject) {
                        const tracks = videoEl.srcObject.getVideoTracks();
                        if (tracks.length > 0) {
                            currentVideoTrack = tracks[0];
                            const capabilities = currentVideoTrack.getCapabilities ? currentVideoTrack.getCapabilities() : {};
                            if (btnToggleTorch && capabilities.torch) {
                                btnToggleTorch.classList.remove("d-none");
                            }
                        }
                    }
                } catch (e) {}
            })
            .catch((err) => {
                console.error("Camera start error:", err);
                stopCameraScanner();
                showToast("Presione 'Activar' para capturar fotos de códigos");
                if (nativeCamInput) nativeCamInput.click();
            });
    }

    function stopCameraScanner() {
        if (html5QrCode && isCameraActive) {
            html5QrCode
                .stop()
                .then(() => {
                    html5QrCode.clear();
                    isCameraActive = false;
                    currentVideoTrack = null;
                    torchEnabled = false;
                    if (cameraViewport) cameraViewport.classList.add("d-none");
                })
                .catch((err) => {
                    console.error("Camera stop error:", err);
                    isCameraActive = false;
                    if (cameraViewport) cameraViewport.classList.add("d-none");
                });
        } else {
            if (cameraViewport) cameraViewport.classList.add("d-none");
        }
    }

    if (btnStopCam) btnStopCam.addEventListener("click", stopCameraScanner);

    if (btnToggleTorch) {
        btnToggleTorch.addEventListener("click", function () {
            if (currentVideoTrack && currentVideoTrack.applyConstraints) {
                torchEnabled = !torchEnabled;
                currentVideoTrack
                    .applyConstraints({
                        advanced: [{ torch: torchEnabled }],
                    })
                    .then(() => {
                        btnToggleTorch.classList.toggle("active", torchEnabled);
                        showToast(torchEnabled ? "🔦 Linterna Encendida" : "🔦 Linterna Apagada");
                    })
                    .catch((err) => showToast("Linterna no soportada en este dispositivo"));
            } else {
                showToast("Linterna no disponible");
            }
        });
    }
});
