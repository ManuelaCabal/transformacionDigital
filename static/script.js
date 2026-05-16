// ============================================================
// TECHSOLUTIONS CRM - JavaScript Principal
// ============================================================

// Variables globales
let revenueChart, clientsChart;
const API_BASE = '/api';

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ CRM iniciado');
    loadDashboardData();
    initCharts();
    setLastUpdate();
});

// ============================================================
// CARGAR DATOS DEL DASHBOARD
// ============================================================

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);
        const data = await response.json();

        // Actualizar KPIs
        document.getElementById('total-clients').textContent = data.stats.total_clients || 0;
        document.getElementById('total-orders').textContent = data.stats.total_orders || 0;
        document.getElementById('total-revenue').textContent = formatCurrency(data.stats.total_revenue || 0);
        document.getElementById('delivered-orders').textContent = data.stats.delivered_orders || 0;

        // Cargar productos top
        loadTopProducts(data.top_products);

        // Cargar gráfico de clientes por estado
        updateClientsChart(data.clients_by_status);

    } catch (error) {
        console.error('❌ Error al cargar dashboard:', error);
    }
}

// ============================================================
// INICIALIZAR GRÁFICOS
// ============================================================

function initCharts() {
    // Gráfico de ingresos
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
                datasets: [{
                    label: 'Ingresos (€)',
                    data: [12000, 15000, 18000, 22000, 19000, 25000],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: '#334155' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    }

    // Gráfico de estado de clientes
    const clientsCtx = document.getElementById('clientsChart');
    if (clientsCtx) {
        clientsChart = new Chart(clientsCtx, {
            type: 'doughnut',
            data: {
                labels: ['Activos', 'Prospect', 'Inactivos', 'Perdidos'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                    borderColor: '#1e293b',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#e2e8f0' },
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// ============================================================
// ACTUALIZAR GRÁFICO DE CLIENTES
// ============================================================

function updateClientsChart(data) {
    if (!clientsChart || !data) return;

    const labels = data.map(d => capitalize(d.status));
    const values = data.map(d => d.count);

    clientsChart.data.labels = labels;
    clientsChart.data.datasets[0].data = values;
    clientsChart.update();
}

// ============================================================
// CARGAR PRODUCTOS TOP
// ============================================================

function loadTopProducts(products) {
    const container = document.getElementById('topProducts');
    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = '<p class="text-slate-400 text-sm text-center py-4">Sin datos disponibles</p>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
            <div>
                <p class="text-white font-medium">${product.name}</p>
                <p class="text-slate-400 text-sm">${product.total_sold || 0} unidades</p>
            </div>
            <p class="text-green-400 font-semibold">${formatCurrency(product.revenue || 0)}</p>
        </div>
    `).join('');
}


            // Cargar datos de ventas para la gráfica mensual (últimos 12 meses)
            try {
                const salesRes = await fetch(`${API_BASE}/analytics/sales?days=365`);
                const salesData = await salesRes.json();
                // salesData is an array with date, orders, revenue
                // Aggregate by month
                const months = {};
                salesData.forEach(r => {
                    const d = new Date(r.date);
                    const key = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;
                    months[key] = (months[key] || 0) + (r.revenue || 0);
                });
                // keep last 12 months sorted
                const keys = Object.keys(months).sort();
                const lastKeys = keys.slice(-12);
                const labels = lastKeys.map(k => {
                    const [y,m] = k.split('-');
                    return `${m}/${y}`;
                });
                const values = lastKeys.map(k => months[k]);
                if (revenueChart) {
                    revenueChart.data.labels = labels;
                    revenueChart.data.datasets[0].data = values;
                    revenueChart.update();
                }
            } catch (err) {
                console.error('Error cargando ventas para la gráfica:', err);
            }
// ============================================================
// FUNCIONES AUXILIARES
// ============================================================

function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0
    }).format(value);
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function setLastUpdate() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
    document.getElementById('lastUpdate').textContent = `${timeStr} - ${dateStr}`;
}

// ============================================================
// FUNCIONES DE MODAL
// ============================================================

function showModal(type) {
    console.log(`📝 Abrir formulario: ${type}`);
    // Aquí irían los modales
}

// ============================================================
// OBTENER CLIENTES
// ============================================================

async function getClients() {
    try {
        const response = await fetch(`${API_BASE}/clients/`);
        return await response.json();
    } catch (error) {
        console.error('❌ Error al obtener clientes:', error);
        return [];
    }
}

// ============================================================
// CREAR CLIENTE
// ============================================================

async function createClient(clientData) {
    try {
        const response = await fetch(`${API_BASE}/clients/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(clientData)
        });
        return await response.json();
    } catch (error) {
        console.error('❌ Error al crear cliente:', error);
    }
}

// Auto-actualizar cada 30 segundos
setInterval(() => {
    loadDashboardData();
}, 30000);

console.log('🚀 Sistema CRM TechSolutions iniciado correctamente');
