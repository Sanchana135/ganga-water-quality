document.addEventListener('DOMContentLoaded', function () {
    const stationSelect = document.getElementById('station-select');
    const btnGen = document.getElementById('btn-gen-reading');
    const btnToggle = document.getElementById('btn-live-toggle');

    let autoSimTimer = null;
    let isSimulating = false;
    let monitoringChart = null;

    loadStationData(stationSelect.value);

    stationSelect.addEventListener('change', function () {
        loadStationData(this.value);
    });

    btnGen.addEventListener('click', function () {
        triggerSimulatedReading(stationSelect.value);
    });

    btnToggle.addEventListener('click', function () {
        isSimulating = !isSimulating;
        if (isSimulating) {
            btnToggle.innerHTML = '<i class="fa-solid fa-pause"></i> Pause Auto Simulation';
            btnToggle.classList.remove('btn-outline');
            btnToggle.classList.add('btn-primary');
            autoSimTimer = setInterval(() => {
                triggerSimulatedReading(stationSelect.value);
            }, 4000);
        } else {
            btnToggle.innerHTML = '<i class="fa-solid fa-play"></i> Start Auto Simulation';
            btnToggle.classList.remove('btn-primary');
            btnToggle.classList.add('btn-outline');
            clearInterval(autoSimTimer);
        }
    });

    function loadStationData(stationId) {
        fetch(`/api/stations/${stationId}`)
            .then(res => res.json())
            .then(data => {
                updateMonitoringUI(data);
            })
            .catch(err => console.error("Error loading station telemetry:", err));
    }

    function triggerSimulatedReading(stationId) {
        fetch('/api/readings/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ station_id: parseInt(stationId) })
        })
        .then(res => res.json())
        .then(resData => {
            loadStationData(stationId);
        })
        .catch(err => console.error("Error triggering IoT reading:", err));
    }

    function updateMonitoringUI(data) {
        const r = data.latest_reading;
        const wq = data.latest_wqi;

        if (r && wq) {
            document.getElementById('card-ph').textContent = r.ph.toFixed(2);
            document.getElementById('card-do').innerHTML = `${r.dissolved_oxygen.toFixed(2)} <span style="font-size: 0.85rem;">mg/L</span>`;
            document.getElementById('card-turb').innerHTML = `${r.turbidity.toFixed(1)} <span style="font-size: 0.85rem;">NTU</span>`;
            document.getElementById('card-wqi').textContent = wq.wqi.toFixed(1);
            
            const badgeEl = document.getElementById('card-wqi-badge');
            badgeEl.className = `badge-status ${wq.quality_category.toLowerCase()}`;
            badgeEl.textContent = wq.quality_category;

            document.getElementById('card-tds').innerHTML = `${r.tds.toFixed(1)} <span style="font-size: 0.85rem;">mg/L</span>`;
            document.getElementById('card-cond').innerHTML = `${r.conductivity.toFixed(1)} <span style="font-size: 0.85rem;">µS/cm</span>`;
            document.getElementById('card-bod').innerHTML = `${r.bod.toFixed(2)} <span style="font-size: 0.85rem;">mg/L</span>`;
            document.getElementById('card-cod').innerHTML = `${r.cod.toFixed(2)} <span style="font-size: 0.85rem;">mg/L</span>`;

            document.getElementById('latest-timestamp').textContent = `Last sync: ${r.timestamp}`;
        }

        renderStreamTable(data.historical_readings);
        renderMonitoringChart(data.historical_readings);
    }

    function renderStreamTable(readings) {
        const tbody = document.getElementById('telemetry-stream-tbody');
        if (!tbody) return;

        if (!readings || readings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No telemetry logs recorded.</td></tr>';
            return;
        }

        tbody.innerHTML = readings.slice(0, 15).map(r => `
            <tr>
                <td>${r.timestamp.split(' ')[1] || r.timestamp}</td>
                <td>${r.ph.toFixed(2)}</td>
                <td>${r.dissolved_oxygen.toFixed(2)}</td>
                <td>${r.turbidity.toFixed(1)}</td>
                <td>${r.bod.toFixed(2)}</td>
                <td><strong>${r.tds > 0 ? (r.ph * 6.5).toFixed(1) : '--'}</strong></td>
            </tr>
        `).join('');
    }

    function renderMonitoringChart(readings) {
        if (!readings || readings.length === 0) return;

        const sliced = readings.slice(0, 20).reverse();
        const timestamps = sliced.map(r => r.timestamp.split(' ')[1] || r.timestamp);
        const doVals = sliced.map(r => r.dissolved_oxygen);
        const turbVals = sliced.map(r => r.turbidity);
        const bodVals = sliced.map(r => r.bod);

        const ctx = document.getElementById('monitoringChart').getContext('2d');
        if (monitoringChart) monitoringChart.destroy();

        monitoringChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [
                    {
                        label: 'Dissolved Oxygen (mg/L)',
                        data: doVals,
                        borderColor: '#10B981',
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Turbidity (NTU)',
                        data: turbVals,
                        borderColor: '#F59E0B',
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'BOD (mg/L)',
                        data: bodVals,
                        borderColor: '#EF4444',
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }
});
