document.addEventListener('DOMContentLoaded', function () {
    const stationSelect = document.getElementById('forecast-station-select');
    const horizonSelect = document.getElementById('forecast-horizon-select');
    const rainfallInput = document.getElementById('forecast-rainfall-input');
    const btnRun = document.getElementById('btn-run-forecast');

    let forecastChart = null;

    // Run initial forecast
    runForecast();

    btnRun.addEventListener('click', runForecast);

    function runForecast() {
        const payload = {
            station_id: parseInt(stationSelect.value),
            horizon_hours: parseInt(horizonSelect.value),
            rainfall_mm: parseFloat(rainfallInput.value) || 0.0
        };

        fetch('/api/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            updateForecastUI(data);
        })
        .catch(err => console.error("Error executing forecast:", err));
    }

    function updateForecastUI(data) {
        const curr = data.current;
        const fc = data.forecast;
        const metrics = data.model_metrics;

        // Current status
        document.getElementById('curr-wqi').textContent = curr.wqi.toFixed(1);
        document.getElementById('curr-do').textContent = curr.do.toFixed(2);
        document.getElementById('curr-turb').textContent = curr.turbidity.toFixed(1);
        
        const currBadge = document.getElementById('curr-badge');
        currBadge.className = `badge-status ${curr.category.toLowerCase()}`;
        currBadge.textContent = curr.category;

        // Predicted status
        document.getElementById('pred-wqi').textContent = fc.predicted_wqi.toFixed(1);
        document.getElementById('pred-do').textContent = fc.predicted_do.toFixed(2);
        document.getElementById('pred-turb').textContent = fc.predicted_turbidity.toFixed(1);
        document.getElementById('pred-confidence').textContent = `${fc.confidence.toFixed(1)}% Confidence`;

        const predBadge = document.getElementById('pred-badge');
        predBadge.className = `badge-status ${fc.predicted_category.toLowerCase()}`;
        predBadge.textContent = fc.predicted_category;

        // Update metrics
        if (metrics) {
            document.getElementById('metric-mae').textContent = metrics.mae.toFixed(4);
            document.getElementById('metric-rmse').textContent = metrics.rmse.toFixed(4);
            document.getElementById('metric-r2').textContent = metrics.r2.toFixed(4);
            document.getElementById('metric-acc').textContent = `${(metrics.accuracy * 100).toFixed(2)}%`;
        }

        renderTrajectoryChart(data.trajectory);
    }

    function renderTrajectoryChart(trajectory) {
        if (!trajectory || trajectory.length === 0) return;

        const labels = trajectory.map(t => t.timestamp);
        const wqiData = trajectory.map(t => t.wqi);
        const doData = trajectory.map(t => t.do);

        const pointBackgrounds = trajectory.map(t => t.type === 'forecast' ? '#EF4444' : '#00A896');
        const pointRadii = trajectory.map(t => t.type === 'forecast' ? 7 : 4);

        const ctx = document.getElementById('forecastChart').getContext('2d');
        if (forecastChart) forecastChart.destroy();

        forecastChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Water Quality Index (WQI)',
                        data: wqiData,
                        borderColor: '#0B2545',
                        backgroundColor: 'rgba(11, 37, 69, 0.05)',
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: pointBackgrounds,
                        pointRadius: pointRadii
                    },
                    {
                        label: 'Dissolved Oxygen (DO mg/L)',
                        data: doData,
                        borderColor: '#10B981',
                        borderDash: [5, 5],
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterBody: function(context) {
                                const idx = context[0].dataIndex;
                                if (trajectory[idx].type === 'forecast') {
                                    return ' (Predicted AI Forecast Horizon)';
                                }
                                return ' (Historical Sensor Telemetry)';
                            }
                        }
                    }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
});
