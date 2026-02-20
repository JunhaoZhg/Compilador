from token_types import TokenType
from errors import SyntacticError, SemanticError
from Tabla_Simbolos.gestor_tabla import GestorTablas

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.previous_token = None 
        self.rules = [] 
        self.errors = []
        
        # --- ANÁLISIS SEMÁNTICO ---
        self.ts = GestorTablas()      
        self.scope_actual = "global"
        self.tipo_retorno_actual = None 

    # ---------------- UTILIDADES ----------------
    def advance(self):
        self.previous_token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None 

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
            return True
        else:
            got = self.current_token.type.name if self.current_token else "EOF"
            lexeme = self.current_token.lexeme if self.current_token else "fin de fichero"
            line = self.current_token.line if self.current_token else 0
            col = self.current_token.column if self.current_token else 0
            
            msg = f"Se esperaba '{token_type.name}', pero se encontró '{got}' ('{lexeme}')"
            self.errors.append(SyntacticError(line, col, msg))
            
            if self.current_token and self.current_token.type != TokenType.EOF:
                self.advance()
            return False

    def parse(self):
        self.P()
        return self.rules, self.errors

    # ---------------- REGLAS GRAMATICALES ----------------

    # 1. P -> L eof
    def P(self):
        self.rules.append(1)
        self.L()
        if self.current_token and self.current_token.type == TokenType.EOF:
            return True
        return False

    # 2. L -> E L
    # 3. L -> lambda
    def L(self):
        ct = self.current_token.type if self.current_token else None
        first_E = [
            TokenType.LET, TokenType.FUNCTION, 
            TokenType.IF, TokenType.DO, TokenType.READ, TokenType.WRITE, TokenType.RETURN, 
            TokenType.ID, TokenType.LBRACE
        ]
        if ct in first_E:
            self.rules.append(2)
            self.E()
            self.L()
        else:
            self.rules.append(3)

    # 4. E -> F 
    # 5. E -> V 
    # 6. E -> S 
    def E(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.FUNCTION:
            self.rules.append(4)
            self.F()
        elif ct == TokenType.LET:
            self.rules.append(5)
            self.V()
        else:
            self.rules.append(6)
            self.S()

    # 7. T -> int 
    # 8. T -> float
    # 9. T -> boolean
    # 10. T -> string
    def T(self):
        """Devuelve el tipo detectado como string."""
        ct = self.current_token.type if self.current_token else None
        tipo_leido = "void"

        if ct == TokenType.INT:
            self.rules.append(7)
            self.eat(TokenType.INT)
            tipo_leido = "int"
        elif ct == TokenType.FLOAT:
            self.rules.append(8)
            self.eat(TokenType.FLOAT)
            tipo_leido = "float"
        elif ct == TokenType.BOOLEAN:
            self.rules.append(9)
            self.eat(TokenType.BOOLEAN)
            tipo_leido = "boolean"
        elif ct == TokenType.STRING:
            self.rules.append(10)
            self.eat(TokenType.STRING)
            tipo_leido = "string"
        else:
             line = self.current_token.line if self.current_token else 0
             col = self.current_token.column if self.current_token else 0
             self.errors.append(SyntacticError(line, col, "Se esperaba un TIPO"))
             self.advance()
        
        return tipo_leido

    # 11. V -> let T id V1
    def V(self):
        self.rules.append(11)
        self.eat(TokenType.LET)
        
        tipo_var = self.T()
        nombre_var = self.current_token.lexeme if self.current_token else "unknown"
        line = self.current_token.line if self.current_token else 0
        col = self.current_token.column if self.current_token else 0
        
        
        ya_existe = False
        if self.scope_actual == "global":
            if self.ts.tabla_global.buscar(nombre_var): ya_existe = True
        else:
            tabla_local = self.ts.locales.get(self.scope_actual)
            if tabla_local and tabla_local.buscar(nombre_var): ya_existe = True

        if ya_existe:
            self.errors.append(SemanticError(line, col, f"Variable '{nombre_var}' ya declarada explícitamente en este ámbito."))
        else:
            if self.scope_actual == "global":
                self.ts.registrar_variable_global(nombre_var, tipo_var)
            else:
                self.ts.registrar_variable_local(self.scope_actual, nombre_var, tipo_var)

        self.eat(TokenType.ID)
        self.V1(tipo_var) 

    # 12. V1 -> ;
    # 13. V1 -> = X ;
    def V1(self, tipo_esperado=None):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.SEMICOLON:
            self.rules.append(12)
            self.eat(TokenType.SEMICOLON)
        elif ct == TokenType.ASSIGN:
            self.rules.append(13)
            self.eat(TokenType.ASSIGN)
            tipo_expr = self.X() 
            
            
            if tipo_esperado and tipo_expr and tipo_esperado != tipo_expr:
                 line = self.previous_token.line if self.previous_token else 0
                 col = self.previous_token.column if self.previous_token else 0
                 self.errors.append(SemanticError(line, col, f"No se puede inicializar '{tipo_esperado}' con '{tipo_expr}'."))

            self.eat(TokenType.SEMICOLON)
        else:
            if self.previous_token:
                line = self.previous_token.line
                col = self.previous_token.column + len(self.previous_token.lexeme)
            else:
                line = self.current_token.line if self.current_token else 0
                col = self.current_token.column if self.current_token else 0
            self.errors.append(SyntacticError(line, col, "Se esperaba ';' o '=' en la declaración"))
            
            safe_tokens = [TokenType.FUNCTION, TokenType.LET, TokenType.IF, TokenType.DO, TokenType.READ, TokenType.WRITE, TokenType.RETURN, TokenType.RBRACE, TokenType.EOF]
            if self.current_token and self.current_token.type not in safe_tokens:
                self.advance()

    # 14. F -> function H id ( A ) B
    def F(self):
        self.rules.append(14)
        self.eat(TokenType.FUNCTION)
        
        tipo_retorno = self.H()
        nombre_func = self.current_token.lexeme if self.current_token else "unknown"
        
        self.ts.registrar_funcion(nombre_func, tipo_retorno)
        
        self.eat(TokenType.ID)
        
        self.scope_actual = nombre_func
        self.tipo_retorno_actual = tipo_retorno 
        
        self.eat(TokenType.LPAREN)
        self.A() 
        self.eat(TokenType.RPAREN)
        
        self.B() 
        
        self.scope_actual = "global"
        self.tipo_retorno_actual = None

    # 15. H -> T
    # 16. H -> void
    def H(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.VOID:
            self.rules.append(16)
            self.eat(TokenType.VOID)
            return "void"
        else:
            self.rules.append(15)
            return self.T()

    # 17. A -> T id A1
    # 18. A -> void
    # 19. A -> lambda
    def A(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.VOID:
            self.rules.append(18)
            self.eat(TokenType.VOID)
        elif ct in [TokenType.INT, TokenType.FLOAT, TokenType.BOOLEAN, TokenType.STRING]:
            self.rules.append(17)
            
            tipo_param = self.T()
            nombre_param = self.current_token.lexeme
            line = self.current_token.line
            col = self.current_token.column
            
            tabla_local = self.ts.locales.get(self.scope_actual)
            if tabla_local and tabla_local.buscar(nombre_param):
                 self.errors.append(SemanticError(line, col, f"Parámetro '{nombre_param}' repetido."))
            else:
                self.ts.registrar_variable_local(self.scope_actual, nombre_param, tipo_param)

            self.eat(TokenType.ID)
            self.A1()
        else:
            self.rules.append(19)

    # 20. A1 -> , T id A1
    # 21. A1 -> lambda
    def A1(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.COMMA:
            self.rules.append(20)
            self.eat(TokenType.COMMA)
            
            tipo_param = self.T()
            nombre_param = self.current_token.lexeme
            
            tabla_local = self.ts.locales.get(self.scope_actual)
            if tabla_local and tabla_local.buscar(nombre_param):
                 pass 
            else:
                self.ts.registrar_variable_local(self.scope_actual, nombre_param, tipo_param)
            
            self.eat(TokenType.ID)
            self.A1()
        else:
            self.rules.append(21)

    # 22. B -> { LS }
    def B(self):
        self.rules.append(22)
        self.eat(TokenType.LBRACE)
        self.LS()
        self.eat(TokenType.RBRACE)

    # 23. LS -> S LS
    # 24. LS -> V LS 
    # 25. LS -> lambda
    def LS(self):
        ct = self.current_token.type if self.current_token else None
        
        if ct == TokenType.LET:
            self.rules.append(24)
            self.V()
            self.LS()
        elif ct in [TokenType.IF, TokenType.DO, TokenType.READ, TokenType.WRITE, 
                    TokenType.RETURN, TokenType.LBRACE, TokenType.ID]:
            self.rules.append(23)
            self.S()
            self.LS()
        else:
            self.rules.append(25)

    # ------------------ SENTENCIAS ------------------

    # S -> Sentencia General
    def S(self):
        ct = self.current_token.type if self.current_token else None

        # 26. S -> if ( X ) SS
        if ct == TokenType.IF:
            self.rules.append(26)
            self.eat(TokenType.IF)
            self.eat(TokenType.LPAREN)
            
            tipo_cond = self.X()
            if tipo_cond != "boolean":
                self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                 f"Condición del 'if' debe ser boolean, se encontró '{tipo_cond}'."))
            
            self.eat(TokenType.RPAREN)
            self.SS() 
        
        else:
            self.rules.append(27)
            self.SS()

    # SS -> Sentencia Simple
    def SS(self):
        ct = self.current_token.type if self.current_token else None
        
        # 28. SS -> do B while ( X ) ;
        if ct == TokenType.DO:
            self.rules.append(28)
            self.eat(TokenType.DO)
            self.B()
            self.eat(TokenType.WHILE)
            self.eat(TokenType.LPAREN)
            
            tipo_cond = self.X()
            if tipo_cond != "boolean":
                self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                 f"Condición del 'while' debe ser boolean, se encontró '{tipo_cond}'."))

            self.eat(TokenType.RPAREN)
            self.eat(TokenType.SEMICOLON)
            
        # 29. SS -> read id ;
        elif ct == TokenType.READ:
            self.rules.append(29)
            self.eat(TokenType.READ)
            
            if self.current_token.type == TokenType.ID:
                nombre_var = self.current_token.lexeme
                simbolo = self._buscar_simbolo_o_declarar_implicito(nombre_var)
                
                categoria = getattr(simbolo, "categoria", "Variable")
                if categoria == "Función":
                     self.errors.append(SemanticError(self.current_token.line, self.current_token.column, 
                                        f"No se puede leer ('read') sobre la función '{nombre_var}'."))

            self.eat(TokenType.ID)
            self.eat(TokenType.SEMICOLON)
            
        # 30. SS -> write X ;
        elif ct == TokenType.WRITE:
            self.rules.append(30)
            self.eat(TokenType.WRITE)
            self.X()
            self.eat(TokenType.SEMICOLON)
            
        # 31. SS -> return R1 ;
        elif ct == TokenType.RETURN:
            self.rules.append(31)
            self.eat(TokenType.RETURN)
            
            tipo_retornado = self.R1()
            
            if self.tipo_retorno_actual and self.tipo_retorno_actual != tipo_retornado:
                 self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                  f"Función espera retornar '{self.tipo_retorno_actual}' pero retorna '{tipo_retornado}'."))

            self.eat(TokenType.SEMICOLON)
            
        # 34. SS -> B
        elif ct == TokenType.LBRACE:
            self.rules.append(34)
            self.B()
            
        # 35. SS -> id SE1
        elif ct == TokenType.ID:
            self.rules.append(35)
            
            nombre_var = self.current_token.lexeme
            simbolo = self._buscar_simbolo_o_declarar_implicito(nombre_var)

            self.eat(TokenType.ID)
            self.SE1(simbolo) 
            
        else:
             line = self.current_token.line if self.current_token else 0
             col = self.current_token.column if self.current_token else 0
             self.errors.append(SyntacticError(line, col, "Sentencia simple esperada"))
             self.advance()

    # Metodo auxiliar para las declaraciones implícita
    def _buscar_simbolo_o_declarar_implicito(self, nombre_var):
        simbolo = None
        if self.scope_actual != "global":
            tabla_local = self.ts.locales.get(self.scope_actual)
            if tabla_local: simbolo = tabla_local.buscar(nombre_var)
        if not simbolo:
            simbolo = self.ts.tabla_global.buscar(nombre_var)
        
        if not simbolo:
            self.ts.registrar_variable_global(nombre_var, "int")
            simbolo = self.ts.tabla_global.buscar(nombre_var)
        return simbolo

    # 32. R1 -> X
    # 33. R1 -> lambda
    def R1(self):
        ct = self.current_token.type if self.current_token else None
        first_X = [
            TokenType.LPAREN, TokenType.INT_CONST, TokenType.FLOAT_CONST, TokenType.STRING_CONST,
            TokenType.TRUE, TokenType.FALSE, TokenType.ID, TokenType.NOT
        ]
        if ct in first_X:
            self.rules.append(32)
            return self.X()
        
        else:
            self.rules.append(33)
            return "void"

    # SE1 -> ...
    def SE1(self, simbolo=None):
        ct = self.current_token.type if self.current_token else None
        
        tipo_lhs = simbolo.tipo if simbolo else "error"
        categoria = getattr(simbolo, "categoria", "Variable") if simbolo else "Variable"
        
        # 36. SE1 -> = X ;
        if ct == TokenType.ASSIGN:
            self.rules.append(36)
            self.eat(TokenType.ASSIGN)
            tipo_rhs = self.X()
            
            if categoria == "Función":
                self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                f"No se puede asignar un valor a '{simbolo.lexema}' porque es una Función."))
            
            elif tipo_lhs and tipo_rhs and tipo_lhs != "error" and tipo_rhs != "error":
                if tipo_lhs != tipo_rhs:
                     self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                      f"No se puede asignar '{tipo_rhs}' a variable '{tipo_lhs}'."))

            self.eat(TokenType.SEMICOLON)
            
        # 37. SE1 -> |= X ;
        elif ct == TokenType.OR_ASSIGN:
            self.rules.append(37)
            self.eat(TokenType.OR_ASSIGN)
            self.X()
            if categoria == "Función":
                 self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                f"No se puede operar con '{simbolo.lexema}' porque es una Función."))
            self.eat(TokenType.SEMICOLON)
            
        # 38. SE1 -> ( G ) ; 
        elif ct == TokenType.LPAREN:
            self.rules.append(38)
            
            if simbolo and categoria != "Función":
                self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                f"El identificador '{simbolo.lexema}' es una Variable, no una Función. No se puede invocar."))

            self.eat(TokenType.LPAREN)
            self.G()
            self.eat(TokenType.RPAREN)
            self.eat(TokenType.SEMICOLON)
        else:
            line = self.current_token.line if self.current_token else 0
            col = self.current_token.column if self.current_token else 0
            msg = "Se esperaba una asignación ('=') o una llamada a función ('(')"
            self.errors.append(SyntacticError(line, col, msg))
            self.advance()

    # --- EXPRESIONES ---

    # 39. G -> X G1
    # 40. G -> lambda
    def G(self):
        ct = self.current_token.type if self.current_token else None
        first_X = [ TokenType.LPAREN, TokenType.INT_CONST, TokenType.FLOAT_CONST, TokenType.STRING_CONST,
            TokenType.TRUE, TokenType.FALSE, TokenType.ID, TokenType.NOT ]
        if ct in first_X:
            self.rules.append(39)
            self.X()
            self.G1()
        else:
            self.rules.append(40)

    # 41. G1 -> , X G1
    # 42. G1 -> lambda
    def G1(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.COMMA:
            self.rules.append(41)
            self.eat(TokenType.COMMA)
            self.X()
            self.G1()
        else:
            self.rules.append(42)

    # 43. X -> D R
    def X(self):
        self.rules.append(43)
        tipo_d = self.D()
        tipo_r = self.R(tipo_d) 
        
        if tipo_r: return tipo_r
        return tipo_d

    # 44. R -> < D R
    # 45. R -> lambda
    def R(self, tipo_izq=None):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.LT:
            self.rules.append(44)
            self.eat(TokenType.LT)
            tipo_der = self.D()
            
            if tipo_izq and tipo_der and tipo_izq != tipo_der:
                 self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                  f"Comparación incompatible: '{tipo_izq}' < '{tipo_der}'."))
            
            self.R(tipo_der)
            return "boolean" 
        else:
            self.rules.append(45)
            return None

    # 46. D -> M D1
    def D(self):
        self.rules.append(46)
        tipo_m = self.M()
        tipo_d1 = self.D1(tipo_m)
        
        if tipo_d1: return tipo_d1
        return tipo_m

    # 47. D1 -> + M D1
    # 48. D1 -> lambda
    def D1(self, tipo_izq=None):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.PLUS:
            self.rules.append(47)
            self.eat(TokenType.PLUS)
            tipo_der = self.M()
            
            if tipo_izq and tipo_der and tipo_izq != tipo_der:
                self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                  f"Suma incompatible: '{tipo_izq}' + '{tipo_der}'."))
            
            return self.D1(tipo_izq) or tipo_izq
        else:
            self.rules.append(48)
            return None

    # 49. M -> ! M
    # 50. M -> K
    def M(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.NOT:
            self.rules.append(49)
            self.eat(TokenType.NOT)
            tipo = self.M()
            if tipo != "boolean":
                 self.errors.append(SemanticError(self.previous_token.line, self.previous_token.column, 
                                                  f"Operador '!' espera boolean, se encontró '{tipo}'."))
            return "boolean"
        else:
            self.rules.append(50)
            return self.K()

    # 51. K -> ( X )
    # 52. K -> int
    # 53. K -> float
    # 54. K -> string
    # 55. K -> true
    # 56. K -> false
    # 57. K -> id K1
    def K(self):
        ct = self.current_token.type if self.current_token else None
        
        if ct == TokenType.LPAREN:
            self.rules.append(51)
            self.eat(TokenType.LPAREN)
            t = self.X()
            self.eat(TokenType.RPAREN)
            return t
            
        elif ct == TokenType.INT_CONST:
            self.rules.append(52)
            self.eat(TokenType.INT_CONST)
            return "int"
            
        elif ct == TokenType.FLOAT_CONST:
            self.rules.append(53)
            self.eat(TokenType.FLOAT_CONST)
            return "float"
            
        elif ct == TokenType.STRING_CONST:
            self.rules.append(54)
            self.eat(TokenType.STRING_CONST)
            return "string"
            
        elif ct == TokenType.TRUE:
            self.rules.append(55)
            self.eat(TokenType.TRUE)
            return "boolean"
            
        elif ct == TokenType.FALSE:
            self.rules.append(56)
            self.eat(TokenType.FALSE)
            return "boolean"
            
        elif ct == TokenType.ID:
            self.rules.append(57)
            nombre_var = self.current_token.lexeme
            simbolo = self._buscar_simbolo_o_declarar_implicito(nombre_var)
            tipo = simbolo.tipo if simbolo else "error"
            
            self.eat(TokenType.ID)
            self.K1() 
            return tipo
            
        else:
             line = self.current_token.line if self.current_token else 0
             col = self.current_token.column if self.current_token else 0
             self.errors.append(SyntacticError(line, col, "Factor inesperado en expresión"))
             self.advance()
             return "error"

    # 58. K1 -> ( G )
    # 59. K1 -> lambda
    def K1(self):
        ct = self.current_token.type if self.current_token else None
        if ct == TokenType.LPAREN:
            self.rules.append(58)
            self.eat(TokenType.LPAREN)
            self.G()
            self.eat(TokenType.RPAREN)
        else:
            self.rules.append(59)

            
