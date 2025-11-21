"""
Simple x86-64 Assembly Generator for the CMPE 152 Python Subset Compiler.

This module takes the existing three-address code (TAC) instructions from
`codegen.CodeGenerator` and produces a *rough* x86-64 assembly listing.

Notes / Limitations:
- This is intended for educational visualization, not for producing a
  fully runnable executable.
- We use a very simple memory model: every variable / temporary is
  treated as a global in `.data` and we mostly use the `rax` register
  for computations.
- Complex operations (lists, builtins like `print`, `len`, etc.) are
  emitted as comments instead of real x86 code.
"""

from __future__ import annotations

from typing import List, Any, Set

from codegen import Instruction


class X86CodeGenerator:
    """
    Translates TAC `Instruction` objects into approximate x86-64 assembly.
    """

    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.lines: List[str] = []
        self.variables: Set[str] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self) -> List[str]:
        """
        Generate x86-64 assembly lines from TAC instructions.
        """
        if not self.instructions:
            return []

        self._collect_variables()
        self._emit_header()
        self._emit_body()
        return self.lines

    def save(self, filename: str) -> None:
        """
        Save the generated assembly to a file.
        """
        if not self.lines:
            self.generate()

        with open(filename, "w") as f:
            f.write("; Generated x86-64 Assembly (approximate)\n")
            f.write("; CMPE 152 Python Subset Compiler\n\n")
            for line in self.lines:
                f.write(line + "\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _collect_variables(self) -> None:
        """
        Collect a simple set of "variables" and temporaries that will be
        represented as global data. This is a heuristic based on TAC.
        """
        def maybe_add(value: Any) -> None:
            if isinstance(value, str):
                # Skip labels like L1, L2, ...
                if value.startswith("L") and value[1:].isdigit():
                    return
                # Skip known builtin prefixes
                if value.startswith("builtin_"):
                    return
                self.variables.add(value)

        for instr in self.instructions:
            if instr.result is not None:
                maybe_add(instr.result)
            if instr.arg1 is not None:
                maybe_add(instr.arg1)
            if instr.arg2 is not None:
                maybe_add(instr.arg2)

    def _emit_header(self) -> None:
        """
        Emit .data and .text headers and a simple `main` entry point.
        """
        self.lines.append("section .data")
        if self.variables:
            for name in sorted(self.variables):
                # Reserve 8 bytes per variable/temporary.
                self.lines.append(f"{name}:    dq 0")
        else:
            # Still emit a dummy so section is not empty.
            self.lines.append("tmp_dummy: dq 0")

        self.lines.append("")
        self.lines.append("section .text")
        self.lines.append("global main")
        self.lines.append("")
        self.lines.append("main:")
        self.lines.append("    ; Entry point corresponding to top-level TAC")
        self.lines.append("")

    def _emit_body(self) -> None:
        """
        Emit assembly for each TAC instruction.
        """
        for instr in self.instructions:
            op = instr.op

            if op == "LABEL":
                label = str(instr.arg1)
                self.lines.append(f"{label}:")

            elif op == "GOTO":
                target = str(instr.arg1)
                self.lines.append(f"    jmp {target}")

            elif op in ("IF_FALSE", "IF_TRUE"):
                cond = instr.arg1
                label = instr.result
                self._emit_if(op, cond, label)

            elif op == "ASSIGN":
                self._emit_assign(instr.arg1, instr.result)

            elif op in ("+", "-", "*", "/", "%"):
                self._emit_arithmetic(op, instr.arg1, instr.arg2, instr.result)

            elif op in ("==", "!=", "<", "<=", ">", ">="):
                self._emit_comparison(op, instr.arg1, instr.arg2, instr.result)

            elif op in ("NEG", "POS", "NOT"):
                self._emit_unary(op, instr.arg1, instr.result)

            elif op in ("FUNCTION", "END_FUNCTION"):
                self._emit_function(op, instr.arg1)

            elif op == "RETURN":
                self._emit_return(instr.arg1)

            elif op == "CALL":
                self._emit_call(instr.arg1, instr.arg2, instr.result)

            elif op == "PARAM":
                # Parameter passing is non-trivial; emit as comment for now.
                self.lines.append(f"    ; PARAM {self._format_value(instr.arg1)} "
                                  f"(argument setup for next CALL)")

            elif op == "PRINT":
                # We do not implement I/O here; just document it.
                self.lines.append(f"    ; PRINT {self._format_value(instr.arg1)} "
                                  f"(no real x86 I/O implemented)")

            elif op in ("LEN", "CREATE_LIST", "APPEND", "INDEX"):
                self.lines.append(
                    f"    ; {op} {self._format_value(instr.arg1)} "
                    f"{self._format_value(instr.arg2)} -> "
                    f"{self._format_value(instr.result)} "
                    "(high-level operation not lowered to x86)"
                )

            else:
                # Fallback for anything we don't recognize.
                self.lines.append(
                    f"    ; UNSUPPORTED TAC: {op} "
                    f"{self._format_value(instr.arg1)} "
                    f"{self._format_value(instr.arg2)} -> "
                    f"{self._format_value(instr.result)}"
                )

        # Ensure we return from `main` somehow.
        self.lines.append("")
        self.lines.append("    ; Exit from main (placeholder)")
        self.lines.append("    mov rax, 0")
        self.lines.append("    ret")

    # ------------------------------------------------------------------
    # Instruction-specific emitters
    # ------------------------------------------------------------------
    def _emit_assign(self, src: Any, dest: Any) -> None:
        self._load_to_rax(src)
        self.lines.append(f"    mov QWORD [{dest}], rax    ; {dest} = {self._format_value(src)}")

    def _emit_arithmetic(self, op: str, left: Any, right: Any, dest: Any) -> None:
        self._load_to_rax(left)
        rhs = self._operand(right)

        if op == "+":
            self.lines.append(f"    add rax, {rhs}")
        elif op == "-":
            self.lines.append(f"    sub rax, {rhs}")
        elif op == "*":
            self.lines.append(f"    imul rax, {rhs}")
        elif op == "/":
            # Very simplified integer division using rdx:rax / rhs
            self.lines.append("    cqo                 ; sign-extend rax into rdx:rax")
            self.lines.append(f"    idiv {rhs}")
        elif op == "%":
            self.lines.append("    cqo                 ; sign-extend rax into rdx:rax")
            self.lines.append(f"    idiv {rhs}")
            self.lines.append("    mov rax, rdx        ; remainder in rdx")

        self.lines.append(f"    mov QWORD [{dest}], rax    ; {dest} = "
                          f"{self._format_value(left)} {op} {self._format_value(right)}")

    def _emit_comparison(self, op: str, left: Any, right: Any, dest: Any) -> None:
        self._load_to_rax(left)
        rhs = self._operand(right)
        self.lines.append(f"    cmp rax, {rhs}")

        # Use setcc to materialize boolean 0/1 in al, then zero-extend.
        setcc_map = {
            "==": "sete",
            "!=": "setne",
            "<": "setl",
            "<=": "setle",
            ">": "setg",
            ">=": "setge",
        }
        setcc = setcc_map.get(op, "sete")
        self.lines.append(f"    {setcc} al")
        self.lines.append("    movzx rax, al")
        self.lines.append(f"    mov QWORD [{dest}], rax    ; {dest} = "
                          f"{self._format_value(left)} {op} {self._format_value(right)}")

    def _emit_unary(self, op: str, operand: Any, dest: Any) -> None:
        self._load_to_rax(operand)

        if op == "NEG":
            self.lines.append("    neg rax")
        elif op == "POS":
            # No-op, but keep for clarity.
            self.lines.append("    ; POS - unary plus, no change to rax")
        elif op == "NOT":
            # Logical not: result = 1 if rax == 0 else 0
            self.lines.append("    cmp rax, 0")
            self.lines.append("    sete al")
            self.lines.append("    movzx rax, al")

        self.lines.append(f"    mov QWORD [{dest}], rax    ; {dest} = {op} {self._format_value(operand)}")

    def _emit_if(self, op: str, cond: Any, label: Any) -> None:
        self._load_to_rax(cond)
        self.lines.append("    cmp rax, 0")
        if op == "IF_FALSE":
            jmp = "je"
        else:
            jmp = "jne"
        self.lines.append(f"    {jmp} {label}    ; branch on {op.lower()} {self._format_value(cond)}")

    def _emit_function(self, op: str, name: Any) -> None:
        if op == "FUNCTION":
            self.lines.append("")
            self.lines.append(f"{name}:")
            self.lines.append("    push rbp")
            self.lines.append("    mov rbp, rsp")
            self.lines.append("    ; function body begins")
        else:  # END_FUNCTION
            self.lines.append("    ; function epilogue")
            self.lines.append("    mov rsp, rbp")
            self.lines.append("    pop rbp")
            self.lines.append("    ret")
            self.lines.append("")

    def _emit_return(self, value: Any) -> None:
        if value is not None:
            self._load_to_rax(value)
        self.lines.append("    ; return from current function")
        self.lines.append("    mov rsp, rbp")
        self.lines.append("    pop rbp")
        self.lines.append("    ret")

    def _emit_call(self, func_name: Any, arg_count: Any, dest: Any) -> None:
        self.lines.append(f"    ; CALL {func_name} with {arg_count} args "
                          "(argument passing not modeled)")
        self.lines.append(f"    call {func_name}")
        if dest is not None:
            self.lines.append(f"    mov QWORD [{dest}], rax    ; result of {func_name}")

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _load_to_rax(self, value: Any) -> None:
        """
        Load a TAC value into rax (either immediate or from memory).
        """
        if isinstance(value, (int, float)):
            self.lines.append(f"    mov rax, {value}")
        elif isinstance(value, str):
            # Treat as variable / temporary stored in memory
            self.lines.append(f"    mov rax, QWORD [{value}]")
        else:
            # Fallback: just comment it.
            self.lines.append(f"    ; unable to load value {repr(value)} into rax")

    def _operand(self, value: Any) -> str:
        """
        Format a value as an x86 operand (immediate or memory reference).
        """
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f"QWORD [{value}]"
        else:
            return f";bad_operand({repr(value)})"

    def _format_value(self, value: Any) -> str:
        """
        Human-readable representation used in comments.
        """
        if value is None:
            return "None"
        return repr(value)


