// Universidade Federal do Rio de Janeiro
// Laboratorio de Processamento de Sinais
// Autor: Joao Victor da Fonseca Pinto
//
// Inicio: 21 de dezembro de 2012
// Objetivo: Criar um simulador de circuitos em analise
// nodal modificada no tempo


#include "MnaHeader.h"


// Essa funcao abre o arquivo NetList e monta a estrutura Elements com
// todos os paramentros para simula��o.
void ClearNetList(Element *NetList, int NumberOfElements){
		NetList[NumberOfElements].Node_1 = NOT_USER;
		NetList[NumberOfElements].Node_2 = NOT_USER;
		NetList[NumberOfElements].Control_Node_1 = NOT_USER;
		NetList[NumberOfElements].Control_Node_2 = NOT_USER;
		NetList[NumberOfElements].Current_Main_Branch = NOT_USER;
		NetList[NumberOfElements].Current_Control_Branch = NOT_USER;
		NetList[NumberOfElements].NumberOfElement = NOT_USER;
		NetList[NumberOfElements].ElementValue = NOT_USER;
		NetList[NumberOfElements].ParametersValue[0] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[1] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[2] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[3] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[4] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[5] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[6] = NOT_USER;
		NetList[NumberOfElements].ParametersValue[7] = NOT_USER;
		NetList[NumberOfElements].InitialCondition[0] = 0;
		NetList[NumberOfElements].SourceType = "NotUser";
		NetList[NumberOfElements].Number_Of_Nodes = NOT_USER;

}


string convertInt(int number)
{
   stringstream ss;//create a stringstream
   ss << number;//add number to the stream
   return ss.str();//return a string with the contents of the stream
}


