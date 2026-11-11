/* TOTAL DES VENTES PAR RÉGION POUR L'ANNÉE DE RÉFÉRENCE 
   Note : On utilise l'année 2014 car c'est la dernière année complète de la base. */
SELECT 
    T.Name AS Region, 
    ROUND(SUM(S.TotalDue), 2) AS TotalVentes
FROM Sales.SalesOrderHeader S
JOIN Sales.SalesTerritory T ON S.TerritoryID = T.TerritoryID
WHERE YEAR(S.OrderDate) = 2014
GROUP BY T.Name
ORDER BY TotalVentes DESC;


/* LISTE DES CLIENTS AYANT PASSÉ COMMANDE RÉCEMMENT (DERNIERS MOIS DE LA BASE)
   On joint Customer et Person pour obtenir le nom complet. */
SELECT DISTINCT 
    C.CustomerID, 
    P.FirstName, 
    P.LastName, 
    MAX(S.OrderDate) AS DerniereCommande
FROM Sales.Customer C
JOIN Person.Person P ON C.PersonID = p.BusinessEntityID
JOIN Sales.SalesOrderHeader S ON C.CustomerID = S.CustomerID
WHERE S.OrderDate >= '2014-01-01'
GROUP BY C.CustomerID, P.FirstName, P.LastName;


/* CHIFFRE D'AFFAIRES GÉNÉRÉ PAR CHAQUE COMMERCIAL
   Le SalesPersonID est lié au BusinessEntityID de la table Person. */
SELECT 
    P.FirstName + ' ' + P.LastName AS AgentVente,
    ROUND(SUM(S.TotalDue), 2) AS RevenuTotal
FROM Sales.SalesOrderHeader S
JOIN Sales.SalesPerson SP ON S.SalesPersonID = SP.BusinessEntityID
JOIN Person.Person P ON SP.BusinessEntityID = P.BusinessEntityID
GROUP BY P.FirstName, P.LastName
ORDER BY RevenuTotal DESC;


/* IDENTIFICATION DES 5 MEILLEURS PRODUITS EN TERMES DE REVENU 
   On utilise TOP 5 pour limiter le classement. */
SELECT TOP 5 
    PR.Name AS NomProduit, 
    ROUND(SUM(SD.LineTotal), 2) AS RevenuGenere
FROM Sales.SalesOrderDetail SD
JOIN Production.Product PR ON SD.ProductID = PR.ProductID
GROUP BY PR.Name
ORDER BY RevenuGenere DESC;

/* SEGMENTATION RFM SIMPLIFIÉE (BASÉ SUR LE MONTANT)
   Segmentation : Bas < 5 000 | Moyen 5 000 - 20 000 | Élevé > 20 000 */
SELECT 
    C.CustomerID,
    ROUND(SUM(S.TotalDue), 2) AS TotalDepense,
    CASE 
        WHEN SUM(S.TotalDue) > 20000 THEN 'Élevé'
        WHEN SUM(S.TotalDue) BETWEEN 5000 AND 20000 THEN 'Moyen'
        ELSE 'Bas'
    END AS SegmentClient
FROM Sales.Customer C
JOIN Sales.SalesOrderHeader S ON C.CustomerID = S.CustomerID
GROUP BY C.CustomerID
ORDER BY TotalDepense DESC;

/* ÉVOLUTION MENSUELLE DES VENTES ET CUMUL (KPI AVANCÉ)
   On utilise la fonction de fenêtre pour calculer la progression. */
/* ÉVOLUTION MENSUELLE DES VENTES ET CUMUL (CORRIGÉ) 
   On simplifie le ORDER BY dans la fonction OVER pour éviter l'erreur de taille de fenêtre. */
SELECT 
    P.Name AS Produit,
    YEAR(S.OrderDate) AS Annee,
    MONTH(S.OrderDate) AS Mois,
    ROUND(SUM(SD.LineTotal), 2) AS VentesMensuelles,
    ROUND(SUM(SUM(SD.LineTotal)) OVER (
        PARTITION BY P.Name 
        ORDER BY YEAR(S.OrderDate), MONTH(S.OrderDate)
    ), 2) AS CumulAnnuel
FROM Sales.SalesOrderDetail SD
JOIN Production.Product P ON SD.ProductID = P.ProductID
JOIN Sales.SalesOrderHeader S ON SD.SalesOrderID = S.SalesOrderID
WHERE S.OrderDate >= '2013-01-01'
GROUP BY P.Name, YEAR(S.OrderDate), MONTH(S.OrderDate)
ORDER BY P.Name, Annee, Mois;




/* CRÉATION D'UNE VUE POUR LES RAPPORTS DE PERFORMANCE NIVEAU 1
   Cette vue automatise les jointures complexes entre Ventes, Produits et Régions. */
CREATE VIEW dbo.vw_RapportPerformanceGlobale AS
SELECT 
    T.Name AS Region,
    PC.Name AS Categorie,
    P.Name AS Produit,
    S.OrderDate,
    SD.LineTotal AS MontantVente
FROM Sales.SalesOrderHeader S
JOIN Sales.SalesTerritory T ON S.TerritoryID = T.TerritoryID
JOIN Sales.SalesOrderDetail SD ON S.SalesOrderID = SD.SalesOrderID
JOIN Production.Product P ON SD.ProductID = P.ProductID
JOIN Production.ProductSubcategory PS ON P.ProductSubcategoryID = PS.ProductSubcategoryID
JOIN Production.ProductCategory PC ON PS.ProductCategoryID = PC.ProductCategoryID;
GO

