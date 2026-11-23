----drop database [ComponentVersionCatalog]
----create database [ComponentVersionCatalog]

----drop database CDPDatabase
----create database CDPDatabase

--create database [CDSPLUSP]

--select * from [ComponentVersionCatalog].dbo.change_files
--select * from [ComponentVersionCatalog].dbo.[changes]
--select * from [ComponentVersionCatalog].dbo.files
--select * from [ComponentVersionCatalog].dbo.tickets
--select * from [ComponentVersionCatalog].dbo.projects
--select * from [ComponentVersionCatalog].dbo.components

--drop table [ComponentVersionCatalog].dbo.projects



--[CDSPLUS].dbo.GetListProyects

--[CDSPLUS].dbo.GetListComponentsByProyect


--create database CDPDatabase


--select * from CDPDatabase.dbo.change_files
--select * from CDPDatabase.dbo.[changes]
--select * from CDPDatabase.dbo.components
--select * from CDPDatabase.dbo.files
--select * from CDPDatabase.dbo.projects
--select * from CDPDatabase.dbo.tickets

--update CDPDatabase.dbo.projects set name = 'Banco jsjsj' where cust_num = 312


--use [CDSPLUS];
--go
--CREATE PROCEDURE .[dbo].GetListProjects
--AS
--BEGIN
--    SET NOCOUNT ON;

--    SELECT
--        cust_num, [name], [description]
--    FROM
--        CDPDatabase.dbo.projects

--END
--GO



--use [CDSPLUS];
--go
--ALTER PROCEDURE .[dbo].GetListComponentsByProyect
--@cust_num varchar(5)
--AS
--BEGIN
--    SET NOCOUNT ON;

--    SELECT
--        C.ref_id, C.[name], C.[description], C.last_modified_at, C.type_component
--    FROM
--        CDPDatabase.dbo.components AS C
--    INNER JOIN 
--        CDPDatabase.dbo.projects AS P ON C.project_id = P.id
--    WHERE P.cust_num = @cust_num
--END
--GO



--exec [CDSPLUS].[dbo].GetListComponentsByProyect 
--'616'


USE [CDSPLUSP]
GO

/** Object:  StoredProcedure [dbo].[SP_GetDialogues]    Script Date: 11/22/2026 1:33:39 PM **/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


create PROCEDURE [dbo].SP_GetRecurringJobs
    @CustNum NVARCHAR(3)
AS
BEGIN
    SET NOCOUNT ON;

RETRY:
    BEGIN TRANSACTION;

    BEGIN TRY

        SELECT
            '' AS ref_id,
            '' AS name,
            '' AS description,
            '2026-11-14 02:14:20.3756970' AS last_modified_at,
            'Recurring Job' AS type_component


        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;

        IF ERROR_NUMBER() = 1205
        BEGIN
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