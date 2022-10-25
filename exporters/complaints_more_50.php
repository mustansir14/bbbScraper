<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport;
use DataExport\Helpers\TextFormatter;

$config = require __DIR__."/config.php";

##################################################################################

$profileName = "local";
$removeAll = true; # set true if need remove all records from db
$createAll = true; # set true if need add new records
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = 2;
$makeSpamComplaints = true;
$importInfoScraper = "BBB Mustansir";

##################################################################################

$profile = $config["dest"][ $profileName ];
if ( !is_array( $profile ) ) die( "Error: no profile data" );

$srcDb = new Db();
$srcDb->connectOrDie( $config["source_db"]["host"], $config["source_db"]["user"], $config["source_db"]["pass"], $config["source_db"]["name"] );

$destDb = new Db();
$destDb->connectOrDie(  $profile["db"]["host"], $profile["db"]["user"], $profile["db"]["pass"], $profile["db"]["name"] );

##################################################################################

$companies = $srcDb->queryColumn("select company_id, count(*) cnt from complaint group by company_id having cnt > 50", "company_id" );
if ( !$companies ) die( $srcDb->getExtendedError() );

# ONLY FOR TESTING, IN RELEASE MUST BE REMOVED
$companies = [
    42297,
];

$exporter = new CBExport( $destDb );

