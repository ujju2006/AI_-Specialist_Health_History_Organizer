/* ==========================================================================
   HealthVault Pro - Application Logic & UI Controller (app.js)
   ========================================================================== */

const AppState = {
    theme: "light",
    activePane: "dashboard"
};

// Initialize Application UI when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    initState();
    registerInteractions();
    registerFormHandlers();
    if (window.lucide) {
        lucide.createIcons();
    }
});

function initState() {
    // 1. Theme Configuration
    const storedTheme = localStorage.getItem("app_theme") || "light";
    setTheme(storedTheme);

    // 2. Authentication Checks
    if (auth.isAuthenticated()) {
        showAppShell();
    } else {
        showAuthShell();
    }

    // 3. Bind custom auth listener events
    window.addEventListener("unauthorized-endpoint-event", () => {
        showToast("Please log in to continue.", "warning");
        showAuthShell();
    });

    window.addEventListener("session-terminated-event", () => {
        showToast("Session ended successfully.", "success");
        showAuthShell();
    });
}

function setTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("app_theme", theme);

    const themeIcon = document.getElementById("theme-btn-icon");
    if (themeIcon) {
        if (theme === "light") {
            themeIcon.setAttribute("data-lucide", "moon");
        } else {
            themeIcon.setAttribute("data-lucide", "sun");
        }
        if (window.lucide) lucide.createIcons();
    }
}

function showAuthShell() {
    const authFlow = document.getElementById("auth-flow-container");
    const appWorkspace = document.getElementById("app-workspace-container");
    if (authFlow) authFlow.classList.remove("hidden");
    if (appWorkspace) appWorkspace.classList.add("hidden");
}

function updateDynamicGreeting(user) {
    const hour = new Date().getHours();
    let greeting = "Good Evening,";
    if (hour < 12) greeting = "Good Morning,";
    else if (hour < 17) greeting = "Good Afternoon,";

    const name = user ? (user.first_name || (user.email ? user.email.split("@")[0] : "User")) : "";
    const titleEl = document.getElementById("dynamic-greeting-title");
    if (titleEl) titleEl.innerText = `${greeting} ${name} 👋`;
}

