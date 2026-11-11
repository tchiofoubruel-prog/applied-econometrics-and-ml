
/*********/
/* START */
/*********/


/*ETAPE 1 Créer bibliothèque moteur SAS:*/
/*
*nom bibliothèque : EXA2526
*dossier source : défini par la macro-variable &chemin (à adapter)
*/

%let chemin = ./data;
libname EXA2526 "&chemin";




/*ETAPE 2: Importation fichier BANK.TXT*/
/* 
*Importer le fichier : bank.txt (copié dans &chemin)
*Stocker la table SAS appellée Bank dans la bibliotheque exa2526
*/

proc import datafile="&chemin/bank.txt"
	out=exa2526.bank
	dbms=dlm
	replace;
	DELIMITER='09'x;      
	getnames=yes;
	guessingrows=max;
run;



/*ETAPE 3: Manipulation table Bank*/
/*
*Utiliser la procédure correcte pour supprimer les doublons de lignes (lignes en double).
*Stocker les doublons de lignes dans la table temporaire bank_doublons.
*Stocker la table dédupliquée dans la table temporaire bank. 
*/

proc sort data=exa2526.bank out=work.bank noduprecs dupout=work.bank_doublons;
	by _all_;
run;



/*
*Modifier la table temporaire BANK pour :

*Créer la variable caractère Phone_tot dans la façon suivante:
	concaténer (800) avec la valeur de Phone
	exemple : pour 	BankID 101010101
					Phone = 5550100
					Phone_tot = (800)5550100

*Créer la variable caractère E_mail
	concaténer la valeur de la variable Name (prendre uniquement la partie à gauche de la virgule, en supprimant les espaces)
	avec @
	avec la variable Domain
	exemple : pour 	BankID=101010101
					Name = Biggest Bank, Inc.
					Domain = bbfake.com
					e_mail = BiggestBankInc@bbfake.com

*Supprimer de la table en sortie les variables suivantes :
	Domain
	Phone

*/
data work.bank;
	set work.bank;
	length Phone_tot $20;
	Phone_tot = cats('(800)', Phone);

	
	length E_mail $200;
	_nom_gauche = scan(Name, 1, ',');
	_nom_gauche = compress(_nom_gauche, ' ');
	E_mail = cats(_nom_gauche, '@', Domain);

	/* Suppressions */
	drop Domain Phone _nom_gauche;
run;




/*ETAPE 4: Importation fichier supercustomer.TXT*/
/* 
*Importer le fichier : supercustomer.txt (copié dans &chemin)
*Stocker la table SAS appellée supercustomer dans la bibliotheque exa2526
*/

proc import datafile="&chemin/supercustomer.txt"
	out=exa2526.supercustomer
	dbms=dlm
	replace;
	delimiter='*';     
	getnames=yes;
	guessingrows=max;
run;


/*ETAPE 5: Manipulation table supercustomer*/
/*
*Créer la table temporaire supercustomer à partir de supercustomer dans la bibliothèque exa2526
*Modifier la table temporaire supercustomer pour :

*Conserver uniquement les observations sans valeurs manquantes dans TOUTES les variables suivantes :
	FirstName
	LastName
	AccountID
	ET dont la valeur de DOB est supérieure ou égale au 01/01/1900


*Certaines valeurs de BankID peuvent être manquantes, il faut les réaffecter :
	Utiliser l’instruction RETAIN pour réaffecter les valeurs manquantes en reprenant la valeur de BankID de la ligne précédente
	exemple pour :FirstName=Gary
				  LastName=Sienkiewicz
				  BankID=101010101
			e pour FirstName=Sergio
				   LastName=Lefeld
				   BankID=. mais avec votre programme on a BankID=101010101 (la valeur de la ligne precedente)
				  

*Créer la variable caractère AgeGroup à partir de l’année de la variable DOB selon les règles suivantes :
1900–1924 (inclus) → G.I. Generation
1925–1945 (inclus) → Silent Generation
1946–1964 (inclus) → Baby Boomers
1965–1979 (inclus) → Thirteeners or Generation X
1980–2000 (inclus) → Millennials or Generation Y
2001–2019 (inclus) → New Silent Generation or Generation Z
sinon → PROBLEME
	exemple pour :FirstName=Gary
				  LastName=Sienkiewicz
				  DOB=6371 (càd 11JUN1977)
				  AgeGroup=Thirteeners or Generation X

*Créer la variable caractère State en extrayant l’État depuis la variable Address (l’État se trouve toujours à la même position dans la chaîne)
	exemple pour :FirstName=Gary
				  LastName=Sienkiewicz	
				  address=1953 Rosewood Lane Los Angeles CA 90001
				  state=CA 
				  
*Supprimer la variable idbank et address de la table en sortie

*/

