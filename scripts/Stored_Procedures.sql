USE [CDSPLUSP]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- SP_GetDialogues
IF OBJECT_ID('dbo.SP_GetDialogues', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetDialogues AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetDialogues]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            d.PUB AS name,
            ISNULL(d.NOTE, '') AS description,
            ISNULL(d.UPDATED,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Dialogue' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[DIALOGUE_TEMPLATE] d
            ON r.ObjectID = d.ID AND r.CustomerNo = d.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 11;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetScripts
IF OBJECT_ID('dbo.SP_GetScripts', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetScripts AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetScripts]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            s.Name AS name,
            ISNULL(s.Description, '') AS description,
            ISNULL(s.Updated,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Script' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FScript] s
            ON r.ObjectID = s.ID AND r.CustomerNo = s.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 14;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetVariables
IF OBJECT_ID('dbo.SP_GetVariables', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetVariables AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetVariables]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            v.VarName AS name,
            ISNULL(v.Description, '') AS description,
            ISNULL(v.EditTimeStamp,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Variable' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FVariables] v
            ON r.ObjectID = v.VarID AND r.CustomerNo = v.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 13;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetRecurringJobs
IF OBJECT_ID('dbo.SP_GetRecurringJobs', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetRecurringJobs AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetRecurringJobs]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            j.RJOB_DESCRIPTION AS name,
            j.RJOB_DESCRIPTION AS description,
            ISNULL(j.RJOB_ROW_TIME,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Recurring Job' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[RECCURING_JOBS_DEF] j
            ON r.ObjectID = j.RJOB_ID AND r.CustomerNo = j.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 7;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetChains
IF OBJECT_ID('dbo.SP_GetChains', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetChains AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetChains]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            c.Description AS name,
            c.Description AS description,
            ISNULL(c.EditTimeStamp,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Chain' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[ChainLookup] c
            ON r.ObjectID = c.ChainID AND r.CustomerNo = c.CustomerNo
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 1;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetMappings
IF OBJECT_ID('dbo.SP_GetMappings', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetMappings AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetMappings]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            m.description AS name,
            m.description AS description,
            ISNULL(m.EditTimeStamp,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Mapping' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FMap_Table] m
            ON r.ObjectID = m.ID AND r.CustomerNo = m.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 2;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetFileDefinitions
IF OBJECT_ID('dbo.SP_GetFileDefinitions', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetFileDefinitions AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetFileDefinitions]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            f.Description AS name,
            ISNULL(f.Note, '') AS description,
            ISNULL(f.Updated,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'File Definition' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FFile] f
            ON r.ObjectID = f.ID AND r.CustomerNo = f.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 3;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetXMLTemplates
IF OBJECT_ID('dbo.SP_GetXMLTemplates', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetXMLTemplates AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetXMLTemplates]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            x.MISC AS name,
            x.MISC AS description,
            ISNULL(x.ROW_TIME,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'XML' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[MC_XMLTEMPLATES] x
            ON r.ObjectID = x.ID AND r.CustomerNo = x.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 6;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetSorting
IF OBJECT_ID('dbo.SP_GetSorting', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetSorting AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetSorting]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            s.description AS name,
            ISNULL(s.note, '') AS description,
            ISNULL(s.updated,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Sorting' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FHsort] s
            ON r.ObjectID = s.ID
        INNER JOIN [CDSPLUSP].[dbo].[FFile] f
            ON s.fid = f.ID
            AND r.CustomerNo = f.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 8;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetSplit
IF OBJECT_ID('dbo.SP_GetSplit', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetSplit AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetSplit]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            r.RefID AS ref_id,
            p.description AS name,
            ISNULL(p.note, '') AS description,
            ISNULL(p.[date],
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Split' AS type_component
        FROM [CDSPLUSP].[dbo].[FObjectRefID] r
        INNER JOIN [CDSPLUSP].[dbo].[FHsplit] p
            ON r.ObjectID = p.ID
        INNER JOIN [CDSPLUSP].[dbo].[FFile] f
            ON p.fid = f.ID
            AND r.CustomerNo = f.CUST_NUM
        WHERE r.CustomerNo = CAST(@CustNum AS INT)
          AND r.ObjectTypeID = 9;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO

-- SP_GetDictionaries
IF OBJECT_ID('dbo.SP_GetDictionaries', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetDictionaries AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetDictionaries]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Retries INT;
    SET @Retries = 0;

    IF @CustNum IS NULL OR LTRIM(RTRIM(@CustNum)) = ''
        OR @CustNum LIKE '%[^0-9]%'
    BEGIN
        RAISERROR('Invalid customer number.', 16, 1);
        RETURN;
    END;

RETRY:
    BEGIN TRANSACTION;
    BEGIN TRY
        SELECT
            'DICT' + CAST(d.CUST_NUM AS VARCHAR(3)) + '_'
                   + CAST(d.DICT_ID AS VARCHAR(20)) AS ref_id,
            d.DICT_KEY AS name,
            d.DICT_DESCR AS description,
            ISNULL(d.ROW_TIME,
                CONVERT(DATETIME, '2014-03-04 20:27:55.493', 121)
            ) AS last_modified_at,
            'Dictionary' AS type_component
        FROM [CDSPLUSP].[dbo].[BOM_CUST_DICTIONARY] d
        WHERE d.CUST_NUM = CAST(@CustNum AS INT);

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        IF ERROR_NUMBER() = 1205 AND @Retries < 3
        BEGIN
            SET @Retries = @Retries + 1;
            WAITFOR DELAY '00:00:00.05';
            GOTO RETRY;
        END
        ELSE
        BEGIN
            THROW;
        END
    END CATCH
END
GO
