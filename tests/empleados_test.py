import unittest
from unittest.mock import patch, MagicMock
import json
from app import app  # Importa tu instancia global de Flask

class DecoHomeEmployeesTestCase(unittest.TestCase):

    def setUp(self):
        """Configuración previa a cada test: inicializa el cliente de pruebas de Flask."""
        self.app = app
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        # Activamos el contexto de aplicación persistente para el conector MySQL
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        """Limpieza al finalizar cada test."""
        self.ctx.pop()

    @patch('app.mysql.connection.cursor')
    def test_get_employees_success(self, mock_cursor):
        """Prueba que GET /api/employees/ devuelve la lista completa para poblar la tabla."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchall.return_value = [
            {
                "id": 1,
                "first_name": "Manuela",
                "last_name": "Cabal",
                "position": "Interiorista Senior",
                "department": "Proyectos",
                "email": "manuela@decohome.com",
                "phone": "+34 600 111 222",
                "hire_date": "2026-01-10"
            }
        ]
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/employees/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        
        # Soportar si el backend encapsula la respuesta en un diccionario o lista directa
        employees_list = data.get('employees', data) if isinstance(data, dict) else data
        
        self.assertEqual(len(employees_list), 1)
        self.assertEqual(employees_list[0]['first_name'], "Manuela")
        self.assertEqual(employees_list[0]['department'], "Proyectos")

    @patch('app.mysql.connection.cursor')
    def test_get_single_employee_success(self, mock_cursor):
        """Prueba que GET /api/employees/<id> devuelva los datos para rellenar el modal de edición."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.fetchone.return_value = {
            "id": 1,
            "first_name": "Manuela",
            "last_name": "Cabal",
            "position": "Interiorista Senior",
            "department": "Proyectos",
            "email": "manuela@decohome.com",
            "phone": "+34 600 111 222",
            "hire_date": "2026-01-10"
        }
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.get('/api/employees/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        
        # Validar según el formato esperado por la función openEmployeeForm() (d.employee o d directo)
        employee_data = data.get('employee', data) if isinstance(data, dict) and ('employee' in data or 'error' in data) else data
        self.assertEqual(employee_data['first_name'], "Manuela")

    @patch('app.mysql.connection.cursor')
    def test_create_employee_success(self, mock_cursor):
        """Prueba la creación de un nuevo miembro del equipo mediante POST."""
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.lastrowid = 2
        mock_cursor.return_value = mock_cursor_instance

        # Payload calcado milimétricamente de la función JS employeeFormSubmit
        payload = {
            "first_name": "Carlos",
            "last_name": "Sainz",
            "position": "Especialista Render 3D",
            "department": "Diseño",
            "email": "carlos@decohome.com",
            "phone": "+34 600 333 444",
            "hire_date": "2026-03-15"
        }

        response = self.client.post(
            '/api/employees/',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('error', data)

    @patch('app.mysql.connection.cursor')
    def test_update_employee_success(self, mock_cursor):
        """Prueba la actualización (PUT) de la ficha de un empleado existente."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        payload = {
            "first_name": "Manuela",
            "last_name": "Cabal Modificado",
            "position": "Directora de Arte & Interiorismo",
            "department": "Proyectos",
            "email": "manuela@decohome.com",
            "phone": "+34 600 111 222",
            "hire_date": "2026-01-10"
        }

        response = self.client.put(
            '/api/employees/1',
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('error', data)

    @patch('app.mysql.connection.cursor')
    def test_delete_employee_success(self, mock_cursor):
        """Prueba que DELETE /api/employees/<id> elimine al empleado de forma permanente."""
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value = mock_cursor_instance

        response = self.client.delete('/api/employees/1')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('error', data)

if __name__ == '__main__':
    unittest.main()