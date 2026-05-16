import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Importa tu instancia global de Flask

class DecoHomeClientsTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test: inicializa el cliente de pruebas de Flask."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        # Creamos un contexto de aplicación persistente para los mocks de MySQL
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Limpieza al finalizar cada test."""
        self.ctx.pop()

    @patch('app.mysql.connection.cursor')
    def test_get_clients_success(self, mock_cursor):
        """Prueba que GET /api/clients/ devuelve la lista de clientes correctamente."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchall.return_value = [
            {"id": 1, "name": "Alejandro Sanz Gómez", "email": "alejandro@email.com", "status": "activo"}
        ]
        mock_cursor_instance.fetchone.return_value = {"total": 1}
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/clients/?search=Alejandro&status=activo')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('clients', data)
        self.assertEqual(data['total'], 1)

    @patch('app.mysql.connection.cursor')
    def test_get_client_not_found(self, mock_cursor):
        """Prueba el error 404 si el cliente solicitado no existe."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchone.return_value = None  
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/clients/999')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['error'], "Cliente no encontrado")

    @patch('app.mysql.connection.cursor')
    def test_add_client_success(self, mock_cursor):
        """Prueba la creación exitosa de un cliente mediante POST."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.lastrowid = 42  
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "name": "Estudio Arquitectura Vanguardia",
            "email": "contacto@vanguardia.com",
            "company": "Vanguardia S.L.",
            "phone": "600123456"
        }

        response = self.client.post(
            '/api/clients/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 42)

    @patch('app.mysql.connection.cursor')
    def test_update_client_success(self, mock_cursor):
        """Prueba la actualización de los datos de un cliente mediante PUT."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "name": "Estudio Vanguardia Modificado",
            "email": "contacto@vanguardia.com",
            "status": "activo"
        }

        response = self.client.put(
            '/api/clients/42',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Cliente actualizado")

    @patch('app.mysql.connection.cursor')
    def test_delete_client_success(self, mock_cursor):
        """Prueba la eliminación lógica o física de un cliente por su ID."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.delete('/api/clients/42')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Cliente eliminado")

    @patch('app.mysql.connection.cursor')
    def test_assign_client(self, mock_cursor):
        """Prueba el endpoint para asignar un cliente a un ejecutivo de cuentas."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {"assigned_to": 3}

        response = self.client.put(
            '/api/clients/42/assign',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Cliente asignado")

    @patch('app.mysql.connection.cursor')
    def test_add_interaction(self, mock_cursor):
        """Prueba el registro de una nueva interacción con el cliente."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "type": "llamada",
            "subject": "Presupuesto Mesa Comedor",
            "description": "Descuento por volumen",
            "result": "pendiente"
        }

        response = self.client.post(
            '/api/clients/42/interactions',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Interacción registrada")

    @patch('app.mysql.connection.cursor')
    def test_get_analytics_summary(self, mock_cursor):
        """Prueba el endpoint de analíticas de rendimiento de clientes."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchone.return_value = {
            "total_clients": 150,
            "active_clients": 90,
            "prospects": 60,
            "avg_ltv": 2450.50,
            "total_ltv": 367575.00
        }
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/clients/analytics/summary')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['total_clients'], 150)

if __name__ == '__main__':
    unittest.main()