#!/bin/env python
from copy import deepcopy


class Compiler(object):

    def __init__(self):
        self.string_constants = {}
        self.seq = 0
        self.call_arg_registers = {
            "integers": ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'],
            "float": ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4',
                      'xmm5', 'xmm6', 'xmm7']
        }

    def get_arg(self, a):

        # not string const
        if not isinstance(a, str):
            return None

        # string const
        if a in self.string_constants.keys():
            return self.string_constants[a]
        else:
            self.seq += 1
            self.string_constants[a] = self.seq
            return self.seq

    def output_constants(self):
        """
        generate constant string
        """
        for str_constant, seq in self.string_constants.items():
            print('''L{0}.str:
	.asciz	"{1}"'''.format(seq, str_constant))

    def compile_exp(self, exp):
        call = exp[0]
        args = [self.get_arg(arg) for arg in exp[1:]]
        args_tuple = zip(args, exp[1:])
        ununsed_registers = deepcopy(self.call_arg_registers)

        # push args into register
        for (i, arg) in args_tuple:

            if isinstance(arg, str):
                register = ununsed_registers['integers'][0]
                ununsed_registers['integers'].remove(register)
                print('	leaq	L{0}.str(%rip), %{1}'.format(i, register))
            elif isinstance(arg, int):
                register = ununsed_registers['integers'][0]
                ununsed_registers['integers'].remove(register)
                print('	movq	${0}, %{1}'.format(arg, register))
            elif isinstance(arg, float):
                pass  # TODO
        print('	callq	{0}'.format(call))

    def compile(self, exp):
        Compiler.before_exp()
        self.compile_exp(exp)
        Compiler.end_exp()
        self.output_constants()

    @staticmethod
    def before_exp():
        print(r'''
	.section	__TEXT,__text,regular,pure_instructions
	.globl	_main
	.align	4, 0x90
_main:                                  ## @main
	.cfi_startproc
## BB#0:
	pushq	%rbp
Ltmp2:
	.cfi_def_cfa_offset 16
Ltmp3:
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
Ltmp4:
	.cfi_def_cfa_register %rbp
	movl	$0, %eax''')

    @staticmethod
    def end_exp():
        print('''
	popq	%rbp
	retq
	.cfi_endproc

	.section	__TEXT,__cstring,cstring_literals''')


compiler = Compiler()
compiler.compile(['_printf', r'%20ld\n', 100])
