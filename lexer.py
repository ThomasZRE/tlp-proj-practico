import re 
import json

# ============================
# TOKENIZER (LEXER)
# ============================

token_specs = [ 
	('STRING', r'\"([^\"]*)\"'),
	('KEYWORD', r'\blet\b'),  # palabra clave let
	('IDENTIFIER', r'\b(?!\d)\w+\b'),  # nombres q no empiecen con número
	('NUMBER', r'(\d+\.?\d*)'),  # números con o sin decimal
	('SYMBOL', r'({|}|\[|\]|=|,|:)'),
	('SKIP', r'\s+'),
	('COMMENT', r'#')
]

def tokenizer(source_code):
	tokens = []
	pos = 0

	# recorre todo el texto buscando tokens
	while pos < len(source_code):
		found = None
		for token_type, pattern in token_specs:
			rex = re.compile(pattern)
			m = rex.match(source_code, pos)
			if m:
				if token_type == 'COMMENT':
					rex1 = re.compile(r'.+(\n)*')
					nlmatch = rex1.match(source_code, pos)
					if nlmatch:
						pos = nlmatch.end(0)
						found = True
					else:
						print("no se encontró salto de línea")				
					break
		
				text = m.group(0)
				if token_type != 'SKIP':
					tokens.append((token_type, text))

				pos = m.end(0)
				found = True
				break
		
		if not found:
			print(f"Error léxico: no se reconoce el carácter {source_code[pos]}")
			break
	
	return tokens


# ============================
# PARSER
# ============================

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.symbol_table = {}  # guarda variables ya definidas con su valor

	def peek(self):
		# mira el token actual sin avanzar
		if self.pos < len(self.tokens):
			return self.tokens[self.pos]
		return (None, None)

	def consume(self):
		# devuelve el token actual y avanza
		tok = self.peek()
		self.pos += 1
		return tok

	def parse(self):
		# recorre los tokens y arma el árbol
		ast = {}
		
		while self.pos < len(self.tokens):
			ttype, tval = self.peek()
			if ttype is None:
				break

			# si aparece "let", la variable es editable
			is_mutable = False
			if ttype == 'KEYWORD' and tval == 'let':
				is_mutable = True
				self.consume()
				ttype, tval = self.peek()

			# debería venir un nombre de variable
			if ttype == 'IDENTIFIER':
				key = tval
				self.consume()

				# puede venir '=' o no
				ttype, tval = self.peek()
				if tval == '=':
					self.consume()

				# lee el valor (num, texto, obj, etc)
				value = self.parse_value()
				
				# guarda el resultado
				ast[key] = value
				self.symbol_table[key] = value
			else:
				# si no hay identificador, se avanza para evitar loops
				self.consume()
				
		return ast

	def parse_value(self):
		# interpreta valores: string, número, objeto o array
		ttype, tval = self.peek()

		if ttype == 'STRING':
			self.consume()
			return tval.strip('"')

		elif ttype == 'NUMBER':
			self.consume()
			return float(tval) if '.' in tval else int(tval)

		elif tval == '{':
			return self.parse_object()

		elif tval == '[':
			return self.parse_array()

		elif ttype == 'IDENTIFIER':
			# puede ser referencia a algo definido antes
			self.consume()
			return self.symbol_table.get(tval, tval)

		else:
			raise SyntaxError(f"valor inesperado: {tval}")

	def parse_object(self):
		# maneja objetos entre llaves { ... }
		self.consume()  # abre llave

		ttype, tval = self.peek()
		
		# si solo hay un valor directo dentro ej { 5 }
		if ttype in ['STRING', 'NUMBER'] or tval == '[':
			value = None
			if ttype == 'STRING':
				value = tval.strip('"')
				self.consume()
			elif ttype == 'NUMBER':
				value = float(tval) if '.' in tval else int(tval)
				self.consume()
			elif tval == '[':
				value = self.parse_array()
			
			# cerrar llave
			ttype, tval = self.peek()
			if tval == '}':
				self.consume()
			
			return value
		
		# si no, se arma dict con key: value
		obj = {}
		while True:
			ttype, tval = self.peek()
			if tval == '}':
				self.consume()
				break

			if ttype is None:
				raise SyntaxError("faltó '}' al final")

			if ttype == 'IDENTIFIER':
				key = tval
				self.consume()

				# puede venir ':' o un bloque directo
				ttype, tval = self.peek()
				if tval == ':':
					self.consume()
					ttype, tval = self.peek()
					if ttype == 'NUMBER':
						obj[key] = float(tval) if '.' in tval else int(tval)
						self.consume()
					elif ttype == 'STRING':
						obj[key] = tval.strip('"')
						self.consume()
					elif ttype == 'IDENTIFIER':
						obj[key] = self.symbol_table.get(tval, tval)
						self.consume()
					elif tval == '{':
						obj[key] = self.parse_object()
					elif tval == '[':
						obj[key] = self.parse_array()
					else:
						raise SyntaxError(f"valor raro dsp de ':' -> {tval}")
				else:
					obj[key] = self.parse_value()

				# coma opcional al final
				ttype, tval = self.peek()
				if tval == ',':
					self.consume()
			else:
				self.consume()

		return obj

	def parse_array(self):
		# maneja listas [ ... ]
		arr = []
		self.consume()  # abre corchete
		
		while True:
			ttype, tval = self.peek()
			if tval == ']':
				self.consume()
				break

			if ttype is None:
				raise SyntaxError("faltó ']' al final")

			# cada elemento puede ser valor o referencia
			if ttype == 'IDENTIFIER':
				self.consume()
				arr.append(self.symbol_table.get(tval, tval))
			else:
				arr.append(self.parse_value())

			# coma opcional entre elementos
			ttype, tval = self.peek()
			if tval == ',':
				self.consume()
				
		return arr


# ============================
# MAIN
# ============================

def main():
	filename = input("Ingresa el nombre del archivo a procesar: ").strip()
	
	if '.' not in filename:
		filename += '.txt'
	
	try:
		with open(filename, "r", encoding="utf-8") as f:
			source = f.read()
	except FileNotFoundError:
		print(f"Error: no se encontró el archivo '{filename}'")
		return
	except Exception as e:
		print(f"Error al leer el archivo: {e}")
		return

	tokens = tokenizer(source)
	
	try:
		parser = Parser(tokens)
		ast = parser.parse()
		
		print(json.dumps(ast, indent=4, ensure_ascii=False))
		
		with open('arbol.ast', 'w', encoding='utf-8') as f:
			json.dump(ast, f, indent=4, ensure_ascii=False)
		
	except SyntaxError as e:
		print(f"ERROR DE SINTAXIS: {e}")
	except Exception as e:
		print(f"ERROR: {e}")

if __name__ == "__main__":
	main()