data work.supercustomer;
	set exa2526.supercustomer;

	/* garder obs sans manquants sur FirstName LastName AccountID
	   + DOB >= 01/01/1900 */
	if cmiss(FirstName, LastName, AccountID) = 0
	   and DOB >= '01JAN1900'd;


	/* RETAIN pour réaffecter BankID manquants depuis la ligne précédente */
	retain BankID_retenu;
	if not missing(BankID) then BankID_retenu = BankID;
	else BankID = BankID_retenu;

	/* AgeGroup à partir de l'année de DOB */
	length AgeGroup $40;
	annee = year(DOB);

	if 1900 <= annee <= 1924 then AgeGroup = 'G.I. Generation';
	else if 1925 <= annee <= 1945 then AgeGroup = 'Silent Generation';
	else if 1946 <= annee <= 1964 then AgeGroup = 'Baby Boomers';
	else if 1965 <= annee <= 1979 then AgeGroup = 'Thirteeners or Generation X';
	else if 1980 <= annee <= 2000 then AgeGroup = 'Millennials or Generation Y';
	else if 2001 <= annee <= 2019 then AgeGroup = 'New Silent Generation or Generation Z';
	else AgeGroup = 'PROBLEME';

	/* State extrait depuis Address :
	   ex "... Los Angeles CA 90001" -> state = CA
	   => on prend l'avant-dernier mot */
	length State $2;
	State = scan(Address, -2, ' ');

	/* supprimer idbank et address en sortie */
	drop idbank Address BankID_retenu annee;
run;


/*ETAPE 6: Boucle conditionelle */
/*
*Sachant que chaque banque applique un intérêt annuel de 3 % et que la variable Income correspond au montant 2026 de chaque client
*Créer la table temporaire SuperCustomer_50000, composée d’une ligne par AccountID
	Programmer une boucle pour calculer la nouvelle variable annee_50000, qui représente l’année où le client dépassera 50 000 sur son compte courant
	Déterminer au bout de combien d’années chaque client dépassera 50 000
*Attention : si un client a déjà un montant >= à 50 000 en 2026, annee_50000 prendra la valeur 2026
*Conserver uniquement les variables suivantes :
	accountid firstname lastname income annee_50000 income_50000
*/

proc sort data=work.supercustomer out=work.supercustomer_u nodupkey;
	by AccountID;
run;

data work.supercustomer_50000;
	set work.supercustomer_u;
	length annee_50000 8 income_50000 8;

	annee_50000 = 2026;
	income_50000 = Income;

	/* si déjà >= 50000 en 2026 */
	if income_50000 >= 50000 then do;
		/* rien */
	end;
	else do;
		/* boucle annuelle à 3% */
		do while (income_50000 < 50000);
			annee_50000 + 1;
			income_50000 = income_50000 * 1.03;
		end;
	end;

	keep accountid firstname lastname income annee_50000 income_50000;
run;

 /*
*Exporter la table temporaire SuperCustomer_50000 dans le fichier SuperCustomer_50000.csv 
*/

proc export data=work.supercustomer_50000
	outfile="&chemin/SuperCustomer_50000.csv"
	dbms=csv
	replace;
	putnames=yes;
run;


/*ETAPE 7: Importation des fichiers TransactionFull_1.csv et TransactionFull_1.csv*/
/* 
*Importer les fichier : TransactionFull_1.csv et TransactionFull_2.csv (copié dans &chemin)
*Stocker les table SAS appellées TransactionFull_1 et TransactionFull_2 dans la bibliotheque exa2526
*/

proc import datafile="&chemin/TransactionFull_1.csv"
	out=exa2526.TransactionFull_1
	dbms=csv
	replace;
	getnames=yes;
	guessingrows=max;
run;

proc import datafile="&chemin/TransactionFull_2.csv"
	out=exa2526.TransactionFull_2
	dbms=csv
	replace;
	getnames=yes;
	guessingrows=max;
run;


/*ETAPE 8: Manipulation des tables TransactionFull_1 et TransactionFull_2*/
/*
*Créer la table temporaire TransactionFull_1 à partir de la concatenation des tables  
	TransactionFull_1 et TransactionFull_2 de la bibliothèque exa2526

*Modifier la table temporaire TransactionFull pour :
*Créer la variable numerique Date en extraiant la date de la variable Datetime
	exemple pour :TransactionID=635f1819-2152-4f61-acaf-38136108a88c
				  datetime=16FEB2018:09:43:17
				  date=21231(16FEB2018)

*Conserver uniquement les variables communes aux deux tables
*Supprimer la variable datetime de la table de sortie				  
*/

data work.transactionfull_all;
	set exa2526.TransactionFull_1
	    exa2526.TransactionFull_2;
	    