foreach( $companies as $companyNbr => $companyId )
{
    if( $maxCompanies > 0 && $companyNbr >= $maxCompanies )
    {
        break;
    }

    $sourceCompanyRow = $srcDb->selectRow( "*", "company", [ "company_id" => $companyId, 'half_scraped' => 0 ] );
    if ( !$sourceCompanyRow ) die( $srcDb->getExtendedError() );

    #print_r( $sourceCompanyRow );

    #####################################################################

    $destCompanyID = 0;
    $destBusinessID = 0;
    $companyNameOriginal = $sourceCompanyRow[ "company_name" ];
    $companyNameWithoutAbbr = TextFormatter::removeAbbreviationsFromCompanyName( $sourceCompanyRow[ "company_name" ] );

    #####################################################################

    if ( $removeAll )
    {
        #echo "Remove business: ".$sourceCompanyRow["company_id"]."\n";

        if ( !$exporter->removeBusinessByImportID( $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }

        #echo "Remove company: ".$sourceCompanyRow["company_id"]."\n";

        if ( !$exporter->removeCompanyByImportID( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }
    }

    if ( $createAll )
    {
        #echo "Create company: ".$sourceCompanyRow["company_id"]."\n";

        $destCompanyID = $exporter->addCompany( $exporter->getCompanyImportID( $sourceCompanyRow[ "company_id" ] ), [
            "name"        => $sourceCompanyRow[ "company_name" ],
            "import_data" => [
                "company_id"   => $sourceCompanyRow[ "company_id" ],
                "company_name" => $companyNameWithoutAbbr,
                "company_url"  => $sourceCompanyRow[ "url" ],
                "scraper"      => $importInfoScraper,
                "version"      => 1,
            ],
        ] );

        if ( !$destCompanyID )
        {
            die( $exporter->getErrorsAsString() );
        }
    }

    $userName = "{$companyNameWithoutAbbr} Support";

    if ( $removeAll )
    {
        #echo "Remove user: {$userName}\n";

        if ( !$exporter->removeUserByImportID( $exporter->getUserImportID( $userName ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }
    }

    #####################################################################

    $businessImportID = $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] );

    if ( $createAll )
    {
        $destBusinessID = $exporter->hasBusiness( $destCompanyID );
        if ( !$destBusinessID )
        {
            if ( !preg_match( '#bbb\.org/(us|ca)/#si', $sourceCompanyRow["url"], $match ) )
            {
                echo "Url: ".$sourceCompanyRow["url"]."\n";
                die( "Error:unknown country in url!" );
            }

            $countryShortName = $match[1];

            $destBusinessID = $exporter->addBusiness( $businessImportID, [
                "name"        => $companyNameWithoutAbbr,
                "ltd"         => $companyNameOriginal,
                "country"     => $countryShortName,
                "state"       => $sourceCompanyRow["address_region"],
                "city"        => $sourceCompanyRow["address_locality"],
                "address"     => $sourceCompanyRow["street_address"],
                "zip"         => $sourceCompanyRow["postal_code"],
                "phone"       => $sourceCompanyRow["phone"],
                "website"     => array_map( "trim", explode( "\n", $sourceCompanyRow[ "website" ] ) ),
                "import_data" => [
                    "company_id"   => $sourceCompanyRow[ "company_id" ],
                    "company_name" => $sourceCompanyRow[ "company_name" ],
                    "company_url"  => $sourceCompanyRow[ "url" ],
                    "scraper"      => $importInfoScraper,
                    "version"      => 1,
                ],
            ] );

            if ( !$destBusinessID )
            {
                die( $exporter->getErrorsAsString() );
            }

            if ( !$exporter->linkCompanyToBusiness( $destCompanyID, $destBusinessID ) )
            {
                die( $exporter->getErrorsAsString() );
            }
        }
    }

    # check if business created by scraper or is BN already exists
    $businessRow = $exporter->getBusiness( $businessImportID );
    if ( $businessRow )
    {
        if ( $makeSpamComplaints )
        {
            $exporter->disableBusiness( $businessImportID );
        }
        else
        {
            $exporter->enableBusiness( $businessImportID );
        }
    }

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
            $isInsert = $createAll && ( $addOnly < 1 || $addOnly === $counter );

            if ( $removeAll )
            {
                #echo "Remove complaint: ".$complaint["complaint_id"]."\n";

                if ( !$exporter->removeComplaintByImportID( $exporter->getComplaintImportID( $complaint["complaint_id"])) )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }

            if ( $isInsert )
            {
                /*echo $counter.") ({$complaint['complaint_id']}) ".$complaint["complaint_date"].": ".
                    substr( TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' ), 0, 60 )."...\n".
                    "Update: ".
                    substr( TextFormatter::fixText( $complaint["company_response_text"], 'complaintsboard.com' ), 0, 60 )."...\n";*/

                $subject = explode( ".", $complaint["complaint_text"] );

                $subject = mb_strlen( $subject[0], "utf-8" ) > 15
                    ? mb_substr( $subject[0], 0, 90, "utf-8" )
                    : mb_substr( $complaint["complaint_text"], 0, 90, "utf-8" );

                $subject = stripos( $subject, ' ' ) !== false
                    ? preg_replace( "#[a-z0-9']{1,}$#si", "", $subject )
                    : $subject;
                #echo "Insert complaint\n";

                print_r( $complaint );

                $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $complaint[ "complaint_id" ] ), [
                    "company_id"  => $destCompanyID,
                    "subject"     => $subject,
                    "text"        => TextFormatter::fixText( $complaint[ "complaint_text" ], 'complaintsboard.com' ),
                    "date"        => $complaint[ "complaint_date" ],
                    "user_name"   => $faker->name(),
                    "import_data" => [
                        "company_id"   => $sourceCompanyRow[ "company_id" ],
                        "complaint_id" => $complaint[ "complaint_id" ],
                        "company_url"  => $sourceCompanyRow[ "url" ],
                        "type"         => "complaint",
                        "scraper"      => $importInfoScraper,
                        "version"      => 1,
                    ],
                ] );
                if ( !$complaintID )
                {
                    die( $exporter->getErrorsAsString() );
                }

                if ( $makeSpamComplaints )
                {
                    $exporter->spamComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ), basename( __FILE__ ).": make private" );
                } else {
                    $exporter->unspamComplaint( $exporter->getComplaintImportID( $complaint["complaint_id"] ) );
                }
            }

            if ( $complaint["company_response_text"] )
            {
                $userName = "{$companyNameWithoutAbbr} Support";

                if ( $removeAll )
                {
                    #echo "Remove comment: ".$complaint["complaint_id"]."\n";

                    if ( !$exporter->removeCommentByImportID( $exporter->getCommentImportID( $complaint["complaint_id"] ) ) )
                    {
                        die( $exporter->getErrorsAsString() );
                    }
                }

                if ( $isInsert )
                {
                    #echo "Insert update to {$complaintID}\n";
                    #echo $complaint["company_response_text"]."\n";

                    $commentID = $exporter->addComment( $exporter->getCommentImportID( $complaint["complaint_id"] ), [
                        "complaint_id" => $complaintID,
                        "text" => TextFormatter::fixText( $complaint["company_response_text"], 'complaintsboard.com' ),
                        "is_update" => true,
                        "date" => $complaint["company_response_date"],
                        "user_name" => $userName,
                        "user_date" => date( "Y-m-d", strtotime( $complaint["company_response_date"] ) - 1 * 365 * 24 * 3600 ),
                        "user_email" => $faker->email(),
                        "user_support" => $destBusinessID,
                        "import_data" => [
                            "company_id" => $sourceCompanyRow["company_id"],
                            "complaint_id" => $complaint["complaint_id"],
                            "company_url"  => $sourceCompanyRow["url"],
                            "type" => "complaint-response",
                            "scraper" => $importInfoScraper,
                            "version" => 1,
                        ]
                    ] );

                    if ( !$commentID ) die( $exporter->getErrorsAsString() );
                }
            }

            if ( $isInsert )
            {
                $exporter->callUpdateComplaint( $complaintID );
            }
        }
    }

    if ( $destBusinessID )
    {
        $exporter->callUpdateCompany( $destCompanyID );
        $exporter->callUpdateBusiness( $destBusinessID );

        echo $profile["host"]."/asd-b".$destBusinessID."\n";
    } else {
        echo "Removed all from company: ".$sourceCompanyRow["company_id"]."\n";
    }
}