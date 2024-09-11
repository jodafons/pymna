// Nome: Joao Victor da Fonseca Pinto
// 21 de dezembro de 2012
// Objetivo: Criar um cabeçalho para criação de estruturas
// usados no simulador MNA

#ifndef MNAHEADER
#define MNAHEADER

#include <cstdlib>	
#include <string>
#include <iostream>
#include <fstream>
#include <time.h>
#include <windows.h>
#include <iomanip>
#include <sstream>
#include <math.h>
using namespace std;


#define OPENING_FILE_FAILED					0
#define NUMBER_MAX_OF_NODES_EXCEEDED		1

#define NUMBER_MAX_ELEMENTS                50
#define NUMBER_MAX_OF_NODES				   50
#define NUMBER_MAX_OF_GUESSES		      100
#define FIRST_CARACTER						0
#define MAX_NUMBER_OF_PARAMETERS			7
#define NOT_USER						    0
#define PI						   3.14159265
#define NUMBER_MAX_OF_POINT			   100000
#define TOLERANCE						1E-12
#define STEPFACTOR						  1E9

// Condições iniciais
#define MAX_INITIAL_CONDITION			    3
#define REATIVE_IC							0
#define LOGIC_IC_A							1
#define LOGIC_IC_B							2

// Fonte DC
#define DC_VALUE							0

// Fonte SIN
#define NIVEL_CONTINUO						0
#define AMPLITUDE							1
#define FREQUENCIA							2
#define ATRASO								3
#define ATENUACAO							4
#define ANGULO								5
#define NUMERO_DE_CICLOS_SIN				6

// Fonte PULSE
#define AMPLITUDE_1							0
#define AMPLITUDE_2							1
#define ATRASO_PULSE						2
#define TIME_RISE							3
#define TIME_FALL							4
#define TIME_ON								5
#define PERIODO								6
#define NUMERO_DE_CICLOS_PULSE				7

// Portas logicas: Inversor, AND, NAND, OR, NOR, XOR e NXOR
#define V_LOGIC								0
#define R_LOGIC								1
#define C_LOGIC								2
#define	A_LOGIC								3

// Funcao NoLinearSourceOfLogicGate
#define MAX_CONTROL_LOGIC					3
#define CONTROL_NO_SOURCE					0
#define	DEPENDENT_SOURCE					1
#define INDEPENDENT_SOURCE					2


// Parametos das curvas do resistor não linear
#define NOLINEAR_VOLTAGE_1					0
#define NOLINEAR_CURRENT_1					1
#define NOLINEAR_VOLTAGE_2					2
#define NOLINEAR_CURRENT_2					3
#define NOLINEAR_VOLTAGE_3					4
#define NOLINEAR_CURRENT_3					5
#define NOLINEAR_VOLTAGE_4					6
#define NOLINEAR_CURRENT_4					7




struct Element
{
	int Node_1;
	int Node_2;
	int Control_Node_1;
	int Control_Node_2;
	int Current_Main_Branch;
	int Current_Control_Branch;
	int NumberOfElement;
	double ElementValue;
	double ParametersValue[MAX_NUMBER_OF_PARAMETERS];
	double InitialCondition[MAX_INITIAL_CONDITION];
	string SourceType;
	string ElementName;
	int Number_Of_Nodes;
};

struct Simulation
{
	int UIC;
	int NoLinearCircuit;
	double Tempo_Final;
	double Step;
	double Internal_Step;
	string BE;						// Metodo de analise
	string FistLineOfOutputFile;	// Esse vetor sera posto na primeira linha do arquivo de saida
};



int  MakeNetList(string, Element *, Simulation *);
void NetListShow(Element *);
void ClearNetList(Element *, int);

void IndependentSourceControlByTime(double, double*, Element, double);
void NoLinearSourceOfLogicGate(string, double *, Element);

// Funcao:			           NetList      A         x		   xNR		 B      PSPICE          t     deltaT
void SystemOfEquationBackward(Element *, double *, double *, double*, double *, Simulation *,  double, double);
void ShowMatriz(double *, double *, double *, int, Element *);
void GaussJordan(double *, double *, double *, int );
string convertInt(int);


#endif