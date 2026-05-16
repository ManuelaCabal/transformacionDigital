import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Importa tu instancia global de Flask

class DecoHomeDashboardTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test: inicializa el entorno de simulación."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        # Forzamos el contexto de aplicación activo para evitar bloqueos con las conexiones de BD
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Limpieza al finalizar cada test."""
        self.ctx.pop()

    @patch('app.mysql.connection.cursor')
    def test_dashboard_data_sources(self, mock_cursor):
        """Valida que los endpoints de la API retornen las estructuras que el JS del Dashboard procesa."""
        
        # 1. Configurar Mock de Clientes (Espera la propiedad .clients o la lista directamente)
        mock_cursor_instance_clients = MagicMock()
        mock_cursor_instance_clients.fetchall.return_value = [
            {"id": 1, "name": "Estudio Almodóvar", "status": "activo"},
            {"id": 2, "name": "Hotel Ritz", "status": "prospect"}
        ]
        
        # 2. Configurar Mock de Pedidos (Espera la propiedad .orders o la lista con montos y fechas)
        mock_cursor_instance_orders = MagicMock()
        mock_cursor_instance_orders.fetchall.return_value = [
            {"id": 10, "order_number": "PED-001", "client_name": "Estudio Almodóvar", "final_amount": 1250.00, "status": "entregado", "order_date": "2026-05-15"},
            {"id": 11, "order_number": "PED-002", "client_name": "Hotel Ritz", "final_amount": 3500.00, "status": "pendiente", "order_date": "2026-05-16"}
        ]
        
        # 3. Configurar Mock de Productos (Espera el catálogo de stock)
        mock_cursor_instance_products = MagicMock()
        mock_cursor_instance_products.fetchall.return_value = [
            {"id": 1, "name": "Sofá Modular Velvet", "stock": 14, "price": 1200.00},
            {"id": 2, "name": "Mesa Comedor Roble", "stock": 5, "price": 850.00}
        ]

        # Vinculamos los mocks de manera secuencial para simular las llamadas de Promise.all()
        mock_cursor.side_effect = [
            mock_cursor_instance_clients, 
            mock_cursor_instance_orders, 
            mock_cursor_instance_products
        ]

        # --- TEST 1: API de Clientes para el Doughnut Chart ---
        response_clients = self.client.get('/api/clients/')
        self.assertEqual(response_clients.status_code, 200)
        data_clients = json.loads(response_clients.data.decode('utf-8'))
        clients_list = data_clients.get('clients', data_clients)
        self.assertEqual(len(clients_list), 2)

        # --- TEST 2: API de Pedidos para el Line Chart e Ingresos ---
        response_orders = self.client.get('/api/orders/')
        self.assertEqual(response_orders.status_code, 200)
        data_orders = json.loads(response_orders.data.decode('utf-8'))
        orders_list = data_orders.get('orders', data_orders)
        self.assertEqual(len(orders_list), 2)
        # Comprobar que los montos se puedan castear a float (vital para el .reduce() de tu JS)
        self.assertEqual(float(orders_list[0]['final_amount']), 1250.00)

        # --- TEST 3: API de Productos para el Catálogo Destacado (Stock) ---
        response_products = self.client.get('/api/products/')
        self.assertEqual(response_products.status_code, 200)
        data_products = json.loads(response_products.data.decode('utf-8'))
        products_list = data_products.get('products', data_products)
        self.assertEqual(len(products_list), 2)
        self.assertEqual(int(products_list[0]['stock']), 14)

    def test_dashboard_view_rendering(self):
        """Verifica que la ruta base del panel cargue el HTML corporativo y los scripts necesarios."""
        # Suponiendo que tu endpoint para renderizar este HTML en el servidor sea '/dashboard' o '/'
        response = self.client.get('/dashboard')
        
        # Si requiere inicio de sesión y te redirige (302), el estatus es válido.
        # Si carga directo, dará 200. Evaluamos ambas opciones corporativas comunes:
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            # Validamos que estén presentes los elementos clave que busca el DOM
            self.assertIn('id="total-clients"', html_content)
            self.assertIn('id="total-orders"', html_content)
            self.assertIn('id="total-revenue"', html_content)
            self.assertIn('id="revenueChart"', html_content)
            self.assertIn('cdn.jsdelivr.net/npm/chart.js', html_content)
        else:
            self.assertIn(response.status_code, [302, 200])

if __name__ == '__main__':
    unittest.main()