Date = datepart(DateTime);
	format Date date9.;	    

	drop DateTime;
run;


/*
*Utiliser la procédure correcte pour supprimer les doublons de lignes (lignes en double).
	*Stocker les doublons de lignes dans la table temporaire transaction_doublons.
	*Stocker la table dédupliquée dans la table temporaire transactionfull. 
 
*/


proc sort data=work.transactionfull_all
	out=work.transactionfull
	noduprecs
	dupout=work.transactionfull_doublons;
	by _all_;
run;

/*ETAPE 9: Tableaux cumulatif des transactions par jour*/
/*
*Créer une table temporaire transaction_amount_day permettant d’obtenir un récapitulatif :
	Day_transaction -> nombre de transactions par jour
	Day_Amount -> somme des Amount par jour
*Chaque observation de la table correspond à un jour différent
*Affecter le format date9. à la variable date et dollar20.3 à day_amount
*Conserver uniquement les variables suivantes : Date Day_transaction Day_Amount
*/

proc means data=work.transactionfull nway n sum;
	class Date;
	var Amount;
	output out=work.transaction_amount_day(drop=_type_ _freq_)
		n=Day_transaction
		sum=Day_Amount;
run;

data work.transaction_amount_day;
	set work.transaction_amount_day;
	format Date date9. Day_Amount dollar20.3;
	keep Date Day_transaction Day_Amount;
run;


/*
*Exporter la table temporaire Transaction_Amount_Day dans le fichier Transaction_Amount_Day.dat
delimiteur ;  
*/

proc export data=work.transaction_amount_day
	outfile="&chemin/Transaction_Amount_Day.dat"
	dbms=dlm
	replace;
	delimiter=';';
	putnames=yes;
run;


/*ETAPE 10: Joindre les tables*/
/*
*Effectuer les contrôles sur les doublons de lignes (lignes totalement en double) et suivre les étapes nécessaires pour joindre les tables :
	SuperCustomer et Bank via la variable BankID
	la table temporaire SuperCustomer_B contiendra les observations issues de la jointure interne
  */

proc sort data=work.supercustomer
	out=work.supercustomer
	noduprecs
	dupout=work.supercustomer_doublons;
	by _all_;
run;

/*
*Effectuer les contrôles sur les doublons de lignes (lignes totalement en double) et suivre les étapes nécessaires pour joindre les tables :
	Transactionfull et SuperCustomer_B via la variable AccountID
	
	la table Transactionfull_Customer_B sera composée des observations issues de la jointure interne
	la table Transactionfull_Customer_B n’inclura pas les variables : Type, Service, City, Zip

	la table TransactionFull_Autres_B sera composée des observations dans Transactionfull mais pas dans SuperCustomer_B
	la table TransactionFull_Autres_B contiendra uniquement les variables suivantes : TransactionID, BankID, AccountID, Amount, Date, Creditscore

 NOTE: There were 48 observations read from the data set WORK.TRANSACTIONFULL.
 NOTE: There were 7 observations read from the data set WORK.SUPERCUSTOMER_B.
 NOTE: The data set WORK.TRANSACTIONFULL_CUSTOMER_B has 10 observations and 20 variables.
 NOTE: The data set WORK.TRANSACTIONFULL_AUTRES_B has 38 observations and 6 variables.
*/



proc sort data=work.bank
	out=work.bank
	noduprecs
	dupout=work.bank_doublons;
	by _all_;
run;


proc sort data=work.supercustomer; by BankID; run;
proc sort data=work.bank;         by BankID; run;

data work.supercustomer_b;
	merge work.supercustomer(in=a) work.bank(in=b);
	by BankID;
	if a and b; /* jointure interne */
run;

proc sort data=work.transactionfull;  by AccountID; run;
proc sort data=work.supercustomer_b;  by AccountID; run;

data work.transactionfull_customer_b
     work.transactionfull_autres_b;

	merge work.transactionfull(in=t)
	      work.supercustomer_b(in=c);
	by AccountID;

	/* Jointure interne */
	if t and c then do;
		
		output work.transactionfull_customer_b;
	end;

	if t and not c then do;
		
		keep TransactionID BankID AccountID Amount Date MerchantID Creditscore;
		output work.transactionfull_autres_b;
	end;

run;



/*
*Exporter la table temporaire TransactionFull_Autres_B dans le fichier TransactionFull_Autres_B.txt delimiteur *
*/

proc export data=work.transactionfull_autres_b
	outfile="&chemin/TransactionFull_Autres_B.txt"
	dbms=dlm
	replace;
	delimiter='*';
	putnames=yes;
run;