function showAppShell() {
    const authFlow = document.getElementById("auth-flow-container");
    const appWorkspace = document.getElementById("app-workspace-container");
    if (authFlow) authFlow.classList.add("hidden");
    if (appWorkspace) appWorkspace.classList.remove("hidden");

    // Display profile details on sidebar
    const user = auth.getCurrentUser();
    if (user) {
        const fullnameEl = document.getElementById("sidebar-user-fullname");
        if (fullnameEl) fullnameEl.innerText = `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email;
        
        const emailEl = document.getElementById("sidebar-user-email");
        if (emailEl) emailEl.innerText = user.email || "";

        const initials = `${user.first_name ? user.first_name[0] : ""}${user.last_name ? user.last_name[0] : ""}`.toUpperCase();
        const avatarEl = document.getElementById("sidebar-avatar-initials");
        if (avatarEl) avatarEl.innerText = initials || "U";

        const roleEl = document.getElementById("sidebar-user-role");
        const menuPatient = document.getElementById("sidebar-menu-patient");
        const menuDoctor = document.getElementById("sidebar-menu-doctor");
        const menuAdmin = document.getElementById("sidebar-menu-admin");

        if (menuPatient) menuPatient.classList.add("hidden");
        if (menuDoctor) menuDoctor.classList.add("hidden");
        if (menuAdmin) menuAdmin.classList.add("hidden");

        let defaultPane = "dashboard";
        if (user.is_admin || user.role === "Administrator" || (user.roles && user.roles.includes("Administrator")) || user.email === "admin@healthvault.pro") {
            if (roleEl) roleEl.innerText = "System Administrator";
            if (menuAdmin) menuAdmin.classList.remove("hidden");
            defaultPane = "admin-dashboard";
        } else if ((user.email && user.email.includes("dr.")) || user.role === "Doctor" || (user.roles && user.roles.includes("Doctor"))) {
            if (roleEl) roleEl.innerText = "Clinical Physician";
            if (menuDoctor) menuDoctor.classList.remove("hidden");
            defaultPane = "doctor-overview";
        } else {
            if (roleEl) roleEl.innerText = "Patient Health Record";
            if (menuPatient) menuPatient.classList.remove("hidden");
            defaultPane = "dashboard";
        }

        // Set Current Formatted Date
        const dateEl = document.getElementById("current-date-text");
        if (dateEl) {
            const now = new Date();
            dateEl.innerText = now.toLocaleDateString('en-US', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
        }

        updateDynamicGreeting(user);

        // Activate role default page
        switchPane(defaultPane);
    }
}

// SPA pane routing function
function switchPane(paneId) {
    if (paneId === "settings-doc" || paneId === "settings-admin") {
        paneId = "settings";
    }
    AppState.activePane = paneId;

    // Toggle nav active backgrounds
    document.querySelectorAll(".sidebar .nav-item").forEach(item => {
        item.classList.remove("active");
    });
    const activeNavItem = document.getElementById(`nav-${paneId}`);
    if (activeNavItem) activeNavItem.classList.add("active");

    // Toggle visible panels
    document.querySelectorAll(".content-pane").forEach(pane => {
        pane.classList.add("hidden");
    });
    const activePaneElement = document.getElementById(`pane-${paneId}`);
    if (activePaneElement) activePaneElement.classList.remove("hidden");

    // Set page headings
    let rawHeading = paneId.replace("admin-", "Admin: ").replace("doctor-", "Physician: ");
    rawHeading = rawHeading.charAt(0).toUpperCase() + rawHeading.slice(1);
    const titleLabel = document.getElementById("page-title-label");
    if (titleLabel) {
        if (paneId === "visits") titleLabel.innerText = "Doctor Consult Visits";
        else if (paneId === "emergency") titleLabel.innerText = "Emergency Medical Profile";
        else if (paneId === "admin-dashboard") titleLabel.innerText = "Administrator Operations & Revenue Unit";
        else if (paneId === "admin-inquiries") titleLabel.innerText = "Patient Inquiry & Email Forwarding Center";
        else if (paneId === "admin-community") titleLabel.innerText = "Upgraded vs Free Community Management";
        else if (paneId === "admin-audit") titleLabel.innerText = "System Security & Compliance Audit Logs";
        else if (paneId === "doctor-overview") titleLabel.innerText = "Physician Triage & Overview";
        else if (paneId === "doctor-patients") titleLabel.innerText = "Comprehensive Patient EHR Review";
        else if (paneId === "doctor-consults") titleLabel.innerText = "Record Consultation & e-Prescription";
        else if (paneId === "doctor-schedule") titleLabel.innerText = "Physician Schedule & Appointments";
        else titleLabel.innerText = rawHeading;
    }

    // Trigger loading actions based on routing
    loadPageData(paneId);
}

// Load data corresponding to the active view pane
async function loadPageData(paneId) {
    try {
        switch (paneId) {
            case "dashboard":
                await loadDashboardOverview();
                break;
            case "vitals":
                await loadVitalsPane();
                break;
            case "conditions":
                await loadConditionsPane();
                break;
            case "medications":
                await loadMedicationsPane();
                break;
            case "visits":
                await loadVisitsPane();
                break;
            case "vaccinations":
                await loadVaccinationsPane();
                break;
            case "documents":
                await loadDocumentsPane();
                break;
            case "emergency":
                if (window.emergency) await emergency.updateEmergencyCard();
                break;
            case "settings":
                await loadSettingsPane();
                break;
            case "admin-dashboard":
                if (window.charts && charts.renderAdminOperations) {
                    charts.renderAdminOperations("chart-admin-operations", "month");
                    charts.renderAdminRevenue("chart-admin-revenue", "month");
                    charts.renderAdminMembership("chart-admin-membership");
                }
                break;
        }
    } catch (e) {
        console.warn(`Failed loading ${paneId} catalog:`, e);
    }
    if (window.lucide) lucide.createIcons();
}

// --- Dashboard Loader ---
async function loadDashboardOverview() {
    let summaryData = null;
    try {
        summaryData = await api.request("/analytics/summary", "GET");
    } catch (e) {
        console.warn("Could not fetch analytics summary:", e);
    }

    if (summaryData) {
        const bpEl = document.getElementById("dash-val-bp");
        if (bpEl && summaryData.blood_pressure) {
            bpEl.innerText = summaryData.blood_pressure.avg_systolic ? `${summaryData.blood_pressure.avg_systolic}/${summaryData.blood_pressure.avg_diastolic}` : "120/80";
        }
        const bpStatusEl = document.getElementById("dash-status-bp");
        if (bpStatusEl && summaryData.blood_pressure) {
            bpStatusEl.innerText = summaryData.blood_pressure.trend || "Normal";
        }

        const weightEl = document.getElementById("dash-val-weight");
        if (weightEl && summaryData.weight_bmi) {
            weightEl.innerText = summaryData.weight_bmi.current_weight || "--";
        }

        const sugarEl = document.getElementById("dash-val-sugar");
        if (sugarEl && summaryData.blood_sugar) {
            sugarEl.innerText = summaryData.blood_sugar.average || "--";
        }

        const pulseEl = document.getElementById("dash-val-pulse");
        if (pulseEl && summaryData.pulse) {
            pulseEl.innerText = summaryData.pulse.avg_bpm || "--";
        }

        const bmiEl = document.getElementById("dash-val-bmi");
        if (bmiEl && summaryData.weight_bmi) {
            bmiEl.innerText = summaryData.weight_bmi.bmi || "--";
        }
    }

    // Render chart
    try {
        const rawVitals = await api.request("/vitals", "GET");
        if (window.charts) {
            charts.renderDashboardOverview("chart-dashboard-trends", rawVitals);
        }
    } catch (e) {
        console.warn("Could not load vitals chart:", e);
    }

    // Load Upcoming Appointments
    try {
        const visits = await api.request("/visits", "GET");
        const apptContainer = document.getElementById("dashboard-appointments-list");
        if (apptContainer) {
            apptContainer.innerHTML = "";
            if (!visits || visits.length === 0) {
                apptContainer.innerHTML = '<div style="font-size:13px; color:var(--text-muted); padding:12px 0;">No consultations recorded yet.</div>';
            } else {
                visits.slice(0, 3).forEach(v => {
                    const row = document.createElement("div");
                    row.className = "list-item-row";
                    row.innerHTML = `
                        <div class="list-icon"><i data-lucide="calendar"></i></div>
                        <div class="list-content">
                            <div class="list-title">${v.specialty || "Clinical Consult"}</div>
                            <div class="list-subtitle">${v.doctor_name}</div>
                        </div>
                        <div class="list-meta">${new Date(v.visit_date).toLocaleDateString()}<br><span class="text-muted" style="font-size: 11px;">Completed</span></div>
                    `;
                    apptContainer.appendChild(row);
                });
            }
        }
    } catch (e) { console.warn(e); }

    // Load Medications
    try {
        const meds = await api.request("/medications", "GET");
        const medsContainer = document.getElementById("dashboard-meds-list");
        if (medsContainer) {
            medsContainer.innerHTML = "";
            if (!meds || meds.length === 0) {
                medsContainer.innerHTML = '<div style="font-size:13px; color:var(--text-muted); padding:12px 0;">No prescriptions recorded yet.</div>';
            } else {
                meds.slice(0, 3).forEach(m => {
                    const row = document.createElement("div");
                    row.className = "list-item-row";
                    row.innerHTML = `
                        <div class="list-icon" style="background: var(--info-bg); color: var(--primary-blue);"><i data-lucide="pill"></i></div>
                        <div class="list-content">
                            <div class="list-title">${m.name} ${m.dosage || ""}</div>
                            <div class="list-subtitle">${m.frequency || "Daily"}</div>
                        </div>
                        <div class="list-meta text-success">${m.status || "Active"}</div>
                    `;
                    medsContainer.appendChild(row);
                });
            }
        }
    } catch (e) { console.warn(e); }

    if (window.lucide) lucide.createIcons();
}

// --- Vitals Loader ---
async function loadVitalsPane() {
    const rawVitals = await api.request("/vitals", "GET");
    const container = document.getElementById("vitals-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!rawVitals || rawVitals.length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="text-secondary" style="text-align: center;">No vital readings recorded yet.</td></tr>';
        return;
    }

    rawVitals.forEach(v => {
        const tr = document.createElement("tr");
        const bpText = v.systolic_bp ? `${v.systolic_bp}/${v.diastolic_bp}` : "--/--";
        const weightText = v.weight_kg ? `${v.weight_kg} kg` : "--";
        const sugarText = v.blood_sugar_mgdl ? `${v.blood_sugar_mgdl} mg/dL` : "--";
        const pulseText = v.pulse_bpm ? `${v.pulse_bpm} bpm` : "--";
        const dateStr = new Date(v.recorded_at).toLocaleDateString() + " " + new Date(v.recorded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        tr.innerHTML = `
            <td class="font-semibold">${dateStr}</td>
            <td><span class="status-badge normal">${bpText}</span></td>
            <td>${weightText}</td>
            <td>${sugarText}</td>
            <td>${pulseText}</td>
            <td>
                <button class="btn-secondary" onclick="deleteVitalRecord('${v.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Delete</button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteVitalRecord(id) {
    if (confirm("Delete this vital reading?")) {
        await api.request(`/vitals/${id}`, "DELETE");
        showToast("Vital reading removed.", "success");
        loadVitalsPane();
    }
}
window.deleteVitalRecord = deleteVitalRecord;

// --- Conditions Loader ---
async function loadConditionsPane() {
    const list = await api.request("/conditions", "GET");
    const container = document.getElementById("conditions-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = '<tr><td colspan="5" class="text-secondary" style="text-align: center;">No conditions recorded yet.</td></tr>';
        return;
    }

    list.forEach(c => {
        const tr = document.createElement("tr");
        const statusClass = c.status === "Active" ? "normal" : "warning";
        tr.innerHTML = `
            <td class="font-semibold">${c.name}</td>
            <td><span class="status-badge ${statusClass}">${c.status}</span></td>
            <td>${c.diagnosed_date || "--"}</td>
            <td class="text-secondary">${c.notes || "No notes"}</td>
            <td>
                <button class="btn-secondary" onclick="deleteConditionRecord('${c.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Delete</button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteConditionRecord(id) {
    if (confirm("Delete this medical condition record?")) {
        await api.request(`/conditions/${id}`, "DELETE");
        showToast("Condition removed.", "success");
        loadConditionsPane();
    }
}
window.deleteConditionRecord = deleteConditionRecord;

// --- Medications Loader ---
async function loadMedicationsPane() {
    const list = await api.request("/medications", "GET");
    const container = document.getElementById("medications-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="text-secondary" style="text-align: center;">No medications recorded yet.</td></tr>';
        return;
    }

    list.forEach(m => {
        const tr = document.createElement("tr");
        const statusClass = m.status === "Active" ? "normal" : "warning";
        tr.innerHTML = `
            <td class="font-semibold">${m.name} <span class="text-muted" style="font-weight:normal;">(${m.dosage || ""})</span></td>
            <td>${m.frequency || "Once daily"}</td>
            <td>${m.start_date || "--"}</td>
            <td><span class="status-badge normal">${m.adherence_rate || 100}%</span></td>
            <td><span class="status-badge ${statusClass}">${m.status}</span></td>
            <td>
                <button class="btn-secondary" onclick="deleteMedicationRecord('${m.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Delete</button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteMedicationRecord(id) {
    if (confirm("Delete this prescription medication record?")) {
        await api.request(`/medications/${id}`, "DELETE");
        showToast("Medication removed.", "success");
        loadMedicationsPane();
    }
}
window.deleteMedicationRecord = deleteMedicationRecord;

// --- Doctor Visits Loader ---
async function loadVisitsPane() {
    const list = await api.request("/visits", "GET");
    const container = document.getElementById("visits-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = '<tr><td colspan="5" class="text-secondary" style="text-align: center;">No clinical consultations recorded yet.</td></tr>';
        return;
    }

    list.forEach(v => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="font-semibold">${v.visit_date || "--"}</td>
            <td>${v.doctor_name} <span class="text-muted" style="font-size: 12px; display: block;">${v.specialty || ""}</span></td>
            <td>${v.symptoms || "--"}</td>
            <td>${v.diagnosis || "--"} <span class="text-muted" style="font-size: 12px; display: block;">${v.notes || ""}</span></td>
            <td>
                <button class="btn-secondary" onclick="deleteVisitRecord('${v.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Delete</button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteVisitRecord(id) {
    if (confirm("Delete this doctor consult note?")) {
        await api.request(`/visits/${id}`, "DELETE");
        showToast("Consult note deleted.", "success");
        loadVisitsPane();
    }
}
window.deleteVisitRecord = deleteVisitRecord;

// --- Vaccinations Loader ---
async function loadVaccinationsPane() {
    const list = await api.request("/vaccinations", "GET");
    const container = document.getElementById("vaccinations-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="text-secondary" style="text-align: center;">No immunization records found.</td></tr>';
        return;
    }

    list.forEach(v => {
        const tr = document.createElement("tr");
        const statusClass = v.status === "Completed" ? "normal" : "warning";
        tr.innerHTML = `
            <td class="font-semibold">${v.vaccine_name}</td>
            <td>${v.dose_number || "Booster"}</td>
            <td>${v.date_administered || "--"}</td>
            <td>${v.next_due_date || "--"}</td>
            <td><span class="status-badge ${statusClass}">${v.status || "Completed"}</span></td>
            <td>
                <button class="btn-secondary" onclick="deleteVaccinationRecord('${v.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i> Delete</button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteVaccinationRecord(id) {
    if (confirm("Delete this vaccination record?")) {
        await api.request(`/vaccinations/${id}`, "DELETE");
        showToast("Vaccine record removed.", "success");
        loadVaccinationsPane();
    }
}
window.deleteVaccinationRecord = deleteVaccinationRecord;

// --- Documents Loader ---
async function loadDocumentsPane() {
    const list = await api.request("/documents", "GET");
    const container = document.getElementById("documents-list-target");
    if (!container) return;
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = '<tr><td colspan="5" class="text-secondary" style="text-align: center;">No medical documents uploaded yet.</td></tr>';
        return;
    }

    list.forEach(d => {
        const sizeMb = d.file_size ? (d.file_size / (1024 * 1024)).toFixed(2) + " MB" : "Unknown";
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="font-semibold"><i data-lucide="file-text" style="color:var(--primary-blue); margin-right:6px; vertical-align:middle; width:16px; height:16px;"></i> ${d.title || "Report"}</td>
            <td class="text-secondary">${d.description || "--"}</td>
            <td>${new Date(d.uploaded_at).toLocaleDateString()}</td>
            <td>${sizeMb}</td>
            <td style="display:flex; gap:6px;">
                <a class="btn-secondary" href="/api/v1/documents/${d.id}/download" target="_blank" style="padding: 4px 8px; font-size: 12px; text-decoration: none;"><i data-lucide="download" style="width: 14px; height: 14px;"></i></a>
                <button class="btn-secondary" onclick="deleteDocumentRecord('${d.id}')" style="padding: 4px 8px; font-size: 12px; color: var(--danger-color); border-color: var(--danger-bg);"><i data-lucide="trash-2" style="width: 14px; height: 14px;"></i></button>
            </td>
        `;
        container.appendChild(tr);
    });
    if (window.lucide) lucide.createIcons();
}

async function deleteDocumentRecord(id) {
    if (confirm("Delete this medical document?")) {
        await api.request(`/documents/${id}`, "DELETE");
        showToast("Document deleted.", "success");
        loadDocumentsPane();
    }
}
window.deleteDocumentRecord = deleteDocumentRecord;

// --- Settings Loader ---
async function loadSettingsPane() {
    const user = auth.getCurrentUser();
    if (user) {
        const fnEl = document.getElementById("set-first-name");
        if (fnEl) fnEl.value = user.first_name || "";
        const lnEl = document.getElementById("set-last-name");
        if (lnEl) lnEl.value = user.last_name || "";
        const phEl = document.getElementById("set-phone");
        if (phEl) phEl.value = user.phone_number || "";
        const dobEl = document.getElementById("set-dob");
        if (dobEl) dobEl.value = user.date_of_birth || "";
        const genEl = document.getElementById("set-gender");
        if (genEl) genEl.value = user.gender || "Male";
    }

    const pe = document.getElementById("pref-email"); if (pe) pe.checked = true;
    const pa = document.getElementById("pref-appointments"); if (pa) pa.checked = true;
    const pm = document.getElementById("pref-meds"); if (pm) pm.checked = true;
}

// --- Bind Interactions & Event Listeners ---
function registerInteractions() {
    // 1. Sidebar Nav triggers routing
    document.querySelectorAll(".sidebar .nav-item").forEach(item => {
        item.addEventListener("click", () => {
            const paneId = item.id.replace("nav-", "");
            switchPane(paneId);
        });
    });

    // 2. Theme Toggle click binds
    const themeBtn = document.getElementById("btn-toggle-theme");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const next = AppState.theme === "dark" ? "light" : "dark";
            setTheme(next);
        });
    }

    // 3. Close search result box
    const closeSearchBtn = document.getElementById("btn-close-search");
    if (closeSearchBtn) {
        closeSearchBtn.addEventListener("click", () => {
            document.getElementById("search-results-panel").classList.add("hidden");
            document.getElementById("global-search-input").value = "";
        });
    }

    // 4. Global search typing binding
    const searchInput = document.getElementById("global-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", debounce(async (e) => {
            const val = e.target.value.trim();
            const searchBox = document.getElementById("search-results-panel");
            const target = document.getElementById("search-matches-target");
            if (!searchBox || !target) return;

            if (val.length < 2) {
                searchBox.classList.add("hidden");
                return;
            }

            try {
                const results = await api.request(`/search?query=${encodeURIComponent(val)}`, "GET");
                target.innerHTML = "";
                searchBox.classList.remove("hidden");

                let hitsCount = 0;
                if (results.conditions && results.conditions.length > 0) {
                    const grp = document.createElement("div");
                    grp.innerHTML = '<h6 style="color:var(--primary-blue); font-weight:600; margin-bottom:6px;">Medical Conditions</h6>';
                    results.conditions.forEach(c => {
                        hitsCount++;
                        grp.innerHTML += `<div style="font-size:13px; padding:6px 0; border-bottom:1px solid var(--border-color);">${c.name} (${c.status})</div>`;
                    });
                    target.appendChild(grp);
                }
                if (results.medications && results.medications.length > 0) {
                    const grp = document.createElement("div");
                    grp.innerHTML = '<h6 style="color:var(--success-color); font-weight:600; margin:12px 0 6px;">Medications</h6>';
                    results.medications.forEach(m => {
                        hitsCount++;
                        grp.innerHTML += `<div style="font-size:13px; padding:6px 0; border-bottom:1px solid var(--border-color);">${m.name} ${m.dosage}</div>`;
                    });
                    target.appendChild(grp);
                }
                if (hitsCount === 0) {
                    target.innerHTML = '<div style="font-size:13px; color:var(--text-muted); padding:8px 0;">No matching medical records found.</div>';
                }
            } catch (err) {
                console.error("Global search call failed:", err);
            }
        }, 300));
    }

    // 5. Setup Auth swapping buttons
    const toReg = document.getElementById("toggle-to-register");
    if (toReg) {
        toReg.addEventListener("click", (e) => {
            e.preventDefault();
            document.getElementById("card-login").classList.add("hidden");
            document.getElementById("card-register").classList.remove("hidden");
        });
    }

    const toLog = document.getElementById("toggle-to-login");
    if (toLog) {
        toLog.addEventListener("click", (e) => {
            e.preventDefault();
            document.getElementById("card-register").classList.add("hidden");
            document.getElementById("card-login").classList.remove("hidden");
        });
    }

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            auth.logout();
        });
    }

    // 6. Quick Demo Account Switchers (Visakhapatnam Network)
    const btnPatient = document.getElementById("btn-demo-patient");
    if (btnPatient) {
        btnPatient.addEventListener("click", async () => {
            try {
                await auth.login("spoorthi.verma@healthvault.pro", "DemoPatient123!");
                showToast("Logged in as Urological Recovered Patient: Spoorthi Verma", "success");
                showAppShell();
            } catch (err) { showToast(err.message || "Login failed", "error"); }
        });
    }

    const btnEmergency = document.getElementById("btn-demo-emergency");
    if (btnEmergency) {
        btnEmergency.addEventListener("click", async () => {
            try {
                await auth.login("ramesh.rao@healthvault.pro", "DemoPatient123!");
                showToast("Logged in as Active Emergency Neuro Patient: Ramesh Rao (QR Active)", "success");
                showAppShell();
            } catch (err) { showToast(err.message || "Login failed", "error"); }
        });
    }

    const btnDoctor = document.getElementById("btn-demo-doctor");
    if (btnDoctor) {
        btnDoctor.addEventListener("click", async () => {
            try {
                await auth.login("dr.rohan@healthvault.pro", "DemoDoctor123!");
                showToast("Logged in as Urology Specialist: Dr. Rohan Sharma", "success");
                showAppShell();
            } catch (err) { showToast(err.message || "Login failed", "error"); }
        });
    }

    const btnDoctorNeuro = document.getElementById("btn-demo-doctor-neuro");
    if (btnDoctorNeuro) {
        btnDoctorNeuro.addEventListener("click", async () => {
            try {
                await auth.login("dr.priya@healthvault.pro", "DemoDoctor123!");
                showToast("Logged in as Neurology Specialist: Dr. Priya Menon", "success");
                showAppShell();
            } catch (err) { showToast(err.message || "Login failed", "error"); }
        });
    }

    const btnAdmin = document.getElementById("btn-demo-admin");
    if (btnAdmin) {
        btnAdmin.addEventListener("click", async () => {
            try {
                await auth.login("admin@healthvault.pro", "DemoAdmin123!");
                showToast("Logged in as Vizag System Administrator", "success");
                showAppShell();
            } catch (err) { showToast(err.message || "Login failed", "error"); }
        });
    }

    // Quick actions shortcuts
    const logVitalsBtn = document.getElementById("btn-quick-log-vitals");
    if (logVitalsBtn) {
        logVitalsBtn.addEventListener("click", () => switchPane("vitals"));
    }

    const gotoVitalsBtn = document.getElementById("btn-goto-vitals-charts");
    if (gotoVitalsBtn) {
        gotoVitalsBtn.addEventListener("click", () => switchPane("vitals"));
    }

    // Modal toggles
    setupModalToggles("btn-trigger-add-condition-modal", "modal-condition");
    setupModalToggles("btn-trigger-add-medication-modal", "modal-medication");
    setupModalToggles("btn-trigger-add-visit-modal", "modal-visit");
    setupModalToggles("btn-trigger-add-vaccination-modal", "modal-vaccination");
    setupModalToggles("btn-trigger-upload-doc-modal", "modal-document");
    setupModalToggles("btn-trigger-emergency-contact-modal", "modal-emergency-contact");
    setupModalToggles("btn-trigger-appointment-modal", "modal-appointment");
}

