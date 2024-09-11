// Universidade Federal do Rio de Janeiro
// Laboratorio de Processamento de Sinais
// Autor: Joao Victor da Fonseca Pinto
//
// Inicio: 21 de dezembro de 2012
// Objetivo: Criar um simulador de circuitos em analise
// nodal modificada no tempo



#include "MnaHeader.h"



int main(){

	// Criando o sistema Ax = B
	double A[NUMBER_MAX_OF_NODES*NUMBER_MAX_OF_NODES];		// Pseudo matriz bidimencional
	double x[NUMBER_MAX_OF_NODES] = {0};
	double xNewtonRaphson[NUMBER_MAX_OF_NODES] = {0};		// Vetor usado para o metode de Newton Raphson
	double B[NUMBER_MAX_OF_NODES] = {0};

	
	// Parametros de simulação
	double deltaT = 0;
	double t = 0;
	double tolerance = 1,
		   MaxInternalStep    = 1;
	
	// Variaveis usadas
	string NetListName, OutputFileName,debugMode = " ";
	Element NetList[NUMBER_MAX_ELEMENTS];
	Simulation PSPICE;
	PSPICE.NoLinearCircuit = 0;
	int NumberOfVariables  = 0,
		NumberOfElements   = 0,
		NumberOfGuesses    = 0,
		internalStep	   = 0,
						i  = 0,
						j  = 0;
	
	int NumberOfExecutionNewtonRaphson = 20;	// O numero 20 trata o erro no tempo igual a zero no modo Newton Raphson
	
	
	// Tela Inicial
	cout << "Circuit Simulator by Aesir                 Begin: 21/12/2012" << endl;
	cout << "Names: Joao Victor da Fonseca Pinto" << endl;
	cout << "       Felipe Gonzalez Tubio Machado" << endl;
	cout << "       Henrique Dias de Alexandria Goncalves" << endl << endl;
	cout << "Enter the name of the Netlist: ";
	cin >> NetListName;
	
	
	// Capturando NetList do arquivo 
	NumberOfVariables = MakeNetList(NetListName, &NetList[0], &PSPICE);
	cout << endl;
	NetListShow(&NetList[0]);
	cout << endl;
	

	// Perfil de simulacao
	cout << "Perfil de simulacao:" << endl;
	cout << "Passo: " << PSPICE.Step << "s " << ", Passo interno: " << PSPICE.Internal_Step;
	cout << ", Tempo final: " << PSPICE.Tempo_Final << "s ";
	deltaT = PSPICE.Step/PSPICE.Internal_Step;	// Passo interno da simulacao
	cout << ", Passo de integracao: " << deltaT << endl;
	cout << "Numero de variaveis: " << NumberOfVariables << endl;
	cout << "Condicoes iniciais: " << PSPICE.UIC << endl;
	cout << "Numero de pontos: " << PSPICE.Tempo_Final/PSPICE.Step << endl;
	

	// caso haja um numero de pontos muito grande, abortara a simulacao para evitar espera.
	if ((PSPICE.Tempo_Final/PSPICE.Step) > NUMBER_MAX_OF_POINT){
		cout << "Tempo muito grande ou passo muito pequeno, numero de pontos maior que 10000000" << endl;
		system("pause");
		exit(0);
	}
	
	// Pergunta se deseja habilitar o mode debug
	cout << "Debug mode y/n: ";
	cin >> debugMode;
	cout << endl;

	// Criando arquivo de saida
	OutputFileName = NetListName.substr(0 , NetListName.length() - 4);			// Retirando o .txt da variavel
	ofstream OutputFile(OutputFileName.append("_Simulated.tab").c_str());		// Adicionando o _Simulated.tab na variavel
	OutputFile << PSPICE.FistLineOfOutputFile << endl;							// Colocando as variaveis na primeira linha	
	
	
	
	// Laco de resolucao da simulacao no tempo
	while (t <= PSPICE.Tempo_Final){

		if (t == 0){
			MaxInternalStep = 1;
			// Inicio da simulacao: passo bem menor para acomodar o circuito ao primeiro loop (dica!)
			deltaT = (PSPICE.Step/PSPICE.Internal_Step)/STEPFACTOR;	// Esse passo interno so roda em t igual a zero na primeiro passo interno
		}

		if (t > 0){
			MaxInternalStep = PSPICE.Internal_Step;
			deltaT = (PSPICE.Step/PSPICE.Internal_Step);	
		}


		// Loop de passos internos
		while (internalStep < MaxInternalStep){	
		


			// Laco do Newton Raphson:
			// Ele executa o ciclo por 20 vezes, caso nao convirja, abandonar aproximacao
			// e chutar novamente. Caso o numero maximo de chutes seja atingido (100 chutes)
			// eu aborto a analise. Caso o ciclo de Newton Raphson nao esteja habilitado, eu entro
			// no laco e saio com o ESCAPE_NEWTON_RAPHSON.
			while(tolerance > TOLERANCE){
			
				// Se o circuito tiver um elemento nao linear (N e portas logicas)
				if(PSPICE.NoLinearCircuit == 1){
					if((NumberOfExecutionNewtonRaphson == 20)){
						if(NumberOfGuesses > NUMBER_MAX_OF_GUESSES){
							cout << "Sistema impossivel" << endl;
							system("pause");
							exit(3);
						}
						// chutando um valor para o ciclo de Newton Raphson 
						for(i = 1; i <= NumberOfVariables; i++)
							xNewtonRaphson[i] = (rand()%100) + 1;
					
						NumberOfGuesses++;
						NumberOfExecutionNewtonRaphson = 0;
					}
				}

		
				// Montando as estampas na matriz de analise nodal
				SystemOfEquationBackward(&NetList[0], &A[0], &x[0], &xNewtonRaphson[0], &B[0], &PSPICE, t, deltaT);
				
				// Resolve o sistema de equacoes
				GaussJordan(&A[0], &B[0], &x[0], NumberOfVariables);
				
				// Funcao para DEBUG do simulador
				if(debugMode == "y"){
					cout << "t: " << t << "s, Passo de integracao: " << deltaT << ", Passo interno: " << internalStep + 1 << endl;
					ShowMatriz(&A[0], &x[0], &B[0], NumberOfVariables, &NetList[0]);
					system("pause");
				}

				// Se nao tiver elementos nao lineares, pule para fora do laco de Newton Raphson
				if(PSPICE.NoLinearCircuit == 0)
					goto ESCAPE_NEWTON_RAPHSON;

				// Caso exista um elemento nao linear, continua o laco.
				for(i = 1; i <= NumberOfVariables; i++){
					tolerance = fabs((x[i]) - xNewtonRaphson[i]);
				
					if(tolerance > TOLERANCE){
						// Atualizando o vetor do Newton Raphson
						for(j = 1; j <=NumberOfVariables; j++)
							xNewtonRaphson[j] = x[j];

						// Forca a saida do laco
						i = NumberOfVariables;
					}
				}
			
			NumberOfExecutionNewtonRaphson++;
			// End of Newton Raphson
			}

			ESCAPE_NEWTON_RAPHSON:

			// Atualizando as condicoes iniciais do capacitor, indutor e capacitores das portas logicas
			while(NetList[NumberOfElements].ElementName != "EndOfNetList"){
				switch(NetList[NumberOfElements].ElementName[FIRST_CARACTER])
				{
				case 'C':
					{
						NetList[NumberOfElements].InitialCondition[REATIVE_IC] = x[NetList[NumberOfElements].Node_1] - x[NetList[NumberOfElements].Node_2];
						break;
					}
	
				case 'L':
					{
						NetList[NumberOfElements].InitialCondition[REATIVE_IC] = x[NetList[NumberOfElements].Current_Main_Branch];
						break;
					}
				
				case '>':
					{
						NetList[NumberOfElements].InitialCondition[LOGIC_IC_A] = x[NetList[NumberOfElements].Control_Node_1] - x[0];
						break;
					}

				case ')': case '(': case '}': case '{': case ']': case '[':
					{
						NetList[NumberOfElements].InitialCondition[LOGIC_IC_A] = x[NetList[NumberOfElements].Control_Node_1] - x[0];
						NetList[NumberOfElements].InitialCondition[LOGIC_IC_B] = x[NetList[NumberOfElements].Control_Node_2] - x[0];
						break;
			    	}
				}

				NumberOfElements++;
				// End Of update (UIC)
			}
		
			internalStep++;
			NumberOfElements = 0;					// Volta para o inicio da NetList para a atualizacao das UICs
			NumberOfGuesses = 0;					// Zera o numero de chutes para a proxima rodada
			NumberOfExecutionNewtonRaphson = 20;		
			tolerance =  1;							// Habilita o ciclo de Newton Raphson novamente
			
			//end of internal step
			}
		
		// Passando resultado da simulacao para o arquivo de saida
		OutputFile << t << "  ";
		for(i = 1; i <= NumberOfVariables; i++)
			OutputFile << setw(10) << x[i] << "  ";
		OutputFile << endl;
		
		internalStep = 0;
		t += PSPICE.Step;						// Proximo passo
		
		
	// End of Time
	}

cout << "Analise concluida! O arquivo gerado tem o nome: " << OutputFileName << endl;
system("pause");
OutputFile.close();
}
