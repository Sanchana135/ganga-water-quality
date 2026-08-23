document.addEventListener('DOMContentLoaded', function () {
    let map = L.map('full-gis-map').setView([26.5, 82.0], 6.5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | Ganga River Basin DSS'
    }).addTo(map);

    fetch('/api/stations')
        .then(res => res.json())
        .then(stations => {
            stations.forEach((st, idx) => {
                let color = '#10B981'; // Green
                if (st.wqi > 100) color = '#EF4444';
                else if (st.wqi > 75) color = '#E76F51';
                else if (st.wqi > 50) color = '#F59E0B';

                const marker = L.circleMarker([st.latitude, st.longitude], {
                    color: '#FFFFFF',
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.85,
                    radius: 12
                }).addTo(map);

                marker.bindPopup(`
                    <div style="font-family: 'Inter', sans-serif;">
                        <h4 style="margin-bottom: 4px; color: #0B2545;">${st.name} Station</h4>
                        <div style="font-size: 0.75rem; color: #64748B; margin-bottom: 6px;">${st.location}</div>
                        <span class="badge-status ${st.quality_category.toLowerCase()}">${st.quality_category}</span><br><br>
                        <b>WQI Score:</b> ${st.wqi}<br>
                        <b>DO:</b> ${st.dissolved_oxygen} mg/L<br>
                        <b>Turbidity:</b> ${st.turbidity} NTU<br>
                        <div style="font-size: 0.72rem; color: #64748B; margin-top: 6px;">Last Updated: ${st.last_updated}</div>
                    </div>
                `);

                marker.on('click', function () {
                    inspectStation(st.id);
                });

                // Auto inspect first station
                if (idx === 0) inspectStation(st.id);
            });
        })
        .catch(err => console.error("Error loading GIS map stations:", err));

    function inspectStation(stationId) {
        const inspector = document.getElementById('map-station-inspector');
        inspector.innerHTML = '<div style="text-align: center; padding: 2rem;">Loading station details...</div>';

        fetch(`/api/stations/${stationId}`)
            .then(res => res.json())
            .then(data => {
                const st = data.station;
                const r = data.latest_reading;
                const wq = data.latest_wqi;
                const dss = data.dss_recommendations;

                inspector.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <h3 style="font-size: 1.25rem; margin-bottom: 0.2rem;">${st.name}</h3>
                        <div style="font-size: 0.82rem; color: var(--text-muted);">${st.location}</div>
                        <div style="font-size: 0.78rem; color: var(--ocean-cyan);">Lat: ${st.latitude.toFixed(4)}, Lng: ${st.longitude.toFixed(4)}</div>
                    </div>

                    <div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; margin-bottom: 1.25rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.85rem; font-weight: 600;">WQI Index:</span>
                            <span class="badge-status ${wq.quality_category.toLowerCase()}">${wq.wqi.toFixed(1)} (${wq.quality_category})</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.82rem;">
                            <div><b>pH:</b> ${r.ph.toFixed(2)}</div>
                            <div><b>DO:</b> ${r.dissolved_oxygen.toFixed(2)} mg/L</div>
                            <div><b>Turbidity:</b> ${r.turbidity.toFixed(1)} NTU</div>
                            <div><b>TDS:</b> ${r.tds.toFixed(1)} mg/L</div>
                            <div><b>BOD:</b> ${r.bod.toFixed(2)} mg/L</div>
                            <div><b>COD:</b> ${r.cod.toFixed(2)} mg/L</div>
                        </div>
                    </div>

                    <div class="dss-recommendation-card" style="padding: 1rem;">
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.4rem; color: var(--primary-navy);">
                            <i class="fa-solid fa-lightbulb text-warning"></i> AI DSS Recommendation
                        </h4>
                        <p style="font-size: 0.82rem; color: var(--text-primary); margin-bottom: 0.5rem;">${dss.executive_summary}</p>
                        <div style="font-size: 0.78rem; font-weight: 600; color: var(--river-blue);">Action Suggestion:</div>
                        <ul style="font-size: 0.78rem; color: var(--text-primary); padding-left: 1.2rem; margin-top: 0.2rem;">
                            ${dss.immediate_actions.map(act => `<li>${act}</li>`).join('')}
                        </ul>
                    </div>
                `;
            });
    }
});