function setupModalToggles(triggerId, modalId) {
    const trigger = document.getElementById(triggerId);
    const modal = document.getElementById(modalId);

    if (trigger && modal) {
        trigger.addEventListener("click", () => {
            modal.classList.remove("hidden");
            if (window.lucide) lucide.createIcons();
        });
    }
}

// Form Handlers
function registerFormHandlers() {
    // 1. Login submission
    const loginForm = document.getElementById("form-login-credentials");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email-input").value;
            const pass = document.getElementById("login-password-input").value;

            try {
                await auth.login(email, pass);
                showToast("Authentication Successful.", "success");
                showAppShell();
            } catch (err) {
                showToast(err.message || "Invalid credentials.", "error");
            }
        });
    }

    // 2. Register submission
    const regForm = document.getElementById("form-register-new-user");
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const first = document.getElementById("reg-first-name").value;
            const last = document.getElementById("reg-last-name").value;
            const email = document.getElementById("reg-email-input").value;
            const pass = document.getElementById("reg-password-input").value;
            const dob = document.getElementById("reg-dob").value;
            const gender = document.getElementById("reg-gender").value;

            try {
                await auth.register(email, pass, first, last, dob, gender);
                showToast("Patient profile registered! Please sign in.", "success");
                document.getElementById("card-register").classList.add("hidden");
                document.getElementById("card-login").classList.remove("hidden");
            } catch (err) {
                showToast(err.message || "Registration failed.", "error");
            }
        });
    }

    // 3. Post vitals Form
    const vitalsForm = document.getElementById("form-add-vitals");
    if (vitalsForm) {
        vitalsForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                systolic_bp: parseFloat(document.getElementById("vital-systolic").value) || null,
                diastolic_bp: parseFloat(document.getElementById("vital-diastolic").value) || null,
                weight_kg: parseFloat(document.getElementById("vital-weight").value) || null,
                height_cm: parseFloat(document.getElementById("vital-height").value) || null,
                blood_sugar_mgdl: parseFloat(document.getElementById("vital-sugar").value) || null,
                pulse_bpm: parseFloat(document.getElementById("vital-pulse").value) || null,
                temperature_c: parseFloat(document.getElementById("vital-temp").value) || null,
                oxygen_saturation: parseFloat(document.getElementById("vital-oxygen").value) || null
            };

            try {
                await api.request("/vitals", "POST", payload);
                showToast("Vitals reading logged.", "success");
                vitalsForm.reset();
                loadVitalsPane();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 4. Add Condition
    const condForm = document.getElementById("form-condition");
    if (condForm) {
        condForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById("cond-name").value,
                status: document.getElementById("cond-status").value,
                diagnosed_date: document.getElementById("cond-date").value,
                notes: document.getElementById("cond-notes").value
            };

            try {
                await api.request("/conditions", "POST", payload);
                document.getElementById("modal-condition").classList.add("hidden");
                condForm.reset();
                showToast("Condition logged.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 5. Add Medication
    const medForm = document.getElementById("form-medication");
    if (medForm) {
        medForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById("med-name").value,
                dosage: document.getElementById("med-dosage").value,
                frequency: document.getElementById("med-frequency").value,
                start_date: document.getElementById("med-start-date").value,
                end_date: document.getElementById("med-end-date").value || null,
                status: document.getElementById("med-status").value,
                adherence_rate: parseFloat(document.getElementById("med-adherence").value) || 100
            };

            try {
                await api.request("/medications", "POST", payload);
                document.getElementById("modal-medication").classList.add("hidden");
                medForm.reset();
                showToast("Prescription saved.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 6. Add Visit
    const visitForm = document.getElementById("form-visit");
    if (visitForm) {
        visitForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                doctor_name: document.getElementById("visit-doctor").value,
                specialty: document.getElementById("visit-specialty").value,
                visit_date: document.getElementById("visit-date").value,
                symptoms: document.getElementById("visit-symptoms").value,
                diagnosis: document.getElementById("visit-diagnosis").value,
                notes: document.getElementById("visit-notes").value
            };

            try {
                await api.request("/visits", "POST", payload);
                document.getElementById("modal-visit").classList.add("hidden");
                visitForm.reset();
                showToast("Consultation notes saved.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 7. Add Vaccination
    const vaccForm = document.getElementById("form-vaccination");
    if (vaccForm) {
        vaccForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                vaccine_name: document.getElementById("vacc-name").value,
                dose_number: document.getElementById("vacc-dose").value,
                date_administered: document.getElementById("vacc-date").value || null,
                next_due_date: document.getElementById("vacc-due").value || null,
                status: document.getElementById("vacc-status").value
            };

            try {
                await api.request("/vaccinations", "POST", payload);
                document.getElementById("modal-vaccination").classList.add("hidden");
                vaccForm.reset();
                showToast("Immunization recorded.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 8. Add Appointment
    const apptForm = document.getElementById("form-appointment");
    if (apptForm) {
        apptForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                doctor_name: document.getElementById("app-doctor").value,
                specialty: document.getElementById("app-specialty").value,
                appointment_date: new Date(document.getElementById("app-datetime").value).toISOString(),
                location: document.getElementById("app-location").value
            };

            try {
                await api.request("/appointments", "POST", payload);
                document.getElementById("modal-appointment").classList.add("hidden");
                apptForm.reset();
                showToast("Appointment booked.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 9. Upload Document
    const docForm = document.getElementById("form-document");
    if (docForm) {
        docForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData();
            formData.append("title", document.getElementById("doc-title").value);
            formData.append("description", document.getElementById("doc-desc").value);
            const fileInput = document.getElementById("doc-file");
            if (fileInput && fileInput.files[0]) {
                formData.append("file", fileInput.files[0]);
            }

            try {
                await api.request("/documents", "POST", formData, true);
                document.getElementById("modal-document").classList.add("hidden");
                docForm.reset();
                showToast("Report uploaded.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 10. Add Emergency Contact
    const emForm = document.getElementById("form-emergency-contact");
    if (emForm) {
        emForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById("em-contact-name").value,
                relationship: document.getElementById("em-contact-relationship").value,
                phone_number: document.getElementById("em-contact-phone").value,
                email: document.getElementById("em-contact-email").value || null,
                blood_group: document.getElementById("em-contact-blood").value,
                notes: document.getElementById("em-contact-notes").value || null
            };

            try {
                await api.request("/emergency", "POST", payload);
                document.getElementById("modal-emergency-contact").classList.add("hidden");
                emForm.reset();
                showToast("Emergency contact saved.", "success");
                loadPageData(AppState.activePane);
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 11. Profile Update
    const profForm = document.getElementById("form-update-profile");
    if (profForm) {
        profForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                first_name: document.getElementById("set-first-name").value,
                last_name: document.getElementById("set-last-name").value,
                phone_number: document.getElementById("set-phone").value || null,
                date_of_birth: document.getElementById("set-dob").value,
                gender: document.getElementById("set-gender").value
            };

            try {
                const updated = await api.request("/auth/me", "PUT", payload);
                sessionStorage.setItem("current_user", JSON.stringify(updated));
                showToast("Account profile updated.", "success");
                showAppShell();
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    // 12. Password Change
    const pwdForm = document.getElementById("form-change-password");
    if (pwdForm) {
        pwdForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const payload = {
                current_password: document.getElementById("pwd-current").value,
                new_password: document.getElementById("pwd-new").value
            };

            try {
                await api.request("/auth/me/password", "PUT", payload);
                pwdForm.reset();
                showToast("Password updated successfully.", "success");
            } catch (err) {
                showToast(err.message, "error");
            }
        });
    }

    const prefBtn = document.getElementById("btn-save-preferences");
    if (prefBtn) {
        prefBtn.addEventListener("click", () => {
            showToast("Alert preferences updated.", "success");
        });
    }
}

// Sleek Toast Notification Helper (Replaces intrusive alerts)
function showToast(msg, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    // Prevent duplicate spam if an identical toast is already displayed
    const existingToasts = container.querySelectorAll(".toast span");
    for (let i = 0; i < existingToasts.length; i++) {
        if (existingToasts[i].innerText.trim() === msg.trim()) {
            return;
        }
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    let icon = "check-circle";
    if (type === "error") icon = "alert-circle";
    if (type === "warning") icon = "alert-triangle";

    toast.innerHTML = `<i data-lucide="${icon}"></i> <span>${msg}</span>`;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 200ms ease";
        setTimeout(() => toast.remove(), 200);
    }, 4000);
}

function showSuccessMessage(msg) {
    showToast(msg, "success");
}

function showErrorMessage(msg) {
    showToast(msg, "error");
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// =========================================================
// SYSTEM ADMINISTRATOR PORTAL INTERACTIVE HELPERS
// =========================================================

// 1. Admin Graph Time Horizon Filter
function switchAdminGraphHorizon(period) {
    ["week", "month", "year"].forEach(p => {
        const btn = document.getElementById(`btn-admin-graph-${p}`);
        if (btn) btn.classList.remove("active");
    });
    const activeBtn = document.getElementById(`btn-admin-graph-${period}`);
    if (activeBtn) activeBtn.classList.add("active");

    if (window.charts && charts.renderAdminOperations) {
        charts.renderAdminOperations("chart-admin-operations", period);
    }
    showToast(`Displaying Visakhapatnam Grid operations for Past ${period.charAt(0).toUpperCase() + period.slice(1)}`, "info");
}
window.switchAdminGraphHorizon = switchAdminGraphHorizon;

function switchAdminRevenueHorizon(period) {
    if (window.charts && charts.renderAdminRevenue) {
        charts.renderAdminRevenue("chart-admin-revenue", period);
    }
    showToast(`Displaying Simulated Revenue Analytics for Past ${period.charAt(0).toUpperCase() + period.slice(1)}`, "info");
}
window.switchAdminRevenueHorizon = switchAdminRevenueHorizon;

// 2. Patient Email & Inquiry Forwarding
function forwardPatientEmail(rowId, patientName, targetDoc) {
    const statusEl = document.getElementById(`status-inq-${rowId}`);
    if (statusEl) {
        statusEl.className = "badge badge-normal";
        statusEl.innerText = `Forwarded to ${targetDoc.split(" ")[1] || "Specialist"}`;
    }

    const dashStatusEl = document.getElementById(`dash-inq-status-${rowId}`);
    if (dashStatusEl) {
        dashStatusEl.className = "badge badge-warning";
        dashStatusEl.style.background = "rgba(245, 158, 11, 0.15)";
        dashStatusEl.style.color = "#f59e0b";
        dashStatusEl.innerText = "Forwarded";
    }

    const rowEl = document.getElementById(`row-inq-${rowId}`);
    if (rowEl) {
        const btnTd = rowEl.cells[rowEl.cells.length - 1];
        if (btnTd) {
            btnTd.innerHTML = `<button type="button" class="btn-secondary" style="padding: 6px 12px; font-size: 12px;" disabled><i data-lucide="check" style="width:14px;height:14px;"></i> Shared with Doc</button>`;
        }
    }

    const countBadge = document.getElementById("admin-unforwarded-count");
    if (countBadge) {
        let currentText = countBadge.innerText.trim();
        if (currentText.includes("2")) {
            countBadge.innerText = "1 Unforwarded Patient Email";
        } else {
            countBadge.innerText = "All Patient Emails Forwarded ✓";
            countBadge.style.background = "rgba(16, 185, 129, 0.15)";
            countBadge.style.color = "#10b981";
        }
    }

    let fwdList = JSON.parse(localStorage.getItem("hv_forwarded_inquiries") || "[]");
    fwdList.push({ rowId, patientName, targetDoc, timestamp: new Date().toISOString() });
    localStorage.setItem("hv_forwarded_inquiries", JSON.stringify(fwdList));

    showToast(`Inquiry from ${patientName} forwarded to ${targetDoc} with Admin triage priority!`, "success");
    if (window.lucide) lucide.createIcons();
}

// 3. Community Tier Management (Upgraded vs Free)
function toggleCommunityTier(rowId, patientName, upgradeToPremium) {
    const badgeEl = document.getElementById(`comm-badge-${rowId}`);
    const feeEl = document.getElementById(`comm-fee-${rowId}`);
    const rowEl = document.getElementById(`comm-row-${rowId}`);
    const revEl = document.getElementById("admin-val-revenue");
    const upgEl = document.getElementById("admin-val-upgraded");

    if (upgradeToPremium) {
        if (badgeEl) {
            badgeEl.style.background = "rgba(139, 92, 246, 0.2)";
            badgeEl.style.color = "#8b5cf6";
            badgeEl.style.fontWeight = "700";
            badgeEl.style.border = "1px solid #8b5cf6";
            badgeEl.innerHTML = "👑 Upgraded Community";
        }
        if (feeEl) {
            feeEl.style.fontWeight = "700";
            feeEl.style.color = "#10b981";
            feeEl.innerText = "₹999 / yr (Paid)";
        }
        if (rowEl) {
            const btnTd = rowEl.cells[rowEl.cells.length - 1];
            if (btnTd) {
                btnTd.innerHTML = `<button type="button" class="btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="toggleCommunityTier(${rowId}, '${patientName}', false)">Downgrade to Free ⬇️</button>`;
            }
        }
        if (revEl) {
            revEl.innerText = "Revenue Index";
        }
        if (upgEl) {
            let currentUpg = parseInt(upgEl.innerText.replace(/[^0-9]/g, "")) || 1420;
            currentUpg += 1;
            upgEl.innerText = currentUpg.toLocaleString('en-IN');
        }
        showToast(`${patientName} upgraded to Upgraded Community (Premium Tier)! Priority Emergency Grid enabled.`, "success");
    } else {
        if (badgeEl) {
            badgeEl.style.background = "rgba(100, 116, 139, 0.15)";
            badgeEl.style.color = "#64748b";
            badgeEl.style.fontWeight = "600";
            badgeEl.style.border = "none";
            badgeEl.innerHTML = "🆓 Free Community";
        }
        if (feeEl) {
            feeEl.style.fontWeight = "500";
            feeEl.style.color = "#64748b";
            feeEl.innerText = "Simulated Standard Tier";
        }
        if (rowEl) {
            const btnTd = rowEl.cells[rowEl.cells.length - 1];
            if (btnTd) {
                btnTd.innerHTML = `<button type="button" class="btn-primary" style="padding: 6px 12px; font-size: 12px; background: #8b5cf6;" onclick="toggleCommunityTier(${rowId}, '${patientName}', true)">Upgrade Membership ⬆️</button>`;
            }
        }
        if (revEl) {
            revEl.innerText = "Revenue Index";
        }
        if (upgEl) {
            let currentUpg = parseInt(upgEl.innerText.replace(/[^0-9]/g, "")) || 1421;
            currentUpg = Math.max(0, currentUpg - 1);
            upgEl.innerText = currentUpg.toLocaleString('en-IN');
        }
        showToast(`${patientName} moved to Free Community tier.`, "info");
    }
}
