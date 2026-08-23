document.addEventListener('DOMContentLoaded', function () {
    const stationSelect = document.getElementById('analytics-station-select');
    const paramSelect = document.getElementById('analytics-param-select');
    const daysSelect = document.getElementById('analytics-days-select');

    let analyticsChart = null;

    loadAnalytics();

    stationSelect.addEventListener('change', loadAnalytics);
    paramSelect.addEventListener('change', loadAnalytics);
    daysSelect.addEventListener('change', loadAnalytics);

    function loadAnalytics() {
        const st = stationSelect.value;
        const param = paramSelect.value;
        const days = daysSelect.value;

        fetch(`/api/analytics?station_id=${st}&days=${days}`)
            .then(res => res.json())
            .then(data => {
                renderAnalyticsChart(data, param);
            })
            .catch(err => console.error("Error loading analytics:", err));
    }

    function renderAnalyticsChart(data, selectedParam) {
        if (!data || !data.timestamps) return;

        const paramLabels = {
            'wqi': 'Water Quality Index (WQI)',
            'dissolved_oxygen': 'Dissolved Oxygen (DO mg/L)',
            'turbidity': 'Turbidity (NTU)',
            'ph': 'pH Level',
            'temperature': 'Temperature (°C)'
        };

        const paramColors = {
            'wqi': '#00A896',
            'dissolved_oxygen': '#10B981',
            'turbidity': '#F59E0B',
            'ph': '#0B2545',
            'temperature': '#E76F51'
        };

        const targetData = data[selectedParam] || data['wqi'];
        const color = paramColors[selectedParam] || '#00A896';
        const label = paramLabels[selectedParam] || 'Parameter';

        const ctx = document.getElementById('analyticsMainChart').getContext('2d');
        if (analyticsChart) analyticsChart.destroy();

        analyticsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timestamps,
                datasets: [{
                    label: label,
                    data: targetData,
                    borderColor: color,
                    backgroundColor: `${color}15`,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' }
                },
                scales: { y: { beginAtZero: false } }
            }
        });
    }
});
