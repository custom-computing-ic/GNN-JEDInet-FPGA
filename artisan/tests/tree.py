from artisan import *

# include: relative path to jedi50p_baseline_u1/ (workdir)
ast = Ast("../../jedi50p_baseline_u1/jedi.cpp -I ../artisan/include")

ast.tree()