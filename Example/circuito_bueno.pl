% ============================================
% Hechos de componentes
% ============================================
componente(c1, cap10, '10uf').
componente(d1, led-aqua, 'led-aqua').
componente(r1, resistor, '220').
componente(r2, resistor, '1k').
componente(v1, vsource, '5v').

% ============================================
% Hechos de conexiones
% ============================================
conexion(n00000, v1, 1).
conexion(n00000, r1, 1).
conexion(n00001, v1, 2).
conexion(n00001, r2, 2).
conexion(n00001, c1, 2).
conexion(n00001, d1, k).
conexion(n00002, c1, 1).
conexion(n00002, r2, 1).
conexion(n00002, r1, 2).
conexion(n00002, d1, a).
