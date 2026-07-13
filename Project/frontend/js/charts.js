class ChartsManager {
    constructor() {
        this.charts = {};
        // Set Chart.js global defaults for soft light theme
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
            Chart.defaults.color = "#64748B";
            Chart.defaults.scale.grid.color = "#E5EAF1";
            Chart.defaults.plugins.tooltip.backgroundColor = "#0F172A";
            Chart.defaults.plugins.tooltip.titleColor = "#FFFFFF";
            Chart.defaults.plugins.tooltip.bodyColor = "#F8FAFC";
            Chart.defaults.plugins.tooltip.cornerRadius = 8;
            Chart.defaults.plugins.tooltip.padding = 10;
        }
    }

    destroyChart(id) {
        if (this.charts[id]) {
            this.charts[id].destroy();
            delete this.charts[id];
        }
    }

    formatLabelDate(isoString) {
        try {
            const date = new Date(isoString);
            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        } catch (e) {
            return "";
        }
    }

    renderDashboardOverview(canvasId, vitals) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const dataSorted = [...vitals].slice(0, 7).reverse();
        if (dataSorted.length === 0) {
            this.renderEmptyState(ctx);
            return;
        }

        const labels = dataSorted.map(v => this.formatLabelDate(v.recorded_at));
        const systolic = dataSorted.map(v => v.systolic_bp || 120);
        const sugar = dataSorted.map(v => v.blood_sugar_mgdl || 95);
        const heartRate = dataSorted.map(v => v.pulse_bpm || 72);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Blood Pressure (Systolic)',
                        data: systolic,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: '#3B82F6',
                        pointRadius: 4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Blood Sugar (mg/dL)',
                        data: sugar,
                        borderColor: '#16A34A',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        tension: 0.3,
                        pointBackgroundColor: '#16A34A',
                        pointRadius: 4,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Heart Rate (bpm)',
                        data: heartRate,
                        borderColor: '#EF4444',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.3,
                        pointBackgroundColor: '#EF4444',
                        pointRadius: 4,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8,
                            padding: 16,
                            font: { size: 12, weight: '500' },
                            color: '#0F172A'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#64748B', font: { size: 11 } },
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: { color: '#64748B', font: { size: 11 } },
                        grid: { color: '#E5EAF1' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#64748B', font: { size: 11 } },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    renderBpChart(canvasId, vitals) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const dataSorted = [...vitals].slice(0, 10).reverse();
        const records = dataSorted.filter(v => v.systolic_bp !== null && v.diastolic_bp !== null);
        if (records.length === 0) return;

        const labels = records.map(v => this.formatLabelDate(v.recorded_at));
        const systolic = records.map(v => v.systolic_bp);
        const diastolic = records.map(v => v.diastolic_bp);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Systolic BP (mmHg)',
                        data: systolic,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2
                    },
                    {
                        label: 'Diastolic BP (mmHg)',
                        data: diastolic,
                        borderColor: '#60A5FA',
                        backgroundColor: 'rgba(96, 165, 250, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { usePointStyle: true, color: '#0F172A' } } },
                scales: {
                    x: { ticks: { color: '#64748B' }, grid: { display: false } },
                    y: { ticks: { color: '#64748b' }, grid: { color: '#E5EAF1' } }
                }
            }
        });
    }

    renderWeightChart(canvasId, vitals) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const dataSorted = [...vitals].slice(0, 10).reverse();
        const records = dataSorted.filter(v => v.weight_kg !== null);
        if (records.length === 0) return;

        const labels = records.map(v => this.formatLabelDate(v.recorded_at));
        const weights = records.map(v => v.weight_kg);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Weight (kg)',
                        data: weights,
                        borderColor: '#16A34A',
                        backgroundColor: 'rgba(22, 163, 74, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { usePointStyle: true, color: '#0F172A' } } },
                scales: {
                    x: { ticks: { color: '#64748B' }, grid: { display: false } },
                    y: { ticks: { color: '#64748b' }, grid: { color: '#E5EAF1' } }
                }
            }
        });
    }

    renderSugarChart(canvasId, vitals) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const dataSorted = [...vitals].slice(0, 10).reverse();
        const records = dataSorted.filter(v => v.blood_sugar_mgdl !== null);
        if (records.length === 0) return;

        const labels = records.map(v => this.formatLabelDate(v.recorded_at));
        const sugar = records.map(v => v.blood_sugar_mgdl);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Blood Sugar (mg/dL)',
                        data: sugar,
                        borderColor: '#F59E0B',
                        backgroundColor: 'rgba(245, 158, 11, 0.08)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { usePointStyle: true, color: '#0F172A' } } },
                scales: {
                    x: { ticks: { color: '#64748B' }, grid: { display: false } },
                    y: { ticks: { color: '#64748b' }, grid: { color: '#E5EAF1' } }
                }
            }
        });
    }

    renderAdherenceChart(canvasId, medications) {
        this.destroyChart(canvasId);
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (!medications || medications.length === 0) return;

        const labels = medications.map(m => m.name);
        const rates = medications.map(m => m.adherence_rate || 100);

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Adherence Rate (%)',
                        data: rates,
                        backgroundColor: '#3B82F6',
                        borderRadius: 6,
                        barThickness: 24
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top', labels: { usePointStyle: true, color: '#0F172A' } } },
                scales: {
                    x: { ticks: { color: '#64748B' }, grid: { display: false } },
                    y: { min: 0, max: 100, ticks: { color: '#64748b' }, grid: { color: '#E5EAF1' } }
                }
            }
        });
    }

    renderAdminOperations(canvasId, period = "week") {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        let labels = [];
        let consultsData = [];
        let icuGridData = [];

        if (period === "week") {
            labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            consultsData = [48, 52, 65, 58, 72, 60, 45];
            icuGridData = [12, 14, 15, 11, 18, 16, 14];
        } else if (period === "month") {
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            consultsData = [320, 380, 410, 450];
            icuGridData = [85, 92, 98, 105];
        } else {
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            consultsData = [1200, 1350, 1420, 1580, 1750, 1920, 2150, 2380, 2650, 2980, 3200, 3480];
            icuGridData = [310, 340, 360, 390, 420, 450, 480, 510, 540, 580, 610, 650];
        }

        const ctx = canvas.getContext('2d');
        const grad1 = ctx.createLinearGradient(0, 0, 0, 300);
        grad1.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
        grad1.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        const grad2 = ctx.createLinearGradient(0, 0, 0, 300);
        grad2.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
        grad2.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        this.charts[canvasId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Network Consultations (Demo Healthcare Network Vizag)',
                        data: consultsData,
                        borderColor: '#3b82f6',
                        backgroundColor: grad1,
                        fill: true,
                        tension: 0.3,
                        borderWidth: 3,
                        pointBackgroundColor: '#3b82f6',
                        pointRadius: 4
                    },
                    {
                        label: 'Active Emergency Telemetry Grid Connections',
                        data: icuGridData,
                        borderColor: '#8b5cf6',
                        backgroundColor: grad2,
                        fill: true,
                        tension: 0.3,
                        borderWidth: 3,
                        pointBackgroundColor: '#8b5cf6',
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { font: { family: 'Outfit', size: 13, weight: '600' }, color: '#334155' }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        padding: 12,
                        titleFont: { family: 'Outfit', size: 14, weight: '700' },
                        bodyFont: { family: 'Outfit', size: 13 }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Outfit', size: 12 }, color: '#64748b' }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(226, 232, 240, 0.6)' },
                        ticks: { font: { family: 'Outfit', size: 12 }, color: '#64748b' }
                    }
                }
            }
        });
    }

    renderAdminRevenue(canvasId, period = "month") {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        let labels = [];
        let revenueData = [];

        if (period === "month") {
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            revenueData = [3.8, 4.5, 4.9, 5.25];
        } else {
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            revenueData = [11.2, 12.4, 13.1, 14.2, 15.0, 15.8, 16.5, 17.1, 17.8, 18.2, 18.45, 19.1];
        }

        this.charts[canvasId] = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Simulated Network Revenue (₹ Lakhs)',
                        data: revenueData,
                        backgroundColor: '#10b981',
                        borderRadius: 6,
                        barThickness: period === 'month' ? 32 : 18
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { font: { family: 'Outfit', size: 13, weight: '600' }, color: '#334155' }
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `₹ ${context.raw} Lakhs`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Outfit', size: 12 }, color: '#64748b' }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(226, 232, 240, 0.6)' },
                        ticks: { font: { family: 'Outfit', size: 12 }, color: '#64748b', callback: val => `₹ ${val}L` }
                    }
                }
            }
        });
    }

    renderAdminMembership(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        this.charts[canvasId] = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Upgraded Premium', 'Free Community'],
                datasets: [
                    {
                        data: [6842, 5616],
                        backgroundColor: ['#3b82f6', '#10b981'],
                        hoverOffset: 4,
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        padding: 10,
                        callbacks: {
                            label: function(context) {
                                const total = 12458;
                                const pct = ((context.raw / total) * 100).toFixed(1);
                                return `${context.label}: ${context.raw.toLocaleString()} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderEmptyState(canvasElement) {
        const parent = canvasElement.parentElement;
        if (parent && !parent.querySelector('.empty-chart-note')) {
            const note = document.createElement('div');
            note.className = 'empty-chart-note';
            note.style.cssText = 'position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #94A3B8; font-size: 13px; font-weight: 500; background: #FFFFFF; border-radius: 12px; border: 1px dashed #E5EAF1;';
            note.innerText = 'Log physiological readings to generate trends analysis.';
            parent.appendChild(note);
        }
    }
}

const charts = new ChartsManager();
window.charts = charts;
