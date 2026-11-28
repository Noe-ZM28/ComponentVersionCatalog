USE [CDSPLUSP]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- Procedimientos de demostracion que leen del catalogo CDPDatabase
IF OBJECT_ID('dbo.SP_GetDialoguesDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetDialoguesDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetDialoguesDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Dialogue';
END
GO

IF OBJECT_ID('dbo.SP_GetScriptsDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetScriptsDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetScriptsDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Script';
END
GO

IF OBJECT_ID('dbo.SP_GetVariablesDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetVariablesDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetVariablesDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Variable';
END
GO

IF OBJECT_ID('dbo.SP_GetRecurringJobsDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetRecurringJobsDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetRecurringJobsDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Recurring Job';
END
GO

IF OBJECT_ID('dbo.SP_GetChainsDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetChainsDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetChainsDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Chain';
END
GO

IF OBJECT_ID('dbo.SP_GetMappingsDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetMappingsDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetMappingsDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Mapping';
END
GO

IF OBJECT_ID('dbo.SP_GetFileDefinitionsDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetFileDefinitionsDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetFileDefinitionsDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'File Definition';
END
GO

IF OBJECT_ID('dbo.SP_GetXMLTemplatesDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetXMLTemplatesDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetXMLTemplatesDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'XML';
END
GO

IF OBJECT_ID('dbo.SP_GetSortingDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetSortingDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetSortingDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Sorting';
END
GO

IF OBJECT_ID('dbo.SP_GetSplitDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetSplitDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetSplitDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Split';
END
GO

IF OBJECT_ID('dbo.SP_GetDictionariesDummy', 'P') IS NULL
    EXEC ('CREATE PROCEDURE dbo.SP_GetDictionariesDummy AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[SP_GetDictionariesDummy]
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT c.ref_id, c.[name], c.[description], c.last_modified_at,
           c.type_component
    FROM [CDPDatabase].[dbo].[components] c
    INNER JOIN [CDPDatabase].[dbo].[projects] p ON c.project_id = p.id
    WHERE p.cust_num = CAST(@CustNum AS INT)
      AND c.type_component = 'Dictionary';
END
GO
