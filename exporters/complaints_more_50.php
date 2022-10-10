<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport;
use DataExport\Helpers\TextFormatter;

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

    #print_r( $sourceCompanyRow );

    #####################################################################

    $destCompanyID = 0;
    $destBusinessID = 0;

    #####################################################################

    $recreateCompanyAllRecords = false;
    $makeSpamComplaints = false;

    #$exporter->removeCompanyByImportID( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ) );

    $companyName = TextFormatter::removeAbbreviationsFromCompanyName( $sourceCompanyRow["company_name"] );
    $destCompanyID = $exporter->addCompany( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ), [
        "name" => $sourceCompanyRow["company_name"],
        "import_data" => [
            "company_id" => $sourceCompanyRow["company_id"],
            "company_name" => $companyName,
            "company_url"  => $sourceCompanyRow["url"],
            "scraper" => "BBB Mustansir",
            "version" => 1,
        ]
    ] );
    if ( !$destCompanyID ) die( $exporter->getErrorsAsString() );

    var_dump( $sourceCompanyRow["company_name"], $destCompanyID );

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

    $limit = 5000;
    $fromID = -1;
    $skip = 50;
    $counter = 0;
    $faker = Faker\Factory::create();

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

            echo $counter.") ({$complaint['complaint_id']}) ".$complaint["complaint_date"].": ".substr( TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' ), 0, 40 )."...\n";

            $subject = explode( ".", $complaint["complaint_text"] );
            $subject = mb_strlen( $subject[0], "utf-8" ) > 15
                ? mb_substr( $subject[0], 0, 90, "utf-8" )
                : mb_substr( $complaint["complaint_text"], 0, 90, "utf-8" );
            $subject = preg_replace( "#[a-z0-9']{1,}$#si", "", $subject );


            if ( $recreateCompanyAllRecords )
            {
                $exporter->removeComplaintByImportID( $exporter->getComplaintImportID( $complaint["complaint_id"] ) );
            }

            $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ), [
                "company_id" => $destCompanyID,
                "subject" => $subject,
                "text" => TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' ),
                "date" => $complaint["complaint_date"],
                "user_name" => $faker->name(),
                "import_data" => [
                    "company_id" => $sourceCompanyRow["company_id"],
                    "company_url"  => $sourceCompanyRow["url"],
                    "complaint_id" => $complaint["complaint_id"],
                    "scraper" => "BBB Mustansir",
                    "version" => 1,
                ]
            ] );

            if ( !$complaintID ) die( $exporter->getErrorsAsString() );

            if ( $makeSpamComplaints )
            {
                $exporter->spamComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ), basename( __FILE__ ).": make private" );
            } else {
                $exporter->unspamComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ) );
            }

            if ( $complaint["company_response_text"] )
            {
                echo $complaint["company_response_text"]."\n";

                if ( $recreateCompanyAllRecords )
                {
                    $exporter->removeUserByImportID( $exporter->getUserImportID( "{$companyName} Support" ) );
                    $exporter->removeCommentByImportID( $exporter->getCommentImportID( $complaint["complaint_id"] ) );
                }

                $commentID = $exporter->addComment( $exporter->getCommentImportID( $complaint["complaint_id"] ), [
                    "complaint_id" => $complaintID,
                    "text" => TextFormatter::fixText( $complaint["company_response_text"], 'complaintsboard.com' ),
                    "date" => $complaint["company_response_date"],
                    "user_name" => "{$companyName} Support",
                    "user_date" => date( "Y-m-d", strtotime( $complaint["company_response_date"] ) - 1 * 365 * 24 * 3600 ),
                    "import_data" => [
                        "company_id" => $sourceCompanyRow["company_id"],
                        "company_url"  => $sourceCompanyRow["url"],
                        "complaint_id" => $complaint["complaint_id"],
                        "scraper" => "BBB Mustansir",
                        "version" => 1,
                    ]
                ] );

                if ( !$commentID ) die( $exporter->getErrorsAsString() );
            }
        }
    }

    break;
}