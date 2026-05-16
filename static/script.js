// ============================================================
// DECOHOME S.L. - Sistema de Control y Dashboard
// ============================================================

// Variables globales para gráficos de Chart.js
let revenueChart, clientsChart;
const API_BASE = '/api';

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Sistema DecoHOME iniciado');
    loadDashboardData();
    initCharts();
    setLastUpdate();
});

// ============================================================
// CARGAR DATOS DEL DASHBOARD (KPIs, Gráficas y Productos)
// ============================================================

async function loadDashboardData() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);
        const data = await response.json();

        // Actualizar tarjetas de KPI con datos reales de la base de datos
        document.getElementById('total-clients').textContent = data.stats.total_clients || 0;
        document.getElementById('total-orders').textContent = data.stats.total_orders || 0;
        document.getElementById('total-revenue').textContent = formatCurrency(data.stats.total_revenue || 0);
        document.getElementById('delivered-orders').textContent = data.stats.delivered_orders || 0;

        // Cargar los muebles más vendidos en el panel lateral
        loadTopProducts(data.top_products);

        // Actualizar los datos del gráfico de pastel/anillo de clientes
        updateClientsChart(data.clients_by_status);

        // Cargar el histórico de facturación en la gráfica de líneas
        await loadSalesAnalytics();

    } catch (error) {
        console.error('❌ Error al cargar el dashboard de DecoHOME:', error);
    }
}

// ============================================================
// CONFIGURACIÓN DE GRÁFICOS (Estilo Corporativo DecoHOME)
// ============================================================

function initCharts() {
    // 1. Gráfico Lineal de Ingresos (Tonos Amber/Orange de Tailwind)
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                datasets: [{
                    label: 'Facturación Ventas (€)',
                    data: [0, 0, 0, 0, 0, 0], // Se llena dinámicamente con la API
                    borderColor: '#b45309', // amber-700
                    backgroundColor: 'rgba(180, 83, 9, 0.08)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: '#b45309',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#44403c' } } // Texto color stone-700
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#e7e5e4' }, // Líneas sutiles stone-200
                        ticks: { color: '#78716c' }
                    },
                    x: {
                        grid: { color: '#e7e5e4' },
                        ticks: { color: '#78716c' }
                    }
                }
            }
        });
    }

    // 2. Gráfico de Anillo de Clientes por Estado (Paleta Orgánica)
    const clientsCtx = document.getElementById('clientsChart');
    if (clientsCtx) {
        clientsChart = new Chart(clientsCtx, {
            type: 'doughnut',
            data: {
                labels: ['Activos', 'Prospect', 'Inactivos', 'Perdidos'],
                datasets: [{
                    data: [0, 0, 0, 0], 
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'], // Emerald, Blue, Amber, Red
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: { color: '#44403c' },
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function updateClientsChart(data) {
    if (!clientsChart || !data) return;
    const labels = data.map(d => capitalize(d.status));
    const values = data.map(d => d.count);

    clientsChart.data.labels = labels;
    clientsChart.data.datasets[0].data = values;
    clientsChart.update();
}

async function loadSalesAnalytics() {
    try {
        const salesRes = await fetch(`${API_BASE}/orders/analytics?days=365`);
        const salesData = await salesRes.json();
        
        if (salesData && !salesData.error) {
            // Si el backend devuelve un objeto global de analítica agrupamos por fechas
            const months = { 'Mayo 2026': salesData.total_revenue || 0 }; 
            
            if (revenueChart) {
                revenueChart.data.labels = Object.keys(months);
                revenueChart.data.datasets[0].data = Object.values(months);
                revenueChart.update();
            }
        }
    } catch (err) {
        console.error('Error cargando analíticas mensuales:', err);
    }
}

// ============================================================
// COMPONENTE: LISTADO DE MUEBLES TOP (ZONA INFERIOR)
// ============================================================

function loadTopProducts(products) {
    const container = document.getElementById('topProducts');
    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = '<p class="text-stone-500 text-sm text-center py-4">No hay datos de piezas vendidas</p>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="flex items-center justify-between p-4 bg-stone-100 rounded-lg border border-stone-200">
            <div>
                <p class="text-stone-900 font-medium">${product.name}</p>
                <p class="text-stone-500 text-sm">${product.total_sold || 0} unidades entregadas</p>
            </div>
            <p class="text-amber-700 font-semibold">${formatCurrency(product.revenue || 0)}</p>
        </div>
    `).join('');
}

// ============================================================
// SOLUCIÓN AL ERROR 1048: GUARDAR NUEVO PEDIDO
// ============================================================

       
        // 2. Construcción correcta del JSON estructurado para el Backend de Flask
        const pedidoPayload = {
            client_id: parseInt(selectCliente.value),
            payment_method: selectMetodoPago ? selectMetodoPago.value : 'transferencia',
            status: 'pendiente',
            discount_percentage: 0,
            items: [
                {
                    // AQUÍ ESTÁ EL ARREGLO: Pasamos explícitamente la clave que busca el bucle 'for item in data["items"]'
                    product_id: parseInt(selectMueble.value), 
                    quantity: parseInt(inputUnidades.value) || 1,
                    unit_price: parseFloat(inputPrecio.value.replace(',', '.')) || 0.00
                }
            ]
        };

        // 3. Envío asíncrono al endpoint controlado del Backend
        const response = await fetch(`${API_BASE}/orders/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pedidoPayload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(`🎉 Pedido creado con éxito de forma interna: ${result.order_number}`);
            // Recargar datos y cerrar modal (si tienes la función de cerrar activa)
            loadDashboardData();
            if (typeof cerrarModal === 'function') cerrarModal(); 
        } else {
            // Muestra en la alerta de la pantalla el mensaje controlado enviado desde Flask
            alert(`Error: ${result.error}`);
        }

    } catch (error) {
        console.error('❌ Error de JS en la pasarela de guardado:', error);
        alert('Ocurrió un error inesperado al procesar la información del pedido.');
    }
}

// ============================================================
// FUNCIONES AUXILIARES DE FORMATEO
// ============================================================

function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0
    }).format(value);
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function setLastUpdate() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (!lastUpdateEl) return;
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
    lastUpdateEl.textContent = `${timeStr} - ${dateStr}`;
}

// Auto-actualización en segundo plano cada 30 segundos
setInterval(() => {
    loadDashboardData();
}, 30000);

console.log('🚀 CRM de DecoHOME S.L. listo para operaciones comerciales.');