int MakeNetList(string NetListName, Element *NetList, Simulation *PSPICE){
	
	// Variaveis
	string NetListLine,
		   Buffer,
		   UseInitialContidions,
		   Auxiliar;


	int NumberOfNodes = 0,
		NumberOfElements = 0,
		i;
	
	PSPICE[0].NoLinearCircuit = 0;		// Tira o lixo

	// Abertura de arquivo
	ifstream NetListFile(NetListName.c_str());
	
	// Verifica se o arquivo foi aberto
	if(NetListFile.is_open() == false)
	{
		cout << "The Opening Of The File Failed." << endl;
		system("Pause");
		exit(OPENING_FILE_FAILED);
	}

	cout << "File opening ok" << endl;
	
	// se o arquivo foi aberto, continuamos com a leitura das linhas
	// getline le uma linha do NetListFile e passa para NetListLine
	getline(NetListFile,NetListLine);
	stringstream(NetListLine) >> NumberOfNodes;

	// Teste de tamanho do circuito. Se o n�mero de nos for maior que o 
	// permitido, o programa � interrompido.
	if (NumberOfNodes > NUMBER_MAX_OF_NODES){
		cout << "Too many nodes" << endl;
		system("Pause");
		exit(NUMBER_MAX_OF_NODES_EXCEEDED);
	}

	cout << "Number max of nodes accepted" << endl;
	
	// Aqui eu monto o vetor de nos e correntes que sera posto na primeira linha
	// do arquivo de saida
	PSPICE[0].FistLineOfOutputFile = "t ";
	for(i = 1; i <= NumberOfNodes; i++)
		PSPICE[0].FistLineOfOutputFile += convertInt(i) + " ";
	// As outras correntes serao nomeadas ao longo da funcao


	// Passando o valor da primeira corrente para analise nodal modificada
	int Current_JX = NumberOfNodes + 1; 
	
	// Construindo a NetList
	while(getline(NetListFile,NetListLine)){
		// Aqui eu leio o primeiro espa�o
		stringstream LineStream(NetListLine);
		LineStream >> Buffer;

		// Passando o nome do componente para a estrutura
		NetList[NumberOfElements].ElementName = Buffer;

		// Tirando o lixo de memoria e colocando NotUser
		ClearNetList(&NetList[0], NumberOfElements);

		switch (NetList[NumberOfElements].ElementName[FIRST_CARACTER])
		{

		// Resistor: RName NoIN NoOUT Value
		case 'R':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NumberOfElements++;
				break;
			}
	
		// Indutor: LName NoIN NoOUT Value InitialCondition(Corrente)
		case 'L':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				
				// Verifica se existe condic�o inicial
				if((LineStream >> Auxiliar).fail())
					NetList[NumberOfElements].InitialCondition[REATIVE_IC] = 0;
				else
					// Converte string para double
					NetList[NumberOfElements].InitialCondition[REATIVE_IC] = atof(Auxiliar.substr(3, Auxiliar.length() - 1).c_str());
				
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NetList[NumberOfElements].Current_Main_Branch = Current_JX;			//Jx
				PSPICE[0].FistLineOfOutputFile += "J" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";

				Current_JX++;
				NumberOfElements++;
				break;	
			}

		// Capacitor: CName NoIN NoOUT Value InitialCondition(Tensao)
		case 'C':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				
				// Verifica se existe condic�o inicial
				if((LineStream >> Auxiliar).fail())
					NetList[NumberOfElements].InitialCondition[REATIVE_IC] = 0;
				else
					// Converte string para double
					NetList[NumberOfElements].InitialCondition[REATIVE_IC] = atof(Auxiliar.substr(3, Auxiliar.length() - 1).c_str());
				
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NumberOfElements++;
				break;
			}
		
		// Fonte de Tensao controlada por tensao: EName NoIN NoOUT NoInControl NoOutControl Av
		case 'E':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].Control_Node_1;
				LineStream >> NetList[NumberOfElements].Control_Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NetList[NumberOfElements].Current_Main_Branch = Current_JX;			//Jx
				PSPICE[0].FistLineOfOutputFile += "J" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";

				Current_JX++;
				NumberOfElements++;
				break;
			}
			
		// Fonte de corrente controlada a corrente: FNome NoIN NoOUT NoInControl NoOutControl Ai
		case 'F':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].Control_Node_1;
				LineStream >> NetList[NumberOfElements].Control_Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NetList[NumberOfElements].Current_Control_Branch = Current_JX;			//Jx
				PSPICE[0].FistLineOfOutputFile += "J" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";

				Current_JX++;
				NumberOfElements++;
				break;

			}

		// Fonte de corrente controlada por tensao: GNome NoIN NoOUT NoInControl NoOutControl Gm
		case 'G':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].Control_Node_1;
				LineStream >> NetList[NumberOfElements].Control_Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
	

				NumberOfElements++;
				break;
			}

		// Fonte de tensao controlada por corrente: HNome NoIN NoOUT NoInControl NoOutControl Rm
		case 'H':
		{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].Control_Node_1;
				LineStream >> NetList[NumberOfElements].Control_Node_2;
				LineStream >> NetList[NumberOfElements].ElementValue;
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NetList[NumberOfElements].Current_Main_Branch = Current_JX;				//Jx
				PSPICE[0].FistLineOfOutputFile += "Jx_" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";
				NetList[NumberOfElements].Current_Control_Branch = Current_JX + 1;		//Jy
				PSPICE[0].FistLineOfOutputFile += "Jy_" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";

				Current_JX++;
				NumberOfElements++;
				break;
		}


		// Fonte de corrente: INome NoIN NoOUT Value
		// Fonte de tensao: VNome NoIN NoOUT SourceType Parameters
		case 'I': case 'V':
			{
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;

				if(NetList[NumberOfElements].ElementName[FIRST_CARACTER] == 'V'){
					NetList[NumberOfElements].Current_Main_Branch = Current_JX;
					PSPICE[0].FistLineOfOutputFile += "J" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";
					Current_JX++;
				}


				LineStream >> NetList[NumberOfElements].SourceType;
				// Existe tres tipos de fonte: DC, PULSE e SENOIDAL
				

				// Fonte DC
				if(NetList[NumberOfElements].SourceType == "DC"){
					LineStream >> NetList[NumberOfElements].ParametersValue[DC_VALUE];
				}

				// Fonte SIN
				if(NetList[NumberOfElements].SourceType == "SIN"){
					LineStream >> NetList[NumberOfElements].ParametersValue[NIVEL_CONTINUO];
					LineStream >> NetList[NumberOfElements].ParametersValue[AMPLITUDE];
					LineStream >> NetList[NumberOfElements].ParametersValue[FREQUENCIA];
					LineStream >> NetList[NumberOfElements].ParametersValue[ATRASO];
					LineStream >> NetList[NumberOfElements].ParametersValue[ATENUACAO];
					LineStream >> NetList[NumberOfElements].ParametersValue[ANGULO];
					LineStream >> NetList[NumberOfElements].ParametersValue[NUMERO_DE_CICLOS_SIN];
				}

				// Fonte PULSE
				if(NetList[NumberOfElements].SourceType == "PULSE"){
					LineStream >> NetList[NumberOfElements].ParametersValue[AMPLITUDE_1];
					LineStream >> NetList[NumberOfElements].ParametersValue[AMPLITUDE_2];
					LineStream >> NetList[NumberOfElements].ParametersValue[ATRASO_PULSE];
					LineStream >> NetList[NumberOfElements].ParametersValue[TIME_RISE];
					LineStream >> NetList[NumberOfElements].ParametersValue[TIME_FALL];
					LineStream >> NetList[NumberOfElements].ParametersValue[TIME_ON];
					LineStream >> NetList[NumberOfElements].ParametersValue[PERIODO];
					LineStream >> NetList[NumberOfElements].ParametersValue[NUMERO_DE_CICLOS_PULSE];
				}

				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NumberOfElements++;
				break;
			}

		// Amplificador Operacional Ideal: ONome NoOUT+ NoOUT- NoIN+ NoIN- (esse modelo nao e o usado no edfil)
		// Modelo do edfil: ONome c d a (Referente a pag 15)
		case 'O':
			{                                                                           // Modelo pag:15
				LineStream >> NetList[NumberOfElements].Control_Node_1;					// c entrada +
				LineStream >> NetList[NumberOfElements].Control_Node_2;					// d entrada -
				LineStream >> NetList[NumberOfElements].Node_1;							// a saida +
				NetList[NumberOfElements].Node_2 = 0;									// b saida -

				NetList[NumberOfElements].NumberOfElement = NumberOfElements;			//
				NetList[NumberOfElements].Current_Main_Branch = Current_JX;				//Jx (a para b)
				PSPICE[0].FistLineOfOutputFile += "J" + convertInt(Current_JX) + NetList[NumberOfElements].ElementName + " ";

				Current_JX++;
				NumberOfElements++;
				break;
			}


		// Os par�metros para as portas l�gicas s�o: <V> <R> <C> <A>
		// A tens�o V � a tens�o de sa�da m�xima, R a resist�ncia da sa�da, C a capacit�ncia de entrada, para cada entrada,
		// e o ganho A � a derivada da tens�o de sa�da em aberto em rela��o � varia��o da tens�o em qualquer entrada,
		// antes da satura��o da sa�da.
		
		// Inversor: >Nome NoIN NoOUT Parameters
		case '>':
			{
				PSPICE[0].NoLinearCircuit = 1;		// Habilita o laco do Newton Raphson	
				LineStream >> NetList[NumberOfElements].Control_Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				LineStream >> NetList[NumberOfElements].ParametersValue[V_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[R_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[C_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[A_LOGIC];
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NetList[NumberOfElements].InitialCondition[LOGIC_IC_A] = 0;		// Capacitor do modelo de entrada
				NumberOfElements++;
				break;
			}

		// Portas: Nome NoControlIn NoControlIN(OUT) NoOUT Parameters
		case ')': case '(': case '}': case '{': case ']': case '[':
			{
				PSPICE[0].NoLinearCircuit = 1;		// Habilita o laco do Newton Raphson
				LineStream >> NetList[NumberOfElements].Control_Node_1;		//In A
				LineStream >> NetList[NumberOfElements].Control_Node_2;		//In B
				LineStream >> NetList[NumberOfElements].Node_2;				//Out
				LineStream >> NetList[NumberOfElements].ParametersValue[V_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[R_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[C_LOGIC];
				LineStream >> NetList[NumberOfElements].ParametersValue[A_LOGIC];
				NetList[NumberOfElements].InitialCondition[LOGIC_IC_A] = 0;		// Capacitor do modelo de entrada
				NetList[NumberOfElements].InitialCondition[LOGIC_IC_B] = 0;		// Capacitor do modelo de entrada
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NumberOfElements++;
				break;
			}
		
		// Resistor n�o Linear
		case 'N':
			{
				PSPICE[0].NoLinearCircuit = 1;		// Habilita o laco do Newton Raphson	
				LineStream >> NetList[NumberOfElements].Node_1;
				LineStream >> NetList[NumberOfElements].Node_2;
				// Definindo retas
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_1];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_1];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_2];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_3];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_4];
				LineStream >> NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_4];
				NetList[NumberOfElements].NumberOfElement = NumberOfElements;
				NumberOfElements++;
				break;
			}



		// Parametros de Simulacao: <.TRAN> <TempoFinal> <Passo> <BE> <PassoInterno> <UIC>
		case '.':
			{
				LineStream >> PSPICE[0].Tempo_Final;
				LineStream >> PSPICE[0].Step;
				LineStream >> PSPICE[0].BE;
				LineStream >> PSPICE[0].Internal_Step;
				NetList[NumberOfElements].ElementName = "EndOfNetList";		
				if((LineStream >> UseInitialContidions).fail())
					PSPICE[0].UIC = 0;
				else
					PSPICE[0].UIC = 1;

				break;
			}

		// Tratamento de erro: caso haja elemento desconhecido na netlist
		default:
			{
				cout << "Elemento " << NetList[NumberOfElements].ElementName << " desconhecido." << endl;
				system("pause");
				exit(0);
			}

		// End of Swich
		}
	// End of While
	}

	NetListFile.close();
	NetList[NumberOfElements].Number_Of_Nodes = NumberOfNodes;		// Repassa o numero de nos do circuito
	int NumberOfVariables = Current_JX - 1;		//Aqui eu ja conto a linha e coluna zero da MNA
	return (NumberOfVariables);
	// End of MakeNetList
}


