DROP TABLE IF EXISTS t_DiodesRectifiersDiscrete;

create table t_DiodesRectifiersDiscrete
(
    `componentlink1url`            VARCHAR(250) DEFAULT NULL,
    `componentlink2description`    VARCHAR(100) DEFAULT NULL,
    `componentlink2url`            VARCHAR(250) DEFAULT NULL,
    `componentlink3description`    VARCHAR(100) DEFAULT NULL,
    `componentlink3url`            VARCHAR(250) DEFAULT NULL,
    `componentlink4description`    VARCHAR(100) DEFAULT NULL,
    `componentlink4url`            VARCHAR(250) DEFAULT NULL,
    `componentlink5description`    VARCHAR(100) DEFAULT NULL,
    `componentlink5url`            VARCHAR(250) DEFAULT NULL,
    `componentlink6description`    VARCHAR(100) DEFAULT NULL,
    `componentlink6url`            VARCHAR(250) DEFAULT NULL,
    `footprintpath2`               VARCHAR(100) DEFAULT NULL,
    `componentlink1description`    VARCHAR(100) DEFAULT NULL,
    `footprintref2`                VARCHAR(100) DEFAULT NULL,
    `footprintref3`                VARCHAR(100) DEFAULT NULL,
    `PartStatus`                   VARCHAR(127) DEFAULT NULL,
    `DiodeType`                    VARCHAR(127) DEFAULT NULL,
    `VoltageDCReverseVrMax`        VARCHAR(127) DEFAULT NULL,
    `CurrentAverageRectifiedIo`    VARCHAR(127) DEFAULT NULL,
    `VoltageForwardVfMaxIf`        VARCHAR(127) DEFAULT NULL,
    `Speed`                        VARCHAR(127) DEFAULT NULL,
    `ReverseRecoveryTimetrr`       VARCHAR(127) DEFAULT NULL,
    `CurrentReverseLeakageVr`      VARCHAR(127) DEFAULT NULL,
    `CapacitanceVrF`               VARCHAR(127) DEFAULT NULL,
    `MountingType`                 VARCHAR(127) DEFAULT NULL,
    `PackageCase`                  VARCHAR(127) DEFAULT NULL,
    `footprintpath3`               VARCHAR(100) DEFAULT NULL,
    `SupplierDevicePackage`        VARCHAR(127) DEFAULT NULL,
    `supplier6partno`              VARCHAR(150) DEFAULT NULL,
    `supplier5partno`              VARCHAR(150) DEFAULT NULL,
    `lastupdated`                  DATETIME ON UPDATE CURRENT_TIMESTAMP,
    `archived`                     BIT          DEFAULT 0,
    `value`                        VARCHAR(100) DEFAULT NULL,
    `comment`                      VARCHAR(100) DEFAULT NULL,
    `manufacturerpartno`           VARCHAR(100) NOT NULL,
    `manufacturer`                 VARCHAR(100) NOT NULL,
    `description`                  VARCHAR(200) DEFAULT NULL,
    `price`                        VARCHAR(100) DEFAULT NULL,
    `lifecycle`                    VARCHAR(100) DEFAULT NULL,
    `series`                       VARCHAR(100) DEFAULT NULL,
    `footprintref`                 VARCHAR(100) DEFAULT NULL,
    `footprintpath`                VARCHAR(100) DEFAULT NULL,
    `supplier6`                    VARCHAR(100) DEFAULT NULL,
    `symbolref`                    VARCHAR(100) DEFAULT NULL,
    `devicepackage`                VARCHAR(100) DEFAULT NULL,
    `type`                         VARCHAR(100) DEFAULT NULL,
    `packaging`                    VARCHAR(100) DEFAULT NULL,
    `minimumorder`                 INT          DEFAULT 0,
    `supplier1`                    VARCHAR(100) DEFAULT NULL,
    `supplier1partno`              VARCHAR(150) DEFAULT NULL,
    `supplier2`                    VARCHAR(100) DEFAULT NULL,
    `supplier2partno`              VARCHAR(150) DEFAULT NULL,
    `supplier3`                    VARCHAR(100) DEFAULT NULL,
    `supplier3partno`              VARCHAR(150) DEFAULT NULL,
    `supplier4`                    VARCHAR(100) DEFAULT NULL,
    `supplier4partno`              VARCHAR(150) DEFAULT NULL,
    `supplier5`                    VARCHAR(100) DEFAULT NULL,
    `symbolpath`                   VARCHAR(100) DEFAULT NULL,
    `OperatingTemperatureJunction` VARCHAR(127) DEFAULT NULL,
    INDEX (`lastupdated`),
    INDEX (`archived`),
    INDEX (`manufacturerpartno`),
    PRIMARY KEY (`manufacturerpartno`, `manufacturer`)
);

