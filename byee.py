import http.server
import socketserver
import json
import mysql.connector


PORT = 8000


def get_all_users():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database="byee_database"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Usuario')
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

def get_all_products():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database="byee_database"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Produto')
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return products

def create_product(product_data):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database="byee_database"
    )
    cursor = connection.cursor(dictionary=True)
    
    # Utilize a passagem de parâmetros para evitar injeção de SQL
    query = '''INSERT INTO Produto 
               (id, nome, tipo, preco, SKU, fk_Usuario_vendedor_fk) 
               VALUES (%s, %s, %s, %s, %s, %s)'''
    values = (
        product_data["id"], 
        product_data["nome"], 
        product_data["tipo"], 
        product_data["preco"], 
        product_data["SKU"], 
        product_data["fk_Usuario_vendedor_fk"]
    )
    
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    return product_data["id"]


class RequestHandler(http.server.BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/users':
            self._set_headers(200)
            users = get_all_users()
            self.wfile.write(json.dumps(users).encode())
        elif self.path == '/products':
            self._set_headers(200)
            products = get_all_products()
            self.wfile.write(json.dumps(products).encode())
        else:
            self._set_headers(404)

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        if self.path == '/create-product':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            product_data = json.loads(post_data)

            # Insira o usuário no banco de dados
            user_id = create_product(product_data)
            if user_id:
                self._set_headers(201)
                self.wfile.write(json.dumps({'id': user_id}).encode())
            else:
                self._set_headers(400)
        else:
            self._set_headers(404)

with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    print(f"Conectado na porta {PORT}")
    httpd.serve_forever()
