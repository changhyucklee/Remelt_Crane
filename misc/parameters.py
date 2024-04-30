username = 'mesapp'
password = 'Me$app123'
conn_string = 'DSN=AsiaMES_PROD;' + ';UID=' + username + ';PWD=' + password

da_username = 'token'
da_password = 'dapi1f5990903533367408bd33808a3fbf78'
da_conn_string = 'DSN=DAA_DEV;' + ';UID=' + da_username + ';PWD=' + da_password

# Azure_server = 'daafilelog.database.windows.net'
Azure_server = 'AUEGLBWVDAPDP09'
Azure_username = 'agw_de_admin'
Azure_password = 'N0vel1$1'
Azure_database = 'YJ_DIGITAL_USECASE'
Azure_conn_string = 'DSN=Azure_YJ_AGW;' + 'SERVER=' + Azure_server + ';PORT=1433;DATABASE=' + Azure_database + ';UID=' + Azure_username + ';PWD=' + Azure_password


sql_REMELT_CRANE="""
DECLARE @SHOPID  nvarchar(50) = 'YJ1'
DECLARE @LANGID  nvarchar(50) = 'KO-KR'
DECLARE @FROMDATE  nvarchar(50) = CONVERT(CHAR(8),GETDATE(),112)
DECLARE @TODATE  nvarchar(50) = CONVERT(CHAR(8),GETDATE()+3,112)
DECLARE @WKPLANSTAT  nvarchar(50) = 'PC'
DECLARE @CASTEQPTID  nvarchar(50) = '{}'

SELECT 
       A.RTPLANID       
       ,MAX(W1.BATCHNO)                                  AS  BATCHNO
       ,MAX(W2.BATCHNO)                                  AS  SUB_BATCHNO  
       ,MAX(A.CASTEQPTID)                                AS  CASTEQPTID 
       ,MAX(F.EQPTSHORTNM)                               AS  CASTEQPTNM 
       ,MAX(D.MAKEALLOY)                                 AS  ALLOY
       ,MAX(D.MAKEGAUGE)                                 AS  GAUGE
       ,MAX(D.MAKEWIDTH)                                 AS  WIDTH       
       ,MAX(D.MAKELEN)                                   AS  LENGTH
       ,MIN(A.PLANDTTM)                                  AS  PLANDTTM
       ,MAX(DC.WIPDTTM_ST) AS CASTING_START_TIME
       ,MAX(DC.WIPDTTM_ED) AS CASTING_END_TIME
FROM RTWORKPLAN A   WITH (NOLOCK)
LEFT OUTER JOIN (
                     SELECT SHOPID
                           ,RTPLANID
                           ,MAX(CASE WHEN MAINSUB = 'M' THEN LOTID END)      LOTID
                           ,MAX(CASE WHEN MAINSUB = 'S' THEN LOTID END)      SUB_LOTID
                           ,MAX(CASE WHEN ABSSEQ = 1 THEN 'Y' END)                          ABSSEND 
                           ,MAX(CASE WHEN MAINSUB = 'M' THEN MFEQPTID END)                  MFEQPTID
                       FROM RTWorkPlanLotMapp   WITH (NOLOCK)
                      WHERE SHOPID = 'YJ1'
                     GROUP BY SHOPID, RTPLANID
                   )  E ON (A.SHOPID = E.SHOPID AND A.RTPLANID =  E.RTPLANID)
LEFT OUTER JOIN EQUIPMENT F   WITH (NOLOCK) ON (A.CASTEQPTID = F.EQPTID)
   LEFT OUTER JOIN WIP W1   WITH (NOLOCK) ON E.LOTID = W1.LOTID 
   LEFT OUTER JOIN MATERIALCLASS    D   WITH (NOLOCK)  ON (W1.PRODID = D.MTRLID) 
   LEFT OUTER JOIN WIP W2   WITH (NOLOCK)  ON E.SUB_LOTID = W2.LOTID 
   LEFT OUTER JOIN EQUIPMENT M   WITH (NOLOCK) ON E.MFEQPTID = M.EQPTID
   LEFT OUTER JOIN LOT L   WITH (NOLOCK)  ON W1.LOTID = L.LOTID
   LEFT OUTER JOIN LOT L1   WITH (NOLOCK)  ON L1.RTLOTID_M = L.LOTID
   LEFT OUTER JOIN WIPHISTORY WH   WITH (NOLOCK)  ON L1.LOTID = WH.LOTID AND WH.PROCID IN ('RTCS', 'RCCS')
   LEFT OUTER JOIN WIPHISTORY DC   WITH (NOLOCK) ON substring(DC.BATCHNO,1,6) = W1.BATCHNO AND DC.PROCID = 'RTCS'
WHERE 1=1      
  AND A.PLANDTTM >= CONVERT(DATETIME, CONVERT(VARCHAR, @FROMDATE, 112), 112)
  AND A.PLANDTTM < CONVERT(DATETIME, CONVERT(VARCHAR, @TODATE, 112), 112) + 1
   AND       A.WKPLANSTAT =@WKPLANSTAT
   AND       A.RTPLANID IS NOT NULL
   AND       A.SHOPID     = @SHOPID
   AND      A.CASTEQPTID = @CASTEQPTID
GROUP BY A.SHOPID, A.RTPLANID
ORDER BY SUBSTRING(A.RTPLANID, 5, LEN(A.RTPLANID) - 3)
"""
