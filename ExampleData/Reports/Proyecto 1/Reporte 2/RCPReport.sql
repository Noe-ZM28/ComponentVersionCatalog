CREATE OR ALTER PROCEDURE dbo.usp_ReceiveRCP_Dummy
    @RecordType  CHAR(3),
    @FileId      CHAR(10),
    @RecordCount CHAR(7),
    @FileDate    CHAR(8),
    @FileName    CHAR(72)
AS
BEGIN
    SET NOCOUNT ON;

    -- Validaciones básicas del ejemplo
    IF LTRIM(RTRIM(@RecordType)) = ''
    BEGIN
        RAISERROR('RecordType es obligatorio.', 16, 1);
        RETURN;
    END;

    IF LTRIM(RTRIM(@FileId)) = ''
    BEGIN
        RAISERROR('FileId es obligatorio.', 16, 1);
        RETURN;
    END;

    IF LTRIM(RTRIM(@RecordCount)) = ''
    BEGIN
        RAISERROR('RecordCount es obligatorio.', 16, 1);
        RETURN;
    END;

    IF LEN(LTRIM(RTRIM(@FileDate))) <> 8
    BEGIN
        RAISERROR('FileDate debe tener formato YYYYMMDD (8 caracteres).', 16, 1);
        RETURN;
    END;

    -- Salida de ejemplo: los cinco campos recibidos.
    SELECT
        @RecordType  AS RecordType,
        @FileId      AS FileId,
        @RecordCount AS RecordCount,
        @FileDate    AS FileDate,
        @FileName    AS FileName;
END;
GO

-- Ejemplo de ejecución:
EXEC dbo.usp_ReceiveRCP_Dummy
    @RecordType  = 'RCP',
    @FileId      = 'FILE000001',
    @RecordCount = '0000001',
    @FileDate    = '20261019',
    @FileName    = 'CARD_PRODUCTION_20261019.RCP';
GO