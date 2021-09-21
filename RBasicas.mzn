include "globals.mzn"; 

%%Entradas
%%Cantidad de muelles
int: muelles;

%%Cantidad de barcos
int: barcos;

%Si el usuario desea preasignación fuerte (1) o debil (0)
0..1: PreasignacionHoraLlegada;

%%set 
set of int: ships = 1..barcos;

%%ID de Barcos
array [int] of int : B_codigoBarcos; 

%%Tiempo maximo de espera por barco
array [int] of int : B_tpEspera;

%Condiciones de clima a garantizar durante la estadía de cada barco. Se asume un ordenamiento [seco,húmedo,lluvia]
array [int,1..3] of 0..1 : B_estadost;

%%Tiempo de descarga de un barco (los valores vienen en slots, es decir un valor de 3 equivale a 15minutos)
array [int] of int : B_tpdescarga;

%estados de mareas para un barco dado un ordenamiento [baja,media,alta]
array [int,1..3] of  0..1 :B_estadosm;

%%ID muelles
array [int] of int : M_codigoMuelles;

%Estados del tiempo en el puerto. 1 = seco, 2 = húmedo, 3 = lluvia
array [int] of 1..3 : P_estadost;

%Estados de la marea cada 5 minutos en el puerto. 4 = baja, 5 = media, 6 = alta
array [int] of 4..6 : P_estadosm;

%Preasignacion de hora de llegada
array [int,int] of 1..length(P_estadost) : horaLlegada;

%Horario de muelles
array [int, int] of 1..length(P_estadost) : horasHabiles;

%%Limitando las entradas al numero de barcos
%%IDs
array [ships] of int: shipsID = [B_codigoBarcos[i] | i in ships]; 

%%Tiempo de espera
array [ships] of int: shipsWaitTime = [B_tpEspera[i] | i in ships]; 

%%Condiciones del clima
array [ships,1..3] of 0..1: shipsWeather = array2d(ships,1..3,[B_estadost[i,j] | i in ships, j in 1..3]); 

%%Tiempo de descarga
array [ships] of int: shipsUnloadTime = [B_tpdescarga[i] | i in ships]; 

%%Estados de la marea
array [ships,1..3] of 0..1: shipsTideState = array2d(ships,1..3,[B_estadosm[i,j] | i in ships, j in 1..3]); 


%%Limitando las entradas al numero de muelles
%%IDs
set of int: docksID = {M_codigoMuelles[i] | i in 1..muelles};

%%Variables
%%muelles
array[ships] of var docksID : docks;

%%Hora de llegada
array[ships] of var 1..length(P_estadost) : arrivalTime;

%%Hora para empezar la descarga
array[ships] of var 1..length(P_estadost) : unloadStartTime;


%%Restricciones Básicas
%Verificación para evitar cruces de tiempo en el mismo muelle
constraint forall([
              if i != j then
                if docks[i] = docks[j] then 
                  if arrivalTime[i] <= arrivalTime[j] then 
                    unloadStartTime[i] + shipsUnloadTime[i]-1 < arrivalTime[j]
                  endif
                endif
              endif 
           | i in ships, j in ships]);

%Validación del tiempo de espera y de evitar incoherencias
constraint forall([(unloadStartTime[i]-arrivalTime[i]) <= shipsWaitTime[i] /\ unloadStartTime[i] >= arrivalTime[i] | i in ships]);

%%Verificacion climatológica (100% confirmada)
constraint forall(s in ships, n in arrivalTime[s]..unloadStartTime[s] + shipsUnloadTime[s]-1)(
  if n <= length(P_estadost) then
    (P_estadost[n] = 1*shipsWeather[s,1]  \/ P_estadost[n] = 2*shipsWeather[s,2] \/ P_estadost[n] = 3*shipsWeather[s,3]) /\ 
    (P_estadosm[n] = 4*shipsTideState[s,1] \/ P_estadosm[n] = 5*shipsTideState[s,2] \/ P_estadosm[n] = 6*shipsTideState[s,3])
    else false 
    endif);

%resolver
solve satisfy;

%%Salida           
output ["{'Barcos' :",show(shipsID),",\n"];
output ["'Muelles' :",show([M_codigoMuelles[i] | i in 1..muelles]),",\n"];
output ["'TiempoEspera' :",show(shipsWaitTime),",\n"];
output ["'ClimaBarco' :",show(shipsWeather),",\n"];
output ["'TiempoDesca' :",show(shipsUnloadTime),",\n"];
output ["'MareaBarco' :",show(shipsTideState),",\n"];
output ["'Clima' :",show(P_estadost),",\n"];
output ["'Marea' :",show(P_estadosm),",\n"];
output ["'HoraLlegadas' :",show(horaLlegada),",\n"];
output ["'HorasHabil' :",show(horasHabiles),",\n"];
output ["'PreFuerte' :",show(PreasignacionHoraLlegada),",\n"];
%%Vbles
output ["'MuelleCorresp' :",show(docks),",\n"];
output ["'HoraLlegada' :",show(arrivalTime),",\n"];
output ["'HoraDescarga' :",show(unloadStartTime),"}"];
