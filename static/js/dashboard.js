document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
});

let trendChart = null;
let miniMap = null;

function loadDashboardData() {
    fetch('/api/dashboard/stats')
        .then(res => res.json())
        .then(data => {
            updateDashboardMetrics(data);
            initTrendChart(data);
            initDashboardMiniMap(data.latest_readings);
            renderStationsTable(data.latest_readings);
            renderAlertsList(data.recent_alerts);
        })
        .catch(err => console.error("Error loading dashboard data:", err));
}

function updateDashboardMetrics(data) {
    document.getElementById('stat-wqi').textContent = data.avg_wqi.toFixed(1);
    
    const badgeEl = document.getElementById('stat-status-badge');
    const status = data.overall_status.toLowerCase();
    badgeEl.className = `badge-status ${status}`;
    badgeEl.textContent = data.overall_status;

    // Calculate averages across stations
    if (data.latest_readings && data.latest_readings.length > 0) {
        const avgDo = data.latest_readings.reduce((acc, r) => acc + r.dissolved_oxygen, 0) / data.latest_readings.length;
        const avgTurb = data.latest_readings.reduce((acc, r) => acc + r.turbidity, 0) / data.latest_readings.length;
        
        document.getElementById('stat-do').innerHTML = `${avgDo.toFixed(1)} <span style="font-size: 0.9rem;">mg/L</span>`;
        document.getElementById('stat-turb').innerHTML = `${avgTurb.toFixed(1)} <span style="font-size: 0.9rem;">NTU</span>`;
    }

    document.getElementById('stat-alerts-count').textContent = data.recent_alerts ? data.recent_alerts.length : 0;
}

function initTrendChart(data) {
    fetch('/api/analytics?days=30')
        .then(res => res.json())
        .then(chartData => {
            const ctx = document.getElementById('dashboardTrendChart').getContext('2d');
            if (trendChart) trendChart.destroy();

            trendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.timestamps,
                    datasets: [{
                        label: 'Ganga Basin Avg WQI',
                        data: chartData.wqi,
                        borderColor: '#00A896',
                        backgroundColor: 'rgba(0, 168, 150, 0.08)',
                        fill: true,
                        tension: 0.35,
                        pointRadius: 2
                    }, {
                        label: 'Dissolved Oxygen (mg/L)',
                        data: chartData.dissolved_oxygen,
                        borderColor: '#10B981',
                        borderDash: [4, 4],
                        fill: false,
                        tension: 0.3,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top' }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        });
}

function initDashboardMiniMap(stations) {
    if (!document.getElementById('dashboard-mini-map')) return;
    if (miniMap) miniMap.remove();

    miniMap = L.map('dashboard-mini-map').setView([26.8, 81.5], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(miniMap);

    stations.forEach(st => {
        let markerColor = '#10B981'; // Good/Excellent
        if (st.wqi > 100) markerColor = '#EF4444';
        else if (st.wqi > 75) markerColor = '#E76F51';
        else if (st.wqi > 50) markerColor = '#F59E0B';

        const circle = L.circleMarker([st.lat, st.lng], {
            color: markerColor,
            fillColor: markerColor,
            fillOpacity: 0.8,
            radius: 9
        }).addTo(miniMap);

        circle.bindPopup(`
            <div style="font-family: 'Inter', sans-serif;">
                <strong style="font-size: 1rem;">${st.station_name}</strong><br>
                <span class="badge-status ${st.quality_category.toLowerCase()}" style="margin: 4px 0; display: inline-block;">${st.quality_category}</span><br>
                <b>WQI:</b> ${st.wqi} | <b>DO:</b> ${st.dissolved_oxygen} mg/L<br>
                <b>Turbidity:</b> ${st.turbidity} NTU
            </div>
        `);
    });
}

function renderStationsTable(readings) {
    const tbody = document.getElementById('dashboard-stations-tbody');
    if (!tbody) return;

    if (!readings || readings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No station readings available.</td></tr>';
        return;
    }

    tbody.innerHTML = readings.map(r => `
        <tr>
            <td><strong>${r.station_name}</strong></td>
            <td>${r.ph.toFixed(2)}</td>
            <td>${r.dissolved_oxygen.toFixed(2)}</td>
            <td>${r.turbidity.toFixed(1)}</td>
            <td><strong>${r.wqi.toFixed(1)}</strong></td>
            <td><span class="badge-status ${r.quality_category.toLowerCase()}">${r.quality_category}</span></td>
        </tr>
    `).join('');
}

function renderAlertsList(alerts) {
    const container = document.getElementById('dashboard-alerts-container');
    if (!container) return;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 1.5rem;"><i class="fa-solid fa-circle-check text-success"></i> No active early warning alerts.</div>';
        return;
    }

    container.innerHTML = alerts.map(a => `
        <div class="alert-box ${a.severity}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <strong style="font-size: 0.9rem;">${a.alert_type} - ${a.station_name}</strong>
                <span class="badge-severity ${a.severity}">${a.severity}</span>
            </div>
            <p style="font-size: 0.82rem; color: var(--text-primary); margin-bottom: 0.3rem;">${a.message}</p>
            <div style="font-size: 0.72rem; color: var(--text-muted);">${a.created_at}</div>
        </div>
    `).join('');
}
