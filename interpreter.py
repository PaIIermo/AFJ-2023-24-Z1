import sys

def sanitize_args(arg1, arg2, variables):
    try:
        if arg1 not in variables:
            arg1 = int(arg1)
        else:
            arg1 = variables[arg1]
        
        if arg2 not in variables:
            arg2 = int(arg2)
        else:
            arg2 = variables[arg2]
        if not isinstance(arg1, int) or not isinstance(arg2, int):
           raise ValueError("Oba operandy musia mať číselnú hodnotu.")

    except ValueError:
        raise ValueError("Neplatné operandy. Musia byť integer, alebo názov premennej.")
    
    return arg1, arg2

def execute_arithmetic(op, arg1, arg2):
    return {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
    }[op](arg1, arg2)

def execute_comparison(op, arg1, arg2):
    return {
        '<': lambda x, y: x < y,
        '>': lambda x, y: x > y,
        '>=': lambda x, y: x >= y,
        '<=': lambda x, y: x <= y,
        '==': lambda x, y: x == y,
    }[op](arg1, arg2)

def validate_target_line(target_line, total_lines):
    if target_line <= 0 or target_line > total_lines:
        raise ValueError("Cieľový riadok je mimo hraníc textového súboru!")
    return target_line

def handle_read_operation(parts, variables):
    if len(parts) != 2:
        raise ValueError("Neplatný formát pre READ.")
    var_name = parts[1]
    if not var_name.isalpha():
        raise ValueError("Názvy premenných musia byť abecedné!")
    user_input = input(f"Zadajte hodnotu pre {var_name}: ")
    try:
        variables[var_name] = int(user_input)
    except ValueError:
        raise ValueError("Neplatný vstup. Musí byť celé číslo.")
    return None

def handle_write_operation(parts, variables):
    if len(parts) != 2:
        raise ValueError("Neplatný formát pre WRITE.")
    var_name = parts[1]
    if var_name not in variables:
        raise ValueError(f"Premenná {var_name} neexistuje.")
    print(f"Obsah premennej {var_name}: {variables[var_name]}")
    return None

def execute_jump_operation(parts, total_lines, condition=True):
    try:
        target_line = int(parts[-1]) 
    except ValueError:
        raise ValueError("Cieľový riadok musí mať hodnotu typu integer.")
    
    target_line = validate_target_line(target_line, total_lines)
    
    if condition:
        return ("JUMP", target_line)
    return None

def execute_instruction(instruction, variables, total_lines):
    permitted_operations = [ 'READ', 'WRITE', '+', '-', '*', '=', '<', '>', '<=', '>=', '==', 'JUMP', 'JUMPT', 'JUMPF', 'NOP']

    parts = instruction.split(',')
    op = parts[0]
    
    if len(parts) == 4 and not parts[3][0].isalpha():
        raise ValueError("Názvy premenných musia byť abecedné!")

    if op == "NOP" or op not in permitted_operations:
        return None 
    elif op == "READ":
        return handle_read_operation(parts, variables)
    elif op == "WRITE":
        return handle_write_operation(parts, variables)
    elif op in ("JUMP", "JUMPT", "JUMPF"):
        condition = True  # Default condition for JUMP
        if op in ("JUMPT", "JUMPF"):
            condition_var = parts[1]
            if condition_var not in variables:
                raise ValueError(f"Premenná {condition_var} neexistuje.")
            condition = variables[condition_var]
            if op == "JUMPF":
                condition = not condition
        return execute_jump_operation(parts, total_lines, condition=condition)
    
    if op == '=':  # Handle assignment
        if len(parts) != 3:
            raise ValueError("Nepodporovaný formát operácie")
        var_name, value = parts[1], sanitize_args(parts[2], '0', variables)[0]
        variables[var_name] = value
    else:  # Handle arithmetic and comparison
        if len(parts) != 4:
            raise ValueError("Nepodporovaný formát operácie")
        arg1, arg2, result_var = parts[1], parts[2], parts[3]
        arg1, arg2 = sanitize_args(arg1, arg2, variables)
        
        if op in ['+', '-', '*']:
            result = execute_arithmetic(op, arg1, arg2)
        elif op in ['<', '>', '>=', '<=', '==']:
            result = execute_comparison(op, arg1, arg2)
        else:
            raise ValueError(f"Nepodporovaná operácia: {op}")
        
        variables[result_var] = result
    return None
    
def main(input_file):
    try:
        with open(input_file, 'r') as file:
            instructions = file.readlines()

        instructions.insert(0, "# Placeholder line to align indexes with line numbers\n")
        variables = {}
        current_line = 1
        
        while current_line < len(instructions):
            line = instructions[current_line].strip()
            line = line.split('#')[0].strip()
            
            if not line:
                current_line += 1
                continue
            
            try:
                result = execute_instruction(line, variables, len(instructions)-1)
                if result is not None:
                    if isinstance(result, tuple) and result[0] == "JUMP":
                        current_line = result[1]
                        continue
                    else:
                        print(f"{result[0]}: {result[1]}")
                current_line += 1
            except Exception as e:
                print(f"Chyba na riadku {current_line}: {e}")
                sys.exit(1)
            
    except FileNotFoundError:
        print(f"Súbor nebol nájdený: {input_file}")
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Použitie: interpreter.exe <input_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    main(input_file)
