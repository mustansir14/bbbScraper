<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport;

$config = require __DIR__."/config.php";

$srcDb = new Db();
$srcDb->connectOrDie( $config["source_db"]["host"], $config["source_db"]["user"], $config["source_db"]["pass"], $config["source_db"]["name"] );

$destDb = new Db();
$destDb->connectOrDie(  $config["dest_db"]["host"], $config["dest_db"]["user"], $config["dest_db"]["pass"], $config["dest_db"]["name"] );

$companies = $srcDb->queryColumn("select company_id, count(*) cnt from complaint group by company_id having cnt > 50", "company_id" );
if ( !$companies ) die( $srcDb->getExtendedError() );

$exporter = new CBExport( $destDb );

foreach( $companies as $companyId )
{
    $sourceCompanyRow = $srcDb->selectRow( "*", "company", [ "company_id" => $companyId ] );
    if ( !$sourceCompanyRow ) die( $srcDb->getExtendedError() );

    print_r( $sourceCompanyRow );

    #####################################################################

    $destCompanyID = 0;
    $destBusinessID = 0;

    #####################################################################

    #$exporter->removeCompanyByImportID( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ) );

    $destCompanyID = $exporter->addCompany( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ), [
        "name" => $sourceCompanyRow["company_name"],
        "import_data" => [
            "company_id" => $sourceCompanyRow["company_id"],
            "company_name" => $sourceCompanyRow["company_name"],
            "company_url"  => $sourceCompanyRow["url"],
            "scraper" => "BBB Mustansir",
            "version" => 1,
        ]
    ] );
    if ( !$destCompanyID ) die( $exporter->getErrorsAsString() );

    #####################################################################

    # Need many information for business

    /*
     *
     * $exporter->removeBusinessByImportID( $exporter->getBusinessImportID( $sourceCompanyRow["company_id"] ) );
    if ( !$exporter->hasBusiness( $sourceCompanyRow["company_id"] ) )
    {
        $destBusinessID = $exporter->addBusiness( $exporter->getBusinessImportID( $sourceCompanyRow["company_id"] ), [
            "name" => $sourceCompanyRow["company_name"],
            "import_data" => [
                "company_id" => $sourceCompanyRow["company_id"],
                "company_name" => $sourceCompanyRow["company_name"],
                "company_url"  => $sourceCompanyRow["url"],
                "scraper" => "BBB Mustansir",
                "version" => 1,
            ]
        ]);

        if ( !$destBusinessID ) die( $exporter->getErrorsAsString() );
    }*/

    #####################################################################

    #$exporter->removeUserByImportID($exporter->getUserImportID( "test4567" ));
    $userID = $exporter->addUser( $exporter->getUserImportID( "test4567" ), [
        "user_name" => "test4567",
        "import_data" => "asdsa"
    ] );
    if ( !$userID ) die( $exporter->getErrorsAsString() );

    var_dump($userID);
    exit;

    #####################################################################

    $limit = 5000;
    $fromID = -1;
    $skip = 50;
    $counter = 0;

    while ( 1 )
    {
        $complaints = $srcDb->selectArray(
            "*",
            "complaint",
            "company_id = {$sourceCompanyRow["company_id"]}".( $fromID > 0 ? " and complaint_id < {$fromID}" : "" ),
            false,
            "complaint_id desc",
            $limit
        );
        if ( $complaints === false ) die( $srcDb->getExtendedError() );
        if ( !$complaints ) break;

        foreach( $complaints as $complaint )
        {
            $counter++;
            if ( $counter < $skip ) continue;

            $fromID = $complaint["complaint_id"];

            #echo $counter.") ".$complaint["complaint_date"].": ".substr( $complaint["complaint_text"], 0, 40 )."...\n";

            $exporter->removeComplaintByImportID( $exporter->getComplaintImportID( $complaint["complaint_id"] ) );
            $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ), [

            ] );

            if ( !$complaintID ) die( $exporter->getErrorsAsString() );

            exit;
        }
    }

    break;
}