// Funcao de DEBUG para o MakeNetList
void NetListShow(Element *NetList){
	int auxiliar = 0;
	cout << "Componentes da NetList: " << endl;
	while(NetList[auxiliar].ElementName != "EndOfNetList"){
		
		switch(NetList[auxiliar].ElementName[FIRST_CARACTER]){
		
		case 'R':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " " << NetList[auxiliar].ElementValue << " " << endl;
			auxiliar++;
			break;
			}

		case 'C': case 'L':
			{
				cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " " << NetList[auxiliar].ElementValue << " " << NetList[auxiliar].InitialCondition[REATIVE_IC] << endl;
			auxiliar++;
			break;
			}

		case 'E': case 'F': case 'G': case 'H':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].ElementValue << " (Fonte controlada) " << endl;
			auxiliar++;
			break;
			}

		case 'V': case 'I':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " " << NetList[auxiliar].SourceType << " " << NetList[auxiliar].ParametersValue[0] << " "  << NetList[auxiliar].ParametersValue[1] << " " << NetList[auxiliar].ParametersValue[2] << " (Fonte independente) " << endl; 
			auxiliar++;
			break;
			}
		case 'O':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].ElementValue << " (Ampop Ideal) " << endl;
			auxiliar++;
			break;
			}
		case 'N':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Node_1 << " " << NetList[auxiliar].Node_2 << " (Resistor Nao Linear) " << endl;
			auxiliar++;
			break;
			}
		case '>':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " (Inversor) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}

		case ')':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (AND) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}

		case '(':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (NAND) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}


		case '}':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (OR) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}

		case '{':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (NOR) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}

		case ']':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (XOR) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}

		case '[':
			{
			cout << NetList[auxiliar].ElementName << " " << NetList[auxiliar].Control_Node_1 << " " << NetList[auxiliar].Control_Node_2 << " " << NetList[auxiliar].Control_Node_2 << " (XNOR) " << " R: " <<
				NetList[auxiliar].ParametersValue[R_LOGIC] << " C: " << NetList[auxiliar].ParametersValue[C_LOGIC] << " A: "<<NetList[auxiliar].ParametersValue[A_LOGIC] <<
				" V: " << NetList[auxiliar].ParametersValue[V_LOGIC] << endl;
			auxiliar++;
			break;
			}


		default:
			auxiliar++;

		}
	}
	cout << "Numero de nos: " << NetList[auxiliar].Number_Of_Nodes << endl;
}