DROP VIEW IF EXISTS Diodes_Rectifiers_Discrete;

CREATE VIEW Diodes_Rectifiers_Discrete AS
SELECT `CapacitanceVrF`               AS `Capacitance @ Vr, F`,
       `comment`                      AS `Comment`,
       `componentlink1description`    AS `ComponentLink1Description`,
       `componentlink1url`            AS `ComponentLink1URL`,
       `componentlink2description`    AS `ComponentLink2Description`,
       `componentlink2url`            AS `ComponentLink2URL`,
       `componentlink3description`    AS `ComponentLink3Description`,
       `componentlink3url`            AS `ComponentLink3URL`,
       `componentlink4description`    AS `ComponentLink4Description`,
       `componentlink4url`            AS `ComponentLink4URL`,
       `componentlink5description`    AS `ComponentLink5Description`,
       `componentlink5url`            AS `ComponentLink5URL`,
       `componentlink6description`    AS `ComponentLink6Description`,
       `componentlink6url`            AS `ComponentLink6URL`,
       `CurrentAverageRectifiedIo`    AS `Current - Average Rectified (Io)`,
       `CurrentReverseLeakageVr`      AS `Current - Reverse Leakage @ Vr`,
       `description`                  AS `Description`,
       `devicepackage`                AS `Device Package`,
       `DiodeType`                    AS `Diode Type`,
       `footprintpath`                AS `Footprint Path`,
       `footprintpath2`               AS `Footprint Path 2`,
       `footprintpath3`               AS `Footprint Path 3`,
       `footprintref`                 AS `Footprint Ref`,
       `footprintref2`                AS `Footprint Ref 2`,
       `footprintref3`                AS `Footprint Ref 3`,
       `lastupdated`                  AS `LastUpdated`,
       `lifecycle`                    AS `Lifecycle Status`,
       `manufacturer`                 AS `Manufacturer`,
       `manufacturerpartno`           AS `Part Number`,
       `minimumorder`                 AS `Minimum Order`,
       `MountingType`                 AS `Mounting Type`,
       `OperatingTemperatureJunction` AS `Operating Temperature - Junction`,
       `PackageCase`                  AS `Package / Case`,
       `packaging`                    AS `Packaging`,
       `PartStatus`                   AS `Part Status`,
       `price`                        AS `Price`,
       `ReverseRecoveryTimetrr`       AS `Reverse Recovery Time (trr)`,
       `series`                       AS `Series`,
       `Speed`                        AS `Speed`,
       `supplier1`                    AS `Supplier 1`,
       `supplier1partno`              AS `Supplier Part Number 1`,
       `supplier2`                    AS `Supplier 2`,
       `supplier2partno`              AS `Supplier Part Number 2`,
       `supplier3`                    AS `Supplier 3`,
       `supplier3partno`              AS `Supplier Part Number 3`,
       `supplier4`                    AS `Supplier 4`,
       `supplier4partno`              AS `Supplier Part Number 4`,
       `supplier5`                    AS `Supplier 5`,
       `supplier5partno`              AS `Supplier Part Number 5`,
       `supplier6`                    AS `Supplier 6`,
       `supplier6partno`              AS `Supplier Part Number 6`,
       `SupplierDevicePackage`        AS `Supplier Device Package`,
       `symbolpath`                   AS `Library Path`,
       `symbolref`                    AS `Library Ref`,
       `type`                         AS `Type`,
       `value`                        AS `Value`,
       `VoltageDCReverseVrMax`        AS `Voltage - DC Reverse (Vr) (Max)`,
       `VoltageForwardVfMaxIf`        AS `Voltage - Forward (Vf) (Max) @ If`
FROM t_DiodesRectifiersDiscrete t;
