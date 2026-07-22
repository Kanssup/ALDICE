% ============================================
% ALDICE — Reglas de Diagnóstico
% Motor de inferencia deductivo para detección
% de fallos en circuitos electrónicos.
% ============================================

% --------------------------------------------
% Regla 1: Alerta de Cortocircuito Crítico
% --------------------------------------------
% alerta_cortocircuito(?Nodo, ?Ref, ?Pin1, ?Pin2)
%
% Un nodo está en cortocircuito si conecta dos pines
% del MISMO componente (distintos pines). Esto significa
% que los dos terminales del componente están unidos
% directamente, provocando un bypass de la carga.
%
% Ejemplo: si v1,1 y v1,2 aparecen en n00000,
%          entonces V1 tiene un cortocircuito interno.

alerta_cortocircuito(Nodo, Ref, Pin1, Pin2) :-
    conexion(Nodo, Ref, Pin1),
    conexion(Nodo, Ref, Pin2),
    Pin1 \= Pin2.

% --------------------------------------------
% Regla 2: Alerta de Camino Abierto
% --------------------------------------------
% alerta_camino_abierto(?Ref, ?Pin)
%
% Un componente tiene un camino abierto en un pin si
% ese pin está conectado a un nodo que solo tiene
% exactamente una conexión (el propio pin). El pin
% queda flotante sin retorno de corriente.

alerta_camino_abierto(Ref, Pin) :-
    componente(Ref, _, _),
    conexion(Nodo, Ref, Pin),
    \+ (conexion(Nodo, Ref2, _), Ref2 \= Ref).

% --------------------------------------------
% Regla 3: Fuente en Cortocircuito (extensión)
% --------------------------------------------
% alerta_fuente_cortocircuito(?Nodo, ?Ref)
%
% Una fuente de voltaje (vsource) está en cortocircuito
% si sus dos pines (1 y 2) están en el mismo nodo.
% Es un caso particular y crítico de alerta_cortocircuito.

alerta_fuente_cortocircuito(Nodo, Ref) :-
    componente(Ref, vsource, _),
    alerta_cortocircuito(Nodo, Ref, 1, 2).

% --------------------------------------------
% Regla 4: Nodo Sobrecargado
% --------------------------------------------
% alerta_nodo_sobrecargado(?Nodo, ?NumConexiones)
%
% Un nodo se considera sobrecargado si tiene más de
% 4 conexiones, lo que puede indicar un error de diseño
% o una unión accidental de nets.

alerta_nodo_sobrecargado(Nodo, NumConexiones) :-
    setof(_, conexion(Nodo, _, _), Conexiones),
    length(Conexiones, NumConexiones),
    NumConexiones > 4.