// Funcao para as fontes DC, SIN e PULSE
void IndependentSourceControlByTime(double t, double *out, Element NetList, double Step){
		   // SIN
	double Amp,				// Amplitude
		   Ang,				// Angulo
		   Delay,			// Atraso
		   NivelDC,			// Nivel DC da Senoide
		   alpha,			// Atenuacao da exponencial
		   f,				// Frequencia
		   // PULSE
		   Amp_1,			// Amplitude 1 da fonte PULSE
		   Amp_2,			// Amplitude 2 da fonte PULSE
		   TR,				// TIME RISE
		   TF,				// TIME FALL
		   T_ON,			// TIME ON
		   CoeficienteAngularDaReta;

	// Fonte DC
	if(NetList.SourceType == "DC")
		out[0] = NetList.ParametersValue[DC_VALUE];	
				

	// Fonte Senoidal
	if(NetList.SourceType == "SIN"){
			
		// Parametros da senoide
		Amp = NetList.ParametersValue[AMPLITUDE];
		NivelDC = NetList.ParametersValue[NIVEL_CONTINUO];
		Delay = NetList.ParametersValue[ATRASO];
		f = NetList.ParametersValue[FREQUENCIA];
		Ang = NetList.ParametersValue[ANGULO];
		alpha = NetList.ParametersValue[ATENUACAO];

		// A senoide comeca como uma exponencial crescente, fica estabilizda entorno de uma amplitude
		// e apos o tempo de termino, cai exponencialmente
		if((t < Delay)||(t > (Delay + (1/f)*NetList.ParametersValue[NUMERO_DE_CICLOS_SIN])))
			// Senoide
			out[0] = (NivelDC + Amp*sin((PI*Ang)/180));
						
		else
			// Senoide + exponencial
			out[0] = (NivelDC + Amp*exp(-alpha*(t - Delay))*sin(2*PI*f*(t - Delay) + (PI*Ang)/180));				
	}

	// Fonte PULSE
	if(NetList.SourceType == "PULSE"){

		// Parametros da Fonte PULSE
		Amp_1 = NetList.ParametersValue[AMPLITUDE_1];	
		Amp_2 =	NetList.ParametersValue[AMPLITUDE_2];	
		TR = NetList.ParametersValue[TIME_RISE];
		TF = NetList.ParametersValue[TIME_FALL];
		T_ON = NetList.ParametersValue[TIME_ON];
		Delay = NetList.ParametersValue[ATRASO_PULSE];
					
		// Tratamento caso tempo de subido ou descida sejam zero
		if(TR == 0){
			NetList.ParametersValue[TIME_RISE] = Step;
			TR = NetList.ParametersValue[TIME_RISE];
		}
		if(TF == 0){
			NetList.ParametersValue[TIME_FALL] = Step;
			TF = NetList.ParametersValue[TIME_FALL];
		}

		if((t <= (NetList.ParametersValue[PERIODO]*NetList.ParametersValue[NUMERO_DE_CICLOS_PULSE] + Delay)) && (t > Delay)){
			
			// Aqui eu ajusto o tempo para ficar dentro da faixa de um periodo (fica mais simples de fazer!)
			t -= Delay;
			while(t > NetList.ParametersValue[PERIODO])
				t -= NetList.ParametersValue[PERIODO];
										
			if((t >= 0) && (t < TR)){
				CoeficienteAngularDaReta = (Amp_2 - Amp_1)/TR;
				out[0] = (NetList.ParametersValue[AMPLITUDE_1] + t*CoeficienteAngularDaReta);	
			}

			if((t >= TR) && (t <= (TR + T_ON)))
				out[0] = NetList.ParametersValue[AMPLITUDE_2];	
			
			if((t > (TR + T_ON)) && (t <= (TR + T_ON + TF))){
				CoeficienteAngularDaReta = (Amp_1 - Amp_2)/TF;
				out[0] = (NetList.ParametersValue[AMPLITUDE_2] + (t-(TR + T_ON))*CoeficienteAngularDaReta);
			}

			if(t > (TR + T_ON + TF))
				out[0] = NetList.ParametersValue[AMPLITUDE_1];
		}
				
		// t maior que os ciclos especificados
		else
		out[0] = NetList.ParametersValue[AMPLITUDE_1];
	}
					

//End of function
}

// Funcao nao utilizada no programa
void NoLinearSourceOfLogicGate(double  in_A, double in_B, double *out, Element NetList){

int Control_No_Source,	// No de controle da fonte n�o linear
	Control_No_1,		// Entrada A
	Control_No_2,		// Entrada B
	No_2,				// Saida
	VM,
	VIH,
	VIL;


double VoltageControlSource,	// Tens�o no n� de controle
       G,						// Derivada da fonte controlada
	   V_NoLinear;				// Ten�o da fonte independente


Control_No_1 = NetList.Control_Node_1;
Control_No_2 = NetList.Control_Node_2;
No_2 = NetList.Node_2;
VM  = NetList.ParametersValue[V_LOGIC]/2;
VIH = VM + VM/NetList.ParametersValue[A_LOGIC];
VIL = VM - VM/NetList.ParametersValue[A_LOGIC];
	
switch (NetList.ElementName[FIRST_CARACTER])
	{

		// NOT: Curva da fonte de corrente controlada n�o linear
		case '>':
			{
			VoltageControlSource = in_A;
			Control_No_Source = Control_No_1;
			// Aqui, G � a derivada da equacao da reta
			if(VoltageControlSource > VIH){
				G = 0;		
				V_NoLinear = 0;
			}
			if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
				G = -(NetList.ParametersValue[A_LOGIC]);
				V_NoLinear = NetList.ParametersValue[V_LOGIC]/2 - G*NetList.ParametersValue[V_LOGIC]/2;
			}
			if((VoltageControlSource <= VIL)){
				G = 0;
				V_NoLinear = NetList.ParametersValue[V_LOGIC];
			}
			break;
			}
				
		// AND: Curva da fonte de corrente controlada n�o linear
		case ')':
			{
				
			if(in_A > in_B){
				VoltageControlSource = in_B;
				Control_No_Source = Control_No_2;
			}
			if(in_B > in_A){
				VoltageControlSource = in_A;
				Control_No_Source = Control_No_1;
			}

			// Aqui, G � a derivada da equacao da reta
			if(VoltageControlSource > VIH){
				G = 0;		
				V_NoLinear = NetList.ParametersValue[V_LOGIC];
			}	
			if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
				G = (NetList.ParametersValue[A_LOGIC]);
				V_NoLinear = NetList.ParametersValue[V_LOGIC]/2 - G*NetList.ParametersValue[V_LOGIC]/2;
			}
			if((VoltageControlSource <= VIL)){
				G = 0;
				V_NoLinear = 0;
			}

			break;
			}

				
		// NAND: Curva da fonte de corrente controlada n�o linear OK
		case '(':
			{
					
			if(in_A > in_B){
				VoltageControlSource = in_B;
				Control_No_Source = Control_No_2;
			}
			if(in_B > in_A){
				VoltageControlSource = in_A;
				Control_No_Source = Control_No_1;
			}
		// Aqui, G � a derivada da equacao da reta
			if(VoltageControlSource > VIH){
				G = 0;
				V_NoLinear = 0;
			}	
			if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
				G = -(NetList.ParametersValue[A_LOGIC]);
				V_NoLinear = NetList.ParametersValue[V_LOGIC]/2 - G*NetList.ParametersValue[V_LOGIC]/2;
			}
			if((VoltageControlSource <= VIL)){
				G = 0;		
				V_NoLinear = NetList.ParametersValue[V_LOGIC];
			}	
			
			break;
			}

		// OR: Curva da fonte de corrente controlada n�o linear OK
		case '}':
			{
						
			if(in_A > in_B){
				VoltageControlSource = in_A;
				Control_No_Source = Control_No_1;
			}
			if(in_B > in_A){
				VoltageControlSource = in_B;
				Control_No_Source = Control_No_2;
			}
			// Aqui, G � a derivada da equacao da reta
			if(VoltageControlSource > VIH){
				G = 0;		
				V_NoLinear = NetList.ParametersValue[V_LOGIC];
			}	
			if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
				G = (NetList.ParametersValue[A_LOGIC]);
				V_NoLinear = NetList.ParametersValue[V_LOGIC]/2 - G*NetList.ParametersValue[V_LOGIC]/2;
			}
			if((VoltageControlSource <= VIL)){
				G = 0;
				V_NoLinear = 0;	
			}

			break;
			}

		// NOR: Curva da fonte de corrente controlada n�o linear OK
		case '{':
			{
						
			if(in_A > in_B){
				VoltageControlSource = in_A;
				Control_No_Source = Control_No_1;
			}
			if(in_B > in_A){
				VoltageControlSource = in_B;
				Control_No_Source = Control_No_2;
			}
			// Aqui, G � a derivada da equacao da reta
			if(VoltageControlSource > VIH){
				G = 0;		
				V_NoLinear = 0;
			}	
			if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
				G = -(NetList.ParametersValue[A_LOGIC]);
				V_NoLinear = NetList.ParametersValue[V_LOGIC]/2 - G*NetList.ParametersValue[V_LOGIC]/2;
			}
			if((VoltageControlSource <= VIL)){
				G = 0;
				V_NoLinear = NetList.ParametersValue[V_LOGIC];
			}
			break;
			}

	// End of switch
	}

	out[CONTROL_NO_SOURCE] = Control_No_Source;
	out[DEPENDENT_SOURCE] = G;
	out[INDEPENDENT_SOURCE] = V_NoLinear;

}


