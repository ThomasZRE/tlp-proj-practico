import re 

token_specs = [ 
	('STRING', r'\"([^\"]*)\"'),
	('KEYWORD', r'let'),
	('IDENTIFIER', r'\b(?!\d)\w+\b'), # Excluye cuando empiezan en numeros
	('NUMBER', r'(\d+\.?\d*)'), 	# Detecta digitos y decimales
	('SYMBOL', r'({|}|\[|\]|=|,|:)'),
	('SKIP', r'\s+'),
	('COMMENT', r'#')
]

def tokenizer(source_code):
	#print(source_code)
	tokens = []
	pos = 0

	# Recorre todo el texto
	while pos < len(source_code):
		found = None
		for token_type, pattern in token_specs:
			# Compila el patron y busca match
			rex = re.compile(pattern)
			m = rex.match(source_code, pos)
			if m:
				if token_type == 'COMMENT':
					# Compila el patron de salto de linea y busca match
					rex1 = re.compile(r'.+(\n)*')
					nlmatch = rex1.match(source_code, pos)
					if nlmatch:
						pos = nlmatch.end(0)
						found = True
					else:
						print("No newline found. Error")				
					break
					'''
					for i in range(pos, len(source_code)):
						# Skips until next line
						if source_codeh.end(0)
					else: 
						print("No new line found. Error[i] == "\n":
							pos = i + 1
							break 	# To break in first newline
'''
				text = m.group(0)
				if token_type != 'SKIP':
					tokens.append((token_type, text))

				pos = m.end(0)
				found = True
				break
		
		if not found:
			print(f"Error léxico: No se reconoce el carácter {source_code[pos]}")
			break
	
	print(tokens)
	return tokens


# Basic structure of the lang
'''
(IDENTIFIER | KEYWORD) BLOCK-VALUE
Comienza con una keyword o un identificador para constantes o variables seguido de un "bloque de valores"

----- BLOCK-VALUE ----

Un bloque de valores sigue una estructura similar a la del formato JSON removiendo los '=', es decir, valores dentro de llaves {}

{ "Hola mundo" }	# Bloque con un string
{ 5 }				# Bloque con un numero

Lo que implica que todo se define como un objeto, lo que naturalmente da lugar a definición de objetos dentro de otros objetos como en un típico JSON.

Ademas, en este lenguaje todos los identificadores definen valores constantes por defecto a no ser que se especifique que son variables con el keyword "let"

# Asigna el string "Guillermo" a name
name { "Guillermo" }	# name es inmutable

# Crea una variable y le asigna el numero 10
let number { 5 }		# number se puede modificar

Pueden crearse objetos mas complejos:

let dog {
	nombre { "Firulais" },
	edad { 5 },
	color { "black" },
	raza { "borer collie" }
}	# dog es una variable asignada a un objeto compuesto por los objetos: nombre (string), edad (numero), color (string), raza (string)

----- Arrays -----
Se pueden definir listas/arreglos usando '[', ']'. Puede hacerse de dos formas:

eventos { ["click", "keydown", "hover"] } # Brackets dentro de las llaves

acciones ["comer_fruta", "sacar_perro", "dormir"] # como bloques en sí mismos

Esto permite construir bloques con mayor complejidad:

let stadium {
	nombre { "Camp Nou" },
	tribunas [
		norte [ "alta", "baja" ],
		sur [ "alta", "baja"],
		este [ "alta", "media", "baja" ],
		oeste [ "alta", "media", "baja" ]
	],
	palcos { 2200 },
	banquillos {
		A { 25 },
		B { 25 }	
	},
	area_cancha { [120, 90] },
	area_porteria { [7.32, 2.44] },
	area_penaltis { [5.5, 16.5] },
}
# La indentacion no es requerida
'''

def parser(tokens):
	indx = 0	# Index of token
	t_simbolos = {}

	while indx < len(tokens):
		tkn_type, token = tokens[indx]

		if tkn_type != 'IDENTIFIER':
			raise SyntaxError(f'Error de sintaxis: se esperaba un identificador, en su lugar se obtuvo {token}')
		
		tkn_type, token = tokens[indx + 1]
		if token != '{' or token != '[':
			raise SyntaxError(f'Error de sintaxis: se esperaba bloque valor, en su lugar se obtuvo {token}')

		value = parseBlock(tkn_type, token)
		t_simbolos[token] = value


def parseBlock(tkn_type, token):
	# TODO: Completar el parser para bloques de codigo
	# Identifica arreglos
	if token == '[':
		parseArray(tkn_type, token)
	
	# sigue parser para bloques de código {}

def parseArray(tkn_type, token):
	...

def main():
	file = '' 
	with open("./lang1.txt") as f:
		for line in f:
			file += ''.join(line)

	print(tokenizer(file))

if __name__ == "__main__":
	main()
