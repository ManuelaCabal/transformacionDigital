#!/usr/bin/env python
"""
Script para ejecutar CRM TechSolutions con opciones de puerto y configuración
Uso: python run.py [--port 5000] [--host 0.0.0.0]
"""

import sys
import argparse
import os

# Importar la aplicación
from app import app

def main():
    parser = argparse.ArgumentParser(
        description='Ejecutar CRM TechSolutions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run.py                    # Ejecutar en puerto 5000
  python run.py --port 8000       # Ejecutar en puerto 8000
  python run.py --port 3000 --host localhost  # Ejecutar localmente en puerto 3000
        """
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Puerto donde ejecutar la aplicación (default: 5000)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host donde ejecutar la aplicación (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=True,
        help='Ejecutar en modo debug (default: True)'
    )
    
    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='Desactivar auto-recarga en cambios de archivos'
    )
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   🚀 CRM TECHSOLUTIONS - INICIANDO                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📍 Host:     {args.host}")
    print(f"🔌 Puerto:   {args.port}")
    print(f"🐛 Debug:    {'Activado' if args.debug else 'Desactivado'}")
    print(f"♻️  Recarga:  {'Activada' if not args.no_reload else 'Desactivada'}")
    print(f"\n🌐 Accede en: http://{args.host}:{args.port}")
    print(f"\n⚠️  Presiona CTRL+C para detener\n")
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=not args.no_reload,
            threaded=True
        )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: El puerto {args.port} está en uso")
            print(f"\n💡 Soluciones:")
            print(f"   1. Prueba con otro puerto: python run.py --port 8000")
            print(f"   2. O mata el proceso: lsof -i :{args.port}")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✅ Aplicación detenida correctamente")
        sys.exit(0)

if __name__ == '__main__':
    main()