// Costroi o sistema Ax = B da MNA
// Usaremos o m�todo de backward de Euler para a solucao no tempo
// Backward:
//			y(t + deltaT) = y(t) + deltaT*x(t + deltaT)
//			Ax(t + deltaT) = B
//
void SystemOfEquationBackward(Element *NetList, double *A_Externo, double *x, double *xNewtonRaphsonInterno,double *B, Simulation *PSPICE, double t, double deltaT){


	int NumberOfElements  = 0;
	int No_1			  = 0,	// +
		No_2			  = 0,	// -
		Control_No_1	  = 0,	// +
		Control_No_2	  = 0,	// 
		Control_No_Source = 0,
				 i,j	  = 0;
	

	double G = 0,					// Condutancia
		   R = 0,					// Resistencia
		   V_Linear,				// Fonte de tensao 
		   // Parametros para componentes l�gicos
		   I_Linear,				// Fonte de corrente	
		   I_NoLinear,				// Fonte de corrente dependente do resistor n�o linear 
		   V_NoLinear,				// No de controle e fonte de tensao da saida da porta logica 
		   VoltagePartOne,
		   derivedPartTwo,
		   VoltagePartThree,
		   VoltageControlSource,
		   VM, VIL, VIH;


	// Tirando o lixo da matriz auxiliar interna e do vetor b
	double A[NUMBER_MAX_OF_NODES][NUMBER_MAX_OF_NODES] = {0};

	for(i = 0; i< NUMBER_MAX_OF_NODES;i++)
		B[i] = 0;
		

	// Estampas
	while (NetList[NumberOfElements].ElementName != "EndOfNetList"){
		
		// Facilita na escrita do programa
		No_1 = NetList[NumberOfElements].Node_1;
		No_2 = NetList[NumberOfElements].Node_2;
		Control_No_1 = NetList[NumberOfElements].Control_Node_1;
		Control_No_2 = NetList[NumberOfElements].Control_Node_2;
			
		

		switch(NetList[NumberOfElements].ElementName[FIRST_CARACTER]){
			cout << NetList[NumberOfElements].ElementName;
			system("pause");

		// Resistor
		case 'R':
			{
				G = (1/NetList[NumberOfElements].ElementValue);
				A[No_1][No_1] +=  G;		// G
				A[No_1][No_2] += -G;		// G
				A[No_2][No_1] += -G;		// G
				A[No_2][No_2] +=  G;		// G
				NumberOfElements++;
				break;
			}
		
		// Indutor (Modelo de Thevenin)
		case 'L':
			{
				// Ax(t + deltaT) = B(t)
				R = NetList[NumberOfElements].ElementValue/deltaT;					// L/dt
				A[No_1][NetList[NumberOfElements].Current_Main_Branch] +=  1;		// I
				A[No_2][NetList[NumberOfElements].Current_Main_Branch] += -1;		// I
				A[NetList[NumberOfElements].Current_Main_Branch][No_1] += -1;		// V
				A[NetList[NumberOfElements].Current_Main_Branch][No_2] +=  1;		// V				
				A[NetList[NumberOfElements].Current_Main_Branch][NetList[NumberOfElements].Current_Main_Branch] += R;		// R
				
				B[NetList[NumberOfElements].Current_Main_Branch] += (NetList[NumberOfElements].ElementValue/deltaT)*NetList[NumberOfElements].InitialCondition[REATIVE_IC]; 
				
				NumberOfElements++;
				break;
			}
		
		// Capacitor (Modelo de Norton)
		case 'C':
			{
				// Ax(t + deltaT) = B(t)
				G = (1/(deltaT/NetList[NumberOfElements].ElementValue));	// dt/c
				A[No_1][No_1] +=  G;		// G
				A[No_1][No_2] += -G;		// G
				A[No_2][No_1] += -G;		// G
				A[No_2][No_2] +=  G;		// G
				
				// CVc(to)/dt
				B[No_1] +=  NetList[NumberOfElements].ElementValue*(NetList[NumberOfElements].InitialCondition[REATIVE_IC]/deltaT);	// Entra no n� 1
				B[No_2] += -NetList[NumberOfElements].ElementValue*(NetList[NumberOfElements].InitialCondition[REATIVE_IC]/deltaT);	// Sai do n� 2
				
				NumberOfElements++;
				break;
			}

		// Fonte de tensao controlada por tensao	
		case 'E':
			{
				// Ax(t + deltaT) = B(t)

				A[No_1][NetList[NumberOfElements].Current_Main_Branch] +=  1;		// I
				A[No_2][NetList[NumberOfElements].Current_Main_Branch] += -1;		// I
				A[NetList[NumberOfElements].Current_Main_Branch][No_1] += -1;		// V
				A[NetList[NumberOfElements].Current_Main_Branch][No_2] +=  1;		// V
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_1] +=  NetList[NumberOfElements].ElementValue;		// V
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_2] += -NetList[NumberOfElements].ElementValue;		// V
				NumberOfElements++;
				break;
			}

		// Fonte de corrente controlada por corrente
		case 'F':
			{
				// Ax(t + deltaT) = B(t)
				A[Control_No_1][NetList[NumberOfElements].Current_Control_Branch] +=  1;		// I
				A[Control_No_2][NetList[NumberOfElements].Current_Control_Branch] += -1;		// I
				A[NetList[NumberOfElements].Current_Control_Branch][Control_No_1] += -1;		// V
				A[NetList[NumberOfElements].Current_Control_Branch][Control_No_2] +=  1;		// V
				A[No_1][NetList[NumberOfElements].Current_Control_Branch] +=  NetList[NumberOfElements].ElementValue;		// I
				A[No_2][NetList[NumberOfElements].Current_Control_Branch] += -NetList[NumberOfElements].ElementValue;		// I
				NumberOfElements++;
				break;
			}


		// Fonte de corrente controlada por tensao (Tratar como analise nodal simples)
		case 'G':
			{
				// Gm do modelo
				G = NetList[NumberOfElements].ElementValue;
				A[No_1][Control_No_1] +=  G;		// G
				A[No_1][Control_No_2] += -G;		// G
				A[No_2][Control_No_1] += -G;		// G
				A[No_2][Control_No_2] +=  G;		// G
				NumberOfElements++;
				break;
			}

		// Fonte de tensao controlada por corrente:  Rm
		case 'H':
			{
				// Jx
				A[No_1][NetList[NumberOfElements].Current_Main_Branch] +=  1;					// I	
				A[No_2][NetList[NumberOfElements].Current_Main_Branch] += -1;					// I
				// Jy
				A[Control_No_1][NetList[NumberOfElements].Current_Control_Branch] +=  1;		// I
				A[Control_No_2][NetList[NumberOfElements].Current_Control_Branch] += -1;		// I
				// Jx
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_1] += -1;			// V
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_2] +=  1;			// V
				// Jy
				A[NetList[NumberOfElements].Current_Control_Branch][Control_No_1] += -1;		// V
				A[NetList[NumberOfElements].Current_Control_Branch][Control_No_2] +=  1;		// V
				// Resistor Rm do modelo
				A[NetList[NumberOfElements].Current_Main_Branch][NetList[NumberOfElements].Current_Control_Branch] = NetList[NumberOfElements].ElementValue;	// R
				NumberOfElements++;
				break;
			}
		
		// Resistor N�o Linear (por partes)
		case 'N':
			{
				// Escolha do segmento
				if((xNewtonRaphsonInterno[No_1]-xNewtonRaphsonInterno[No_2]) > NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3]){
					// Tangente da reta ou derivada da funcao
					G = (NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_4] - NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_3])/(NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_4] - NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3]);
					I_NoLinear = NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_4] - G*NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_4];
				}

				if(((xNewtonRaphsonInterno[No_1]-xNewtonRaphsonInterno[No_2]) <= NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3]) && ((xNewtonRaphsonInterno[No_1]-xNewtonRaphsonInterno[No_2]) > NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2])){
					// Tangente da reta ou derivada da funcao
					G = (NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_3] - NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_2])/(NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3] - NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2]);
					I_NoLinear = NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_3] - G*NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_3];
				}

				if((xNewtonRaphsonInterno[No_1]-xNewtonRaphsonInterno[No_2]) <= NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2]){
					// Tangente da reta ou derivada da funcao
					G = (NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_2] - NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_1])/(NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2] - NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_1]);
					I_NoLinear = NetList[NumberOfElements].ParametersValue[NOLINEAR_CURRENT_2] - G*NetList[NumberOfElements].ParametersValue[NOLINEAR_VOLTAGE_2];
				}

				A[No_1][No_1] +=  G;		// G
				A[No_1][No_2] += -G;		// G
				A[No_2][No_1] += -G;		// G
				A[No_2][No_2] +=  G;		// G
				// Fonte de corrente referente ao modelo do resistor nao linear indo do no 1 para o no 2.
				B[No_1] += -I_NoLinear;		
				B[No_2] +=  I_NoLinear;
				NumberOfElements++;
				break;
			}


		// Fonte de corrente (tratar como analise nodal simples)
		case 'I':
			{
				IndependentSourceControlByTime(t, &I_Linear, NetList[NumberOfElements],PSPICE[0].Step);
				B[No_1] = -I_Linear;
				B[No_2] =  I_Linear;
				
				NumberOfElements++;
				break;
			}
	

		// Fonte de tensao
		case 'V':
			{
				// Sentido da corrente Jx
				A[No_1][NetList[NumberOfElements].Current_Main_Branch] +=  1;		// I 
				A[No_2][NetList[NumberOfElements].Current_Main_Branch] += -1;		// I
				A[NetList[NumberOfElements].Current_Main_Branch][No_1] += -1;		// V 
				A[NetList[NumberOfElements].Current_Main_Branch][No_2] +=  1;		// V

				IndependentSourceControlByTime(t, &V_Linear, NetList[NumberOfElements], PSPICE[0].Step);		// B
				B[NetList[NumberOfElements].Current_Main_Branch] += -V_Linear;
									
				NumberOfElements++;
				break;
			}
																						
																						
		// Amplificador Operacional Ideal															
		case 'O':
			{																			// Modelo da pag 15:
				A[No_1][NetList[NumberOfElements].Current_Main_Branch]		   =  1;	// a saida +
				A[No_2][NetList[NumberOfElements].Current_Main_Branch]		   = -1;	// b saida -
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_1] = -1;	// c entrada +
				A[NetList[NumberOfElements].Current_Main_Branch][Control_No_2] =  1;	// d entrada -
				NumberOfElements++;
				break;
			}
			

		// Portas Logicas: NOT AND NAND OR NOR XOR EXOR
		// Objetos nao lineares
		// Modelo demostrado no manual
		// Entrada: Um capacitor em serie indo do no de entrada para o terra com uma fonte de corrente para simular 
		// condi��o inicial
		// Saida: Uma fonte de corrente independente, Uma fonte de corrente controlada por tensao e um
		// Resistor, tudo em paralelo indo do terra para a saida.
		case '>': case ')': case '(': case '}': case '{': case ']': case '[':
				{
				// Entrada A:

				// Capacitor ligado da entrada A para o terra
				G = (1/(deltaT/NetList[NumberOfElements].ParametersValue[C_LOGIC]));
				A[Control_No_1][Control_No_1] +=  G;		// G
				A[Control_No_1][0]            += -G;		// G
				A[0][Control_No_1]            += -G;		// G
				A[0][0]                       +=  G;		// G

				// Fonte de corrente (simula��o da condi��o inicial do capacitor) CVc(to)/dt
				B[Control_No_1]  +=  NetList[NumberOfElements].ParametersValue[C_LOGIC]*(NetList[NumberOfElements].InitialCondition[LOGIC_IC_A]/deltaT);	// Entra no n� 1
				B[0] += -NetList[NumberOfElements].ParametersValue[C_LOGIC]*(NetList[NumberOfElements].InitialCondition[LOGIC_IC_A]/deltaT);	// Sai do n� 2



				// Se n�o for um NOT
				if(NetList[NumberOfElements].ElementName[FIRST_CARACTER] != '>'){
					// Entrada B:
					// Capacitor ligado da entrada B para o terra
					A[Control_No_2][Control_No_2] +=  G;		// G
					A[Control_No_2][0]            += -G;		// G
					A[0][Control_No_2]            += -G;		// G
					A[0][0]                       +=  G;		// G

					// Fonte de corrente (simula��o da condi��o inicial do capacitor) CVc(to)/dt
					B[Control_No_2]  +=  NetList[NumberOfElements].ParametersValue[C_LOGIC]*(NetList[NumberOfElements].InitialCondition[LOGIC_IC_B]/deltaT);	// Entra no n� 1
					B[0] += -NetList[NumberOfElements].ParametersValue[C_LOGIC]*(NetList[NumberOfElements].InitialCondition[LOGIC_IC_B]/deltaT);	// Sai do n� 
				}
				

				VM  = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2,
				VIH = VM + VM/NetList[NumberOfElements].ParametersValue[A_LOGIC],
				VIL = VM - VM/NetList[NumberOfElements].ParametersValue[A_LOGIC];
	
				switch (NetList[NumberOfElements].ElementName[FIRST_CARACTER])
				{
				// NOT: Curva da fonte de corrente controlada n�o linear
					case '>':
						{
							VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
							Control_No_Source = Control_No_1;
							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = 0;
							}
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
							break;
						}
				
					// AND: Curva da fonte de corrente controlada n�o linear
					case ')':
						{
							
							if((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);	
								Control_No_Source = Control_No_2;
							}
							if((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);;
								Control_No_Source = Control_No_1;
							}
	
							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = 0;
							}
	
							break;
						}
	
						
					// NAND: Curva da fonte de corrente controlada n�o linear OK
					case '(':
						{
							
							if((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_2;
							}
							if((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);;
								Control_No_Source = Control_No_1;
							}
	
							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;
								V_NoLinear = 0;
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;		
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC];						
							}

							break;
						}

					// OR: Curva da fonte de corrente controlada n�o linear OK
					case '}':
						{
							
							if((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
							}
							if((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);;
								Control_No_Source = Control_No_2;
							}

							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = 0;	
							}
	
							break;
						}

					// NOR: Curva da fonte de corrente controlada n�o linear OK
					case '{':
						{
							
							if((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
							}
							if((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);;
								Control_No_Source = Control_No_2;
							}
	
							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = 0;
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
	
							break;
						}

					// XOR: Curva da fonte de corrente controlada n�o linear
					case ']':
						{

							// VA => VB e VA + VB > V
							if(((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) > NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_2;
								VoltagePartOne = NetList[NumberOfElements].ParametersValue[V_LOGIC];
								derivedPartTwo = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = 0;
							}
							
							// VB > VA e VA + VB > V
							if(((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) > NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
								VoltagePartOne = NetList[NumberOfElements].ParametersValue[V_LOGIC];
								derivedPartTwo = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = 0;
							}
							
							// VA > VB e VA + VB < V
							if(((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) < NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
								VoltagePartOne = 0;
								derivedPartTwo = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
	
							// VB > VA e VA + VB < V
							if(((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) < NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_2;
								VoltagePartOne = 0;
								derivedPartTwo = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
	

							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = VoltagePartThree;
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = derivedPartTwo;
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = VoltagePartOne;
							}

							break;
						}

					// XNOR: Curva da fonte de corrente controlada n�o linear
					case '[':
						{

							// VA >= VB e VA + VB > V
							if(((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) > NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_2;
								VoltagePartOne = 0;
								derivedPartTwo = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
							
							// VB > VA e VA + VB > V
							if(((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) > NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
								VoltagePartOne = 0;
								derivedPartTwo = (NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = NetList[NumberOfElements].ParametersValue[V_LOGIC];
							}
							
							// VA > VB e VA + VB < V
							if(((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) >= (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) < NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_1;
								VoltagePartOne = NetList[NumberOfElements].ParametersValue[V_LOGIC];
								derivedPartTwo = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = 0; 
							}
	
							// VB > VA e VA + VB < V
							if(((xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]) > (xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0])) && (((xNewtonRaphsonInterno[Control_No_1] - xNewtonRaphsonInterno[0]) + (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0])) < NetList[NumberOfElements].ParametersValue[V_LOGIC])){
								VoltageControlSource = (xNewtonRaphsonInterno[Control_No_2] - xNewtonRaphsonInterno[0]);
								Control_No_Source = Control_No_2;
								VoltagePartOne = NetList[NumberOfElements].ParametersValue[V_LOGIC];
								derivedPartTwo = -(NetList[NumberOfElements].ParametersValue[A_LOGIC]);
								VoltagePartThree = 0;
							}
	


							// Aqui, G � a derivada da equacao da reta
							if(VoltageControlSource > VIH){
								G = 0;		
								V_NoLinear = VoltagePartThree;
							}	
							if((VoltageControlSource <= VIH) && (VoltageControlSource > VIL)){
								G = derivedPartTwo;
								V_NoLinear = NetList[NumberOfElements].ParametersValue[V_LOGIC]/2 - G*NetList[NumberOfElements].ParametersValue[V_LOGIC]/2;
							}
							if((VoltageControlSource <= VIL)){
								G = 0;
								V_NoLinear = VoltagePartOne;
							}

							break;
						}

				// End of logic gate
				}

				// Saida:
				// Fonte de corrente controlada por tensao 
				G = G/NetList[NumberOfElements].ParametersValue[R_LOGIC];
				A[0][Control_No_Source]    +=  G;	// G.
				A[0][0]					   += -G;	// G
				A[No_2][Control_No_Source] += -G;	// G
				A[No_2][0]				   +=  G;	// G
			
				
				// Fonte de corrente indo do terra para a saida do inversor
				B[0]    += -(V_NoLinear/NetList[NumberOfElements].ParametersValue[R_LOGIC]);	// Sai do n� 1
				B[No_2] +=  (V_NoLinear/NetList[NumberOfElements].ParametersValue[R_LOGIC]);	// Entra no n� 2

				
				// Resistor de saida em paralelo com a saida
				G = (1/NetList[NumberOfElements].ParametersValue[R_LOGIC]);
				A[No_2][No_2] +=  G;		// G
				A[No_2][0]    += -G;		// G
				A[0][No_2]    += -G;		// G
				A[0][0]       +=  G;		// G

				NumberOfElements++;
				break;
				}

		// End of switch			
		}
		
	// End of while
	}

	
	
	// Passando os valores para a pseudo matriz
	for(i = 0; i < NUMBER_MAX_OF_NODES; i++){
		for(j = 0; j < NUMBER_MAX_OF_NODES; j++){
			A_Externo[i*NUMBER_MAX_OF_NODES + j] = A[i][j];
		}
	}

	
// End of function
}


// Funcao de DEBUG da matriz de analise nodal
void ShowMatriz(double *A_Externo, double *X, double *B, int NumberOfVariables, Element *NetList){

	int i,
		j,
		NumberOfElements = 0;

	char x = 'V';

	// Encontra o fim da NetList
	while(NetList[NumberOfElements].ElementName != "EndOfNetList")
		NumberOfElements++;
	// Repassa o numero de nos do circuito (Vx)
	int NumberOfNodes = NetList[NumberOfElements].Number_Of_Nodes;

	// Matriz:
	cout << "Ax = B:" << endl;
	for(i = 1; i <= NumberOfVariables; i++){
		cout << '|';
		if(i > NumberOfNodes)
			x = 'J';
		for(j = 1; j <= NumberOfVariables; j++){
			cout << setw(15) << A_Externo[i*NUMBER_MAX_OF_NODES + j] << " ";
		}
		cout << "| |"<< x << i << "|  = " << '|'<< setw(15) << B[i] << '|' << endl;
	}
	cout << endl;

	// Solucao:
	cout << "Solucao do sistema:" << endl;
	x = 'V';
	for(i = 1; i <= NumberOfVariables; i++){
		if(i > NumberOfNodes)
			x = 'J';

		cout << x << i << " = " << X[i] << endl;
	}

// End of function
}


// M�todo Gauss Jordan 
void GaussJordan(double *A_Externo, double *B, double *x, int NumberOfVariables){
		
int i,j,l, a;
// p e o pivo
double t, p;
double c = 0;
double AB[NUMBER_MAX_OF_NODES][NUMBER_MAX_OF_NODES + 1] = {0};	

// [1] Desmontando a pseudo-matriz
// Partindo do i = 1 e j = 1, eu zero a primeira linha e coluna e coloco um terra no V0
for(i = 1; i<= NumberOfVariables; i++){
	for(j = 1; j <= NumberOfVariables + 1; j++)
			AB[i][j] = A_Externo[i*NUMBER_MAX_OF_NODES + j];
	AB[i][NumberOfVariables + 1] = B[i];
	}



// [2] Forward
for(i = 1; i <= NumberOfVariables; i++) {
		t=0.0;
		a=i;
		for( l = i; l <= NumberOfVariables; l++) {
			if(fabs(AB[l][i])>fabs(t)){
				a=l;
				t=AB[l][i];
			}
		}

		if(i != a){
			// Troca de linhas
			for (l = 1; l <= NumberOfVariables + 1; l++) {
				p=AB[i][l];
				AB[i][l]=AB[a][l];
				AB[a][l]=p;
			}
		}

		// Verificando se o sistema e singular
		if(fabs(t) < 1e-9){
			cout << "Sistema singular" << endl;
			system("pause");
			exit(1);
		}
  
		// Colocando na forma triangular
		for(j = NumberOfVariables + 1; j > i; j--){  // Ponha j>0 em vez de j>i para melhor visualizacao 
			AB[i][j] /= t;
			p=AB[i][j];
			for(l = 1; l <= NumberOfVariables; l++){
				if(l != i)
				AB[l][j]-=AB[l][i]*p;
			}
		}
  }


// Passando solucao para o vetor X
for(i = 0; i <= NumberOfVariables; i++)
	x[i] = AB[i][NumberOfVariables+1];

}