/*ETAPE 11: Creation formats utilisateurs*/
/*
*Créer le format utilisateur $married_f avec les règles suivantes :
	D->Divorced
	M->Married
	S->Single
	W->Widowed
pour tous les autres cas, y compris les valeurs manquantes -> ERROR
*/
proc format;
	value $married_f
		'D' = 'Divorced'
		'M' = 'Married'
		'S' = 'Single'
		'W' = 'Widowed'
		other = 'ERROR';
run;

/*
*Créer le format utilisateur pour discrétiser la variable creditscore
*NE PAS compliquer le programme, suivre les étapes comme indiqué :
	Appliquer la procédure appropriée pour effectuer l’analyse descriptive de la variable creditscore 
	de la table temporaire SuperCustomer_B et récupérer :
		(le minimum)
		(le maximum)
		le 1er quartile (Q1)
		le 3e quartile (Q3)
		la médiane
	Coder le format utilisateur creditscore_c avec les règles suivantes :
		petit (mais non missing) jusqu’à Q1 -> classe 1
		de Q1 à la médiane -> classe 2
		de la médiane à Q3 -> classe 3
		de Q3 au plus grand -> classe 4
*/

proc univariate data=work.supercustomer_b;
	var Creditscore;
run;

%let CS_MIN = 570 ;   
%let CS_Q1  = 590 ;   
%let CS_MED = 633.5 ;  
%let CS_Q3  = 670 ;   
%let CS_MAX = 750 ;   

proc format;
	value creditscore_c
		. = 'ERROR'
		&CS_MIN -< &CS_Q1 = 'classe 1'
		&CS_Q1  -< &CS_MED = 'classe 2'
		&CS_MED -< &CS_Q3 = 'classe 3'
		&CS_Q3  - &CS_MAX = 'classe 4';
run;

data work.transactionfull_customer_b;
	set work.transactionfull_customer_b;

	format Creditscore creditscore_c.;
run;

/* 
*Importer le fichier : StateCode.csv (copié dans &chemin)
*Stocker la table SAS appellée StateCode dans la bibliotheque exa2526
*/

proc import 
	datafile="&chemin/StateCode.csv"
	out=exa2526.StateCode
	dbms=csv
	replace;
	getnames=yes;
	guessingrows=max;
run;

/*
*Créer le format utilisateur à partir de la table de référence StateCode de la bibliotheque exa2526
*NE PAS compliquer le programme, suivre les étapes comme indiqué :
	Créer la table temporaire statecode_t à partir de la table StateCode de la bibliothèque exa2526
	Créer les variables caractère :
		fmtname : prendra la valeur $StateCode_F
		start : prendra la valeur de la variable StateCode
		label : prendra la valeur de la variable StateName
	Créer le format utilisateur à partir de la table statecode_t que vous venez de créer
*/


data work.statecode_t;
	set exa2526.StateCode;

	/* Création des variables nécessaires au format */
	length fmtname $20 start $2 label $50;

	fmtname = '$StateCode_F';   /* nom du format */
	start   = StateCode;        /* valeur de départ */
	label   = StateName;        /* étiquette associée */

	keep fmtname start label;
run;

proc format cntlin=work.statecode_t;
run;

/*
*Associer vos formats aux variables de la table temporaire Transactionfull_Customer_B :
	State -> format $StateCode_F
	Creditscore -> format creditscore_c
	Married -> format $maried_f
	Date et DOB -> format DATE9
*/

data work.transactionfull_customer_b;
	set work.transactionfull_customer_b;

	format 
		State       $StateCode_F.
		Creditscore creditscore_c.
		Married     $married_f.
		Date        date9.
		DOB         date9.;
run; 

/*
*Exporter la table temporaire Transactionfull_Customer_B dans le fichier Transactionfull_Customer_B.txt delimiteur tabulation
*/

proc export 
	data=work.transactionfull_customer_b
	outfile="&chemin/Transactionfull_Customer_B.txt"
	dbms=tab
	replace;
	putnames=yes;
run;

/*ETAPE 12: Export via macro variable*/
/*
*Tout au long du projet, vous avez effectué de nombreuses exportations
*pour terminer, remplacez les paramètres en dur dans votre code d’exportation par les macro‑variables suivantes :
	table_i -> table SAS en entrée
	table_e -> nom table exporte avec son chemin physique
	del -> délimiteur (dans l'option )
	spec -> delimiteur (dans l'instruction, si necessaire)
*/

/* Définition des macro-variables */


%let table_i = work.transactionfull_autres_b;
%let table_e = &chemin/TransactionFull_Autres_B_v2.txt;
%let del     = dlm;
%let spec1   = delimiter='*';
%let spec2   = putnames=yes;

proc export data=&table_i outfile="&table_e" dbms=&del replace;
  &spec1;
  &spec2;
run;




/********/
/* STOP */
/********/
