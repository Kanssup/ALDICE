% ============================================
% Hechos de componentes
% ============================================
componente(v1, vsource, '12v').
componente(r1, resistor, '10k').
componente(r2, resistor, '10k').

% ============================================
% Hechos de conexiones
% ============================================
conexion(n00000, v1, 1).
conexion(n00000, r1, 1).
conexion(n00001, r1, 2).
conexion(n00001, r2, 1).
conexion(n00002, r2, 2).
conexion(n00002, v1, 2).