-- Pour appeler le rapport maintenant, il suffit de faire :
-- SELECT * FROM dbo.vw_RapportPerformanceGlobale WHERE Region = 'France';


/* TEST DE LA VUE : ANALYSE RAPIDE */
SELECT TOP 100 * FROM dbo.vw_RapportPerformanceGlobale
WHERE Region = 'France'
ORDER BY MontantVente DESC;


/* ON APPELLE LA VUE QUE TU AS CRÉÉE */
SELECT * FROM dbo.vw_RapportPerformanceGlobale
ORDER BY OrderDate DESC;

/* IDENTIFIER LES 10 CLIENTS AYANT GÉNÉRÉ LE PLUS DE REVENUS */
SELECT TOP 10
    P.FirstName, P.LastName,
    ROUND(SUM(S.TotalDue), 2) AS RevenuTotal
FROM Sales.Customer C
JOIN Person.Person P ON C.PersonID = P.BusinessEntityID
JOIN Sales.SalesOrderHeader S ON C.CustomerID = S.CustomerID
GROUP BY P.FirstName, P.LastName
ORDER BY RevenuTotal DESC;

/* RÉPARTITION DES CLIENTS SELON LE CANAL D'ACHAT */
SELECT 
    CASE WHEN OnlineOrderFlag = 1 THEN 'Commande en ligne' ELSE 'Achat en magasin' END AS TypeCommande,
    COUNT(DISTINCT CustomerID) AS NombreClients
FROM Sales.SalesOrderHeader
GROUP BY OnlineOrderFlag;


/* TOP 10 DES PRODUITS LES PLUS ACHETÉS (VOLUME) SUR LES 12 DERNIERS MOIS */
SELECT TOP 10
    PR.Name AS NomProduit,
    SUM(SD.OrderQty) AS QuantiteTotale
FROM Sales.SalesOrderDetail SD
JOIN Production.Product PR ON SD.ProductID = PR.ProductID
JOIN Sales.SalesOrderHeader S ON SD.SalesOrderID = S.SalesOrderID
WHERE S.OrderDate >= '2013-07-01'
GROUP BY PR.Name
ORDER BY QuantiteTotale DESC;/* TOP 10 DES PRODUITS LES PLUS ACHETÉS (VOLUME) SUR LES 12 DERNIERS MOIS */
SELECT TOP 10
    PR.Name AS NomProduit,
    SUM(SD.OrderQty) AS QuantiteTotale
FROM Sales.SalesOrderDetail SD
JOIN Production.Product PR ON SD.ProductID = PR.ProductID
JOIN Sales.SalesOrderHeader S ON SD.SalesOrderID = S.SalesOrderID
WHERE S.OrderDate >= '2013-07-01'
GROUP BY PR.Name
ORDER BY QuantiteTotale DESC;

/* DÉTAIL DES VENTES PAR PRODUIT AU SEIN DE CHAQUE RÉGION */
SELECT 
    T.Name AS Region,
    PR.Name AS Produit,
    ROUND(SUM(SD.LineTotal), 2) AS VentesTotales
FROM Sales.SalesOrderHeader S
JOIN Sales.SalesTerritory T ON S.TerritoryID = T.TerritoryID
JOIN Sales.SalesOrderDetail SD ON S.SalesOrderID = SD.SalesOrderID
JOIN Production.Product PR ON SD.ProductID = PR.ProductID
GROUP BY T.Name, PR.Name
ORDER BY T.Name, VentesTotales DESC;

/* TAUX DE DÉFAUT/RETOUR DES PRODUITS */
SELECT 
    P.Name AS NomProduit,
    SUM(WO.OrderQty) AS TotalProduit,
    SUM(WO.ScrappedQty) AS TotalRejete,
    ROUND(CAST(SUM(WO.ScrappedQty) AS FLOAT) / NULLIF(SUM(WO.OrderQty), 0) * 100, 2) AS TauxRetour_Pourcent
FROM Production.WorkOrder WO
JOIN Production.Product P ON WO.ProductID = P.ProductID
GROUP BY P.Name
HAVING SUM(WO.ScrappedQty) > 0;



/* EXERCICE 3 : VENTES TOTALES PAR CATÉGORIE DE PRODUIT */
SELECT 
    pc.Name AS Categorie,
    ROUND(SUM(sod.LineTotal), 2) AS VentesTotales
FROM Sales.SalesOrderDetail AS sod
JOIN Production.Product AS p ON sod.ProductID = p.ProductID
JOIN Production.ProductSubcategory AS ps ON p.ProductSubcategoryID = ps.ProductSubcategoryID
JOIN Production.ProductCategory AS pc ON ps.ProductCategoryID = pc.ProductCategoryID
GROUP BY pc.Name
ORDER BY VentesTotales DESC;

/* EXERCICE 15 : RENTABILITÉ PAR PRODUIT (MARGE BRUTE) 
   On compare le prix de vente moyen au coût de fabrication. */
SELECT TOP 20
    p.Name AS NomProduit,
    p.StandardCost AS CoûtProduction,
    ROUND(AVG(sod.UnitPrice), 2) AS PrixVenteMoyen,
    ROUND(AVG(sod.UnitPrice) - p.StandardCost, 2) AS MargeUnitaire
FROM Production.Product p
JOIN Sales.SalesOrderDetail sod ON p.ProductID = sod.ProductID
GROUP BY p.Name, p.StandardCost
ORDER BY MargeUnitaire DESC;