import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Importa tu instancia global de Flask

class DecoHomeOrdersTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test: inicializa el cliente de pruebas de Flask."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        # Mantenemos el contexto de la aplicación activo para las extensiones como MySQL
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Limpieza al finalizar cada test."""
        self.ctx.pop()

    @patch('app.mysql.connection.cursor')
    def test_get_orders_success(self, mock_cursor):
        """Prueba que GET /api/orders/ devuelve el historial de pedidos correctamente."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchall.return_value = [
            {
                "id": 101,
                "order_number": "PED-7384",
                "client_name": "Estudio Almodóvar S.L.",
                "order_date": "2026-05-16",
                "final_amount": 4400.00,
                "status": "pendiente"
            }
        ]
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        
        # Validar la estructura que espera pintar la función JS displayOrders()
        if isinstance(data, dict) and 'orders' in data:
            self.assertEqual(data['orders'][0]['order_number'], "PED-7384")
            self.assertEqual(data['orders'][0]['client_name'], "Estudio Almodóvar S.L.")
        else:
            # En caso de que el backend devuelva directamente el array plano
            self.assertEqual(data[0]['order_number'], "PED-7384")

    @patch('app.mysql.connection.cursor')
    def test_post_order_success(self, mock_cursor):
        """Prueba que un payload JSON con múltiples artículos se procesa con éxito."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.lastrowid = 102
        mock_cursor.return_value = mock_cursor_instance

        # Payload calcado milimétricamente de la función JS orderForm.onsubmit
        payload = {
            "order_number": "PED-9941",
            "client_id": 4,
            "payment_method": "transferencia",
            "status": "pendiente",
            "discount_percentage": 0,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 650.00
                },
                {
                    "product_id": 3,
                    "quantity": 1,
                    "unit_price": 3100.00
                }
            ]
        }

        response = self.client.post(
            '/api/orders/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Aceptamos 200 o 201 como respuestas válidas de guardado exitoso
        self.assertIn(response.status_code, [200, 201])

    @patch('app.mysql.connection.cursor')
    def test_delete_order_success(self, mock_cursor):
        """Prueba que la llamada de eliminación física remueve el pedido del mapa."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.delete('/api/orders/101')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        # Valida que devuelva un mensaje de confirmación que active la recarga JS
        self.assertTrue('message' in data or 'status' in data)

if __name__ == '__main__':
    unittest.main()