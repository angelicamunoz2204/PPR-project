include "globals.mzn"; 
include "datosPruebaMinizinc2.dzn";

%%Entradas
%%Cantidad de muelles
1..infinity: muelles;
%%Cantidad de barcos
1..infinity: barcos;
%%set 
set of int: ships = 1..barcos;
%%ID de Barcos
array [int] of  1..infinity : B_codigoBarcos; 
%%Tiempo maximo de espera por barco
array [int] of  1..infinity : B_tpEspera;
%Condiciones de clima a garantizar durante la estadía de cada barco. Se asume un ordenamiento [seco,húmedo,lluvia]
array [int,1..3] of  0..1 : B_estadost;
%%Tiempo de descarga de un barco (los valores vienen en slots, es decir un valor de 3 equivale a 15minutos)
array [int] of  1..infinity :B_tpdescarga;
%estados de mareas para un barco dado un ordenamiento [baja,media,alta]
array [int,1..3] of  0..1 :B_estadosm;
%%ID muelles
array [int] of  1..infinity : M_codigoMuelles;
%Estados del tiempo en el puerto. 1 = seco, 2 = húmedo, 3 = lluvia
array [int] of  1..3 : P_estadost;
%Estados de la marea cada 5 minutos en el puerto. 4 = baja, 5 = media, 6 = alta
array [int] of  4..6 : P_estadosm;

%%Limitando las entradas al numero de barcos
%%IDs
array [int] of 1..infinity: shipsID = [B_codigoBarcos[i] | i in ships]; 
%%Tiempo de espera
array [int] of int: shipsWaitTime = [B_tpEspera[i] | i in ships]; 
%%Condiciones del clima
array [int,1..3] of 0..1: shipsWeather = array2d(ships,1..3,[B_estadost[i,j] | i in ships, j in 1..3]); 
%%Tiempo de descarga
array [int] of int: shipsUnloadTime = [B_tpdescarga[i] | i in ships]; 
%%Estados de la marea
array [int,1..3] of 0..1: shipsTideState = array2d(ships,1..3,[B_estadosm[i,j] | i in ships, j in 1..3]); 

%%Limitando las entradas al numero de muelles
%%IDs
set of int: docksID = {M_codigoMuelles[i] | i in 1..muelles}; 

%%Variables
%%muelles
array[1..barcos] of var docksID : docks;
%%Hora de llegada
array[1..barcos] of var 1..length(P_estadost) : arrivalTime;
%%Hora para empezar la descarga
array[1..barcos] of var 1..length(P_estadost) : unloadStartTime;

%%Predicados
predicate verifyMarineMeteorologyConditions(array [int,1..3] of var 0..1: weather,array [int,1..3] of var 0..1: tide, array [int] of  1..3: weatherState, array [int] of  4..6: tideState) = 
          forall([
              if weather[i,j] = 0 
                 then weatherState[arrivalTime[i]] != j /\ weatherState[unloadStartTime[i]] != j
              endif 
              /\
              if tide[i,j] = 0 
                 then tideState[arrivalTime[i]] != j+3 /\ tideState[unloadStartTime[i]] != j+3
              endif 
           | i in ships, j in 1..3]);

%%Restricciones
%%Condiciones de la meteorologia marina (clima y marea)
constraint verifyMarineMeteorologyConditions(shipsWeather,shipsTideState,P_estadost,P_estadosm);
%constraint forall([
              %if shipsWeather[i,j] = 0 
                 %then P_estadost[arrivalTime[i]] != j /\ P_estadost[unloadStartTime[i]] != j
              %endif 
              %| i in ships, j in 1..3]);
%%Condiciones de la marea
%constraint forall([
              %if shipsTideState[i,j] = 0 
                 %then P_estadosm[arrivalTime[i]] != j+3 /\ P_estadosm[unloadStartTime[i]] != j+3
              %endif 
              %| i in ships, j in 1..3]);

%%Para que entre descarga y llegada no haya más tiempo del que debería
%%el -1 es porque el primer slot tambien cuenta para descargar
constraint forall([(unloadStartTime[i]-arrivalTime[i]) <= shipsWaitTime[i]-1 /\ (unloadStartTime[i]-arrivalTime[i])>= 0 | i in ships]);
%%constraint alldifferent(arrivalTime);
%%constraint alldifferent(unloadStartTime);
constraint disjunctive(unloadStartTime,shipsUnloadTime);
%resolver
solve satisfy;
%%Salida           
output ["Barcos          :",show(shipsID),"\n"];
output ["Muelles         :",show(docks),"\n"];
output ["Hora de llegada :",show(arrivalTime),"\n"];
output ["Hora de descarga:",show(unloadStartTime),"\n"];
%output [show(P_estadost[unloadStartTime[i]])|i in ships];
%output [show(P_estadosm[unloadStartTime[i]])|i in ships];
%output [show(P_estadost)];