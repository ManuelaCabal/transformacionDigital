import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Importa tu instancia global de Flask

class DecoHomeCampaignsTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test: inicializa el cliente de pruebas de Flask."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        # Mantenemos el contexto de la aplicación activo para evitar el RuntimeError de MySQL
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Limpieza al finalizar cada test."""
        self.ctx.pop()

    @patch('app.mysql.connection.cursor')
    def test_get_campaigns_success(self, mock_cursor):
        """Prueba que GET /api/campaigns/ devuelve la lista con métricas y ROI."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchall.return_value = [
            {
                "id": 1,
                "name": "Campaña Primavera 2026",
                "campaign_type": "email",
                "status": "en_curso",
                "budget": 1500.00,
                "total_contacts": 5000,
                "roi": 12.5
            }
        ]
        mock_cursor.return_value = mock_cursor_instance

        # Probamos pasando filtros en el Query String
        response = self.client.get('/api/campaigns/?status=en_curso&type=email')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Campaña Primavera 2026")

    @patch('app.mysql.connection.cursor')
    def test_get_campaign_not_found(self, mock_cursor):
        """Prueba el error 404 cuando una campaña solicitada no existe."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchone.return_value = None
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/campaigns/99')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['error'], "Campaña no encontrada")

    @patch('app.mysql.connection.cursor')
    def test_create_campaign_success(self, mock_cursor):
        """Prueba la creación de una campaña y su inicialización en campaign_results."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.lastrowid = 5
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "name": "Black Friday Mobiliario",
            "campaign_type": "social_media",
            "start_date": "2026-11-20",
            "budget": 3000.00,
            "target_audience": "Diseñadores de interiores"
        }

        response = self.client.post(
            '/api/campaigns/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['message'], "Campaña creada")

    @patch('app.mysql.connection.cursor')
    def test_update_campaign_success(self, mock_cursor):
        """Prueba la actualización de los datos básicos de la campaña."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "name": "Black Friday Extendido",
            "status": "completada",
            "end_date": "2026-11-30"
        }

        response = self.client.put(
            '/api/campaigns/5',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Campaña actualizada")

    @patch('app.mysql.connection.cursor')
    def test_update_campaign_results(self, mock_cursor):
        """Prueba el volcado de métricas analíticas (clicks, conversiones, ROI)."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "total_contacts": 10000,
            "total_opens": 4500,
            "total_clicks": 1200,
            "total_conversions": 150,
            "revenue_generated": 45000.00,
            "roi": 14.0
        }

        response = self.client.put(
            '/api/campaigns/5/results',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Resultados actualizados")

    def test_get_campaign_types(self):
        """Prueba que el endpoint estático de tipos de campañas retorne las opciones correctas."""
        response = self.client.get('/api/campaigns/types')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(any(t['value'] == 'email' for t in data))

    def test_get_campaign_statuses(self):
        """Prueba que el listado de estados contenga los valores del ciclo de vida."""
        response = self.client.get('/api/campaigns/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(any(s['value'] == 'planeada' for s in data))

    @patch('app.mysql.connection.cursor')
    def test_delete_campaign_success(self, mock_cursor):
        """Prueba la eliminación física completa de la campaña."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.delete('/api/campaigns/5')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['message'], "Campaña eliminada")

if __name__ == '__main__':
    unittest.main()