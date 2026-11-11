SET NOCOUNT ON;
GO

CREATE PROCEDURE dbo.usp_Report_MonthlyCardProduction
    @Year  INT,
    @Month INT
AS
BEGIN
    SET NOCOUNT ON;

    /* Validación de parámetros */
    IF @Year < 2000 OR @Year > 2100
    BEGIN
        RAISERROR('The year must be between 2000 and 2100.', 16, 1);
        RETURN;
    END;

    IF @Month < 1 OR @Month > 12
    BEGIN
        RAISERROR('The month must be between 1 and 12.', 16, 1);
        RETURN;
    END;

    DECLARE @StartDate DATE;
    DECLARE @EndDate   DATE;

    SET @StartDate = DATEFROMPARTS(@Year, @Month, 1);
    SET @EndDate = DATEADD(MONTH, 1, @StartDate);

    /*
       Se materializa el conjunto filtrado para reutilizarlo en los dos result sets.
       El filtro usa >= inicio y < inicio del mes siguiente para incluir todo el mes.
    */
    SELECT
        ProductionDate,
        ProductionSite,
        CardProduct,
        CardsProduced,
        CardsApproved,
        CardsRejected,
        BatchReference
    INTO #MonthlyProduction
    FROM dbo.CardProduction
    WHERE ProductionDate >= @StartDate
      AND ProductionDate <  @EndDate;

    /* Result set 1: resumen general del mes */
    SELECT
        @Year AS ReportYear,
        @Month AS ReportMonth,
        @StartDate AS PeriodStart,
        DATEADD(DAY, -1, @EndDate) AS PeriodEnd,
        COUNT(*) AS ProductionBatches,
        ISNULL(SUM(CardsProduced), 0) AS TotalCardsProduced,
        ISNULL(SUM(CardsApproved), 0) AS TotalCardsApproved,
        ISNULL(SUM(CardsRejected), 0) AS TotalCardsRejected,
        CAST(
            100.0 * ISNULL(SUM(CardsApproved), 0)
            / NULLIF(SUM(CardsProduced), 0)
            AS DECIMAL(5,2)
        ) AS ApprovalRatePct,
        CAST(
            100.0 * ISNULL(SUM(CardsRejected), 0)
            / NULLIF(SUM(CardsProduced), 0)
            AS DECIMAL(5,2)
        ) AS RejectionRatePct
    FROM #MonthlyProduction;

    /* Result set 2: desglose por planta y producto */
    SELECT
        ProductionSite,
        CardProduct,
        COUNT(*) AS ProductionBatches,
        SUM(CardsProduced) AS CardsProduced,
        SUM(CardsApproved) AS CardsApproved,
        SUM(CardsRejected) AS CardsRejected,
        CAST(
            100.0 * SUM(CardsApproved)
            / NULLIF(SUM(CardsProduced), 0)
            AS DECIMAL(5,2)
        ) AS ApprovalRatePct
    FROM #MonthlyProduction
    GROUP BY ProductionSite, CardProduct
    ORDER BY ProductionSite, CardProduct;

    DROP TABLE #MonthlyProduction;
END;
GO